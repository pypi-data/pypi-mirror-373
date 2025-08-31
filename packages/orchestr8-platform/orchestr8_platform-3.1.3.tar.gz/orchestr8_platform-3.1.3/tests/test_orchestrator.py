"""Tests for the core Orchestrator class."""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from orchestr8.core import Orchestrator, Config, CloudProvider
from orchestr8.core.config import GitHubConfig, KeycloakConfig


@pytest.fixture
def test_config():
    """Create a test configuration."""
    return Config(
        provider=CloudProvider.LOCAL,
        cluster_name="test-cluster",
        domain="test.local",
        github=GitHubConfig(org="test-org", token="test-token"),
        keycloak=KeycloakConfig(),
    )


@pytest.fixture
def mock_k8s_api():
    """Mock Kubernetes API clients."""
    with (
        patch("kubernetes.config.load_kube_config"),
        patch("kubernetes.client.CoreV1Api") as mock_core,
        patch("kubernetes.client.AppsV1Api") as mock_apps,
    ):
        yield mock_core.return_value, mock_apps.return_value


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_validate_prerequisites_success(test_config, mock_k8s_api):
    """Test successful prerequisites validation."""
    mock_core_api, _ = mock_k8s_api

    with (
        patch("shutil.which"),
        patch.object(Orchestrator, "_command_exists", return_value=True),
    ):
        orchestrator = Orchestrator(test_config)
        orchestrator.k8s_api = mock_core_api

        # Mock successful namespace list
        mock_core_api.list_namespace.return_value = MagicMock()

        result = await orchestrator.validate_prerequisites()

        assert result["valid"] is True
        assert len(result["errors"]) == 0


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_validate_prerequisites_missing_kubectl(test_config):
    """Test prerequisites validation with missing kubectl."""
    with patch.object(Orchestrator, "_command_exists") as mock_exists:
        mock_exists.side_effect = lambda cmd: cmd != "kubectl"

        orchestrator = Orchestrator(test_config)
        result = await orchestrator.validate_prerequisites()

        assert result["valid"] is False
        assert "kubectl not found in PATH" in result["errors"]


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_validate_prerequisites_no_k8s_connection(test_config, mock_k8s_api):
    """Test prerequisites validation with no Kubernetes connection."""
    mock_core_api, _ = mock_k8s_api

    with patch.object(Orchestrator, "_command_exists", return_value=True):
        orchestrator = Orchestrator(test_config)
        orchestrator.k8s_api = mock_core_api

        # Mock failed namespace list
        mock_core_api.list_namespace.side_effect = Exception("Connection refused")

        result = await orchestrator.validate_prerequisites()

        assert result["valid"] is False
        assert any(
            "Cannot connect to Kubernetes cluster" in error
            for error in result["errors"]
        )


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_namespaces(test_config, mock_k8s_api):
    """Test namespace creation."""
    mock_core_api, _ = mock_k8s_api

    orchestrator = Orchestrator(test_config)
    orchestrator.k8s_api = mock_core_api

    # Mock successful namespace creation
    mock_core_api.create_namespace.return_value = MagicMock()

    created = await orchestrator.create_namespaces()

    # Should create all required namespaces
    assert len(created) == 6
    assert "argocd" in created
    assert "platform" in created
    assert "istio-system" in created


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_namespaces_already_exist(test_config, mock_k8s_api):
    """Test namespace creation when namespaces already exist."""
    mock_core_api, _ = mock_k8s_api

    orchestrator = Orchestrator(test_config)
    orchestrator.k8s_api = mock_core_api

    # Mock namespace already exists error
    from kubernetes.client.rest import ApiException

    mock_core_api.create_namespace.side_effect = ApiException(status=409)

    # Should not raise exception
    created = await orchestrator.create_namespaces()
    assert created == []  # Nothing created since all exist


@pytest.mark.asyncio
@pytest.mark.integration
async def test_create_kubernetes_secrets(test_config, mock_k8s_api):
    """Test Kubernetes secret creation."""
    mock_core_api, _ = mock_k8s_api

    with patch("orchestr8.core.orchestrator.SecretsManager") as mock_secrets:
        orchestrator = Orchestrator(test_config)
        orchestrator.k8s_api = mock_core_api

        # Mock secrets manager
        mock_secrets_instance = mock_secrets.return_value
        mock_secrets_instance.export_kubernetes_secrets = AsyncMock(
            return_value={
                "test-secret": {
                    "namespace": "default",
                    "data": {"key1": "value1", "key2": "value2"},
                }
            }
        )
        orchestrator.secrets_manager = mock_secrets_instance

        # Mock successful secret creation
        mock_core_api.create_namespaced_secret.return_value = MagicMock()

        results = await orchestrator.create_kubernetes_secrets()

        assert results["default/test-secret"] is True
        mock_core_api.create_namespaced_secret.assert_called_once()


