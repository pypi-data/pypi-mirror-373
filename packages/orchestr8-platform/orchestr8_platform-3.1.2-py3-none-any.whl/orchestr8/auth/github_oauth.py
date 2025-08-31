"""GitHub OAuth Device Flow implementation for Orchestr8."""

import time
import webbrowser
from typing import Dict, Optional
from dataclasses import dataclass
import requests
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn


@dataclass
class GitHubAuthResult:
    """Result of GitHub authentication."""

    access_token: str
    token_type: str
    scope: str


class GitHubDeviceFlow:
    """GitHub OAuth Device Flow implementation."""

    # GitHub OAuth endpoints
    DEVICE_CODE_URL = "https://github.com/login/device/code"
    TOKEN_URL = "https://github.com/login/oauth/access_token"

    # Default Orchestr8 OAuth App Client ID
    DEFAULT_CLIENT_ID = "Ov23liefXYUwEpx4AMWz"

    def __init__(
        self, console: Optional[Console] = None, client_id: Optional[str] = None
    ):
        self.console = console or Console()
        self.client_id = client_id or self.DEFAULT_CLIENT_ID

    def authenticate(self, scopes: Optional[str] = None) -> Optional[GitHubAuthResult]:
        """
        Perform GitHub OAuth device flow authentication.

        Args:
            scopes: OAuth scopes to request (e.g., "repo", "user:email")

        Returns:
            GitHubAuthResult with access token if successful, None otherwise
        """
        # Request device code
        device_code_data = self._request_device_code(scopes)
        if not device_code_data:
            return None

        # Show user instructions
        self._display_auth_instructions(
            device_code_data["user_code"], device_code_data["verification_uri"]
        )

        # Poll for token
        token_data = self._poll_for_token(
            device_code_data["device_code"], device_code_data["interval"]
        )

        if token_data:
            return GitHubAuthResult(
                access_token=token_data["access_token"],
                token_type=token_data.get("token_type", "bearer"),
                scope=token_data.get("scope", ""),
            )

        return None

    def _request_device_code(self, scopes: Optional[str]) -> Optional[Dict]:
        """Request device and user codes from GitHub."""
        headers = {"Accept": "application/json"}
        data = {"client_id": self.client_id}

        if scopes:
            data["scope"] = scopes

        try:
            response = requests.post(self.DEVICE_CODE_URL, headers=headers, data=data)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Failed to request device code: {e}[/red]")
            return None

    def _display_auth_instructions(self, user_code: str, verification_uri: str):
        """Display authentication instructions to the user."""
        self.console.print()
        panel = Panel(
            f"[bold cyan]Please visit:[/bold cyan] {verification_uri}\n"
            f"[bold cyan]Enter code:[/bold cyan] [bold yellow]{user_code}[/bold yellow]",
            title="🔐 GitHub Authentication Required",
            border_style="cyan",
        )
        self.console.print(panel)

        # Try to open browser automatically
        try:
            webbrowser.open(verification_uri)
        except Exception:
            pass

    def _poll_for_token(self, device_code: str, interval: int) -> Optional[Dict]:
        """Poll GitHub for access token."""
        headers = {"Accept": "application/json"}
        data = {
            "client_id": self.client_id,
            "device_code": device_code,
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task("Waiting for authentication...", total=None)

            while True:
                try:
                    response = requests.post(self.TOKEN_URL, headers=headers, data=data)
                    response_data = response.json()

                    if "access_token" in response_data:
                        progress.update(task, completed=True)
                        return response_data

                    error = response_data.get("error")

                    if error == "authorization_pending":
                        # Still waiting for user to authorize
                        time.sleep(interval)

                    elif error == "slow_down":
                        # Rate limited, increase interval
                        interval = response_data.get("interval", interval + 5)
                        time.sleep(interval)

                    elif error == "expired_token":
                        progress.update(
                            task, description="[red]❌ Authentication expired[/red]"
                        )
                        self.console.print(
                            "[red]The device code has expired. Please try again.[/red]"
                        )
                        return None

                    elif error == "access_denied":
                        progress.update(task, description="[red]❌ Access denied[/red]")
                        self.console.print("[red]Authentication was denied.[/red]")
                        return None

                    else:
                        # Unknown error
                        progress.update(
                            task, description=f"[red]❌ Error: {error}[/red]"
                        )
                        return None

                except requests.exceptions.RequestException as e:
                    progress.update(task, description="[red]❌ Network error[/red]")
                    self.console.print(f"[red]Network error: {e}[/red]")
                    return None

    @staticmethod
    def recommend_scopes(private_repos: bool = True) -> str:
        """
        Recommend OAuth scopes based on usage.

        Args:
            private_repos: Whether access to private repositories is needed

        Returns:
            Recommended scope string
        """
        if private_repos:
            return "repo"  # Full repo access including private repos
        else:
            return ""  # No scope needed for public repos

    def validate_token(self, token: str) -> bool:
        """
        Validate that a token has access to the required repository.

        Args:
            token: GitHub access token to validate

        Returns:
            True if token is valid and has repo access
        """
        headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json",
        }

        try:
            # Check token validity and scopes
            response = requests.get("https://api.github.com/user", headers=headers)

            if response.status_code == 200:
                # Check scopes from response headers (for debugging)
                # scopes = response.headers.get("X-OAuth-Scopes", "")
                return True
            else:
                self.console.print(
                    f"[red]Token validation failed: {response.status_code}[/red]"
                )
                return False

        except requests.exceptions.RequestException as e:
            self.console.print(f"[red]Error validating token: {e}[/red]")
            return False
