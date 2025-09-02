"""Secrets management for Orchestr8."""

import secrets
import string
from typing import Dict, Optional

from ..providers.aws import AWSSecretsProvider
from ..providers.local import LocalSecretsProvider
from .config import Config, CloudProvider


class SecretsManager:
    """Manages secrets across different providers."""

    def __init__(self, config: Config):
        self.config = config
        self.provider = self._create_provider()

    def _create_provider(self):
        """Create the appropriate secrets provider."""
        if self.config.provider == CloudProvider.AWS:
            return AWSSecretsProvider(
                region=self.config.region or "us-east-1",
                cluster_name=self.config.cluster_name,
            )
        else:
            return LocalSecretsProvider()

    async def ensure_all_secrets(self) -> Dict[str, str]:
        """Ensure all required secrets exist."""
        secrets_map = {}

        # GitHub Token
        github_token = await self._ensure_secret(
            "github-token", self.config.github.token, "GitHub personal access token"
        )
        secrets_map["github_token"] = github_token

        # Keycloak OAuth2 Client for OAuth2 Proxy
        keycloak_client_id = await self._ensure_secret(
            "keycloak-oauth2-client-id",
            "oauth2-proxy",
            "Keycloak OAuth2 client ID for OAuth2 Proxy",
        )
        keycloak_client_secret = await self._ensure_secret(
            "keycloak-oauth2-client-secret",
            None,
            "Keycloak OAuth2 client secret",
            generator=lambda: self.generate_random_string(32),
        )
        secrets_map["keycloak_client_id"] = keycloak_client_id
        secrets_map["keycloak_client_secret"] = keycloak_client_secret

        # Keycloak admin password
        keycloak_password = await self._ensure_secret(
            "keycloak-admin-password",
            self.config.keycloak.admin_password,
            "Keycloak admin password",
            generator=self.generate_password,
        )
        secrets_map["keycloak_admin_password"] = keycloak_password

        # Cookie secret for OAuth2 proxy
        cookie_secret = await self._ensure_secret(
            "oauth2-proxy-cookie-secret",
            None,
            "OAuth2 proxy cookie secret",
            generator=lambda: self.generate_random_string(32),
        )
        secrets_map["oauth2_proxy_cookie_secret"] = cookie_secret

        # ArgoCD admin password
        argocd_password = await self._ensure_secret(
            "argocd-admin-password",
            None,
            "ArgoCD admin password",
            generator=self.generate_password,
        )
        secrets_map["argocd_admin_password"] = argocd_password

        return secrets_map

    async def _ensure_secret(
        self,
        key: str,
        value: Optional[str],
        description: str,
        generator: Optional[callable] = None,
    ) -> str:
        """Ensure a secret exists, creating if necessary."""
        # Try to get existing secret
        existing = await self.provider.get_secret(key)
        if existing:
            return existing

        # Use provided value
        if value:
            await self.provider.set_secret(key, value, description)
            return value

        # Generate if generator provided
        if generator:
            generated = generator()
            await self.provider.set_secret(key, generated, description)
            return generated

        # Fail if no way to create
        raise ValueError(
            f"No value provided for secret '{key}' and no generator available"
        )

    @staticmethod
    def generate_password(length: int = 16) -> str:
        """Generate a secure password."""
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        return "".join(secrets.choice(alphabet) for _ in range(length))

    @staticmethod
    def generate_random_string(length: int = 32) -> str:
        """Generate a random string for tokens/secrets."""
        alphabet = string.ascii_letters + string.digits
        return "".join(secrets.choice(alphabet) for _ in range(length))

    async def export_kubernetes_secrets(self) -> Dict[str, Dict[str, str]]:
        """Export secrets as Kubernetes secret manifests."""
        secrets_map = await self.ensure_all_secrets()

        k8s_secrets = {
            "argocd-github-creds": {
                "namespace": "argocd",
                "data": {
                    "username": self.config.github.org,
                    "password": secrets_map["github_token"],
                },
            },
            "keycloak-admin-creds": {
                "namespace": "platform",
                "data": {"admin-password": secrets_map["keycloak_admin_password"]},
            },
            "oauth2-proxy-secrets": {
                "namespace": "auth",
                "data": {
                    "client-id": secrets_map["keycloak_client_id"],
                    "client-secret": secrets_map["keycloak_client_secret"],
                    "cookie-secret": secrets_map["oauth2_proxy_cookie_secret"],
                },
            },
        }

        return k8s_secrets
