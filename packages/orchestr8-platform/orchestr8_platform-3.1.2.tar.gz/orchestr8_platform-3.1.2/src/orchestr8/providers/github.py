"""GitHub provider for OAuth app management."""

from typing import Dict, Any
from github import Github, GithubException


class GitHubProvider:
    """GitHub provider for managing OAuth apps and repositories."""

    def __init__(self, token: str):
        self.github = Github(token)
        self._user = None
        self._org = None

    async def validate_token(self) -> bool:
        """Validate the GitHub token."""
        try:
            # Try to get authenticated user
            self._user = self.github.get_user()
            self._user.login  # Force API call
            return True
        except GithubException:
            return False

    async def create_oauth_app(
        self, org_name: str, app_name: str, homepage_url: str, callback_url: str
    ) -> Dict[str, str]:
        """Create a GitHub OAuth app.

        Note: This requires GitHub App management permissions which are not
        available via the API for OAuth apps. This would need to be done
        manually or via GitHub Apps API.

        Returns:
            Dictionary with client_id and client_secret
        """
        # TODO: GitHub doesn't provide API for creating OAuth apps
        # This would need to be done through GitHub Apps API or manually
        raise NotImplementedError(
            "GitHub OAuth app creation must be done manually. "
            "Visit: https://github.com/organizations/{org_name}/settings/applications/new"
        )

    async def get_organization(self, org_name: str):
        """Get organization details."""
        try:
            self._org = self.github.get_organization(org_name)
            return {
                "name": self._org.name,
                "login": self._org.login,
                "description": self._org.description,
                "url": self._org.html_url,
            }
        except GithubException as e:
            if e.status == 404:
                raise ValueError(
                    f"Organization '{org_name}' not found or not accessible"
                )
            raise

    async def check_repo_access(self, repo_full_name: str) -> bool:
        """Check if we have access to a repository."""
        try:
            repo = self.github.get_repo(repo_full_name)
            # Try to access repo details to verify access
            _ = repo.name
            return True
        except GithubException:
            return False

    async def create_deploy_key(
        self, repo_full_name: str, title: str, key: str, read_only: bool = True
    ) -> Dict[str, Any]:
        """Create a deploy key for a repository.

        Args:
            repo_full_name: Full repository name (org/repo)
            title: Deploy key title
            key: SSH public key
            read_only: Whether the key is read-only

        Returns:
            Deploy key information
        """
        try:
            repo = self.github.get_repo(repo_full_name)
            deploy_key = repo.create_key(title=title, key=key, read_only=read_only)
            return {
                "id": deploy_key.id,
                "title": deploy_key.title,
                "verified": deploy_key.verified,
                "created_at": deploy_key.created_at.isoformat(),
            }
        except GithubException as e:
            if e.status == 404:
                raise ValueError(f"Repository '{repo_full_name}' not found")
            raise
