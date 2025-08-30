import pytest
from unittest.mock import Mock, patch
from blocks.github import GithubRepoProvider
from blocks.config import Config


@pytest.fixture
def mock_config():
    """Create a mock config for testing."""
    config = Mock(spec=Config)
    config.get_github_token.return_value = "test_token"
    config.get_github_api_url.return_value = "https://api.github.com"
    config.get_github_repository_owner.return_value = "test_owner"
    config.get_github_repository_name.return_value = "test_repo"
    return config


@pytest.fixture
def github_provider(mock_config):
    """Create a GithubRepoProvider instance for testing."""
    return GithubRepoProvider(mock_config)


class TestGithubReactions:
    """Test class for GitHub emoji reaction methods."""

    def test_add_reaction_to_issue_comment_success(self, github_provider):
        """Test successfully adding a reaction to an issue comment."""
        with patch.object(github_provider, 'request') as mock_request:
            mock_request.return_value = {
                "id": 1,
                "content": "+1",
                "user": {"login": "testuser"}
            }
            
            result = github_provider.add_reaction_to_issue_comment(
                comment_id=123,
                reaction="+1"
            )
            
            mock_request.assert_called_once_with(
                "/repos/test_owner/test_repo/issues/comments/123/reactions",
                method="POST",
                data={"content": "+1"}
            )
            assert result["content"] == "+1"

    def test_add_reaction_to_issue_comment_invalid_reaction(self, github_provider):
        """Test adding an invalid reaction to an issue comment."""
        with pytest.raises(ValueError) as excinfo:
            github_provider.add_reaction_to_issue_comment(
                comment_id=123,
                reaction="invalid"
            )
        
        assert "reaction must be one of" in str(excinfo.value)

    def test_add_reaction_to_issue_comment_missing_comment_id(self, github_provider):
        """Test adding a reaction without providing comment_id."""
        with pytest.raises(ValueError) as excinfo:
            github_provider.add_reaction_to_issue_comment(
                reaction="+1"
            )
        
        assert "comment_id is required" in str(excinfo.value)

    def test_add_reaction_to_issue_comment_missing_reaction(self, github_provider):
        """Test adding a reaction without providing reaction."""
        with pytest.raises(ValueError) as excinfo:
            github_provider.add_reaction_to_issue_comment(
                comment_id=123
            )
        
        assert "reaction is required" in str(excinfo.value)

    def test_add_reaction_to_pull_request_comment_success(self, github_provider):
        """Test successfully adding a reaction to a PR review comment."""
        with patch.object(github_provider, 'request') as mock_request:
            mock_request.return_value = {
                "id": 1,
                "content": "heart",
                "user": {"login": "testuser"}
            }
            
            result = github_provider.add_reaction_to_pull_request_comment(
                comment_id=456,
                reaction="heart"
            )
            
            mock_request.assert_called_once_with(
                "/repos/test_owner/test_repo/pulls/comments/456/reactions",
                method="POST",
                data={"content": "heart"}
            )
            assert result["content"] == "heart"

    def test_add_reaction_to_pull_request_comment_all_reactions(self, github_provider):
        """Test all valid reactions for PR comments."""
        valid_reactions = ["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"]
        
        with patch.object(github_provider, 'request') as mock_request:
            mock_request.return_value = {"id": 1, "content": "test"}
            
            for reaction in valid_reactions:
                github_provider.add_reaction_to_pull_request_comment(
                    comment_id=123,
                    reaction=reaction
                )
                
                mock_request.assert_called_with(
                    "/repos/test_owner/test_repo/pulls/comments/123/reactions",
                    method="POST",
                    data={"content": reaction}
                )

    def test_list_reactions_for_issue_comment(self, github_provider):
        """Test listing reactions for an issue comment."""
        with patch.object(github_provider, 'request') as mock_request:
            mock_request.return_value = [
                {"id": 1, "content": "+1", "user": {"login": "user1"}},
                {"id": 2, "content": "heart", "user": {"login": "user2"}}
            ]
            
            result = github_provider.list_reactions_for_issue_comment(comment_id=123)
            
            mock_request.assert_called_once_with(
                "/repos/test_owner/test_repo/issues/comments/123/reactions",
                method="GET"
            )
            assert len(result) == 2
            assert result[0]["content"] == "+1"

    def test_list_reactions_for_pull_request_comment(self, github_provider):
        """Test listing reactions for a PR review comment."""
        with patch.object(github_provider, 'request') as mock_request:
            mock_request.return_value = [
                {"id": 3, "content": "rocket", "user": {"login": "user3"}}
            ]
            
            result = github_provider.list_reactions_for_pull_request_comment(comment_id=456)
            
            mock_request.assert_called_once_with(
                "/repos/test_owner/test_repo/pulls/comments/456/reactions",
                method="GET"
            )
            assert len(result) == 1
            assert result[0]["content"] == "rocket"

    def test_delete_reaction_from_issue_comment(self, github_provider):
        """Test deleting a reaction from an issue comment."""
        with patch.object(github_provider, 'request') as mock_request:
            mock_request.return_value = None
            
            result = github_provider.delete_reaction_from_issue_comment(
                comment_id=123,
                reaction_id=789
            )
            
            mock_request.assert_called_once_with(
                "/repos/test_owner/test_repo/issues/comments/123/reactions/789",
                method="DELETE"
            )
            assert result is None

    def test_delete_reaction_from_issue_comment_missing_params(self, github_provider):
        """Test deleting a reaction with missing parameters."""
        with pytest.raises(ValueError) as excinfo:
            github_provider.delete_reaction_from_issue_comment(comment_id=123)
        assert "reaction_id is required" in str(excinfo.value)
        
        with pytest.raises(ValueError) as excinfo:
            github_provider.delete_reaction_from_issue_comment(reaction_id=789)
        assert "comment_id is required" in str(excinfo.value)

    def test_delete_reaction_from_pull_request_comment(self, github_provider):
        """Test deleting a reaction from a PR review comment."""
        with patch.object(github_provider, 'request') as mock_request:
            mock_request.return_value = None
            
            result = github_provider.delete_reaction_from_pull_request_comment(
                comment_id=456,
                reaction_id=101
            )
            
            mock_request.assert_called_once_with(
                "/repos/test_owner/test_repo/pulls/comments/456/reactions/101",
                method="DELETE"
            )
            assert result is None

    def test_custom_owner_repo_parameters(self, github_provider):
        """Test using custom owner and repo parameters."""
        with patch.object(github_provider, 'request') as mock_request:
            mock_request.return_value = {"id": 1, "content": "eyes"}
            
            github_provider.add_reaction_to_issue_comment(
                comment_id=123,
                reaction="eyes",
                owner="custom_owner",
                repo="custom_repo"
            )
            
            mock_request.assert_called_once_with(
                "/repos/custom_owner/custom_repo/issues/comments/123/reactions",
                method="POST",
                data={"content": "eyes"}
            )