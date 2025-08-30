import os
import pexpect
import subprocess
import uuid
import logging
import time
import threading
import ptyprocess
import pyte
import select
import psutil
from collections import deque
from enum import Enum
from dataclasses import dataclass, field

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

@dataclass
class CommandOutput:
    text: str           # stdout if success, stderr if failure
    stdout: str         # Raw stdout
    stderr: str         # Raw stderr
    is_success: bool    # Based on return_code == 0
    pid: int           # Process ID of the executed command  
    return_code: int   # Exit status
    _process: subprocess.Popen = None

    def __str__(self):
        return self.text or ""


@dataclass
class BackgroundCommandOutput:
    """
    Extension of CommandOutput for background processes that allows registering
    callbacks to be executed when the command completes.
    """
    pid: int           # Process ID of the executed command  
    _process: subprocess.Popen = None

    _callbacks: list = field(default_factory=list, init=False, repr=False)
    _monitor_thread: threading.Thread = field(default=None, init=False, repr=False)
    _completed: bool = field(default=False, init=False, repr=False)
    _final_output: CommandOutput = field(default=None, init=False, repr=False)
    _lock: threading.Lock = field(default_factory=threading.Lock, init=False, repr=False)
    
    def register_callback(self, callback):
        """
        Register a callback function to be called when the command completes.
        The callback should accept a CommandOutput object as its argument.
        
        Args:
            callback: A function that takes a CommandOutput object as its parameter
                     and performs some action with the final command output.
        
        Returns:
            self: To allow for method chaining
        
        Example:
            def on_complete(output):
                print(f"Command finished with exit code: {output.return_code}")
                print(f"Output: {output.stdout}")
            
            bg_cmd = bash("sleep 5 && echo 'Done'", background=True)
            bg_cmd.register_callback(on_complete)
        """
        with self._lock:
            if self._completed:
                # If already completed, call the callback immediately
                callback(self._final_output)
            else:
                self._callbacks.append(callback)
        return self
    
    def _start_monitoring(self, suppress_output=False):
        """Start a thread to monitor the process and trigger callbacks on completion"""
        if self._monitor_thread is None and self._process is not None:
            self._monitor_thread = threading.Thread(
                target=self._monitor_process, 
                args=(suppress_output,),
                daemon=True
            )
            self._monitor_thread.start()
    
    def _monitor_process(self, suppress_output=False):
        """Monitor the process and collect output when it completes"""
        if not self._process:
            return
        
        # Buffers to collect output
        stdout_buffer = []
        stderr_buffer = []
        
        def read_stderr():
            try:
                for line in iter(self._process.stderr.readline, ''):
                    if not line:
                        break
                    stderr_buffer.append(line)
                    if not suppress_output:
                        print(line, end='', flush=True)
            except:
                pass
            finally:
                try:
                    self._process.stderr.close()
                except:
                    pass
        
        # Start stderr reading thread
        stderr_thread = threading.Thread(target=read_stderr, daemon=True)
        stderr_thread.start()
        
        # Read stdout
        try:
            for line in iter(self._process.stdout.readline, ''):
                if not line:
                    break
                stdout_buffer.append(line)
                if not suppress_output:
                    print(line, end='', flush=True)
        except:
            pass
        finally:
            try:
                self._process.stdout.close()
            except:
                pass
        
        # Wait for process to complete
        returncode = self._process.wait()
        stderr_thread.join(timeout=5)
        
        # Prepare final output
        stdout_text = ''.join(stdout_buffer)
        stderr_text = ''.join(stderr_buffer)
        is_success = returncode == 0
        text = stdout_text if is_success else stderr_text
        
        # Create final CommandOutput
        final_output = CommandOutput(
            text=text,
            stdout=stdout_text,
            stderr=stderr_text,
            is_success=is_success,
            pid=self._process.pid,
            return_code=returncode,
            _process=self._process
        )
        
        # Update our state and trigger callbacks
        with self._lock:
            self._final_output = final_output
            self._completed = True
            
            # Update our own fields with the final values
            self.text = text
            self.stdout = stdout_text
            self.stderr = stderr_text
            self.is_success = is_success
            self.return_code = returncode
            
            # Trigger all registered callbacks
            for callback in self._callbacks:
                try:
                    callback(final_output)
                except Exception as e:
                    logger.error(f"Error in callback: {e}")
    
    def wait(self, timeout=None):
        """
        Wait for the background command to complete and return the final CommandOutput.
        
        Args:
            timeout: Maximum time to wait in seconds (None for no timeout)
            
        Returns:
            CommandOutput: The final command output with stdout, stderr, etc.
            
        Raises:
            TimeoutError: If the timeout is exceeded
        """
        if self._monitor_thread:
            self._monitor_thread.join(timeout=timeout)
            if self._monitor_thread.is_alive():
                raise TimeoutError(f"Command did not complete within {timeout} seconds")
        
        with self._lock:
            return self._final_output if self._final_output else self
    
    def is_complete(self):
        """
        Check if the background command has completed.
        
        Returns:
            bool: True if the command has completed, False otherwise
        """
        with self._lock:
            return self._completed
    
    def kill(self):
        """
        Kill the background process if it's still running.
        
        Returns:
            bool: True if the process was killed, False if it was already completed
        """
        if self._process and not self._completed:
            try:
                self._process.kill()
                return True
            except:
                pass
        return False
    
    def terminate(self):
        """
        Terminate the background process if it's still running (more graceful than kill).
        
        Returns:
            bool: True if the process was terminated, False if it was already completed
        """
        if self._process and not self._completed:
            try:
                self._process.terminate()
                return True
            except:
                pass
        return False

