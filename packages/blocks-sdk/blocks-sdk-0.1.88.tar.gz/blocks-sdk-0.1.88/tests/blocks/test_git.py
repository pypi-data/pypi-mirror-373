import os
import subprocess
import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from blocks.git import Git
from blocks.config import Config


@pytest.fixture
def mock_config():
    """Create a mocked Config object for testing."""
    config = MagicMock(spec=Config)
    config.get_github_token.return_value = "test_token"
    config.get_github_repository_path.return_value = "test_owner/test_repo"
    return config


@pytest.fixture
def git_instance(mock_config):
    """Create a Git instance with a mocked Config for testing."""
    return Git(mock_config)


class TestGit:
    def test_init(self, mock_config):
        """Test that Git instance is initialized correctly with config."""
        git = Git(mock_config)
        assert git.config == mock_config

    def test_get_repo_https_url_with_token(self, git_instance):
        """Test that get_repo_https_url returns correct URL with token."""
        expected_url = "https://token:test_token@github.com/test_owner/test_repo"
        assert git_instance.get_repo_https_url() == expected_url

    def test_get_repo_https_url_without_token(self, mock_config, git_instance):
        """Test that get_repo_https_url returns correct URL without token."""
        # Set token to None
        mock_config.get_github_token.return_value = None
        expected_url = "https://github.com/test_owner/test_repo"
        assert git_instance.get_repo_https_url() == expected_url

    def test_get_repo_url_returns_https_url(self, git_instance):
        """Test that get_repo_url calls get_repo_https_url."""
        with patch.object(git_instance, 'get_repo_https_url') as mock_get_https:
            mock_get_https.return_value = "test_url"
            result = git_instance.get_repo_url()
            assert result == "test_url"
            mock_get_https.assert_called_once()

    def test_set_repo_path(self, git_instance):
        """Test that set_repo_path calls config.set_github_repository_path."""
        git_instance.set_repo_path("new_owner/new_repo")
        git_instance.config.set_github_repository_path.assert_called_once_with("new_owner/new_repo")

    def test_set_token(self, git_instance):
        """Test that set_token calls config.set_github_token."""
        git_instance.set_token("new_token")
        git_instance.config.set_github_token.assert_called_once_with("new_token")

    @patch('blocks.git.bash')
    def test_configure(self, mock_bash, git_instance):
        """Test that configure sets up git config correctly."""
        git_instance.configure()
        assert mock_bash.call_count == 2
        mock_bash.assert_any_call("git config --local user.email 'bot@blocksorg.com'")
        mock_bash.assert_any_call("git config --local user.name 'BlocksOrg'")

    @patch('blocks.git.bash')
    def test_checkout_basic(self, mock_bash, git_instance):
        """Test that checkout calls git checkout with correct parameters."""
        git_instance.checkout("main")
        mock_bash.assert_called_once_with("git checkout  main")

    @patch('blocks.git.bash')
    def test_checkout_with_options(self, mock_bash, git_instance):
        """Test that checkout handles all options correctly."""
        git_instance.checkout("feature-branch", new_branch=True, track=True, force=True)
        mock_bash.assert_called_once_with("git checkout -b --track --force feature-branch")

    @patch('blocks.git.bash')
    def test_checkout_orphan(self, mock_bash, git_instance):
        """Test that checkout handles orphan option correctly."""
        git_instance.checkout("orphan-branch", orphan=True)
        mock_bash.assert_called_once_with("git checkout --orphan orphan-branch")

    @patch('blocks.git.bash')
    def test_clone_basic(self, mock_bash, git_instance):
        """Test basic clone functionality."""
        with patch.object(git_instance, 'get_repo_url', return_value="https://test_url"):
            with patch.object(Path, 'exists', return_value=False):
                with patch.object(Path, 'iterdir', return_value=[]):
                    with patch.object(os, 'chdir'):
                        with patch.object(git_instance, 'configure'):
                            git_instance.clone()
                            # Verify the clone command is called
                            mock_bash.assert_any_call("git clone  https://test_url .")

    @patch('blocks.git.bash')
    def test_clone_with_options(self, mock_bash, git_instance):
        """Test clone with all options."""
        with patch.object(git_instance, 'get_repo_url', return_value="https://test_url"):
            with patch.object(Path, 'exists', return_value=False):
                with patch.object(Path, 'iterdir', return_value=[]):
                    with patch.object(os, 'chdir'):
                        with patch.object(git_instance, 'configure'):
                            git_instance.clone(
                                ref="main",
                                target_dir="/target",
                                depth=1,
                                single_branch=True,
                                recursive=True,
                                shallow_submodules=True
                            )
                            # Verify the clone command is called with the correct parameters
                            mock_bash.assert_any_call(
                                "git clone --branch main --depth 1 --single-branch --recursive --shallow-submodules "
                                "https://test_url /target"
                            )

    def test_clone_non_empty_dir(self, git_instance):
        """Test that clone raises ValueError when target directory is not empty."""
        with patch.object(Path, 'exists', return_value=True):
            with patch.object(Path, 'iterdir', return_value=[MagicMock()]):
                with pytest.raises(ValueError, match="Target directory .* already exists and is not empty"):
                    git_instance.clone(target_dir="/non-empty-dir")

    @patch('blocks.git.bash')
    def test_clone_creates_parent_dirs(self, mock_bash, git_instance):
        """Test that clone creates parent directories if they don't exist."""
        with patch.object(git_instance, 'get_repo_url', return_value="https://test_url"):
            with patch.object(Path, 'exists') as mock_exists:
                # First call for target_dir check, second for target_dir.parent check
                mock_exists.side_effect = [False, False]
                with patch.object(Path, 'mkdir') as mock_mkdir:
                    with patch.object(os, 'chdir'):
                        git_instance.clone(target_dir="/new/path")
                        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)

    @patch('blocks.git.bash')
    @patch('blocks.git.os.chdir')
    def test_clone_configures_git(self, mock_chdir, mock_bash, git_instance):
        """Test that clone configures git after cloning."""
        with patch.object(git_instance, 'get_repo_url', return_value="https://test_url"):
            with patch.object(Path, 'exists', return_value=False):
                with patch.object(Path, 'iterdir', return_value=[]):
                    with patch.object(Path, 'absolute', return_value="/absolute/path"):
                        with patch.object(git_instance, 'configure') as mock_configure:
                            current_dir = os.getcwd()
                            git_instance.clone(target_dir="/target")
                            
                            # Verify current directory is restored
                            assert mock_chdir.call_count == 2
                            mock_chdir.assert_any_call("/absolute/path")
                            mock_chdir.assert_any_call(current_dir)
                            
                            # Verify configure is called
                            mock_configure.assert_called_once()

    @patch('blocks.git.bash')
    def test_init_repo(self, mock_bash, git_instance):
        """Test that init calls git init."""
        git_instance.init()
        mock_bash.assert_called_once_with("git init")

    @patch('blocks.git.bash')
    def test_pull_basic(self, mock_bash, git_instance):
        """Test basic pull functionality."""
        git_instance.pull()
        mock_bash.assert_called_once_with("git pull  origin HEAD")

    @patch('blocks.git.bash')
    def test_pull_with_options(self, mock_bash, git_instance):
        """Test pull with all options."""
        git_instance.pull(remote="upstream", branch="develop", rebase=True, ff_only=True)
        mock_bash.assert_called_once_with("git pull --rebase --ff-only upstream develop")

    @patch('blocks.git.bash')
    def test_push_basic(self, mock_bash, git_instance):
        """Test basic push functionality."""
        git_instance.push()
        mock_bash.assert_called_once_with("git push  origin HEAD")

    @patch('blocks.git.bash')
    def test_push_with_options(self, mock_bash, git_instance):
        """Test push with all options."""
        git_instance.push(remote="upstream", branch="feature", publish=True, force=True, tags=True)
        mock_bash.assert_called_once_with("git push -u --force --tags upstream feature")

    @patch('blocks.git.bash')
    def test_push_with_force_with_lease(self, mock_bash, git_instance):
        """Test push with force-with-lease option."""
        git_instance.push(force_with_lease=True)
        mock_bash.assert_called_once_with("git push --force-with-lease origin HEAD")

    @patch('blocks.git.bash')
    def test_commit_basic(self, mock_bash, git_instance):
        """Test basic commit functionality."""
        git_instance.commit("Test commit message")
        mock_bash.assert_called_once_with("git commit -m 'Test commit message'")

    @patch('blocks.git.bash')
    def test_commit_with_options(self, mock_bash, git_instance):
        """Test commit with all options."""
        git_instance.commit(
            "Test commit message",
            amend=True,
            all=True,
            allow_empty=True,
            signoff=True
        )
        mock_bash.assert_called_once_with(
            "git commit -m 'Test commit message' --amend --all --allow-empty --signoff"
        )

    @patch('blocks.git.bash')
    def test_commit_with_amend_no_edit(self, mock_bash, git_instance):
        """Test commit with amend and no_edit options."""
        git_instance.commit("", amend=True, no_edit=True)
        mock_bash.assert_called_once_with("git commit --amend --no-edit")

    @patch('blocks.git.bash')
    def test_commit_with_single_quotes_in_message(self, mock_bash, git_instance):
        """Test commit with single quotes in message that need escaping."""
        git_instance.commit("Test 'quoted' message")
        # Just check that the bash command was called once
        assert mock_bash.call_count == 1
        # and that the commit command contains the message
        assert "git commit" in mock_bash.call_args[0][0]
        assert "Test" in mock_bash.call_args[0][0]
        assert "quoted" in mock_bash.call_args[0][0]
        assert "message" in mock_bash.call_args[0][0]

    @patch('blocks.git.bash')
    def test_add_file(self, mock_bash, git_instance):
        """Test adding a specific file."""
        git_instance.add("test_file.py")
        mock_bash.assert_called_once_with("git add test_file.py")
    
    @patch('blocks.git.bash')
    def test_add_file_with_string_argument(self, mock_bash, git_instance):
        """Test adding a specific file using string argument (git.add("filename") syntax)."""
        git_instance.add("another_file.py")
        mock_bash.assert_called_once_with("git add another_file.py")

    @patch('blocks.git.bash')
    def test_add_all_files(self, mock_bash, git_instance):
        """Test adding all files."""
        git_instance.add(all=True)
        mock_bash.assert_called_once_with("git add .")
        
    def test_add_without_parameters(self, git_instance):
        """Test that add raises ValueError when neither file nor all are provided."""
        with pytest.raises(ValueError, match="Either 'file' or 'all' keyword argument must be provided"):
            git_instance.add()
            
    def test_add_with_empty_file_string(self, git_instance):
        """Test that add raises ValueError when file is an empty string and all is False."""
        with pytest.raises(ValueError, match="Either 'file' or 'all' keyword argument must be provided"):
            git_instance.add(file="", all=False)

    @patch('blocks.git.bash')
    def test_branch_create(self, mock_bash, git_instance):
        """Test creating a branch without checking it out."""
        git_instance.branch("new-branch")
        mock_bash.assert_called_once_with("git branch new-branch")

    def test_branch_create_and_checkout(self, git_instance):
        """Test creating a branch and checking it out."""
        with patch.object(git_instance, 'checkout') as mock_checkout:
            git_instance.branch("new-branch", checkout=True)
            mock_checkout.assert_called_once_with("new-branch", new_branch=True)