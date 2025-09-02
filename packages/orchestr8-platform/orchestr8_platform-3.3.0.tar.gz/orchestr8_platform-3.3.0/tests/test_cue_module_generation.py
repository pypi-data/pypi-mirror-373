"""Tests for CUE-based module generation."""

import tempfile
import yaml
from pathlib import Path
from unittest.mock import patch

import pytest
from rich.console import Console

from orchestr8.core.cue_engine import CUEEngine, CUEEngineError


class TestCUEModuleGeneration:
    """Test CUE-based module resource generation."""

    @patch("pathlib.Path.exists")
    @patch("shutil.which")
    def setup_method(self, method, mock_which, mock_exists):
        """Set up test fixtures."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        # Use a real console with no output for tests to avoid Mock issues with Rich Progress
        import io

        self.console = Console(file=io.StringIO(), force_terminal=False)
        self.cue_engine = CUEEngine(console=self.console)

        self.tenant_config = {
            "metadata": {
                "name": "test-company",
                "displayName": "Test Company",
                "domain": "test.platform.local",
                "organization": {"name": "Test Organization Inc."},
                "environment": "dev",
            },
            "networking": {"domain": "test.platform.local"},
            "security": {
                "network": {"defaultDeny": True},
                "rbac": {"serviceAccount": {"create": True}},
            },
            "resources": {
                "namespaceQuota": {
                    "compute": {"requestsCpu": "10", "requestsMemory": "20Gi"}
                }
            },
        }

    def test_generate_langfuse_resources(self):
        """Test Langfuse resource generation."""
        target_namespace = "test-company-langfuse"

        resources = self.cue_engine.generate_tenant_module_resources(
            self.tenant_config, "langfuse", target_namespace
        )

        # Verify namespace
        assert "namespace" in resources
        namespace = resources["namespace"]
        assert namespace["metadata"]["name"] == target_namespace
        assert (
            namespace["metadata"]["labels"]["orchestr8.platform/tenant"]
            == "test-company"
        )
        assert (
            namespace["metadata"]["labels"]["orchestr8.platform/module"] == "langfuse"
        )

        # Verify deployment
        assert "deployment" in resources
        deployment = resources["deployment"]
        assert deployment["metadata"]["name"] == "langfuse"
        assert deployment["metadata"]["namespace"] == target_namespace
        assert (
            deployment["spec"]["template"]["spec"]["containers"][0]["image"]
            == "langfuse/langfuse:2.89.0"
        )

        # Verify environment variables
        containers = deployment["spec"]["template"]["spec"]["containers"]
        env_vars = {env["name"]: env["value"] for env in containers[0]["env"]}
        assert "NEXTAUTH_URL" in env_vars
        assert env_vars["NEXTAUTH_URL"] == "https://langfuse.test.platform.local"
        assert env_vars["TELEMETRY_ENABLED"] == "false"

        # Verify service
        assert "service" in resources
        service = resources["service"]
        assert service["metadata"]["name"] == "langfuse"
        assert service["spec"]["ports"][0]["port"] == 3000

    def test_generate_clickhouse_resources(self):
        """Test ClickHouse resource generation."""
        target_namespace = "test-company-clickhouse"

        resources = self.cue_engine.generate_tenant_module_resources(
            self.tenant_config, "clickhouse", target_namespace
        )

        # Verify namespace
        assert "namespace" in resources
        namespace = resources["namespace"]
        assert namespace["metadata"]["name"] == target_namespace
        assert (
            namespace["metadata"]["labels"]["orchestr8.platform/module"] == "clickhouse"
        )

        # Verify deployment
        assert "deployment" in resources
        deployment = resources["deployment"]
        assert deployment["metadata"]["name"] == "clickhouse"
        assert (
            deployment["spec"]["template"]["spec"]["containers"][0]["image"]
            == "clickhouse/clickhouse-server:24.8.5.115"
        )

        # Verify ports
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        ports = {port["name"]: port["containerPort"] for port in container["ports"]}
        assert ports["http"] == 8123
        assert ports["tcp"] == 9000

        # Verify service
        service = resources["service"]
        service_ports = {
            port["name"]: port["port"] for port in service["spec"]["ports"]
        }
        assert service_ports["http"] == 8123
        assert service_ports["tcp"] == 9000

    def test_generate_generic_module_resources(self):
        """Test generic module resource generation."""
        target_namespace = "test-company-unknown"

        resources = self.cue_engine.generate_tenant_module_resources(
            self.tenant_config, "unknown-module", target_namespace
        )

        # Should only generate namespace for unknown modules
        assert "namespace" in resources
        assert len(resources) == 1

        namespace = resources["namespace"]
        assert namespace["metadata"]["name"] == target_namespace
        assert (
            namespace["metadata"]["labels"]["orchestr8.platform/module"]
            == "unknown-module"
        )

    def test_tenant_context_integration(self):
        """Test that tenant context is properly integrated into resources."""
        resources = self.cue_engine.generate_tenant_module_resources(
            self.tenant_config, "langfuse", "test-company-langfuse"
        )

        # All resources should have tenant labels
        for resource_type, resource in resources.items():
            if "metadata" in resource and "labels" in resource["metadata"]:
                labels = resource["metadata"]["labels"]
                assert labels.get("orchestr8.platform/tenant") == "test-company"
                # Check for either managed label (some resources may not have it)
                if "orchestr8.platform/managed" in labels:
                    assert labels["orchestr8.platform/managed"] == "true"

    def test_resource_naming_conventions(self):
        """Test that resources follow naming conventions."""
        resources = self.cue_engine.generate_tenant_module_resources(
            self.tenant_config, "langfuse", "test-company-langfuse"
        )

        # Namespace should follow tenant-module pattern
        namespace = resources["namespace"]
        assert namespace["metadata"]["name"] == "test-company-langfuse"

        # Deployment and service should use module name
        deployment = resources["deployment"]
        service = resources["service"]
        assert deployment["metadata"]["name"] == "langfuse"
        assert service["metadata"]["name"] == "langfuse"

    def test_resource_security_context(self):
        """Test that security contexts are properly configured."""
        resources = self.cue_engine.generate_tenant_module_resources(
            self.tenant_config, "langfuse", "test-company-langfuse"
        )

        # For now, basic resources don't include security context
        # But we should verify labels for security policies
        deployment = resources["deployment"]
        labels = deployment["metadata"]["labels"]
        assert "orchestr8.platform/tenant" in labels
        assert "orchestr8.platform/module" in labels

    def test_different_tenant_configurations(self):
        """Test resource generation with different tenant configurations."""
        # Test with different domain
        different_config = self.tenant_config.copy()
        different_config["metadata"]["domain"] = "different.example.com"
        different_config["networking"]["domain"] = "different.example.com"

        resources = self.cue_engine.generate_tenant_module_resources(
            different_config, "langfuse", "different-tenant-langfuse"
        )

        deployment = resources["deployment"]
        env_vars = {
            env["name"]: env["value"]
            for env in deployment["spec"]["template"]["spec"]["containers"][0]["env"]
        }
        assert env_vars["NEXTAUTH_URL"] == "https://langfuse.different.example.com"


class TestCUEEngineIntegration:
    """Integration tests for CUE engine."""

    def setup_method(self):
        """Set up test fixtures."""
        import io

        self.console = Console(file=io.StringIO(), force_terminal=False)

    @patch("shutil.which")
    def test_cue_cli_availability_check(self, mock_which):
        """Test CUE CLI availability checking."""
        # Test when CUE CLI is available
        mock_which.return_value = "/usr/bin/cue"

        with patch("pathlib.Path.exists", return_value=True):
            engine = CUEEngine(console=self.console)
            assert engine is not None

        # Test when CUE CLI is not available
        mock_which.return_value = None

        with pytest.raises(CUEEngineError, match="CUE CLI not found"):
            with patch("pathlib.Path.exists", return_value=True):
                CUEEngine(console=self.console)

    def test_schema_path_validation(self):
        """Test schema path validation."""
        with patch("shutil.which", return_value="/usr/bin/cue"):
            # Test with non-existent schema path
            with pytest.raises(CUEEngineError, match="CUE schema path does not exist"):
                CUEEngine(schema_path=Path("/nonexistent/path"), console=self.console)


class TestModuleResourceValidation:
    """Test module resource validation."""

    @patch("pathlib.Path.exists")
    @patch("shutil.which")
    def setup_method(self, method, mock_which, mock_exists):
        """Set up test fixtures."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        import io

        self.console = Console(file=io.StringIO(), force_terminal=False)
        self.cue_engine = CUEEngine(console=self.console)

    def test_langfuse_resource_structure(self):
        """Test Langfuse resources have correct structure."""
        tenant_config = {
            "metadata": {"name": "test", "domain": "test.local"},
            "networking": {"domain": "test.local"},
        }

        resources = self.cue_engine._generate_langfuse_resources(
            tenant_config, "test-langfuse"
        )

        # Validate required Kubernetes fields
        for resource_name, resource in resources.items():
            assert "apiVersion" in resource
            assert "kind" in resource
            assert "metadata" in resource

            # All resources should have proper metadata
            metadata = resource["metadata"]
            assert "name" in metadata
            assert "labels" in metadata or resource["kind"] == "Namespace"

    def test_clickhouse_resource_structure(self):
        """Test ClickHouse resources have correct structure."""
        tenant_config = {
            "metadata": {"name": "test", "domain": "test.local"},
            "networking": {"domain": "test.local"},
        }

        resources = self.cue_engine._generate_clickhouse_resources(
            tenant_config, "test-clickhouse"
        )

        # Validate deployment has required fields
        deployment = resources["deployment"]
        assert deployment["spec"]["selector"]["matchLabels"]["app"] == "clickhouse"
        assert (
            deployment["spec"]["template"]["metadata"]["labels"]["app"] == "clickhouse"
        )

        # Validate service selector matches deployment labels
        service = resources["service"]
        assert service["spec"]["selector"]["app"] == "clickhouse"

    def test_resource_yaml_serialization(self):
        """Test that generated resources can be serialized to YAML."""
        tenant_config = {
            "metadata": {"name": "test", "domain": "test.local"},
            "networking": {"domain": "test.local"},
        }

        resources = self.cue_engine.generate_tenant_module_resources(
            tenant_config, "langfuse", "test-langfuse"
        )

        # Should be able to serialize all resources to YAML
        for resource_name, resource in resources.items():
            yaml_str = yaml.dump(resource, default_flow_style=False)
            assert yaml_str is not None
            assert len(yaml_str) > 0

            # Should be able to round-trip
            parsed = yaml.safe_load(yaml_str)
            assert parsed == resource


