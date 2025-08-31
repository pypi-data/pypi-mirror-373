"""Keycloak Identity Provider configuration for Orchestr8."""

import subprocess
import json
import base64
from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum

import requests
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


class IdentityProviderType(str, Enum):
    """Supported identity provider types."""

    GITHUB = "github"
    GOOGLE = "google"
    MICROSOFT = "microsoft"


@dataclass
class IdentityProviderConfig:
    """Configuration for an identity provider."""

    provider_type: IdentityProviderType
    client_id: str
    client_secret: str
    enabled: bool = True
    trust_email: bool = True

    # Provider-specific settings
    github_org: Optional[str] = None
    google_hosted_domain: Optional[str] = None
    microsoft_tenant_id: Optional[str] = None


class KeycloakIdentityProviderManager:
    """Manage identity providers in Keycloak."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.keycloak_url = "http://localhost:30081"
        self.realm = "platform"

    def configure_provider(
        self, provider_type: IdentityProviderType, interactive: bool = True
    ) -> bool:
        """
        Configure an identity provider in Keycloak.

        Args:
            provider_type: Type of identity provider to configure
            interactive: Whether to prompt for configuration

        Returns:
            True if configuration was successful
        """
        self.console.print(
            f"\n[bold cyan]🔐 Configuring {provider_type.value.title()} Identity Provider[/bold cyan]\n"
        )

        # Check if Keycloak is accessible
        if not self._check_keycloak():
            return False

        # Get admin credentials
        admin_password = self._get_admin_password()
        if not admin_password:
            return False

        # Get provider configuration
        if interactive:
            config = self._prompt_for_config(provider_type)
        else:
            config = self._get_config_from_secret(provider_type)

        if not config:
            return False

        # Store configuration in Kubernetes secret
        if not self._store_config_secret(config):
            return False

        # Configure in Keycloak
        return self._configure_in_keycloak(config, admin_password)

    def _check_keycloak(self) -> bool:
        """Check if Keycloak is accessible."""
        self.console.print("[yellow]Checking Keycloak status...[/yellow]")

        try:
            # Check if Keycloak pod is running
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "pod",
                    "-n",
                    "platform",
                    "-l",
                    "app.kubernetes.io/name=keycloak",
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.console.print("[red]❌ Keycloak is not running[/red]")
                return False

            pods = json.loads(result.stdout)
            if not pods.get("items"):
                self.console.print("[red]❌ No Keycloak pods found[/red]")
                return False

            # Check if port-forward is needed
            try:
                requests.get(f"{self.keycloak_url}/", timeout=2)
            except Exception:
                self.console.print(
                    "[yellow]Setting up port-forward to Keycloak...[/yellow]"
                )
                # Start port-forward in background
                subprocess.Popen(
                    [
                        "kubectl",
                        "port-forward",
                        "-n",
                        "platform",
                        "svc/orchestr8-platform-keycloak",
                        "30081:80",
                    ],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                import time

                time.sleep(3)

            self.console.print("[green]✅ Keycloak is accessible[/green]")
            return True

        except Exception as e:
            self.console.print(f"[red]❌ Error checking Keycloak: {e}[/red]")
            return False

    def _get_admin_password(self) -> Optional[str]:
        """Get Keycloak admin password from Kubernetes secret."""
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "secret",
                    "keycloak-admin-creds",
                    "-n",
                    "platform",
                    "-o",
                    "jsonpath={.data.password}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout:
                return base64.b64decode(result.stdout).decode("utf-8")
            else:
                self.console.print(
                    "[red]❌ Could not retrieve Keycloak admin password[/red]"
                )
                return None

        except Exception as e:
            self.console.print(f"[red]❌ Error getting admin password: {e}[/red]")
            return None

    def _prompt_for_config(
        self, provider_type: IdentityProviderType
    ) -> Optional[IdentityProviderConfig]:
        """Prompt user for provider configuration."""

        if provider_type == IdentityProviderType.GITHUB:
            panel = Panel(
                "[cyan]To create a GitHub OAuth App:[/cyan]\n"
                "1. Go to: https://github.com/settings/developers\n"
                "2. Click 'OAuth Apps' → 'New OAuth App'\n"
                "3. Use these settings:\n"
                "   [yellow]Application name:[/yellow] Orchestr8 Platform (Local)\n"
                "   [yellow]Homepage URL:[/yellow] http://localhost:30081\n"
                "   [yellow]Authorization callback URL:[/yellow] http://localhost:30081/realms/platform/broker/github/endpoint\n"
                "4. Click 'Register application'\n"
                "5. Copy the Client ID and generate a Client Secret",
                title="📝 GitHub OAuth App Setup",
                border_style="cyan",
            )
            self.console.print(panel)

        elif provider_type == IdentityProviderType.GOOGLE:
            panel = Panel(
                "[cyan]To create a Google OAuth Client:[/cyan]\n"
                "1. Go to: https://console.cloud.google.com/apis/credentials\n"
                "2. Click 'Create Credentials' → 'OAuth client ID'\n"
                "3. Choose 'Web application'\n"
                "4. Add authorized redirect URI:\n"
                "   [yellow]http://localhost:30081/realms/platform/broker/google/endpoint[/yellow]\n"
                "5. Copy the Client ID and Client Secret",
                title="📝 Google OAuth Setup",
                border_style="cyan",
            )
            self.console.print(panel)

        self.console.print()
        client_id = Prompt.ask(f"Enter {provider_type.value.title()} Client ID")
        client_secret = Prompt.ask(
            f"Enter {provider_type.value.title()} Client Secret", password=True
        )

        config = IdentityProviderConfig(
            provider_type=provider_type,
            client_id=client_id,
            client_secret=client_secret,
        )

        # Provider-specific options
        if provider_type == IdentityProviderType.GITHUB:
            org = Prompt.ask(
                "GitHub organization to restrict access (optional)", default=""
            )
            if org:
                config.github_org = org

        elif provider_type == IdentityProviderType.GOOGLE:
            domain = Prompt.ask(
                "Google Workspace domain to restrict (optional)", default=""
            )
            if domain:
                config.google_hosted_domain = domain

        return config

    def _get_config_from_secret(
        self, provider_type: IdentityProviderType
    ) -> Optional[IdentityProviderConfig]:
        """Get provider configuration from Kubernetes secret."""
        secret_name = f"{provider_type.value}-oauth-creds"

        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "secret",
                    secret_name,
                    "-n",
                    "platform",
                    "-o",
                    "json",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.console.print(
                    f"[yellow]No existing configuration found for {provider_type.value}[/yellow]"
                )
                return None

            secret_data = json.loads(result.stdout)
            data = secret_data.get("data", {})

            client_id = base64.b64decode(data.get("client-id", "")).decode("utf-8")
            client_secret = base64.b64decode(data.get("client-secret", "")).decode(
                "utf-8"
            )

            if not client_id or not client_secret:
                return None

            return IdentityProviderConfig(
                provider_type=provider_type,
                client_id=client_id,
                client_secret=client_secret,
            )

        except Exception:
            return None

    def _store_config_secret(self, config: IdentityProviderConfig) -> bool:
        """Store provider configuration in Kubernetes secret."""
        secret_name = f"{config.provider_type.value}-oauth-creds"

        try:
            # Create or update secret
            result = subprocess.run(
                [
                    "kubectl",
                    "create",
                    "secret",
                    "generic",
                    secret_name,
                    f"--from-literal=client-id={config.client_id}",
                    f"--from-literal=client-secret={config.client_secret}",
                    "-n",
                    "platform",
                    "--dry-run=client",
                    "-o",
                    "yaml",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                self.console.print("[red]❌ Failed to create secret manifest[/red]")
                return False

            # Apply the secret
            apply_result = subprocess.run(
                ["kubectl", "apply", "-f", "-"],
                input=result.stdout,
                capture_output=True,
                text=True,
            )

            if apply_result.returncode == 0:
                self.console.print(
                    "[green]✅ Configuration stored in Kubernetes secret[/green]"
                )
                return True
            else:
                self.console.print(
                    f"[red]❌ Failed to apply secret: {apply_result.stderr}[/red]"
                )
                return False

        except Exception as e:
            self.console.print(f"[red]❌ Error storing configuration: {e}[/red]")
            return False

    def _configure_in_keycloak(
        self, config: IdentityProviderConfig, admin_password: str
    ) -> bool:
        """Configure the identity provider in Keycloak."""
        self.console.print(
            f"\n[yellow]Configuring {config.provider_type.value} in Keycloak...[/yellow]"
        )

        # Get admin token
        token = self._get_admin_token(admin_password)
        if not token:
            return False

        # Check if provider already exists
        exists = self._check_provider_exists(config.provider_type, token)

        # Create or update provider
        if exists:
            success = self._update_provider(config, token)
        else:
            success = self._create_provider(config, token)

        if success:
            self.console.print(
                f"\n[green]✅ {config.provider_type.value.title()} identity provider configured successfully![/green]"
            )
            self.console.print("\n[cyan]You can now test the integration:[/cyan]")
            self.console.print(
                f"1. Go to: {self.keycloak_url}/realms/{self.realm}/account"
            )
            self.console.print(
                f"2. Click 'Sign in with {config.provider_type.value.title()}'"
            )
            return True
        else:
            return False

    def _get_admin_token(self, admin_password: str) -> Optional[str]:
        """Get Keycloak admin access token."""
        try:
            response = requests.post(
                f"{self.keycloak_url}/realms/master/protocol/openid-connect/token",
                data={
                    "username": "admin",
                    "password": admin_password,
                    "grant_type": "password",
                    "client_id": "admin-cli",
                },
            )

            if response.status_code == 200:
                return response.json().get("access_token")
            else:
                self.console.print(
                    f"[red]❌ Failed to get admin token: {response.status_code}[/red]"
                )
                return None

        except Exception as e:
            self.console.print(f"[red]❌ Error getting admin token: {e}[/red]")
            return None

    def _check_provider_exists(
        self, provider_type: IdentityProviderType, token: str
    ) -> bool:
        """Check if provider already exists in Keycloak."""
        try:
            response = requests.get(
                f"{self.keycloak_url}/admin/realms/{self.realm}/identity-provider/instances/{provider_type.value}",
                headers={"Authorization": f"Bearer {token}"},
            )
            return response.status_code == 200
        except Exception:
            return False

    def _create_provider(self, config: IdentityProviderConfig, token: str) -> bool:
        """Create a new identity provider in Keycloak."""
        provider_data = self._build_provider_data(config)

        try:
            response = requests.post(
                f"{self.keycloak_url}/admin/realms/{self.realm}/identity-provider/instances",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=provider_data,
            )

            if response.status_code == 201:
                self.console.print("[green]✅ Identity provider created[/green]")
                return True
            else:
                self.console.print(
                    f"[red]❌ Failed to create provider: {response.status_code}[/red]"
                )
                if response.text:
                    self.console.print(f"[red]{response.text}[/red]")
                return False

        except Exception as e:
            self.console.print(f"[red]❌ Error creating provider: {e}[/red]")
            return False

    def _update_provider(self, config: IdentityProviderConfig, token: str) -> bool:
        """Update an existing identity provider in Keycloak."""
        provider_data = self._build_provider_data(config)

        try:
            response = requests.put(
                f"{self.keycloak_url}/admin/realms/{self.realm}/identity-provider/instances/{config.provider_type.value}",
                headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json",
                },
                json=provider_data,
            )

            if response.status_code in [200, 204]:
                self.console.print("[green]✅ Identity provider updated[/green]")
                return True
            else:
                self.console.print(
                    f"[red]❌ Failed to update provider: {response.status_code}[/red]"
                )
                return False

        except Exception as e:
            self.console.print(f"[red]❌ Error updating provider: {e}[/red]")
            return False

    def _build_provider_data(self, config: IdentityProviderConfig) -> Dict:
        """Build provider configuration data for Keycloak API."""
        base_data = {
            "alias": config.provider_type.value,
            "displayName": config.provider_type.value.title(),
            "enabled": config.enabled,
            "trustEmail": config.trust_email,
            "storeToken": False,
            "addReadTokenRoleOnCreate": False,
            "firstBrokerLoginFlowAlias": "first broker login",
            "config": {
                "clientId": config.client_id,
                "clientSecret": config.client_secret,
                "useJwksUrl": "false",
            },
        }

        # Provider-specific configuration
        if config.provider_type == IdentityProviderType.GITHUB:
            base_data["providerId"] = "github"
            base_data["config"]["defaultScope"] = "user:email"
            if config.github_org:
                base_data["config"]["org"] = config.github_org

        elif config.provider_type == IdentityProviderType.GOOGLE:
            base_data["providerId"] = "google"
            if config.google_hosted_domain:
                base_data["config"]["hostedDomain"] = config.google_hosted_domain

        elif config.provider_type == IdentityProviderType.MICROSOFT:
            base_data["providerId"] = "oidc"
            base_data["config"]["authorizationUrl"] = (
                f"https://login.microsoftonline.com/{config.microsoft_tenant_id or 'common'}/oauth2/v2.0/authorize"
            )
            base_data["config"]["tokenUrl"] = (
                f"https://login.microsoftonline.com/{config.microsoft_tenant_id or 'common'}/oauth2/v2.0/token"
            )
            base_data["config"]["userInfoUrl"] = (
                "https://graph.microsoft.com/oidc/userinfo"
            )
            base_data["config"]["defaultScope"] = "openid profile email"

        return base_data
