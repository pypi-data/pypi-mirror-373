"""Tests for secrets management."""

import pytest
from unittest.mock import patch

from orchestr8.core.secrets import SecretsManager
from orchestr8.core import Config, CloudProvider
from orchestr8.core.config import GitHubConfig
from orchestr8.providers.local import LocalSecretsProvider
from orchestr8.providers.aws import AWSSecretsProvider


@pytest.fixture
def local_config():
    """Create a local configuration."""
    return Config(
        provider=CloudProvider.LOCAL,
        cluster_name="test-cluster",
        domain="test.local",
        github=GitHubConfig(org="test-org", token="test-token"),
    )


@pytest.fixture
def aws_config():
    """Create an AWS configuration."""
    return Config(
        provider=CloudProvider.AWS,
        region="us-east-1",
        cluster_name="test-cluster",
        domain="test.aws",
        github=GitHubConfig(org="test-org", token="test-token"),
    )


def test_secrets_manager_creates_local_provider(local_config):
    """Test that SecretsManager creates LocalSecretsProvider for local config."""
    manager = SecretsManager(local_config)
    assert isinstance(manager.provider, LocalSecretsProvider)


def test_secrets_manager_creates_aws_provider(aws_config):
    """Test that SecretsManager creates AWSSecretsProvider for AWS config."""
    with patch("orchestr8.providers.aws.boto3.client"):
        manager = SecretsManager(aws_config)
        assert isinstance(manager.provider, AWSSecretsProvider)


def test_generate_password():
    """Test password generation."""
    password = SecretsManager.generate_password(20)
    assert len(password) == 20
    # Should contain letters, digits, and special characters
    assert any(c.isalpha() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in "!@#$%^&*" for c in password)


def test_generate_random_string():
    """Test random string generation."""
    random_str = SecretsManager.generate_random_string(32)
    assert len(random_str) == 32
    # Should only contain letters and digits
    assert all(c.isalnum() for c in random_str)


@pytest.mark.asyncio
async def test_ensure_secret_existing(local_config):
    """Test ensuring a secret that already exists."""
    manager = SecretsManager(local_config)

    with patch.object(manager.provider, "get_secret") as mock_get:
        mock_get.return_value = "existing-value"

        result = await manager._ensure_secret("test-key", None, "Test secret")

        assert result == "existing-value"
        mock_get.assert_called_once_with("test-key")


@pytest.mark.asyncio
async def test_ensure_secret_provided_value(local_config):
    """Test ensuring a secret with provided value."""
    manager = SecretsManager(local_config)

    with (
        patch.object(manager.provider, "get_secret") as mock_get,
        patch.object(manager.provider, "set_secret") as mock_set,
    ):
        mock_get.return_value = None  # Secret doesn't exist

        result = await manager._ensure_secret(
            "test-key", "provided-value", "Test secret"
        )

        assert result == "provided-value"
        mock_set.assert_called_once_with("test-key", "provided-value", "Test secret")


@pytest.mark.asyncio
async def test_ensure_secret_generated(local_config):
    """Test ensuring a secret with generator."""
    manager = SecretsManager(local_config)

    def test_generator():
        return "generated-value"

    with (
        patch.object(manager.provider, "get_secret") as mock_get,
        patch.object(manager.provider, "set_secret") as mock_set,
    ):
        mock_get.return_value = None  # Secret doesn't exist

        result = await manager._ensure_secret(
            "test-key", None, "Test secret", generator=test_generator
        )

        assert result == "generated-value"
        mock_set.assert_called_once_with("test-key", "generated-value", "Test secret")


@pytest.mark.asyncio
async def test_ensure_secret_no_value_no_generator(local_config):
    """Test ensuring a secret with no value and no generator raises error."""
    manager = SecretsManager(local_config)

    with patch.object(manager.provider, "get_secret") as mock_get:
        mock_get.return_value = None  # Secret doesn't exist

        with pytest.raises(ValueError, match="No value provided for secret 'test-key'"):
            await manager._ensure_secret("test-key", None, "Test secret")


@pytest.mark.asyncio
async def test_ensure_all_secrets(local_config):
    """Test ensuring all required secrets."""
    manager = SecretsManager(local_config)

    with patch.object(manager, "_ensure_secret") as mock_ensure:
        # Mock all ensure_secret calls to return test values
        mock_ensure.side_effect = [
            "github-token-value",
            "oauth-app-id",
            "oauth-app-secret",
            "keycloak-password",
            "cookie-secret",
            "argocd-password",
        ]

        results = await manager.ensure_all_secrets()

        assert results["github_token"] == "github-token-value"
        assert results["keycloak_admin_password"] == "keycloak-password"
        assert results["oauth2_proxy_cookie_secret"] == "cookie-secret"
        assert results["argocd_admin_password"] == "argocd-password"

        # Verify all secrets were requested
        assert mock_ensure.call_count == 6


@pytest.mark.asyncio
async def test_export_kubernetes_secrets(local_config):
    """Test exporting secrets as Kubernetes manifests."""
    manager = SecretsManager(local_config)

    with patch.object(manager, "ensure_all_secrets") as mock_ensure:
        mock_ensure.return_value = {
            "github_token": "test-token",
            "github_oauth_app_id": "app-id",
            "github_oauth_app_secret": "app-secret",
            "keycloak_admin_password": "keycloak-pass",
            "oauth2_proxy_cookie_secret": "cookie-secret",
            "argocd_admin_password": "argo-pass",
        }

        k8s_secrets = await manager.export_kubernetes_secrets()

        # Check ArgoCD GitHub credentials
        assert "argocd-github-creds" in k8s_secrets
        assert k8s_secrets["argocd-github-creds"]["namespace"] == "argocd"
        assert k8s_secrets["argocd-github-creds"]["data"]["username"] == "test-org"
        assert k8s_secrets["argocd-github-creds"]["data"]["password"] == "test-token"

        # Check Keycloak admin credentials
        assert "keycloak-admin-creds" in k8s_secrets
        assert k8s_secrets["keycloak-admin-creds"]["namespace"] == "platform"
        assert k8s_secrets["keycloak-admin-creds"]["data"]["username"] == "admin"
        assert (
            k8s_secrets["keycloak-admin-creds"]["data"]["password"] == "keycloak-pass"
        )

        # Check OAuth2 proxy secrets
        assert "oauth2-proxy-secrets" in k8s_secrets
        assert k8s_secrets["oauth2-proxy-secrets"]["namespace"] == "auth"
        assert k8s_secrets["oauth2-proxy-secrets"]["data"]["client-id"] == "app-id"
        assert (
            k8s_secrets["oauth2-proxy-secrets"]["data"]["client-secret"] == "app-secret"
        )
        assert (
            k8s_secrets["oauth2-proxy-secrets"]["data"]["cookie-secret"]
            == "cookie-secret"
        )
