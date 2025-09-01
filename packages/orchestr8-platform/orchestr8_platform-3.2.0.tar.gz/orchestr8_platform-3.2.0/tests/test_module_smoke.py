"""Smoke tests for CUE-based module system.

These tests verify that the basic module functionality works without
complex mocking or integration requirements.
"""

import json
import yaml
from unittest.mock import Mock, patch

import pytest

from orchestr8.core.cue_engine import CUEEngine


class TestModuleSmoke:
    """Smoke tests for module generation."""

    @pytest.fixture
    def sample_tenant_config(self):
        """Sample tenant configuration for testing."""
        return {
            "metadata": {
                "name": "smoke-test",
                "displayName": "Smoke Test Tenant",
                "domain": "smoke.test.local",
                "organization": {"name": "Test Org"},
                "environment": "dev",
            },
            "networking": {"domain": "smoke.test.local"},
            "security": {"network": {"defaultDeny": True}},
        }

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    def test_cue_engine_creation(self, mock_exists, mock_which):
        """Test that CUE engine can be created."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        console = Mock()
        engine = CUEEngine(console=console)

        assert engine is not None
        assert engine.console == console

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    def test_langfuse_resource_generation_smoke(
        self, mock_exists, mock_which, sample_tenant_config
    ):
        """Smoke test for Langfuse resource generation."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        engine = CUEEngine(console=Mock())

        resources = engine.generate_tenant_module_resources(
            sample_tenant_config, "langfuse", "smoke-test-langfuse"
        )

        # Basic smoke test - should have required resources
        assert isinstance(resources, dict)
        assert "namespace" in resources
        assert "deployment" in resources
        assert "service" in resources

        # Should be serializable to JSON/YAML
        json.dumps(resources)
        yaml.dump(resources)

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    def test_clickhouse_resource_generation_smoke(
        self, mock_exists, mock_which, sample_tenant_config
    ):
        """Smoke test for ClickHouse resource generation."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        engine = CUEEngine(console=Mock())

        resources = engine.generate_tenant_module_resources(
            sample_tenant_config, "clickhouse", "smoke-test-clickhouse"
        )

        # Basic smoke test
        assert isinstance(resources, dict)
        assert "namespace" in resources
        assert "deployment" in resources
        assert "service" in resources

        # Verify ClickHouse-specific image
        deployment = resources["deployment"]
        container = deployment["spec"]["template"]["spec"]["containers"][0]
        assert "clickhouse" in container["image"]

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    def test_unknown_module_handling_smoke(
        self, mock_exists, mock_which, sample_tenant_config
    ):
        """Smoke test for unknown module handling."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        engine = CUEEngine(console=Mock())

        resources = engine.generate_tenant_module_resources(
            sample_tenant_config, "unknown-module", "smoke-test-unknown"
        )

        # Should gracefully handle unknown modules
        assert isinstance(resources, dict)
        assert "namespace" in resources

        # Unknown modules should only get namespace
        assert len(resources) == 1

    def test_tenant_config_validation_smoke(self, sample_tenant_config):
        """Smoke test for tenant config handling."""
        from orchestr8.core.cue_engine import CUEEngine

        # Should not crash with valid config
        with patch("shutil.which", return_value="/usr/bin/cue"):
            with patch("pathlib.Path.exists", return_value=True):
                engine = CUEEngine(console=Mock())

                # Should handle missing optional fields gracefully
                minimal_config = {
                    "metadata": {"name": "minimal", "domain": "test.local"},
                    "networking": {"domain": "test.local"},
                }

                resources = engine.generate_tenant_module_resources(
                    minimal_config, "langfuse", "minimal-langfuse"
                )

                assert isinstance(resources, dict)
                assert "namespace" in resources

    def test_resource_labeling_smoke(self, sample_tenant_config):
        """Smoke test for proper resource labeling."""
        with patch("shutil.which", return_value="/usr/bin/cue"):
            with patch("pathlib.Path.exists", return_value=True):
                engine = CUEEngine(console=Mock())

                resources = engine.generate_tenant_module_resources(
                    sample_tenant_config, "langfuse", "smoke-test-langfuse"
                )

                # All resources should have tenant labels
                for resource_name, resource in resources.items():
                    if "metadata" in resource and "labels" in resource["metadata"]:
                        labels = resource["metadata"]["labels"]
                        assert "orchestr8.platform/tenant" in labels
                        assert labels["orchestr8.platform/tenant"] == "smoke-test"

    def test_namespace_naming_smoke(self, sample_tenant_config):
        """Smoke test for namespace naming conventions."""
        with patch("shutil.which", return_value="/usr/bin/cue"):
            with patch("pathlib.Path.exists", return_value=True):
                engine = CUEEngine(console=Mock())

                resources = engine.generate_tenant_module_resources(
                    sample_tenant_config, "langfuse", "custom-namespace"
                )

                # Namespace should match requested name
                namespace = resources["namespace"]
                assert namespace["metadata"]["name"] == "custom-namespace"

                # Other resources should be in that namespace
                deployment = resources["deployment"]
                assert deployment["metadata"]["namespace"] == "custom-namespace"


