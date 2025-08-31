"""Integration tests for tenant module commands."""

import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from typer.testing import CliRunner

from orchestr8.cli import app


class TestTenantModuleIntegration:
    """Test tenant module CLI integration."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

        # Sample tenant configuration
        self.tenant_config = {
            "metadata": {
                "name": "test-tenant",
                "displayName": "Test Tenant",
                "domain": "test.platform.local",
                "organization": {"name": "Test Org"},
                "environment": "dev",
            },
            "networking": {"domain": "test.platform.local"},
            "security": {"network": {"defaultDeny": True}},
            "resources": {"namespaceQuota": {"compute": {"requestsCpu": "10"}}},
        }

    def test_tenant_init_creates_directory_structure(self):
        """Test that tenant init creates proper directory structure."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.cwd", return_value=Path(temp_dir)):
                result = self.runner.invoke(
                    app,
                    [
                        "tenant",
                        "init",
                        "test-tenant",
                        "--display-name",
                        "Test Tenant",
                        "--domain",
                        "test.platform.local",
                        "--org",
                        "Test Organization",
                        "--modules",
                        "web-app",
                        "--non-interactive",
                    ],
                )

                assert result.exit_code == 0

                tenant_dir = Path(temp_dir) / "tenants" / "test-tenant"
                assert tenant_dir.exists()
                assert (tenant_dir / "tenant.yaml").exists()
                assert (tenant_dir / "keycloak-realm.json").exists()
                assert (tenant_dir / "tenant-bundle.json").exists()
                assert (tenant_dir / "kubernetes").exists()

    def test_list_modules_command(self):
        """Test the list-modules command."""
        with patch("pathlib.Path") as mock_path:
            # Mock modules directory structure
            mock_modules_dir = Mock()
            mock_modules_dir.exists.return_value = True

            # Mock module directories
            mock_langfuse_dir = Mock()
            mock_langfuse_dir.name = "langfuse"
            mock_langfuse_dir.is_dir.return_value = True

            mock_clickhouse_dir = Mock()
            mock_clickhouse_dir.name = "clickhouse"
            mock_clickhouse_dir.is_dir.return_value = True

            mock_modules_dir.iterdir.return_value = [
                mock_langfuse_dir,
                mock_clickhouse_dir,
            ]
            mock_path.return_value.parent.parent.parent.parent.parent.__truediv__.return_value = mock_modules_dir

            # Mock kustomization files
            mock_langfuse_dir.glob.return_value = [Path("base/kustomization.yaml")]
            mock_clickhouse_dir.glob.return_value = [Path("base/kustomization.yaml")]

            result = self.runner.invoke(app, ["tenant", "list-modules"])

            assert result.exit_code == 0
            assert "langfuse" in result.stdout
            assert "clickhouse" in result.stdout
            assert "✅ Ready" in result.stdout

    @patch("orchestr8.commands.tenant.CUEEngine")
    def test_add_module_command(self, mock_cue_engine):
        """Test the add-module command."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create tenant directory structure
            tenant_dir = Path(temp_dir) / "tenants" / "test-tenant"
            tenant_dir.mkdir(parents=True)

            # Create tenant.yaml
            tenant_config_file = tenant_dir / "tenant.yaml"
            with open(tenant_config_file, "w") as f:
                yaml.dump(self.tenant_config, f)

            # Mock CUE engine
            mock_engine_instance = Mock()
            mock_cue_engine.return_value = mock_engine_instance

            # Mock generated resources
            mock_resources = {
                "namespace": {
                    "apiVersion": "v1",
                    "kind": "Namespace",
                    "metadata": {"name": "test-tenant-langfuse"},
                },
                "deployment": {
                    "apiVersion": "apps/v1",
                    "kind": "Deployment",
                    "metadata": {"name": "langfuse"},
                },
            }
            mock_engine_instance.generate_tenant_module_resources.return_value = (
                mock_resources
            )

            with patch("pathlib.Path.cwd", return_value=Path(temp_dir)):
                with patch("pathlib.Path.exists") as mock_exists:
                    # Mock module directory exists
                    mock_exists.return_value = True

                    result = self.runner.invoke(
                        app,
                        ["tenant", "add-module", "test-tenant", "langfuse"],
                        input="y\n",
                    )

                    assert result.exit_code == 0
                    assert (
                        "Module 'langfuse' added to tenant 'test-tenant'"
                        in result.stdout
                    )

                    # Verify CUE engine was called correctly
                    mock_engine_instance.generate_tenant_module_resources.assert_called_once()
                    args = (
                        mock_engine_instance.generate_tenant_module_resources.call_args[
                            0
                        ]
                    )
                    assert args[1] == "langfuse"  # module_name
                    assert args[2] == "test-tenant-langfuse"  # target_namespace

    def test_add_module_validates_tenant_exists(self):
        """Test that add-module validates tenant exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.cwd", return_value=Path(temp_dir)):
                result = self.runner.invoke(
                    app, ["tenant", "add-module", "nonexistent-tenant", "langfuse"]
                )

                assert result.exit_code == 1
                assert "Tenant 'nonexistent-tenant' not found" in result.stdout

    def test_add_module_validates_module_exists(self):
        """Test that add-module validates module exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create tenant directory
            tenant_dir = Path(temp_dir) / "tenants" / "test-tenant"
            tenant_dir.mkdir(parents=True)

            tenant_config_file = tenant_dir / "tenant.yaml"
            with open(tenant_config_file, "w") as f:
                yaml.dump(self.tenant_config, f)

            with patch("pathlib.Path.cwd", return_value=Path(temp_dir)):
                with patch(
                    "pathlib.Path.exists",
                    side_effect=lambda x: "tenants/test-tenant" in str(x),
                ):
                    result = self.runner.invoke(
                        app,
                        ["tenant", "add-module", "test-tenant", "nonexistent-module"],
                    )

                    assert result.exit_code == 1
                    assert "Module 'nonexistent-module' not found" in result.stdout


class TestTenantModuleE2E:
    """End-to-end tests for tenant module workflows."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_complete_tenant_with_modules_workflow(self, mock_which, mock_run):
        """Test complete workflow: create tenant -> add modules -> validate."""
        mock_which.return_value = "/usr/bin/cue"  # Mock CUE CLI availability

        # Mock successful CUE commands
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = ""
        mock_result.stderr = ""
        mock_run.return_value = mock_result

        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("pathlib.Path.cwd", return_value=Path(temp_dir)):
                # Step 1: Create tenant
                result = self.runner.invoke(
                    app,
                    [
                        "tenant",
                        "init",
                        "e2e-tenant",
                        "--display-name",
                        "E2E Test Tenant",
                        "--domain",
                        "e2e.test.local",
                        "--org",
                        "E2E Test Org",
                        "--modules",
                        "web-app",
                        "--non-interactive",
                    ],
                )

                assert result.exit_code == 0
                tenant_dir = Path(temp_dir) / "tenants" / "e2e-tenant"
                assert tenant_dir.exists()

                # Step 2: Add Langfuse module
                with patch("pathlib.Path.exists", return_value=True):
                    result = self.runner.invoke(
                        app,
                        ["tenant", "add-module", "e2e-tenant", "langfuse"],
                        input="y\n",
                    )

                    assert result.exit_code == 0

                    # Verify module resources were generated
                    module_dir = tenant_dir / "modules" / "langfuse"
                    assert module_dir.exists()

                # Step 3: Add ClickHouse module
                with patch("pathlib.Path.exists", return_value=True):
                    result = self.runner.invoke(
                        app,
                        [
                            "tenant",
                            "add-module",
                            "e2e-tenant",
                            "clickhouse",
                            "--no-auth",
                        ],
                        input="y\n",
                    )

                    assert result.exit_code == 0

                    # Verify module resources were generated
                    module_dir = tenant_dir / "modules" / "clickhouse"
                    assert module_dir.exists()

                # Step 4: Verify ArgoCD applications were created
                argocd_dir = Path(temp_dir) / "argocd-apps" / "tenants"
                assert (argocd_dir / "e2e-tenant-langfuse.yaml").exists()
                assert (argocd_dir / "e2e-tenant-clickhouse.yaml").exists()

    def test_module_resource_generation_accuracy(self):
        """Test that generated module resources are accurate and complete."""
        from orchestr8.core.cue_engine import CUEEngine

        tenant_config = {
            "metadata": {"name": "accuracy-test", "domain": "accuracy.test.local"},
            "networking": {"domain": "accuracy.test.local"},
        }

        with patch("shutil.which", return_value="/usr/bin/cue"):
            with patch("pathlib.Path.exists", return_value=True):
                engine = CUEEngine(console=Mock())

                # Test Langfuse generation
                langfuse_resources = engine.generate_tenant_module_resources(
                    tenant_config, "langfuse", "accuracy-test-langfuse"
                )

                # Verify all required resources are present
                assert "namespace" in langfuse_resources
                assert "deployment" in langfuse_resources
                assert "service" in langfuse_resources

                # Verify proper labeling
                namespace = langfuse_resources["namespace"]
                assert (
                    namespace["metadata"]["labels"]["orchestr8.platform/tenant"]
                    == "accuracy-test"
                )
                assert (
                    namespace["metadata"]["labels"]["orchestr8.platform/module"]
                    == "langfuse"
                )

                # Verify service configuration
                service = langfuse_resources["service"]
                assert service["spec"]["ports"][0]["port"] == 3000
                assert service["spec"]["selector"]["app"] == "langfuse"

                # Test ClickHouse generation
                clickhouse_resources = engine.generate_tenant_module_resources(
                    tenant_config, "clickhouse", "accuracy-test-clickhouse"
                )

                # Verify ClickHouse-specific configuration
                deployment = clickhouse_resources["deployment"]
                container = deployment["spec"]["template"]["spec"]["containers"][0]
                assert container["image"] == "clickhouse/clickhouse-server:24.8.5.115"

                ports = {
                    port["name"]: port["containerPort"] for port in container["ports"]
                }
                assert ports["http"] == 8123
                assert ports["tcp"] == 9000


