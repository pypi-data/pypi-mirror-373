"""Tests for provider implementations."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path
import tempfile
import os

from orchestr8.providers.local import LocalSecretsProvider
from orchestr8.providers.aws import AWSSecretsProvider
from orchestr8.providers.github import GitHubProvider


class TestLocalSecretsProvider:
    """Tests for LocalSecretsProvider."""

    @pytest.fixture
    def temp_storage(self):
        """Create a temporary storage directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)

    @pytest.mark.smoke
    def test_init_creates_directory(self, temp_storage):
        """Test that initialization creates the storage directory."""
        storage_path = temp_storage / "test_secrets"
        LocalSecretsProvider(storage_path)

        assert storage_path.exists()
        assert storage_path.is_dir()

    @pytest.mark.smoke
    def test_init_uses_default_path(self):
        """Test that default path is used when not specified."""
        with patch("pathlib.Path.home") as mock_home:
            mock_home.return_value = Path("/home/user")
            provider = LocalSecretsProvider()

            assert provider.storage_path == Path("/home/user/.orchestr8/secrets")

    @pytest.mark.asyncio
    @pytest.mark.smoke
    async def test_set_and_get_secret(self, temp_storage):
        """Test setting and getting a secret."""
        provider = LocalSecretsProvider(temp_storage)

        await provider.set_secret("test-key", "test-value", "Test description")
        result = await provider.get_secret("test-key")

        assert result == "test-value"

    @pytest.mark.asyncio
    async def test_get_nonexistent_secret(self, temp_storage):
        """Test getting a non-existent secret returns None."""
        provider = LocalSecretsProvider(temp_storage)

        result = await provider.get_secret("nonexistent")
        assert result is None

    @pytest.mark.asyncio
    async def test_list_secrets(self, temp_storage):
        """Test listing secrets."""
        provider = LocalSecretsProvider(temp_storage)

        await provider.set_secret("key1", "value1")
        await provider.set_secret("key2", "value2")
        await provider.set_secret("key3", "value3", "With description")

        secrets = await provider.list_secrets()

        assert len(secrets) == 3
        assert "key1" in secrets
        assert "key2" in secrets
        assert "key3" in secrets
        # Metadata keys should not be in the list
        assert "_metadata_key3" not in secrets

    @pytest.mark.asyncio
    async def test_delete_secret(self, temp_storage):
        """Test deleting a secret."""
        provider = LocalSecretsProvider(temp_storage)

        await provider.set_secret("test-key", "test-value", "Test description")
        await provider.delete_secret("test-key")

        result = await provider.get_secret("test-key")
        assert result is None

        # Verify metadata was also deleted
        assert "_metadata_test-key" not in provider.secrets

    def test_file_permissions_unix(self, temp_storage):
        """Test that file permissions are set correctly on Unix."""
        if os.name == "nt":
            pytest.skip("Unix permissions test on Windows")

        provider = LocalSecretsProvider(temp_storage)
        provider._save_secrets()

        # Check file permissions (should be 0o600)
        stat_info = os.stat(provider.secrets_file)
        assert stat_info.st_mode & 0o777 == 0o600


