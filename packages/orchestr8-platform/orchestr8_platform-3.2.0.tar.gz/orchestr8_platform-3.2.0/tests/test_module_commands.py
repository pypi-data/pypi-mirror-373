"""Test cases for O8 CLI module commands."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
import typer
from click.testing import CliRunner

# Import the actual module commands that exist
from orchestr8.commands.module import (
    deploy_module,
    module_status,
    list_modules,
    validate_module,
    init_module,
    test_module,
    ModuleSpec,
)


class TestModuleCommands:
    """Test suite for module management commands."""

    @pytest.fixture
    def runner(self):
        """Create a Click test runner."""
        return CliRunner()

    @pytest.fixture
    def temp_module_dir(self):
        """Create a temporary module directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir) / "test-module"
            module_path.mkdir()

            # Create .o8 directory and module.yaml
            o8_dir = module_path / ".o8"
            o8_dir.mkdir()

            module_yaml = o8_dir / "module.yaml"
            module_yaml.write_text("""
name: test-module
version: 1.0.0
description: Test module
tier: custom
""")
            yield module_path

    @pytest.mark.smoke
    def test_module_spec_creation(self, temp_module_dir):
        """Test ModuleSpec class initialization."""
        spec = ModuleSpec(temp_module_dir)
        assert spec.path == temp_module_dir
        assert spec.is_valid
        assert spec.name == "test-module"
        assert spec.version == "1.0.0"

    @pytest.mark.smoke
    def test_module_spec_invalid(self):
        """Test ModuleSpec with invalid module directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            spec = ModuleSpec(Path(tmpdir))
            assert not spec.is_valid

    @pytest.mark.smoke
    def test_validate_module_valid(self, temp_module_dir):
        """Test validating a valid module."""
        # This should not raise an exception
        try:
            validate_module(path=temp_module_dir, verbose=False)
        except typer.Exit:
            pytest.fail("validate_module raised typer.Exit for valid module")

    @pytest.mark.smoke
    def test_validate_module_invalid(self):
        """Test validating an invalid module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(typer.Exit):
                validate_module(path=Path(tmpdir), verbose=False)

    @pytest.mark.integration
    @patch("orchestr8.commands.module.console")
    def test_list_modules_empty(self, mock_console):
        """Test listing modules when none exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            list_modules(path=Path(tmpdir), json_output=False)
            # Should print message about no modules found
            mock_console.print.assert_called()

    @pytest.mark.integration
    @patch("orchestr8.commands.module.console")
    def test_module_status_invalid_module(self, mock_console):
        """Test module status on invalid module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(typer.Exit):
                module_status(path=Path(tmpdir), watch=False)

    @pytest.mark.integration
    @patch("orchestr8.commands.module.subprocess.run")
    @patch("orchestr8.commands.module.console")
    def test_deploy_module_valid(self, mock_console, mock_subprocess, temp_module_dir):
        """Test deploying a valid module."""
        # Mock successful kubectl command
        mock_subprocess.return_value.returncode = 0
        mock_subprocess.return_value.stdout = (
            "application.argoproj.io/test-module created"
        )

        # This should not raise an exception
        try:
            deploy_module(
                path=temp_module_dir, environment="dev", dry_run=False, namespace=None
            )
        except typer.Exit as e:
            if e.exit_code != 0:
                pytest.fail(f"deploy_module failed with exit code {e.exit_code}")

    @pytest.mark.integration
    def test_deploy_module_invalid(self):
        """Test deploying an invalid module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(typer.Exit):
                deploy_module(
                    path=Path(tmpdir), environment="dev", dry_run=False, namespace=None
                )

    @pytest.mark.integration
    @patch("orchestr8.commands.module.console")
    def test_test_module_invalid(self, mock_console):
        """Test running tests on invalid module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            with pytest.raises(typer.Exit):
                test_module(path=Path(tmpdir), test_type="all")

    @pytest.mark.integration
    @patch("orchestr8.commands.module.Path.mkdir")
    @patch("orchestr8.commands.module.console")
    def test_init_module(self, mock_console, mock_mkdir):
        """Test initializing a new module."""
        with tempfile.TemporaryDirectory() as tmpdir:
            module_path = Path(tmpdir) / "new-module"
            init_module(
                name="new-module", path=module_path, tier="custom", deployment="helm"
            )
            mock_console.print.assert_called()