class TestModuleCLISmoke:
    """Smoke tests for module CLI commands."""

    def test_list_modules_import_smoke(self):
        """Smoke test that list-modules command can be imported."""
        from orchestr8.commands.tenant import list_available_modules

        # Should be callable
        assert callable(list_available_modules)

    def test_add_module_import_smoke(self):
        """Smoke test that add-module command can be imported."""
        from orchestr8.commands.tenant import add_module_to_tenant

        # Should be callable
        assert callable(add_module_to_tenant)

    def test_argocd_app_generation_smoke(self):
        """Smoke test for ArgoCD application generation."""
        from orchestr8.commands.tenant import _generate_module_argocd_application

        tenant_config = {"metadata": {"name": "test", "domain": "test.local"}}

        app = _generate_module_argocd_application(
            tenant_name="test",
            module_name="langfuse",
            namespace="test-langfuse",
            tenant_config=tenant_config,
            environment="dev",
            auth_required=True,
            roles=None,
            github_org=None,
            domain_prefix="langfuse",
        )

        # Should produce valid ArgoCD application
        assert app["apiVersion"] == "argoproj.io/v1alpha1"
        assert app["kind"] == "Application"
        assert "metadata" in app
        assert "spec" in app

        # Should be serializable
        yaml.dump(app)


class TestModuleResourceValidationSmoke:
    """Smoke tests for module resource validation."""

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    def test_langfuse_resources_have_required_fields(self, mock_exists, mock_which):
        """Smoke test that Langfuse resources have required Kubernetes fields."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        tenant_config = {
            "metadata": {"name": "validation-test", "domain": "test.local"},
            "networking": {"domain": "test.local"},
        }

        engine = CUEEngine(console=Mock())
        resources = engine._generate_langfuse_resources(tenant_config, "test-langfuse")

        # Every resource should have required K8s fields
        for resource_name, resource in resources.items():
            assert "apiVersion" in resource, f"{resource_name} missing apiVersion"
            assert "kind" in resource, f"{resource_name} missing kind"
            assert "metadata" in resource, f"{resource_name} missing metadata"
            assert "name" in resource["metadata"], (
                f"{resource_name} missing metadata.name"
            )

    @patch("shutil.which")
    @patch("pathlib.Path.exists")
    def test_clickhouse_resources_have_required_fields(self, mock_exists, mock_which):
        """Smoke test that ClickHouse resources have required Kubernetes fields."""
        mock_which.return_value = "/usr/bin/cue"
        mock_exists.return_value = True

        tenant_config = {
            "metadata": {"name": "validation-test", "domain": "test.local"},
            "networking": {"domain": "test.local"},
        }

        engine = CUEEngine(console=Mock())
        resources = engine._generate_clickhouse_resources(
            tenant_config, "test-clickhouse"
        )

        # Every resource should have required K8s fields
        for resource_name, resource in resources.items():
            assert "apiVersion" in resource
            assert "kind" in resource
            assert "metadata" in resource

    def test_resources_yaml_serializable_smoke(self):
        """Smoke test that all generated resources can be serialized to YAML."""
        tenant_config = {
            "metadata": {"name": "yaml-test", "domain": "test.local"},
            "networking": {"domain": "test.local"},
        }

        with patch("shutil.which", return_value="/usr/bin/cue"):
            with patch("pathlib.Path.exists", return_value=True):
                engine = CUEEngine(console=Mock())

                # Test both module types
                for module_name in ["langfuse", "clickhouse"]:
                    resources = engine.generate_tenant_module_resources(
                        tenant_config, module_name, f"yaml-test-{module_name}"
                    )

                    # Should serialize without errors
                    for resource_name, resource in resources.items():
                        yaml_str = yaml.dump(resource)
                        assert len(yaml_str) > 0

                        # Should round-trip correctly
                        parsed = yaml.safe_load(yaml_str)
                        assert parsed == resource


if __name__ == "__main__":
    # Run smoke tests with minimal output
    pytest.main([__file__, "-v", "-x"])  # Stop on first failure for quick feedback
