"""Orchestr8 SDK for programmatic access."""

from typing import Dict, Any, List

from .core import Orchestrator, Config, CloudProvider
from .core.config import GitHubConfig


class Orchestr8SDK:
    """SDK for programmatic access to Orchestr8."""

    def __init__(self, config: Config):
        """Initialize the SDK with configuration.

        Args:
            config: Orchestr8 configuration object

        Example:
            ```python
            from orchestr8 import Orchestr8SDK, Config, CloudProvider
            from orchestr8.core.config import GitHubConfig

            config = Config(
                provider=CloudProvider.AWS,
                region="us-east-1",
                cluster_name="my-cluster",
                domain="platform.example.com",
                github=GitHubConfig(
                    org="my-org",
                    token="ghp_..."
                )
            )

            sdk = Orchestr8SDK(config)
            await sdk.setup()
            ```
        """
        self.config = config
        self.orchestrator = Orchestrator(config)

    async def setup(self) -> Dict[str, Any]:
        """Run the complete platform setup.

        Returns:
            Dictionary containing setup results

        Raises:
            RuntimeError: If prerequisites validation fails
        """
        return await self.orchestrator.setup()

    async def validate_prerequisites(self) -> Dict[str, Any]:
        """Validate prerequisites before setup.

        Returns:
            Dictionary with validation results:
            - valid (bool): Whether all prerequisites are met
            - errors (List[str]): List of error messages
            - warnings (List[str]): List of warning messages
        """
        return await self.orchestrator.validate_prerequisites()

    async def get_status(self) -> Dict[str, Any]:
        """Get current platform status.

        Returns:
            Dictionary with status information:
            - config: Current configuration
            - kubernetes: Kubernetes connection status
            - argocd: ArgoCD installation status
            - platform: Platform deployment status
        """
        return await self.orchestrator.get_status()

    async def create_namespaces(self) -> List[str]:
        """Create required Kubernetes namespaces.

        Returns:
            List of created namespace names
        """
        return await self.orchestrator.create_namespaces()

    async def deploy_module(
        self, module_name: str, config: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Deploy a new module to the platform.

        Args:
            module_name: Name of the module
            config: Module configuration

        Returns:
            Deployment result
        """
        # TODO: Implement module deployment
        raise NotImplementedError("Module deployment coming soon")

    async def get_modules(self) -> List[Dict[str, Any]]:
        """List all deployed modules.

        Returns:
            List of module information
        """
        # TODO: Implement module listing
        raise NotImplementedError("Module listing coming soon")

    async def rotate_secret(self, secret_name: str) -> bool:
        """Rotate a specific secret.

        Args:
            secret_name: Name of the secret to rotate

        Returns:
            True if rotation successful
        """
        # TODO: Implement secret rotation
        raise NotImplementedError("Secret rotation coming soon")

    @classmethod
    def from_env(cls) -> "Orchestr8SDK":
        """Create SDK instance from environment variables.

        Required environment variables:
        - O8_PROVIDER: Cloud provider (aws, gcp, azure, local)
        - O8_CLUSTER_NAME: Kubernetes cluster name
        - O8_DOMAIN: Platform domain
        - O8_GITHUB_ORG: GitHub organization
        - GITHUB_TOKEN: GitHub personal access token

        Optional:
        - O8_REGION: Cloud region (for non-local providers)

        Returns:
            Configured SDK instance
        """
        import os

        provider = CloudProvider(os.environ.get("O8_PROVIDER", "local"))

        config = Config(
            provider=provider,
            region=os.environ.get("O8_REGION")
            if provider != CloudProvider.LOCAL
            else None,
            cluster_name=os.environ["O8_CLUSTER_NAME"],
            domain=os.environ["O8_DOMAIN"],
            github=GitHubConfig(
                org=os.environ["O8_GITHUB_ORG"], token=os.environ["GITHUB_TOKEN"]
            ),
        )

        return cls(config)

    def __repr__(self) -> str:
        """String representation of SDK instance."""
        return f"Orchestr8SDK(cluster='{self.config.cluster_name}', provider='{self.config.provider.value}')"