@dataclass
class PartialCommandOutput:
    text: str                   # Captured output/screen content
    pid: int                   # Process ID
    return_code: int = 0       # Exit code (where available)
    is_success: bool = True    # return_code == 0
    _process: subprocess.Popen = None

    def __str__(self):
        return self.text or ""


class SessionStatus(Enum):
    IDLE = "idle"
    CHANGING = "changing"
    STABLE = "stable"
    STOPPED = "stopped"


logger = logging.getLogger("ShellSession")

global_shell_session = None
global_cli_session = None

def bash(cmd_string, suppress_output=False, suppress_exception=False, background=False):
    """
    Run a shell command in a one-off subprocess, streaming its output in real time.
    Captures stdout and stderr separately while maintaining real-time output.
    
    Args:
        cmd_string: The shell command to execute
        suppress_output: If True, suppress real-time output printing
        suppress_exception: If True, don't raise exception on non-zero exit
        background: If True, run command in background and return BackgroundCommandOutput
    
    Returns:
        CommandOutput or BackgroundCommandOutput: Command result object
        - For foreground: CommandOutput with immediate results
        - For background: BackgroundCommandOutput with callback support
    
    Raises:
        CalledProcessError: On non-zero exit unless suppress_exception=True
    """
    process = subprocess.Popen(
        cmd_string,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        stdin=subprocess.DEVNULL,
        bufsize=1,
        text=True,
        preexec_fn=os.setsid
    )

    if background:
        # Return a BackgroundCommandOutput with callback support
        bg_output = BackgroundCommandOutput(
            pid=process.pid,
            _process=process
        )
        # Start monitoring the process in a background thread
        bg_output._start_monitoring(suppress_output=suppress_output)
        return bg_output

    # Buffers to collect output
    stdout_buffer = []
    stderr_buffer = []

    def read_stderr():
        for line in iter(process.stderr.readline, ''):
            stderr_buffer.append(line)
            if not suppress_output:
                print(line, end='', flush=True)
        process.stderr.close()
    
   
    stderr_thread = threading.Thread(target=read_stderr)
    stderr_thread.start()
    
    for line in iter(process.stdout.readline, ''):
        stdout_buffer.append(line)
        if not suppress_output:
            print(line, end='', flush=True)

    process.stdout.close()
    returncode = process.wait()
    stderr_thread.join()
    
    stdout_text = ''.join(stdout_buffer)
    stderr_text = ''.join(stderr_buffer)
    is_success = returncode == 0
    text = stdout_text if is_success else stderr_text
    
    # Create CommandOutput object
    result = CommandOutput(
        text=text,
        stdout=stdout_text,
        stderr=stderr_text,
        is_success=is_success,
        pid=process.pid,
        return_code=returncode,
        _process=process
    )

    if returncode != 0 and not suppress_exception:
        raise subprocess.CalledProcessError(returncode, cmd_string)

    return result


