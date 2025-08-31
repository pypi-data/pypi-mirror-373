"""Integration tests for Orchestr8."""

import pytest
from unittest.mock import patch, MagicMock
import tempfile
from pathlib import Path
import json

from orchestr8 import Orchestr8SDK, Config, CloudProvider
from orchestr8.core.config import GitHubConfig, KeycloakConfig
from orchestr8.core import Orchestrator


class TestEndToEndSetup:
    """End-to-end integration tests."""

    @pytest.fixture
    def test_config(self):
        """Create test configuration."""
        return Config(
            provider=CloudProvider.LOCAL,
            cluster_name="integration-test",
            domain="test.local",
            github=GitHubConfig(org="test-org", token="test-token"),
            keycloak=KeycloakConfig(
                admin_username="admin", admin_password="test-password"
            ),
        )

    @pytest.mark.local
    @pytest.mark.asyncio
    async def test_sdk_initialization(self, test_config):
        """Test SDK initialization."""
        sdk = Orchestr8SDK(test_config)

        assert sdk.config == test_config
        assert isinstance(sdk.orchestrator, Orchestrator)

    @pytest.mark.local
    @pytest.mark.asyncio
    async def test_sdk_validate_method(self, test_config):
        """Test SDK validate method."""
        sdk = Orchestr8SDK(test_config)

        with patch.object(sdk.orchestrator, "validate_prerequisites") as mock_validate:
            mock_validate.return_value = {"valid": True, "errors": [], "warnings": []}

            result = await sdk.validate()

            assert result["valid"] is True
            mock_validate.assert_called_once()

    @pytest.mark.asyncio
    async def test_sdk_full_setup_flow(self, test_config):
        """Test full setup flow through SDK."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Override local storage path
            test_config.local_storage_path = Path(tmpdir)

            sdk = Orchestr8SDK(test_config)

            # Mock all external calls
            with (
                patch("subprocess.run") as mock_run,
                patch("kubernetes.config.load_kube_config"),
                patch("kubernetes.client.CoreV1Api") as mock_core_api,
                patch("kubernetes.client.AppsV1Api"),
                patch.object(sdk.orchestrator, "_command_exists", return_value=True),
            ):
                # Setup mocks
                mock_run.return_value = MagicMock(
                    returncode=0,
                    stdout="cGFzc3dvcmQ=",  # base64 "password"
                )

                mock_core = mock_core_api.return_value
                mock_core.list_namespace.return_value = MagicMock()
                mock_core.create_namespace.return_value = MagicMock()
                mock_core.create_namespaced_secret.return_value = MagicMock()

                # Run setup
                results = await sdk.setup()

                # Verify results
                assert results["prerequisites"]["valid"] is True
                assert results["secrets"]["created"] is True
                assert results["argocd"]["installed"] is True
                assert results["platform"]["deployed"] is True

                # Verify secrets were saved locally
                secrets_file = Path(tmpdir) / ".o8" / "secrets" / "secrets.json"
                assert secrets_file.exists()

                with open(secrets_file) as f:
                    secrets = json.load(f)
                    assert "github-token" in secrets
                    assert secrets["github-token"] == "test-token"


class TestSecretsIntegration:
    """Integration tests for secrets management."""

    @pytest.mark.asyncio
    async def test_local_to_kubernetes_secrets_flow(self):
        """Test flow from local secrets to Kubernetes secrets."""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = Config(
                provider=CloudProvider.LOCAL,
                cluster_name="test",
                domain="test.local",
                github=GitHubConfig(org="test-org", token="test-token"),
                local_storage_path=Path(tmpdir),
            )

            # Create SDK
            sdk = Orchestr8SDK(config)

            # Ensure secrets
            with (
                patch("kubernetes.config.load_kube_config"),
                patch("kubernetes.client.CoreV1Api"),
            ):
                secrets = await sdk.orchestrator.secrets_manager.ensure_all_secrets()

                # Verify secrets were generated
                assert "github_token" in secrets
                assert "keycloak_admin_password" in secrets
                assert len(secrets["keycloak_admin_password"]) >= 16

                # Export to Kubernetes format
                k8s_secrets = (
                    await sdk.orchestrator.secrets_manager.export_kubernetes_secrets()
                )

                # Verify Kubernetes secrets structure
                assert "argocd-github-creds" in k8s_secrets
                assert (
                    k8s_secrets["argocd-github-creds"]["data"]["password"]
                    == "test-token"
                )


class TestModuleDeployment:
    """Integration tests for module deployment."""

    @pytest.mark.asyncio
    async def test_module_deployment_preparation(self):
        """Test preparing for module deployment."""
        config = Config(
            provider=CloudProvider.LOCAL,
            cluster_name="test",
            domain="test.local",
            github=GitHubConfig(org="test-org", token="test-token"),
        )

        sdk = Orchestr8SDK(config)

        # Mock platform status check
        with patch.object(sdk.orchestrator, "get_status") as mock_status:
            mock_status.return_value = {
                "kubernetes": {"connected": True},
                "argocd": {"installed": True},
                "platform": {"deployed": True},
            }

            status = await sdk.get_status()

            # Verify platform is ready for modules
            assert status["kubernetes"]["connected"] is True
            assert status["argocd"]["installed"] is True
            assert status["platform"]["deployed"] is True


class TestErrorHandling:
    """Integration tests for error handling."""

    @pytest.mark.asyncio
    async def test_setup_with_no_kubernetes(self):
        """Test setup when Kubernetes is not available."""
        config = Config(
            provider=CloudProvider.LOCAL,
            cluster_name="test",
            domain="test.local",
            github=GitHubConfig(org="test-org", token="test-token"),
        )

        sdk = Orchestr8SDK(config)

        # Mock Kubernetes not available
        with patch("kubernetes.config.load_kube_config") as mock_config:
            mock_config.side_effect = Exception("Cannot connect to Kubernetes")

            # Recreate orchestrator to trigger the error
            sdk.orchestrator = Orchestrator(config)

            # Validate should fail
            with patch.object(sdk.orchestrator, "_command_exists", return_value=True):
                result = await sdk.validate()

                assert result["valid"] is False
                assert any(
                    "Kubernetes client not initialized" in error
                    for error in result["errors"]
                )

    @pytest.mark.asyncio
    async def test_setup_with_missing_tools(self):
        """Test setup when required tools are missing."""
        config = Config(
            provider=CloudProvider.LOCAL,
            cluster_name="test",
            domain="test.local",
            github=GitHubConfig(org="test-org", token="test-token"),
        )

        sdk = Orchestr8SDK(config)

        # Mock missing helm
        with patch.object(sdk.orchestrator, "_command_exists") as mock_exists:
            mock_exists.side_effect = lambda cmd: cmd != "helm"

            result = await sdk.validate()

            assert result["valid"] is False
            assert "helm not found in PATH" in result["errors"]