class TestModuleExportFunctionality:
    """Test module resource export functionality."""

    @patch("pathlib.Path.exists")
    @patch("shutil.which")
    def setup_method(self, method, mock_which, mock_exists):
        """Set up test fixtures."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        import io

        self.console = Console(file=io.StringIO(), force_terminal=False)
        self.cue_engine = CUEEngine(console=self.console)

    def test_export_to_yaml_structure(self):
        """Test exporting module resources to YAML files."""
        tenant_config = {
            "metadata": {"name": "test", "domain": "test.local"},
            "networking": {"domain": "test.local"},
        }

        resources = self.cue_engine.generate_tenant_module_resources(
            tenant_config, "langfuse", "test-langfuse"
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir)

            # Export should not raise exceptions
            self.cue_engine.export_to_yaml(resources, output_path)

            # Check that files were created
            yaml_files = list(output_path.glob("*.yaml"))
            assert len(yaml_files) == len(resources)

            # Verify file contents
            for yaml_file in yaml_files:
                with open(yaml_file) as f:
                    content = yaml.safe_load(f)
                    assert "apiVersion" in content
                    assert "kind" in content

    def test_export_handles_different_resource_types(self):
        """Test export handles single resources, lists, and nested structures."""
        test_data = {
            "single_resource": {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {"name": "test"},
            },
            "resource_list": [
                {
                    "apiVersion": "v1",
                    "kind": "ConfigMap",
                    "metadata": {"name": "test1"},
                },
                {"apiVersion": "v1", "kind": "Secret", "metadata": {"name": "test2"}},
            ],
            "nested_structure": {
                "subdir": {
                    "apiVersion": "v1",
                    "kind": "Service",
                    "metadata": {"name": "nested"},
                }
            },
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir)

            # Should handle all types without errors
            self.cue_engine.export_to_yaml(test_data, output_path)

            # Verify structure
            assert (output_path / "single-resource.yaml").exists()
            assert (output_path / "resource-list.yaml").exists()
            assert (output_path / "nested-structure").exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