def experimental_bash(cmd_string, suppress_exception=False):
    """
    Run a shell command in a persistent bash session, streaming its output in real time.
    This is an experimental feature and may not work as expected.
    Args:
        cmd_string (str): The shell command to execute.
        suppress_exception (bool): If True, suppress exceptions on non-zero exit code.
        
    Returns:
        PartialCommandOutput: Object with text, pid, return_code, and is_success.
    """
    global global_shell_session
    if global_shell_session is None:
        global_shell_session = ShellSession()
    return global_shell_session.run_command(cmd_string, suppress_exception=suppress_exception)

class ShellSession:
    """
    A class that manages a persistent interactive bash session using pexpect.
    Provides methods to run commands and process their output through callbacks.
    """
    
    def __init__(self, output_callback=None, timeout=60):
        """
        Initialize a new ShellSession with a persistent bash shell.
        
        Args:
            output_callback (callable, optional): A function that will be called with each 
                                                 line of output. If it returns True, the session will exit.
            timeout (int): Timeout in seconds for expect operations.
        """
        self._output_callback = output_callback
        self._timeout = timeout
        # Use UUID-based prompt marker to avoid conflicts with command output
        self._prompt = f'PEXPECT_PROMPT_{uuid.uuid4().hex}>'
        
        # Create a custom output handler
        class CustomPexpectOutputHandler:
            def __init__(self, callback):
                self.callback = callback
                
            def write(self, data):
                return self.callback(data)
                
            def flush(self):
                pass
        
        # Set up custom output handling
        def custom_output_handler(data):
            # Print the data to stdout (except our custom prompt)
            if self._prompt not in data:
                print(data, end='', flush=True)
            
            # Process the data if callback is provided
            if self._output_callback and data:
                if self._output_callback(data):
                    logger.info("Callback triggered exit condition.")
                    print("\nCallback triggered exit condition.")
                    return True
            return False
        
        # Start a persistent bash session
        logger.info(f"Starting persistent bash session with timeout {timeout} seconds")
        self._child = pexpect.spawn(
            '/bin/bash',
            ['--norc', '--noprofile'], 
            encoding='utf-8',
            echo=False,
            timeout=self._timeout
        )
        
        # Set up a custom prompt to reliably detect command completion
        self._child.sendline(f'export PS1="{self._prompt}"')
        self._child.expect(self._prompt)
        
        # Set up output handling
        self._child.logfile_read = CustomPexpectOutputHandler(custom_output_handler)
        
    def run_command(self, cmd_string: str, suppress_exception: bool = False) -> PartialCommandOutput:
        """
        Runs a command in the persistent bash session, processing real-time output.
        
        Args:
            cmd_string (str): The shell command to execute.
            suppress_exception (bool): If True, suppress exceptions on non-zero exit code.
            
        Returns:
            PartialCommandOutput: Object with text, pid, return_code, and is_success.
        """
        logger.info(f"Running command: {cmd_string}")
        
        # Buffer to collect output
        output_buffer = []
        
        try:
            # Send the command
            self._child.sendline(cmd_string)
            
            # Process output until we see our prompt again (command completed)
            while True:
                try:
                    # Wait for prompt, EOF, or timeout
                    index = self._child.expect([self._prompt, pexpect.EOF, pexpect.TIMEOUT])
                    
                    # Get the output since the last expect
                    output = self._child.before
                    if output:
                        output_buffer.append(output)
                    
                    # Process the output if callback is provided
                    if self._output_callback and output:
                        if self._output_callback(output):
                            logger.info("Callback triggered exit condition.")
                            print("\nCallback triggered exit condition.")
                            return PartialCommandOutput(
                                text=''.join(output_buffer).strip(),
                                pid=self._child.pid,
                                return_code=0,
                                is_success=True
                            )
                    
                    # Check if we've reached the prompt (command completed)
                    if index == 0:  # prompt
                        logger.info("Command completed. Getting exit code.")
                        
                        # Get the exit code
                        exit_code_marker = f"EXITCODE_{uuid.uuid4().hex}"
                        self._child.sendline(f"echo $?; echo {exit_code_marker}")
                        self._child.expect(exit_code_marker)
                        
                        # Extract the exit code from the output
                        exit_code_output = self._child.before.strip()
                        exit_code_lines = exit_code_output.splitlines()
                        try:
                            exit_code = int(exit_code_lines[-1]) if exit_code_lines else 0
                        except ValueError:
                            exit_code = 1
                        
                        # Wait for the prompt again
                        self._child.expect(self._prompt)
                        
                        # Create result object
                        result = PartialCommandOutput(
                            text=''.join(output_buffer).strip(),
                            pid=self._child.pid,
                            return_code=exit_code,
                            is_success=exit_code == 0
                        )
                        
                        # Raise exception if requested and exit code is non-zero
                        if exit_code != 0 and not suppress_exception:
                            raise subprocess.CalledProcessError(
                                exit_code, cmd_string, f"Command failed with exit code {exit_code}: {cmd_string}"
                            )
                        
                        logger.info(f"Command completed with exit code {exit_code}.")
                        return result
                        
                    # Check if we've reached EOF
                    if index == 1:  # pexpect.EOF
                        logger.info("Session ended unexpectedly (EOF).")
                        return PartialCommandOutput(
                            text=''.join(output_buffer).strip(),
                            pid=self._child.pid if self._child else 0,
                            return_code=1,
                            is_success=False
                        )
                        
                    # Check if we've timed out
                    if index == 2:  # pexpect.TIMEOUT
                        logger.debug("Timeout waiting for output, continuing...")
                        continue
                        
                except pexpect.TIMEOUT:
                    logger.debug("Timeout waiting for output, continuing...")
                    continue
                except pexpect.EOF:
                    logger.info("Session ended unexpectedly (EOF).")
                    return PartialCommandOutput(
                        text=''.join(output_buffer).strip(),
                        pid=self._child.pid if self._child else 0,
                        return_code=1,
                        is_success=False
                    )
            
        except KeyboardInterrupt:
            logger.info("Process interrupted by user.")
            return PartialCommandOutput(
                text=''.join(output_buffer).strip(),
                pid=self._child.pid if self._child else 0,
                return_code=1,
                is_success=False
            )
        
    def close(self):
        """Close the persistent bash session."""
        logger.info("PexpectSession closed")
        if self._child and self._child.isalive():
            self._child.sendline("exit")
            self._child.terminate(force=True)

