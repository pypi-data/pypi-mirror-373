import os

class Config:
    def __init__(self):
        self.github_api_url = "https://api.github.com"
        self.github_token = os.getenv("GITHUB_TOKEN")
        self.github_repository_path = os.getenv("GITHUB_REPOSITORY_PATH")
        self.repo_provider = os.getenv("REPO_PROVIDER")

    def set_repo_provider(self, provider):
        self.repo_provider = provider

    def set_github_token(self, token):
        self.github_token = token

    def set_github_repository_path(self, path):
        self.github_repository_path = path

    def get_github_api_url(self):
        """
        Get the GitHub API URL (e.g. https://api.github.com)
        """
        return self.github_api_url

    def get_github_token(self):
        """
        Get the GitHub token
        """
        return self.github_token

    def get_github_repository_path(self):
        """
        Get the Github repository path (e.g. BlocksOrg/client-monorepo)
        """
        return self.github_repository_path
    
    def get_github_repository_owner(self, raise_error_if_not_found = False):
        """
        Get the GitHub repository owner (e.g. BlocksOrg)
        """
        repository_path = self.get_github_repository_path()
        slug_parts = repository_path.split("/") if repository_path else []
        if len(slug_parts) == 2:
            return slug_parts[0]
        else:
            if raise_error_if_not_found:
                raise ValueError("Repo class: 'owner' argument is required")
            return None

    def get_github_repository_name(self, raise_error_if_not_found = False):
        """
        Get the Github repository name (e.g. client-monorepo)
        """
        repository_path = self.get_github_repository_path()
        slug_parts = repository_path.split("/") if repository_path else []
        if len(slug_parts) == 2:
            return slug_parts[1]
        else:
            if raise_error_if_not_found:
                raise ValueError("Repo class: 'repo' argument is required")
            return None

    def get_repo_provider(self):
        """
        Get the repo provider (GITHUB, GITLAB, etc)
        """
        return self.repo_provider
