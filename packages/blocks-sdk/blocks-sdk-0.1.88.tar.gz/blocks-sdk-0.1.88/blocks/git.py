import os
import contextlib
from blocks.config import Config
from .utils import bash
from pathlib import Path

class Git:
    def __init__(self, config: Config):
        self.config = config

    def get_repo_https_url(self):
        """
        Get the HTTPS URL for the GitHub repository with authentication token if available.
        
        Returns:
            str: The HTTPS URL for the GitHub repository, including the authentication token if available.
        """
        token = self.config.get_github_token()
        repo_path = self.config.get_github_repository_path()
        
        url_prefix = f"token:{token}@" if token else ""
        return f"https://{url_prefix}github.com/{repo_path}"
    
    def get_repo_url(self):
        """
        Get the URL for the GitHub repository.
        
        Returns:
            str: The URL for the GitHub repository.
        """
        return self.get_repo_https_url()

    def set_repo_path(self, repo_path):
        """
        Set the GitHub repository path.
        
        Args:
            repo_path (str): The GitHub repository path in the format 'owner/repo'.
        """
        self.config.set_github_repository_path(repo_path)

    def set_token(self, token):
        """
        Set the GitHub authentication token.
        
        Args:
            token (str): The GitHub authentication token.
        """
        self.config.set_github_token(token)
        
    def configure(self):
        """
        Configure Git with default user information.
        
        Sets the local Git user email to 'bot@blocksorg.com' and user name to 'BlocksOrg'.
        """
        bash(f"git config --local user.email 'bot@blocksorg.com'")
        bash(f"git config --local user.name 'BlocksOrg'")

    def checkout(self, ref="", new_branch=False, track=False, orphan=False, force=False):
        """
        Checkout a branch, tag, or commit.
        
        Args:
            ref (str): The branch, tag, or commit to checkout. Default is "" (current branch).
            new_branch (bool): Whether to create a new branch. Default is False.
            track (bool): Whether to set up tracking for a new branch. Default is False.
            orphan (bool): Whether to create an orphan branch. Default is False.
            force (bool): Whether to force checkout. Default is False.
            
        Returns:
            int: The exit code of the git checkout command.
            
        Raises:
            subprocess.CalledProcessError: If the git checkout command fails.
        """
        options = []
        
        if new_branch:
            options.append("-b")
        elif orphan:
            options.append("--orphan")
            
        if track:
            options.append("--track")
            
        if force:
            options.append("--force")
            
        options_str = " ".join(options)
        return bash(f"git checkout {options_str} {ref}")

    def clone(self, url=None, ref="", target_dir=".", depth=None, single_branch=False, recursive=False, shallow_submodules=False):
        """
        Clone a repository.
        
        Args:
            ref (str): The branch, tag, or commit to clone. Default is "" (default branch).
            target_dir (str): The directory to clone into. Default is "." (current directory).
            depth (int): Create a shallow clone with a history truncated to the specified number of commits. Default is None.
            single_branch (bool): Clone only the history leading to the tip of a single branch. Default is False.
            recursive (bool): Initialize all submodules within the cloned repository. Default is False.
            shallow_submodules (bool): All submodules will be shallow with depth=1. Default is False.
            
        Returns:
            int: The exit code of the git clone command.
            
        Raises:
            ValueError: If the target directory already exists and is not empty.
            subprocess.CalledProcessError: If the git clone command fails.
        """
        if url is None:
            url = self.get_repo_url()

        target_path = Path(target_dir)
        
        if target_path.exists() and any(target_path.iterdir()):
            raise ValueError(f"Target directory '{target_dir}' already exists and is not empty. Cannot clone into a non-empty directory.")
        elif not target_path.parent.exists():
            target_path.parent.mkdir(parents=True, exist_ok=True)

        options = []
        
        if ref:
            options.append(f"--branch {ref}")
            
        if depth is not None:
            options.append(f"--depth {depth}")
            
        if single_branch:
            options.append("--single-branch")
            
        if recursive:
            options.append("--recursive")
            
        if shallow_submodules:
            options.append("--shallow-submodules")
            
        options_str = " ".join(options)
        return_value = bash(f"git clone {options_str} {url} {target_dir}")
        current_dir = os.getcwd()
        os.chdir(target_path.absolute())
        with contextlib.suppress(Exception):
            self.configure()
        os.chdir(current_dir)
        return return_value

    def init(self):
        """
        Initialize a new Git repository in the current directory.
        
        Equivalent to running 'git init'.
        """
        bash("git init")

    def pull(self, remote="origin", branch="HEAD", rebase=False, ff_only=False):
        """
        Pull changes from a remote repository.
        
        Args:
            remote (str): The remote to pull from. Default is "origin".
            branch (str): The branch to pull from. Default is "HEAD".
            rebase (bool): Whether to rebase instead of merge. Default is False.
            ff_only (bool): Whether to only allow fast-forward merges. Default is False.
            
        Returns:
            int: The exit code of the git pull command.
            
        Raises:
            subprocess.CalledProcessError: If the git pull command fails.
        """
        options = []
        if rebase:
            options.append("--rebase")
        if ff_only:
            options.append("--ff-only")
        
        options_str = " ".join(options)
        return bash(f"git pull {options_str} {remote} {branch}")
        
    def push(self, remote="origin", branch="HEAD", publish=False, force=False, force_with_lease=False, tags=False):
        """
        Push changes to a remote repository.
        
        Args:
            remote (str): The remote to push to. Default is "origin".
            branch (str): The branch to push. Default is "HEAD".
            publish (bool): Whether to set up tracking with -u. Default is False.
            force (bool): Whether to force push. Default is False.
            force_with_lease (bool): Whether to force push with lease. Default is False.
            tags (bool): Whether to push tags. Default is False.
            
        Returns:
            int: The exit code of the git push command.
            
        Raises:
            subprocess.CalledProcessError: If the git push command fails.
        """
        options = []
        
        if publish:
            options.append("-u")
        if force:
            options.append("--force")
        elif force_with_lease:
            options.append("--force-with-lease")
        if tags:
            options.append("--tags")
        
        options_str = " ".join(options)
        return bash(f"git push {options_str} {remote} {branch}")

    def commit(self, message, amend=False, no_edit=False, all=False, allow_empty=False, signoff=False):
        """
        Commit changes to the repository.
        
        Args:
            message (str): The commit message.
            amend (bool): Whether to amend the previous commit. Default is False.
            no_edit (bool): When amending, whether to reuse the previous commit message. Default is False.
            all (bool): Whether to automatically stage all modified and deleted files. Default is False.
            allow_empty (bool): Whether to allow creating empty commits. Default is False.
            signoff (bool): Whether to add a Signed-off-by line to the commit message. Default is False.
            
        Returns:
            int: The exit code of the git commit command.
            
        Raises:
            subprocess.CalledProcessError: If the git commit command fails.
        """
        options = []
        
        if message and not (amend and no_edit):
            # Escape single quotes in the message
            escaped_message = message.replace("'", "'\\''")
            options.append(f"-m '{escaped_message}'")
        
        if amend:
            options.append("--amend")
            
        if no_edit:
            options.append("--no-edit")
            
        if all:
            options.append("--all")
            
        if allow_empty:
            options.append("--allow-empty")
            
        if signoff:
            options.append("--signoff")
        
        options_str = " ".join(options)
        return bash(f"git commit {options_str}")

    def add(self, file=None, all=False):
        """
        Add file contents to the index.
        
        Args:
            file (str): The file to add. Ignored if all=True.
            all (bool): Whether to add all files (including untracked). Default is False.
            
        Raises:
            subprocess.CalledProcessError: If the git add command fails.
        """
        if all:
            bash("git add .")
        elif file:
            bash(f"git add {file}")
        else:
            raise ValueError("Either 'file' or 'all' keyword argument must be provided")

    def branch(self, branch_name, checkout=False):
        """
        Create a new branch.
        
        Args:
            branch_name (str): The name of the branch to create.
            checkout (bool): Whether to checkout the new branch after creating it. Default is False.
            
        Raises:
            subprocess.CalledProcessError: If the git branch command fails.
        """
        if checkout:
            self.checkout(branch_name, new_branch=True)
        else:
            bash(f"git branch {branch_name}")