class TestAWSSecretsProvider:
    """Tests for AWSSecretsProvider."""

    @pytest.fixture
    def mock_boto_client(self):
        """Mock boto3 client."""
        with patch("orchestr8.providers.aws.boto3.client") as mock_client:
            yield mock_client.return_value

    @pytest.mark.external
    def test_init_with_profile(self, mock_boto_client):
        """Test initialization with AWS profile."""
        with patch("orchestr8.providers.aws.boto3.Session") as mock_session:
            AWSSecretsProvider(
                region="us-east-1", cluster_name="test", aws_profile="test-profile"
            )

            mock_session.assert_called_once_with(profile_name="test-profile")

    @pytest.mark.asyncio
    @pytest.mark.external
    async def test_get_secret_success(self, mock_boto_client):
        """Test successfully getting a secret from AWS."""
        mock_boto_client.get_secret_value.return_value = {"SecretString": "test-value"}

        provider = AWSSecretsProvider(region="us-east-1", cluster_name="test")
        result = await provider.get_secret("test-key")

        assert result == "test-value"
        mock_boto_client.get_secret_value.assert_called_once_with(
            SecretId="o8/test/test-key"
        )

    @pytest.mark.asyncio
    async def test_get_secret_not_found(self, mock_boto_client):
        """Test getting a non-existent secret."""
        mock_boto_client.get_secret_value.side_effect = Exception(
            "ResourceNotFoundException"
        )

        provider = AWSSecretsProvider(region="us-east-1", cluster_name="test")
        result = await provider.get_secret("nonexistent")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_secret_new(self, mock_boto_client):
        """Test creating a new secret."""
        mock_boto_client.create_secret.return_value = {"ARN": "test-arn"}

        provider = AWSSecretsProvider(region="us-east-1", cluster_name="test")
        await provider.set_secret("test-key", "test-value", "Test description")

        mock_boto_client.create_secret.assert_called_once_with(
            Name="o8/test/test-key",
            SecretString="test-value",
            Description="Test description",
            Tags=[
                {"Key": "ManagedBy", "Value": "Orchestr8"},
                {"Key": "Cluster", "Value": "test"},
            ],
        )

    @pytest.mark.asyncio
    async def test_set_secret_update_existing(self, mock_boto_client):
        """Test updating an existing secret."""
        # First call fails (secret exists), second succeeds
        mock_boto_client.create_secret.side_effect = Exception(
            "ResourceExistsException"
        )
        mock_boto_client.update_secret.return_value = {"ARN": "test-arn"}

        provider = AWSSecretsProvider(region="us-east-1", cluster_name="test")
        await provider.set_secret("test-key", "new-value")

        mock_boto_client.update_secret.assert_called_once_with(
            SecretId="o8/test/test-key", SecretString="new-value"
        )

    @pytest.mark.asyncio
    async def test_list_secrets(self, mock_boto_client):
        """Test listing secrets."""
        mock_boto_client.list_secrets.return_value = {
            "SecretList": [
                {"Name": "o8/test/key1"},
                {"Name": "o8/test/key2"},
                {"Name": "other/prefix/key3"},  # Should be filtered out
            ]
        }

        provider = AWSSecretsProvider(region="us-east-1", cluster_name="test")
        secrets = await provider.list_secrets()

        assert len(secrets) == 2
        assert "key1" in secrets
        assert "key2" in secrets
        assert "key3" not in secrets

    @pytest.mark.asyncio
    async def test_delete_secret(self, mock_boto_client):
        """Test deleting a secret."""
        provider = AWSSecretsProvider(region="us-east-1", cluster_name="test")
        await provider.delete_secret("test-key")

        mock_boto_client.delete_secret.assert_called_once_with(
            SecretId="o8/test/test-key", ForceDeleteWithoutRecovery=True
        )


class TestGitHubProvider:
    """Tests for GitHubProvider."""

    @pytest.fixture
    def mock_github(self):
        """Mock GitHub API."""
        with patch("orchestr8.providers.github.Github") as mock_github:
            yield mock_github.return_value

    @pytest.mark.asyncio
    async def test_validate_token_success(self, mock_github):
        """Test successful token validation."""
        mock_user = MagicMock()
        mock_user.login = "test-user"
        mock_github.get_user.return_value = mock_user

        provider = GitHubProvider("test-token")
        user = await provider.validate_token()

        assert user == "test-user"

    @pytest.mark.asyncio
    async def test_validate_token_failure(self, mock_github):
        """Test token validation failure."""
        mock_github.get_user.side_effect = Exception("401 Unauthorized")

        provider = GitHubProvider("invalid-token")

        with pytest.raises(ValueError, match="Invalid GitHub token"):
            await provider.validate_token()

    @pytest.mark.asyncio
    async def test_create_oauth_app(self, mock_github):
        """Test creating OAuth app."""
        mock_user = MagicMock()
        mock_app = MagicMock()
        mock_app.client_id = "test-client-id"
        mock_app.client_secret = "test-client-secret"

        # Mock the create_oauth_app method
        mock_user.create_oauth_app = MagicMock(return_value=mock_app)
        mock_github.get_user.return_value = mock_user

        provider = GitHubProvider("test-token")

        app_info = await provider.create_oauth_app(
            name="Test App",
            homepage_url="https://example.com",
            callback_url="https://example.com/callback",
        )

        assert app_info["client_id"] == "test-client-id"
        assert app_info["client_secret"] == "test-client-secret"

        mock_user.create_oauth_app.assert_called_once_with(
            name="Test App",
            url="https://example.com",
            callback_url="https://example.com/callback",
            description="Orchestr8 OAuth Application",
        )

    @pytest.mark.asyncio
    async def test_check_repository_access_success(self, mock_github):
        """Test checking repository access."""
        mock_repo = MagicMock()
        mock_repo.name = "test-repo"
        mock_github.get_repo.return_value = mock_repo

        provider = GitHubProvider("test-token")

        has_access = await provider.check_repository_access("org/test-repo")
        assert has_access is True

    @pytest.mark.asyncio
    async def test_check_repository_access_failure(self, mock_github):
        """Test checking repository access when no access."""
        mock_github.get_repo.side_effect = Exception("404 Not Found")

        provider = GitHubProvider("test-token")

        has_access = await provider.check_repository_access("org/private-repo")
        assert has_access is False
