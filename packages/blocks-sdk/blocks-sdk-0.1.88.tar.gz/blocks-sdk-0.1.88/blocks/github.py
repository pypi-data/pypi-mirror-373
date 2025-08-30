import requests
import json

from .base import BaseRepoProvider
from .config import Config

class GithubRepoProvider(BaseRepoProvider):
    def __init__(self, config: Config):
        self.config = config

    def request(self, endpoint: str, params=None, method='GET', data=None):
        """
        Make a request to the GitHub API.

        Args:
            endpoint (str): The endpoint to request.
            params (dict): The parameters to pass to the request.
            method (str): The HTTP method to use.
            data (dict): The data to pass to the request.
        """
        headers = {
            'Authorization': f'token {self.config.get_github_token()}',
            'Accept': 'application/vnd.github.v3+json',
            'X-GitHub-Api-Version': '2022-11-28'
        }
        url = f'{self.config.get_github_api_url()}{endpoint}'
        response = requests.request(method, url, headers=headers, params=params, json=data)

        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            # if the response is json, print the error message
            print(f"Error with request to Github API: {err}")
            try:
                if response.json():
                    print(response.json())
            except json.JSONDecodeError:
                print(response.text)
            raise

        if (method == "DELETE"):
            return None

        return response.json()

    def update_pull_request(
        self, 
        pull_request_number = None, 
        title = None, 
        body = None, 
        assignees = None, 
        labels = None, 
        state = None, 
        maintainer_can_modify = None,
        target_branch = None,
        owner = None,
        repo = None
    ):
        """
        Update a pull request in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#update-a-pull-request

        Args:
            pull_request_number (int): The number of the pull request to update. (required)
            title (str): The title of the pull request. (optional)
            description (str): The description of the pull request. (optional)
            state (str): The state of the pull request. (optional)
            target_branch (str): The target branch of the pull request. (optional)

        Raises:
            ValueError: If the pull_request_number is not provided.
        """

        if pull_request_number is None:
            raise ValueError("update_pull_request: pull_request_number is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "owner": owner,
            "repo": repo,
            "pull_number": pull_request_number,
        }

        if title is not None:
            payload["title"] = title

        if body is not None:
            payload["body"] = body

        if assignees is not None:
            payload["assignees"] = assignees

        if labels is not None:
            payload["labels"] = labels

        if state is not None:
            payload["state"] = state

        if target_branch is not None:   
            payload["base"] = target_branch

        if maintainer_can_modify is not None:
            payload["maintainer_can_modify"] = maintainer_can_modify

        return self.request(f"/repos/{owner}/{repo}/pulls/{pull_request_number}", method="PATCH", data=payload)

    def update_issue(
            self, 
            issue_number = None, 
            title = None, 
            body = None, 
            assignees = None, 
            labels = None, 
            state = None,
            state_reason = None,
            milestone = None,
            owner = None,
            repo = None
    ):
        """
        Update an issue in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#update-an-issue

        Args:
            issue_number (int): The number of the issue to update. (required)
            title (str): The title of the issue. (optional)
            body (str): The body of the issue. (optional)
            assignees (list): A list of assignees to assign to the issue. (optional)
            labels (list): A list of labels to add to the issue. (optional)
            state (str): The state of the issue. (optional)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If the issue_number is not provided.
        """
        if issue_number is None:
            raise ValueError("update_issue: issue_number is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "owner": owner,
            "repo": repo,
            "issue_number": issue_number,
        }

        if assignees is not None:
            payload["assignees"] = assignees

        if labels is not None:
            payload["labels"] = labels

        if title is not None:
            payload["title"] = title

        if body is not None:
            payload["body"] = body

        if milestone is not None:
            payload["milestone"] = milestone

        if state is not None:
            payload["state"] = state

        if state_reason is not None:
            payload["state_reason"] = state_reason

        return self.request(f"/repos/{owner}/{repo}/issues/{issue_number}", method="PATCH", data=payload)

    def create_issue(
            self, 
            title = None, 
            body = None, 
            milestone = None,
            assignees = None, 
            labels = None,
            owner = None,
            repo = None
    ):
        """
        Create an issue in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/issues/issues?apiVersion=2022-11-28#create-an-issue

        Args:
            title (str): The title of the issue. (required)
            body (str): The body of the issue. (optional) [default: ""]
            assignees (list): A list of assignees to assign to the issue. (optional) [default: []]
            labels (list): A list of labels to add to the issue. (optional) [default: []]
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If the title is not provided.
        """
        if title is None:
            raise ValueError("create_issue: title is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "owner": owner,
            "repo": repo,
            "title": title,
        }

        if body is not None:
            payload["body"] = body

        if assignees is not None:
            payload["assignees"] = assignees

        if labels is not None:
            payload["labels"] = labels

        if milestone is not None:
            payload["milestone"] = milestone

        return self.request(f"/repos/{owner}/{repo}/issues", method="POST", data=payload)

    def create_pull_request(
            self, 
            source_branch = None, 
            target_branch = None, 
            title = None, 
            body = None, 
            draft = False,
            issue_number = None,
            owner = None,
            repo = None
    ):
        """
        Create a pull request in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/pulls/pulls?apiVersion=2022-11-28#create-a-pull-request

        Args:
            source_branch (str): The source branch to create the pull request from. (required)
            target_branch (str): The target branch to create the pull request to. (required)
            title (str): The title of the pull request. (required)
            body (str): The body of the pull request. (optional) [default: ""]
            draft (bool): Whether the pull request is a draft. (optional) [default: False]
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """
        if source_branch is None:
            raise ValueError("create_pull_request: source_branch is required")

        if target_branch is None:
            raise ValueError("create_pull_request: target_branch is required")

        if title is None:
            raise ValueError("create_pull_request: title is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "owner": owner,
            "repo": repo,
            "title": title,
            "draft": draft,
            "head": source_branch,
            "base": target_branch,
        }

        if body is not None:
            payload["body"] = body

        if issue_number is not None:
            payload["issue"] = issue_number

        return self.request(f"/repos/{owner}/{repo}/pulls", method="POST", data=payload)

    def delete_pull_request_comment(
            self, 
            comment_id = None,
            owner = None,
            repo = None
    ):
        """
        Delete a pull request comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#delete-a-review-comment-for-a-pull-request

        Args:
            comment_id (int): The ID of the comment to delete. (required)

        Raises:
            ValueError: If the comment_id is not provided.
        """
        if comment_id is None:
            raise ValueError("delete_pull_request_comment: comment_id is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        return self.request(f"/repos/{owner}/{repo}/pulls/comments/{comment_id}", method="DELETE")

    def update_pull_request_comment(
            self, 
            comment_id = None, 
            body = None,
            owner = None,
            repo = None
    ):
        """
        Update a pull request comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#update-a-review-comment-for-a-pull-request

        Args:
            comment_id (int): The ID of the comment to update. (required)
            body (str): The body of the comment. (required)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """
        if comment_id is None:
            raise ValueError("update_pull_request_comment: comment_id is required")

        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        if body is None:
            raise ValueError("update_pull_request_comment: body is required")

        payload = {
            "body": body,
        }

        return self.request(f"/repos/{self.config.get_github_repository_path()}/pulls/comments/{comment_id}", method="PATCH", data=payload)

    def comment_on_pull_request(
            self, 
            pull_request_number = None, 
            body = None,
            owner = None,
            repo = None
    ):
        """
        Comment on a pull request in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#create-an-issue-comment

        Args:
            pull_request_number (int): The number of the pull request to comment on. (required)
            body (str): The body of the comment. (optional) [default: ""]
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """

        if body is None:
            raise ValueError("comment_on_pull_request: body is required")

        if pull_request_number is None:
            raise ValueError("comment_on_pull_request: pull_request_number is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "owner": owner,
            "repo": repo,
            "body": body,
            "pull_number": pull_request_number,
        }

        return self.request(f"/repos/{owner}/{repo}/issues/{pull_request_number}/comments", method="POST", data=payload)
        
    def comment_on_pull_request_file(
            self, 
            commit_id = None, 
            file_path = None, 
            pull_request_number = None, 
            body = None, 
            line = None, 
            side = "RIGHT",
            reply_to_id = None,
            subject_type = "file",
            owner = None,
            repo = None
    ):
        """
        Comment on a file in a pull request in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#create-a-review-comment-for-a-pull-request

        Args:
            commit_id (str): The SHA of the commit to comment on. (required)
            file_path (str): The path of the file to comment on. (required)
            pull_request_number (int): The number of the pull request to comment on. (required)
            body (str): The body of the comment. (required)
            line (int): The line number in the diff to comment on. Line numbers start at 1. 
                        Required when subject_type is "line". This refers to the line number 
                        in the diff, not the line number in the file.
            side (str): The side of the diff to comment on. (optional) [LEFT, RIGHT] (default: "RIGHT")
                       - "LEFT" refers to the deletion side of the diff (base commit)
                       - "RIGHT" refers to the addition side of the diff (head commit)
            reply_to_id (int): The ID of the comment to reply to. (optional)
            subject_type (str): The type of subject to comment on. (optional) ["line", "file"] (default: "file")
                               - "line": Comment on a specific line in the file
                               - "file": Comment on the entire file
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)  

        Raises:
            ValueError: If any of the required arguments are not provided.
        """
        if body is None:
            raise ValueError("comment_on_pull_request_file: body is required")

        if commit_id is None:
            raise ValueError("comment_on_pull_request_file: commit_id is required")

        if file_path is None:
            raise ValueError("comment_on_pull_request_file: file_path is required")

        if pull_request_number is None:
            raise ValueError("comment_on_pull_request_file: pull_request_number is required")
        
        if subject_type == "line" and line is None:
            raise ValueError("comment_on_pull_request_file: line is required when subject_type is 'line'")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "body": body,
            "commit_id": commit_id,
            "path": file_path,
            "subject_type": subject_type
        }

        if subject_type == "line":
            payload["line"] = line
            payload["side"] = side
        
        if reply_to_id is not None:
            payload["in_reply_to"] = reply_to_id

        return self.request(f"/repos/{owner}/{repo}/pulls/{pull_request_number}/comments", method="POST", data=payload)

    def comment_on_pull_request_lines(
            self,
            commit_id = None,
            file_path = None,
            pull_request_number = None,
            body = None,
            start_line = None,
            end_line = None,
            side = "RIGHT",
            owner = None,
            repo = None
    ):
        """
        Comment on a range of lines in a pull request file.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#create-a-review-comment-for-a-pull-request

        Args:
            commit_id (str): The SHA of the commit to comment on. (required)
            file_path (str): The path of the file to comment on. (required)
            pull_request_number (int): The number of the pull request to comment on. (required)
            body (str): The body of the comment. (required)
            start_line (int): The starting line number in the diff to comment on. For multi-line comments, 
                              this is the first line of the diff hunk. Line numbers start at 1. (required)
            end_line (int): The ending line number in the diff to comment on. For multi-line comments, 
                           this is the last line of the diff hunk. Must be greater than or equal to start_line.
                           If not provided, a single-line comment will be created. (optional)
            side (str): The side of the diff to comment on. For a multi-line comment, this applies to both 
                       start_line and end_line. (optional) [LEFT, RIGHT] (default: "RIGHT")
                       - "LEFT" refers to the deletion side of the diff (base commit)
                       - "RIGHT" refers to the addition side of the diff (head commit)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)
                
        Raises:
            ValueError: If any of the required arguments are not provided.
        """
        if start_line is None:
            raise ValueError("comment_on_pull_request_lines: start_line is required")
            
        if body is None:
            raise ValueError("comment_on_pull_request_lines: body is required")

        if commit_id is None:
            raise ValueError("comment_on_pull_request_lines: commit_id is required")

        if file_path is None:
            raise ValueError("comment_on_pull_request_lines: file_path is required")

        if pull_request_number is None:
            raise ValueError("comment_on_pull_request_lines: pull_request_number is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        # Single line comment
        if end_line is None:
            payload = {
                "body": body,
                "commit_id": commit_id,
                "path": file_path,
                "line": start_line,
                "side": side,
                "subject_type": "line"
            }
        else:
            # Multi-line comment
            payload = {
                "body": body,
                "commit_id": commit_id,
                "path": file_path,
                "line": end_line,
                "start_line": start_line,
                "side": side,
                "start_side": side  # Usually the same as side
            }

        return self.request(f"/repos/{owner}/{repo}/pulls/{pull_request_number}/comments", method="POST", data=payload)

    def update_issue_comment(
            self, 
            comment_id = None, 
            body = None,
            owner = None,
            repo = None
    ):
        """
        Update an issue comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#update-an-issue-comment

        Args:
            comment_id (int): The ID of the comment to update. (required)
            body (str): The body of the comment. (required)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """
        if comment_id is None:
            raise ValueError("update_issue_comment: comment_id is required")

        if body is None:
            raise ValueError("update_issue_comment: body is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "body": body,
        }

        return self.request(f"/repos/{owner}/{repo}/issues/comments/{comment_id}", method="PATCH", data=payload)

    def delete_issue_comment(
            self, 
            comment_id = None,
            owner = None,
            repo = None
    ):
        """
        Delete an issue comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#delete-an-issue-comment

        Args:
            comment_id (int): The ID of the comment to delete. (required)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If the comment_id is not provided.
        """

        if comment_id is None:
            raise ValueError("delete_issue_comment: comment_id is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        return self.request(f"/repos/{owner}/{repo}/issues/comments/{comment_id}", method="DELETE")

    def comment_on_issue(
            self, 
            issue_number = None, 
            body = None,
            owner = None,
            repo = None
    ):
        """
        Comment on an issue in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/issues/comments?apiVersion=2022-11-28#create-an-issue-comment

        Args:
            issue_number (int): The number of the issue to comment on. (required)
            body (str): The body of the comment. (optional) [default: ""]
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """

        if body is None:
            raise ValueError("comment_on_issue: body is required")

        if issue_number is None:
            raise ValueError("comment_on_issue: issue_number is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "owner": owner,
            "repo": repo,
            "body": body,
            "issue_number": issue_number,
        }
    
        return self.request(f"/repos/{owner}/{repo}/issues/{issue_number}/comments", method="POST", data=payload)

    def reply_to_pull_request_comment(
            self,
            reply_to_id = None, 
            pull_request_number = None, 
            body = None,
            owner = None,
            repo = None
    ):
        """
        Reply to a pull request comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/pulls/comments?apiVersion=2022-11-28#create-a-reply-for-a-review-comment

        Args:
            reply_to_id (int): The ID of the comment to reply to. (required)
            pull_request_number (int): The number of the pull request to reply to. (required)
            body (str): The body of the reply. (optional) [default: ""]
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """

        if body is None:
            raise ValueError("reply_to_pull_request_comment: body is required")

        if reply_to_id is None:
            raise ValueError("reply_to_pull_request_comment: reply_to_id is required")

        if pull_request_number is None:
            raise ValueError("reply_to_pull_request_comment: pull_request_number is required")

        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "in_reply_to": reply_to_id,
            "body": body,
        }

        return self.request(f"/repos/{owner}/{repo}/pulls/{pull_request_number}/comments", method="POST", data=payload)

    def review_pull_request(
            self, 
            pull_request_number = None, 
            body = None, 
            commit_id = None, 
            comments = None, 
            event = "COMMENT",
            owner = None,
            repo = None
    ):
        """
        Review a pull request in GitHub. 
        
        Uses the following endpoints:
        - https://docs.github.com/en/rest/pulls/reviews?apiVersion=2022-11-28#create-a-review-for-a-pull-request

        Args:
            pull_request_number (int): The number of the pull request to review. (required)
            body (str): The body of the review. (optional) [default: ""]
            commit_sha (str): The SHA of the commit to review. (optional) [default: None]
            comments (list): A list of comments to add to the review. (optional) [default: []]
            event (str): The event to trigger on the review. (optional) [default: "COMMENT"]
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """

        if body is None:
            raise ValueError("review_pull_request: body is required")

        if pull_request_number is None:
            raise ValueError("review_pull_request: pull_request_number is required")
        
        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)
    
        payload = {
            "owner": owner,
            "repo": repo,
            "pull_number": pull_request_number,
            "event": event,
            "body": body,
        }

        if commit_id is not None:
            payload["commit_id"] = commit_id

        if comments is not None:
            payload["comments"] = comments

        return self.request(f"/repos/{owner}/{repo}/pulls/{pull_request_number}/reviews", method="POST", data=payload)

    def add_reaction_to_issue_comment(
            self,
            comment_id = None,
            reaction = None,
            owner = None,
            repo = None
    ):
        """
        Add an emoji reaction to an issue comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#create-reaction-for-an-issue-comment

        Args:
            comment_id (int): The ID of the comment to react to. (required)
            reaction (str): The reaction emoji. Must be one of: +1, -1, laugh, confused, heart, hooray, rocket, eyes. (required)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided or reaction is invalid.
        """
        if comment_id is None:
            raise ValueError("add_reaction_to_issue_comment: comment_id is required")

        if reaction is None:
            raise ValueError("add_reaction_to_issue_comment: reaction is required")

        valid_reactions = ["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"]
        if reaction not in valid_reactions:
            raise ValueError(f"add_reaction_to_issue_comment: reaction must be one of {valid_reactions}")

        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "content": reaction
        }

        return self.request(f"/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions", method="POST", data=payload)

    def add_reaction_to_pull_request_comment(
            self,
            comment_id = None,
            reaction = None,
            owner = None,
            repo = None
    ):
        """
        Add an emoji reaction to a pull request review comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#create-reaction-for-a-pull-request-review-comment

        Args:
            comment_id (int): The ID of the comment to react to. (required)
            reaction (str): The reaction emoji. Must be one of: +1, -1, laugh, confused, heart, hooray, rocket, eyes. (required)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided or reaction is invalid.
        """
        if comment_id is None:
            raise ValueError("add_reaction_to_pull_request_comment: comment_id is required")

        if reaction is None:
            raise ValueError("add_reaction_to_pull_request_comment: reaction is required")

        valid_reactions = ["+1", "-1", "laugh", "confused", "heart", "hooray", "rocket", "eyes"]
        if reaction not in valid_reactions:
            raise ValueError(f"add_reaction_to_pull_request_comment: reaction must be one of {valid_reactions}")

        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        payload = {
            "content": reaction
        }

        return self.request(f"/repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions", method="POST", data=payload)

    def list_reactions_for_issue_comment(
            self,
            comment_id = None,
            owner = None,
            repo = None
    ):
        """
        List reactions for an issue comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-an-issue-comment

        Args:
            comment_id (int): The ID of the comment to list reactions for. (required)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If the comment_id is not provided.
        """
        if comment_id is None:
            raise ValueError("list_reactions_for_issue_comment: comment_id is required")

        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        return self.request(f"/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions", method="GET")

    def list_reactions_for_pull_request_comment(
            self,
            comment_id = None,
            owner = None,
            repo = None
    ):
        """
        List reactions for a pull request review comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#list-reactions-for-a-pull-request-review-comment

        Args:
            comment_id (int): The ID of the comment to list reactions for. (required)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If the comment_id is not provided.
        """
        if comment_id is None:
            raise ValueError("list_reactions_for_pull_request_comment: comment_id is required")

        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        return self.request(f"/repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions", method="GET")

    def delete_reaction_from_issue_comment(
            self,
            comment_id = None,
            reaction_id = None,
            owner = None,
            repo = None
    ):
        """
        Delete a reaction from an issue comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#delete-an-issue-comment-reaction

        Args:
            comment_id (int): The ID of the comment to delete the reaction from. (required)
            reaction_id (int): The ID of the reaction to delete. (required)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """
        if comment_id is None:
            raise ValueError("delete_reaction_from_issue_comment: comment_id is required")

        if reaction_id is None:
            raise ValueError("delete_reaction_from_issue_comment: reaction_id is required")

        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        return self.request(f"/repos/{owner}/{repo}/issues/comments/{comment_id}/reactions/{reaction_id}", method="DELETE")

    def delete_reaction_from_pull_request_comment(
            self,
            comment_id = None,
            reaction_id = None,
            owner = None,
            repo = None
    ):
        """
        Delete a reaction from a pull request review comment in GitHub.

        Uses the following endpoints:
        - https://docs.github.com/en/rest/reactions/reactions?apiVersion=2022-11-28#delete-a-pull-request-comment-reaction

        Args:
            comment_id (int): The ID of the comment to delete the reaction from. (required)
            reaction_id (int): The ID of the reaction to delete. (required)
            owner (str): The owner of the repository. (optional)
            repo (str): The name of the repository. (optional)

        Raises:
            ValueError: If any of the required arguments are not provided.
        """
        if comment_id is None:
            raise ValueError("delete_reaction_from_pull_request_comment: comment_id is required")

        if reaction_id is None:
            raise ValueError("delete_reaction_from_pull_request_comment: reaction_id is required")

        if owner is None:
            owner = self.config.get_github_repository_owner(raise_error_if_not_found=True)
        
        if repo is None:
            repo = self.config.get_github_repository_name(raise_error_if_not_found=True)

        return self.request(f"/repos/{owner}/{repo}/pulls/comments/{comment_id}/reactions/{reaction_id}", method="DELETE")