class CLISession:
    """
    General-purpose CLI session manager for controlling interactive command-line tools.
    Provides pseudo-terminal support, screen monitoring, and programmatic control.
    Based on termexec patterns for robust CLI automation.
    """
    
    def __init__(self, width=80, height=24, program=None, args=None, suppress_output=False):
        """
        Initialize a new CLI session with optional program to launch.
        
        Args:
            width (int): Terminal width in characters.
            height (int): Terminal height in characters.
            program (str): Optional program to launch (e.g., 'python', 'node')
            args (list): Optional program arguments
            suppress_output (bool): If True, suppress real-time output printing
        """
        self.width = width
        self.height = height
        self.program = program
        self.args = args or []
        self.suppress_output = suppress_output
        
        # Screen state management
        self.screen = pyte.Screen(width, height)
        self.stream = pyte.Stream(self.screen)
        self.last_screen_update = time.time()
        self.screen_lock = threading.Lock()
        
        # Session state
        self.is_running = False
        self.screen_snapshots = deque(maxlen=5000)  # Rolling buffer for screen history
        self.snapshot_interval = 0.001  # 1000 FPS
        
        # Create pseudo-terminal
        if program:
            cmd = [program] + self.args
            logger.info(f"Starting CLI session: {' '.join(cmd)}")
        else:
            cmd = ['/bin/bash', '--norc', '--noprofile']
            logger.info("Starting bash shell session")
            
        self.pty = ptyprocess.PtyProcess.spawn(
            cmd,
            dimensions=(height, width),
            env=dict(os.environ, TERM='vt100')
        )
        
        # Start background monitoring
        self._stop_event = threading.Event()
        self._monitor_thread = threading.Thread(target=self._monitor_output, daemon=True)
        self._snapshot_thread = threading.Thread(target=self._snapshot_loop, daemon=True)
        
        self._monitor_thread.start()
        self._snapshot_thread.start()
        self.is_running = True
        
        # Wait for initial setup
        time.sleep(0.5)
        self.wait_for_stability()
        
    def _monitor_output(self):
        """
        Background thread that continuously reads PTY output and updates screen state.
        """
        while not self._stop_event.is_set():
            try:
                ready, _, _ = select.select([self.pty.fd], [], [], self.snapshot_interval)
                
                if ready:
                    try:
                        data = self.pty.read(1024)
                        if data:
                            with self.screen_lock:
                                self.stream.feed(data.decode('utf-8', errors='replace'))
                                self.last_screen_update = time.time()
                                
                            if not self.suppress_output:
                                print(data.decode('utf-8', errors='replace'), end='', flush=True)
                            
                    except (OSError, EOFError):
                        # PTY closed or no data available
                        break
                        
            except Exception as e:
                logger.debug(f"Monitor thread error: {e}")
                break
    
    def _snapshot_loop(self):
        """
        Continuous screen monitoring at 1000 FPS.
        Maintains a rolling buffer of screen snapshots for comparison.
        """
        while not self._stop_event.is_set():
            try:
                screen_content = self.read_screen_immediate()
                snapshot = {
                    'timestamp': time.time(),
                    'screen': screen_content
                }
                self.screen_snapshots.append(snapshot)
                time.sleep(self.snapshot_interval)
            except Exception as e:
                logger.debug(f"Snapshot thread error: {e}")
                break
    
    def read_screen_immediate(self):
        """
        Read current screen state immediately without stability check.
        
        Returns:
            str: Current screen content as string.
        """
        with self.screen_lock:
            return '\n'.join(line.rstrip() for line in self.screen.display)
                
    def read_screen(self):
        """
        Read current screen state with stability check.
        Waits for screen to be stable.
        
        Returns:
            str: Current screen content as string.
        """
        # Wait for stability (screen hasn't changed for at least 16ms)
        for _ in range(3):
            if time.time() - self.last_screen_update >= 0.016:  # 16ms
                return self.read_screen_immediate()
            time.sleep(0.016)
            
        # Return current state even if not fully stable
        return self.read_screen_immediate()
            
    def wait_for_stability(self, max_wait=5.0, stable_duration=0.5):
        """
        Wait for screen to become stable (no changes for a period).
        
        Args:
            max_wait (float): Maximum time to wait in seconds.
            stable_duration (float): Duration of stability required in seconds.
            
        Returns:
            bool: True if screen became stable, False if timed out.
        """
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            if time.time() - self.last_screen_update >= stable_duration:
                return True
            time.sleep(0.05)
            
        return False
    
    def wait_for_stability_connections(self, idle_time=5, poll_interval=1, max_wait=30):
        """
        Wait until network connections are quiet (no active requests).
        
        Args:
            idle_time (float): How long network must be idle to be considered stable
            poll_interval (float): How often to check network activity
            max_wait (float): Maximum time to wait before giving up
            
        Returns:
            bool: True if network became stable, False if timed out or process not accessible
        """
        if not self.pty.pid:
            logger.warning("No PID available for network monitoring")
            return False
            
        try:
            proc = psutil.Process(self.pty.pid)
            last_activity = time.time()
            start_time = time.time()
            
            logger.debug(f"Monitoring network connections for PID {self.pty.pid}")
            
            while time.time() - start_time < max_wait:
                try:
                    # Get all network connections for the process
                    conns = proc.net_connections(kind='inet')
                    
                    # Filter out certain types of connections that we don't care about
                    active_conns = []
                    for conn in conns:
                        # Skip localhost connections (often persistent)
                        if (hasattr(conn, 'laddr') and conn.laddr and 
                            conn.laddr.ip in ['127.0.0.1', '::1']):
                            continue
                        # Only count established connections
                        if conn.status == psutil.CONN_ESTABLISHED:
                            active_conns.append(conn)
                    
                    if active_conns:
                        last_activity = time.time()
                        logger.debug(f"Active connections found: {len(active_conns)}")
                    
                    # Check if we've been idle long enough
                    if time.time() - last_activity >= idle_time:
                        logger.debug("Network connections are stable")
                        return True
                        
                except psutil.AccessDenied:
                    logger.warning("Access denied when checking network connections")
                    return False
                except psutil.NoSuchProcess:
                    logger.debug("Process no longer exists")
                    return False
                    
                time.sleep(poll_interval)
                
            logger.debug(f"Network stability timeout after {max_wait}s")
            return False
            
        except Exception as e:
            logger.error(f"Error monitoring network connections: {e}")
            return False
    
    def wait_for_complete_stability(self, screen_stable_duration=0.5, network_idle_time=3, 
                                  max_wait=30, check_network=True):
        """
        Wait for both screen and network stability (comprehensive stability check).
        
        Args:
            screen_stable_duration (float): Screen stability requirement
            network_idle_time (float): Network idle time requirement  
            max_wait (float): Maximum total time to wait
            check_network (bool): Whether to check network stability
            
        Returns:
            dict: Status of both stability checks
        """
        start_time = time.time()
        screen_stable = False
        network_stable = False
        
        logger.debug(f"Waiting for complete stability (screen + network)")
        
        # First wait for screen stability with shorter timeout
        screen_timeout = min(max_wait * 0.6, 10.0)  # 60% of max_wait or 10s, whichever is smaller
        screen_stable = self.wait_for_stability(
            max_wait=screen_timeout, 
            stable_duration=screen_stable_duration
        )
        
        remaining_time = max_wait - (time.time() - start_time)
        
        if check_network and remaining_time > 0:
            # Then wait for network stability
            network_stable = self.wait_for_stability_connections(
                idle_time=network_idle_time,
                max_wait=remaining_time
            )
        else:
            network_stable = True  # Skip network check if disabled
            
        result = {
            'screen_stable': screen_stable,
            'network_stable': network_stable,
            'overall_stable': screen_stable and network_stable,
            'elapsed_time': time.time() - start_time
        }
        
        logger.debug(f"Complete stability result: {result}")
        return result
    
    def get_status(self):
        """
        Get current session status based on recent screen activity.
        
        Returns:
            SessionStatus: Current status of the session.
        """
        if not self.is_running:
            return SessionStatus.STOPPED
            
        # Check recent snapshots for changes
        recent_snapshots = list(self.screen_snapshots)[-5:]  # Last 5 snapshots
        
        if len(recent_snapshots) < 2:
            return SessionStatus.IDLE
            
        # Check if all recent snapshots are identical
        first_screen = recent_snapshots[0]['screen']
        for snapshot in recent_snapshots[1:]:
            if snapshot['screen'] != first_screen:
                return SessionStatus.CHANGING
                
        return SessionStatus.STABLE

    def write(self, data):
        """
        Send input to the CLI tool.
        
        Args:
            data (str or bytes): Data to send.
        """
        if isinstance(data, str):
            data = data.encode('utf-8')
        try:
            return self.pty.write(data)
        except OSError as e:
            if e.errno == 5:  # Input/output error - PTY is closed
                self.logger.warning("PTY closed, cannot write data")
                return 0
            raise

    def send_key(self, key):
        """
        Send a specific key to the CLI tool.
        
        Args:
            key (str): Key to send ('enter', 'tab', 'esc', 'ctrl+c', etc.)
        """
        key_mappings = {
            'enter': b'\r',
            'return': b'\r', 
            'tab': b'\t',
            'esc': b'\x1b',
            'escape': b'\x1b',
            'ctrl+c': b'\x03',
            'ctrl+d': b'\x04',
            'ctrl+z': b'\x1a',
            'backspace': b'\x08',
            'delete': b'\x7f',
            'up': b'\x1b[A',
            'down': b'\x1b[B',
            'right': b'\x1b[C',
            'left': b'\x1b[D',
        }
        
        if key.lower() in key_mappings:
            return self.write(key_mappings[key.lower()])
        else:
            # Assume it's a regular character
            return self.write(key)

    def send_esc_key(self):
        """
        Send ESC key to interrupt CLI execution.
        """
        return self.send_key('esc')

    def send_ctrl_c(self):
        """
        Send Ctrl+C to interrupt CLI execution.
        """
        return self.send_key('ctrl+c')
    
    def send_enter(self):
        """
        Send Enter key to the CLI tool.
        """
        return self.send_key('enter')

    def signal(self, sig):
        """
        Send a signal to the process.
        
        Args:
            sig: Signal to send (e.g., signal.SIGINT, signal.SIGTERM)
        """
        if self.pty.pid:
            return os.kill(self.pty.pid, sig)

    def send_message(self, message, wait_for_response=True, timeout=30):
        """
        Send a message and optionally wait for response.
        
        Args:
            message (str): Message to send
            wait_for_response (bool): Whether to wait for screen to stabilize
            timeout (float): Timeout for waiting
            
        Returns:
            str: Screen content after message (if wait_for_response=True)
        """
        # Get screen state before sending
        old_screen = self.read_screen() if wait_for_response else None
        
        # Send the message
        self.write(message)
        
        if not wait_for_response:
            return None
            
        # Wait for screen to stabilize
        start_time = time.time()
        while time.time() - start_time < timeout:
            current_screen = self.read_screen()
            if current_screen != old_screen:
                # Screen changed, wait for stability
                if self.wait_for_stability(max_wait=2.0):
                    return current_screen
            time.sleep(0.1)
            
        # Timeout or no change
        return self.read_screen()

    def refocus_for_next_command(self):
        """
        Re-focus the CLI tool for the next command.
        """
        self.send_message(" ")
        self.send_key("backspace")
        return self.wait_for_complete_stability(
            network_idle_time=1.0, max_wait=1.0
        )

    def send_command(self, command, timeout=30):
        """
        Send a command followed by Enter and wait for response.
        
        Args:
            command (str): Command to send
            timeout (float): Timeout for response
            
        Returns:
            str: Screen content after command
        """
        screen_content = self.send_message(command + '\r', wait_for_response=True, timeout=timeout)
        return screen_content

    def find_new_message(self, old_screen, new_screen):
        """
        Find new message content by comparing screens.
        
        Args:
            old_screen (str): Previous screen state
            new_screen (str): Current screen state
            
        Returns:
            str: New message content or empty string if none found
        """
        old_lines = old_screen.split('\n')
        new_lines = new_screen.split('\n')
        
        # Find first non-matching line
        first_new_line = len(old_lines)
        for i, new_line in enumerate(new_lines):
            if i >= len(old_lines) or old_lines[i] != new_line:
                first_new_line = i
                break
        
        if first_new_line < len(new_lines):
            new_content = '\n'.join(new_lines[first_new_line:])
            return new_content.strip()
        
        return ""

    def run_command(self, cmd_string, suppress_exception=False):
        """
        Run a shell command in the CLI session and return structured output.
        
        Args:
            cmd_string (str): The shell command to execute.
            suppress_exception (bool): If True, suppress exceptions on error.
            
        Returns:
            PartialCommandOutput: Object with text (screen content), pid, return_code, and is_success.
        """
        try:
            # Send command and get screen content
            screen_content = self.send_command(cmd_string)
            
            # Create result object
            result = PartialCommandOutput(
                text=screen_content or "",
                pid=self.pty.pid if self.pty and hasattr(self.pty, 'pid') else 0,
                return_code=0,  # Default to success since we can't easily get exit codes from PTY
                is_success=True
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Command failed: {e}")
            
            # Create error result object
            result = PartialCommandOutput(
                text=str(e),
                pid=self.pty.pid if self.pty and hasattr(self.pty, 'pid') else 0,
                return_code=1,
                is_success=False
            )
            
            if not suppress_exception:
                raise
            return result

    def close(self):
        """
        Close the CLI session and clean up resources.
        """
        logger.info("Closing CLI session")
        self.is_running = False
        self._stop_event.set()
        
        # Give threads time to stop
        if self._monitor_thread.is_alive():
            self._monitor_thread.join(timeout=1.0)
        if self._snapshot_thread.is_alive():
            self._snapshot_thread.join(timeout=1.0)
            
        try:
            self.pty.terminate()
        except:
            pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class FilePoller:
    """
    Polls for the existence of a specific file and executes a callback when found.
    """
    
    def __init__(self, file_path, on_file_found_callback, check_interval=1):
        """
        Initialize a new FilePoller.
        
        Args:
            file_path (str): Path to the file to poll for.
            on_file_found_callback (callable): Function to call when the file is found.
            check_interval (int): How often to check for the file (seconds).
        """
        self.file_path = file_path
        self.on_file_found_callback = on_file_found_callback
        self.check_interval = check_interval
        self._stop_event = threading.Event()
        self._thread = None
        logger.info(f"FilePoller initialized for file: {file_path}")
        
    def start(self):
        """Start polling in a background thread."""
        if self._thread and self._thread.is_alive():
            logger.warning("Poller already running")
            return
            
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._poll_file)
        self._thread.daemon = True
        self._thread.start()
        logger.info("FilePoller started")
        
    def stop(self):
        """Stop the polling thread."""
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        logger.info("FilePoller stopped")
        
    def _poll_file(self):
        """Poll for the file existence."""
        while not self._stop_event.is_set():
            if os.path.exists(self.file_path):
                logger.info(f"Target file found: {self.file_path}")
                if self.on_file_found_callback:
                    self.on_file_found_callback()
                return
            time.sleep(self.check_interval)


def start_interactive_tool(program, width=80, height=24, args=None, suppress_output=False):
    """
    Start an interactive tool and return the session for control.
    
    Args:
        program (str): Program to launch (e.g., 'python')
        width (int): Terminal width  
        height (int): Terminal height
        args (list): Optional program arguments
        suppress_output (bool): If True, suppress real-time output printing
        
    Returns:
        CLISession: Session for controlling the tool
        
    Example:
        session = start_interactive_tool('python')
        session.send_command('1+1')
        response = session.read_screen()
        session.send_esc_key()  # Interrupt if needed
        session.close()
    """
    return CLISession(width=width, height=height, program=program, args=args, suppress_output=suppress_output)