@pytest.mark.asyncio
@pytest.mark.slow
async def test_install_argocd(test_config):
    """Test ArgoCD installation."""
    with (
        patch("subprocess.run") as mock_run,
        patch("tempfile.NamedTemporaryFile"),
        patch("pathlib.Path.unlink"),
    ):
        # Mock successful helm commands
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="cGFzc3dvcmQ=",  # base64 encoded "password"
        )

        orchestrator = Orchestrator(test_config)
        result = await orchestrator.install_argocd()

        assert result["installed"] is True
        assert result["admin_password"] == "password"
        assert result["url"] == "http://localhost:30080"

        # Verify helm commands were called
        calls = [call[0][0] for call in mock_run.call_args_list]
        assert [
            "helm",
            "repo",
            "add",
            "argo",
            "https://argoproj.github.io/argo-helm",
        ] in calls
        assert ["helm", "repo", "update"] in calls


@pytest.mark.asyncio
@pytest.mark.slow
async def test_deploy_platform(test_config):
    """Test platform deployment."""
    with (
        patch("subprocess.run") as mock_run,
        patch("tempfile.NamedTemporaryFile"),
        patch("pathlib.Path.unlink"),
    ):
        # Mock successful kubectl apply
        mock_run.return_value = MagicMock(returncode=0)

        orchestrator = Orchestrator(test_config)

        # Mock secrets manager
        orchestrator.secrets_manager = MagicMock()
        orchestrator.secrets_manager.provider = MagicMock()
        orchestrator.secrets_manager.provider.get_secret = AsyncMock(
            return_value="test-token"
        )

        result = await orchestrator.deploy_platform()

        assert result["deployed"] is True
        assert result["application"] == "orchestr8-platform"

        # Verify kubectl apply was called
        kubectl_calls = [
            call[0][0] for call in mock_run.call_args_list if call[0][0][0] == "kubectl"
        ]
        assert len(kubectl_calls) == 2  # repo secret and app


@pytest.mark.asyncio
@pytest.mark.smoke
async def test_get_status(test_config, mock_k8s_api):
    """Test getting platform status."""
    mock_core_api, _ = mock_k8s_api

    with patch("subprocess.run") as mock_run:
        orchestrator = Orchestrator(test_config)
        orchestrator.k8s_api = mock_core_api

        # Mock successful responses
        mock_core_api.list_namespace.return_value = MagicMock()
        mock_run.return_value = MagicMock(returncode=0)

        status = await orchestrator.get_status()

        assert status["kubernetes"]["connected"] is True
        assert status["argocd"]["installed"] is True
        assert status["platform"]["deployed"] is True


@pytest.mark.asyncio
@pytest.mark.slow
@pytest.mark.cluster
async def test_setup_complete_flow(test_config, mock_k8s_api):
    """Test complete setup flow."""
    mock_core_api, _ = mock_k8s_api

    with (
        patch.object(Orchestrator, "_command_exists", return_value=True),
        patch("subprocess.run") as mock_run,
        patch("tempfile.NamedTemporaryFile"),
        patch("pathlib.Path.unlink"),
    ):
        orchestrator = Orchestrator(test_config)
        orchestrator.k8s_api = mock_core_api

        # Mock all subprocess calls succeed
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="cGFzc3dvcmQ=",  # base64 encoded "password"
        )

        # Mock secrets manager
        with (
            patch.object(
                orchestrator.secrets_manager, "ensure_all_secrets"
            ) as mock_ensure,
            patch.object(
                orchestrator.secrets_manager, "export_kubernetes_secrets"
            ) as mock_export,
        ):
            mock_ensure.return_value = {
                "github_token": "token",
                "keycloak_admin_password": "password",
            }
            mock_export.return_value = {}

            # Mock GitHub provider
            if orchestrator.github_provider:
                orchestrator.github_provider.validate_token = AsyncMock()

            # Mock namespace operations
            mock_core_api.list_namespace.return_value = MagicMock()
            mock_core_api.create_namespace.return_value = MagicMock()

            results = await orchestrator.setup()

            assert results["prerequisites"]["valid"] is True
            assert results["secrets"]["created"] is True
            assert results["argocd"]["installed"] is True
            assert results["platform"]["deployed"] is True
