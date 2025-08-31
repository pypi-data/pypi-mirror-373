"""Test Azure provider integration."""

import subprocess
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from orchestr8.core.config import Config
from orchestr8.providers.azure import AzureProvider


class TestAzureProvider:
    """Test Azure provider functionality."""

    def test_provider_initialization(self):
        """Test Azure provider can be initialized."""
        # Create a mock config with required fields
        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
        )

        # Test provider initialization
        provider = AzureProvider(config)
        assert provider is not None
        assert provider.config == config

    def test_provider_has_required_methods(self):
        """Test Azure provider has all required methods."""
        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
        )
        provider = AzureProvider(config)

        # Check Azure-specific methods exist
        assert hasattr(provider, "validate_credentials")
        assert hasattr(provider, "create_key_vault")
        assert hasattr(provider, "get_aks_credentials")
        assert hasattr(provider, "list_aks_clusters")
        assert hasattr(provider, "ensure_resource_group")
        assert hasattr(provider, "create_storage_account")
        assert hasattr(provider, "setup_workload_identity")
        assert hasattr(provider, "get_cluster_info")
        assert hasattr(provider, "validate_environment")

    @patch("subprocess.run")
    def test_validate_credentials_success(self, mock_run):
        """Test successful Azure credentials validation."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='{"name": "Test Subscription", "id": "12345", "tenantId": "67890"}',
        )

        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
        )
        provider = AzureProvider(config)

        result = provider.validate_credentials()
        assert result is True
        mock_run.assert_called_once_with(
            ["az", "account", "show", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=10,
        )

    @patch("subprocess.run")
    def test_validate_credentials_not_authenticated(self, mock_run):
        """Test Azure credentials validation when not authenticated."""
        mock_run.return_value = Mock(returncode=1, stderr="Please run 'az login'")

        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
        )
        provider = AzureProvider(config)

        result = provider.validate_credentials()
        assert result is False

    @patch("subprocess.run")
    def test_validate_credentials_cli_not_installed(self, mock_run):
        """Test Azure credentials validation when CLI is not installed."""
        mock_run.side_effect = FileNotFoundError()

        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
        )
        provider = AzureProvider(config)

        result = provider.validate_credentials()
        assert result is False

    @patch("subprocess.run")
    def test_list_aks_clusters(self, mock_run):
        """Test listing AKS clusters."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='[{"name": "cluster1", "resourceGroup": "rg1"}, {"name": "cluster2", "resourceGroup": "rg2"}]',
        )

        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
        )
        provider = AzureProvider(config)

        clusters = provider.list_aks_clusters()
        assert len(clusters) == 2
        assert clusters[0]["name"] == "cluster1"
        assert clusters[1]["name"] == "cluster2"

    @patch("subprocess.run")
    def test_ensure_resource_group_exists(self, mock_run):
        """Test ensuring resource group when it already exists."""
        mock_run.return_value = Mock(returncode=0, stdout='{"name": "test-rg"}')

        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
        )
        provider = AzureProvider(config)

        result = provider.ensure_resource_group("test-rg", "eastus2")
        assert result is True
        mock_run.assert_called_once_with(
            ["az", "group", "show", "--name", "test-rg", "--output", "json"],
            capture_output=True,
            text=True,
            timeout=10,
        )

    @patch("subprocess.run")
    def test_ensure_resource_group_creates(self, mock_run):
        """Test creating resource group when it doesn't exist."""
        # First call fails (group doesn't exist), second succeeds (group created)
        mock_run.side_effect = [
            Mock(returncode=1),  # Group doesn't exist
            Mock(returncode=0, stdout='{"name": "test-rg"}'),  # Group created
        ]

        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
            environment="dev",
        )
        provider = AzureProvider(config)

        result = provider.ensure_resource_group("test-rg", "eastus2")
        assert result is True
        assert mock_run.call_count == 2

    @patch("subprocess.run")
    def test_validate_environment(self, mock_run):
        """Test environment validation."""
        # Mock successful responses for all checks
        mock_run.side_effect = [
            Mock(returncode=0),  # az --version
            Mock(
                returncode=0,
                stdout='{"name": "Test", "id": "123", "tenantId": "456"}',
            ),  # az account show
            Mock(returncode=0),  # kubectl version
            Mock(returncode=0),  # terraform version
        ]

        config = Config(
            provider="azure",
            cluster_name="test-cluster",
            domain="test.local",
            github={"org": "test-org", "token": "test-token"},
        )
        provider = AzureProvider(config)

        result = provider.validate_environment()
        assert result is True


class TestTerraformModules:
    """Test Terraform module structure."""

    def test_azure_terraform_modules_exist(self):
        """Test that Azure Terraform modules exist."""
        # Get the correct path to terraform modules
        terraform_path = (
            Path(__file__).parent.parent.parent.parent.parent
            / "terraform"
            / "infrastructure"
            / "azure"
        )

        # Check if the modules exist
        modules = ["networking", "aks"]
        for module in modules:
            module_path = terraform_path / module
            assert module_path.exists(), (
                f"Module {module} should exist at {module_path}"
            )

            # Check for required files
            required_files = ["main.tf", "variables.tf", "outputs.tf"]
            for file in required_files:
                file_path = module_path / file
                assert file_path.exists(), f"File {module}/{file} should exist"


class TestCLICommands:
    """Test CLI command availability."""

    @pytest.mark.skipif(
        subprocess.run(["where", "o8"], capture_output=True, shell=True).returncode
        != 0,
        reason="O8 CLI not installed",
    )
    def test_bootstrap_command_available(self):
        """Test that bootstrap command is available."""
        result = subprocess.run(
            ["o8", "bootstrap", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert result.stdout is not None
        assert "bootstrap" in result.stdout.lower()

    @pytest.mark.skipif(
        subprocess.run(["where", "o8"], capture_output=True, shell=True).returncode
        != 0,
        reason="O8 CLI not installed",
    )
    def test_secrets_command_available(self):
        """Test that secrets command is available."""
        result = subprocess.run(
            ["o8", "secrets", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert result.stdout is not None
        assert "secrets" in result.stdout.lower()

    @pytest.mark.skipif(
        subprocess.run(["where", "o8"], capture_output=True, shell=True).returncode
        != 0,
        reason="O8 CLI not installed",
    )
    def test_azure_provider_in_bootstrap(self):
        """Test that Azure provider is available in bootstrap command."""
        result = subprocess.run(
            ["o8", "bootstrap", "create", "--help"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
        assert result.returncode == 0
        assert result.stdout is not None
        assert "azure" in result.stdout.lower()