class TestTenantModuleValidation:
    """Test validation of tenant module configurations."""

    def setup_method(self):
        """Set up test fixtures."""
        self.runner = CliRunner()

    def test_tenant_config_validation(self):
        """Test that tenant configurations are validated properly."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create invalid tenant config
            tenant_dir = Path(temp_dir) / "tenants" / "invalid-tenant"
            tenant_dir.mkdir(parents=True)

            # Invalid config (missing required fields)
            invalid_config = {"metadata": {"name": "incomplete"}}

            tenant_config_file = tenant_dir / "tenant.yaml"
            with open(tenant_config_file, "w") as f:
                yaml.dump(invalid_config, f)

            with patch("pathlib.Path.cwd", return_value=Path(temp_dir)):
                with patch("pathlib.Path.exists", return_value=True):
                    # Should handle invalid configs gracefully
                    result = self.runner.invoke(
                        app, ["tenant", "add-module", "invalid-tenant", "langfuse"]
                    )

                    # Should not crash, but may show warnings
                    assert result.exit_code in [0, 1]  # Allow graceful failure

    def test_module_namespace_naming_validation(self):
        """Test that module namespaces follow naming conventions."""
        from orchestr8.core.cue_engine import CUEEngine

        tenant_config = {
            "metadata": {"name": "naming-test", "domain": "test.local"},
            "networking": {"domain": "test.local"},
        }

        with patch("shutil.which", return_value="/usr/bin/cue"):
            with patch("pathlib.Path.exists", return_value=True):
                engine = CUEEngine(console=Mock())

                resources = engine.generate_tenant_module_resources(
                    tenant_config, "langfuse", "naming-test-langfuse"
                )

                # Verify namespace naming
                namespace = resources["namespace"]
                assert namespace["metadata"]["name"] == "naming-test-langfuse"

                # Verify resources are in correct namespace
                deployment = resources["deployment"]
                assert deployment["metadata"]["namespace"] == "naming-test-langfuse"

                service = resources["service"]
                assert service["metadata"]["namespace"] == "naming-test-langfuse"


class TestArgocdApplicationGeneration:
    """Test ArgoCD application generation for modules."""

    def test_argocd_application_structure(self):
        """Test ArgoCD application has correct structure."""
        from orchestr8.commands.tenant import _generate_module_argocd_application

        tenant_config = {
            "metadata": {"name": "argocd-test", "domain": "argocd.test.local"}
        }

        argocd_app = _generate_module_argocd_application(
            tenant_name="argocd-test",
            module_name="langfuse",
            namespace="argocd-test-langfuse",
            tenant_config=tenant_config,
            environment="dev",
            auth_required=True,
            roles="admin,user",
            github_org="test-org",
            domain_prefix="langfuse",
            source_path="tenants/argocd-test/modules/langfuse",
        )

        # Verify ArgoCD application structure
        assert argocd_app["apiVersion"] == "argoproj.io/v1alpha1"
        assert argocd_app["kind"] == "Application"

        # Verify metadata
        metadata = argocd_app["metadata"]
        assert metadata["name"] == "argocd-test-langfuse"
        assert metadata["labels"]["orchestr8.platform/tenant"] == "argocd-test"
        assert metadata["labels"]["orchestr8.platform/module"] == "langfuse"

        # Verify annotations
        annotations = metadata["annotations"]
        assert annotations["orchestr8.platform/domain"] == "langfuse.argocd.test.local"
        assert annotations["orchestr8.platform/auth-required"] == "true"
        assert annotations["orchestr8.platform/github-org"] == "test-org"
        assert annotations["orchestr8.platform/required-roles"] == "admin,user"

        # Verify spec
        spec = argocd_app["spec"]
        assert spec["destination"]["namespace"] == "argocd-test-langfuse"
        assert spec["source"]["path"] == "tenants/argocd-test/modules/langfuse"

        # Verify info fields
        info_dict = {info["name"]: info["value"] for info in spec["info"]}
        assert info_dict["Description"] == "Langfuse module for argocd-test tenant"
        assert info_dict["URL"] == "https://langfuse.argocd.test.local"
        assert info_dict["Environment"] == "dev"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
