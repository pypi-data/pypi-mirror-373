"""Orchestr8 Module management commands."""

import json
import subprocess
from pathlib import Path
from typing import Optional
import yaml

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax

from ..core.validator import ModuleValidator

app = typer.Typer(help="Module management commands")
console = Console()


class ModuleSpec:
    """Module specification handler."""

    def __init__(self, path: Path):
        """Initialize from module path."""
        self.path = path
        self.o8_dir = path / ".o8"
        self.spec_file = self.o8_dir / "module.yaml"
        self.root_spec_file = path / "o8-module.yaml"
        self.spec = None

        # Try .o8/module.yaml first (new structure)
        if self.spec_file.exists():
            with open(self.spec_file) as f:
                self.spec = yaml.safe_load(f)
        # Fallback to root o8-module.yaml (legacy/alternative structure)
        elif self.root_spec_file.exists():
            self.spec_file = self.root_spec_file
            with open(self.spec_file) as f:
                self.spec = yaml.safe_load(f)

    @property
    def is_valid(self) -> bool:
        """Check if module has valid Orchestr8 specification."""
        return self.spec is not None and (
            self.spec_file.exists() or self.root_spec_file.exists()
        )

    @property
    def name(self) -> str:
        """Get module name."""
        if self.spec:
            return self.spec.get("spec", {}).get("module", {}).get("name", "unknown")
        return self.path.name

    @property
    def version(self) -> str:
        """Get module version."""
        if self.spec:
            return self.spec.get("spec", {}).get("module", {}).get("version", "0.0.0")
        return "0.0.0"

    @property
    def tier(self) -> str:
        """Get module tier."""
        if self.spec:
            return self.spec.get("spec", {}).get("module", {}).get("tier", "custom")
        return "custom"

    @property
    def deployment_type(self) -> str:
        """Get deployment type."""
        if self.spec:
            return (
                self.spec.get("spec", {}).get("deployment", {}).get("type", "unknown")
            )
        return "unknown"


@app.command("validate")
def validate_module(
    path: Path = typer.Argument(Path.cwd(), help="Path to module directory"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed validation"
    ),
):
    """Validate a module against Orchestr8 specification."""

    console.print(f"[bold cyan]Validating module at:[/bold cyan] {path}")

    # Check for .o8 directory
    module = ModuleSpec(path)

    if not module.is_valid:
        console.print("[red]✗ No Orchestr8 module specification found![/red]")
        console.print("Expected one of:")
        console.print("  - .o8/module.yaml (preferred)")
        console.print("  - o8-module.yaml (alternative)")
        console.print(
            "\n[yellow]Tip:[/yellow] Initialize module with: [cyan]o8 module init[/cyan]"
        )
        raise typer.Exit(1)

    # Create validator
    validator = ModuleValidator()

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        # Validation tasks
        task = progress.add_task("Validating module specification...", total=9)

        errors = []
        warnings = []

        # 1. Validate YAML structure
        progress.update(task, description="Checking YAML structure...")
        if not module.spec:
            errors.append("Failed to parse module.yaml")
        progress.advance(task)

        # 2. Validate required fields
        progress.update(task, description="Checking required fields...")
        required_fields = ["apiVersion", "kind", "metadata", "spec"]
        for field in required_fields:
            if field not in module.spec:
                errors.append(f"Missing required field: {field}")
        progress.advance(task)

        # 3. Validate module metadata
        progress.update(task, description="Validating module metadata...")
        spec = module.spec.get("spec", {})
        module_info = spec.get("module", {})

        if not module_info.get("name"):
            errors.append("Module name is required")
        if not module_info.get("version"):
            errors.append("Module version is required")
        if module_info.get("tier") not in [
            "core",
            "standard",
            "custom",
            "experimental",
        ]:
            warnings.append(f"Unknown tier: {module_info.get('tier')}")
        progress.advance(task)

        # 4. Validate deployment configuration
        progress.update(task, description="Checking deployment configuration...")
        deployment = spec.get("deployment", {})

        if not deployment.get("type"):
            errors.append("Deployment type is required")
        elif deployment["type"] not in ["helm", "kustomize", "raw", "operator"]:
            errors.append(f"Invalid deployment type: {deployment['type']}")

        # Check deployment files exist
        if deployment.get("type") == "kustomize":
            kustomize_path = path / deployment.get("path", "k8s")
            if not kustomize_path.exists():
                errors.append(f"Kustomize path not found: {kustomize_path}")
            elif not (kustomize_path / "kustomization.yaml").exists():
                warnings.append(f"No kustomization.yaml in {kustomize_path}")

        progress.advance(task)

        # 5. Validate testing configuration
        progress.update(task, description="Checking test configuration...")
        testing = spec.get("testing", {})

        if not testing.get("e2e"):
            warnings.append("No E2E test configuration found")
        else:
            e2e = testing["e2e"]
            if e2e.get("framework") != "stagehand":
                warnings.append(f"Non-standard test framework: {e2e.get('framework')}")

            test_path = path / e2e.get("path", "tests/e2e")
            if not test_path.exists():
                warnings.append(f"Test path not found: {test_path}")

        progress.advance(task)

        # 6. Validate requirements
        progress.update(task, description="Validating requirements...")
        requirements = spec.get("requirements", {})

        # Check authentication
        auth = requirements.get("authentication", {})
        if auth.get("enabled", True) and not auth.get("clientId"):
            warnings.append("Authentication enabled but no clientId specified")

        # Check monitoring
        monitoring = requirements.get("monitoring", {})
        if monitoring.get("metrics", {}).get("enabled", True):
            # Metrics path would be checked at runtime
            _ = monitoring["metrics"].get("path", "/metrics")

        progress.advance(task)

        # 7. Validate security configuration
        progress.update(task, description="Validating security settings...")

        # Use the validator for comprehensive security checks
        is_valid, validation_results = validator.validate_spec(module.spec_file)
        for result in validation_results:
            if result.severity == "error" and not result.passed:
                errors.append(result.message)
            elif result.severity == "warning" and not result.passed:
                warnings.append(result.message)

        progress.advance(task)

        # 8. Validate compliance configuration
        progress.update(task, description="Checking compliance requirements...")

        compliance = spec.get("compliance", {})
        if compliance.get("dataClassification") in ["confidential", "restricted"]:
            if not compliance.get("encryption", {}).get("atRest", True):
                errors.append("Encryption at rest required for sensitive data")

        progress.advance(task)

        # 9. Check for additional files in .o8 directory (if it exists)
        progress.update(task, description="Checking additional configurations...")

        if module.o8_dir.exists():
            expected_files = [
                "module.yaml",
                "compliance.yaml",
                "dependencies.yaml",
                "security/network-policy.yaml",
            ]
            for file in expected_files:
                file_path = module.o8_dir / file
                if file != "module.yaml" and not file_path.exists():
                    if verbose:
                        warnings.append(f"Optional file not found: .o8/{file}")
        elif verbose:
            warnings.append("No .o8 directory found - using root o8-module.yaml")

        progress.advance(task)

    # Display results
    console.print()

    if errors:
        console.print("[bold red]Validation Failed![/bold red]\n")
        for error in errors:
            console.print(f"  [red]✗[/red] {error}")
    else:
        console.print("[bold green]Validation Passed![/bold green]")

        # Show module info
        table = Table(title="Module Information")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Name", module.name)
        table.add_row("Version", module.version)
        table.add_row("Tier", module.tier)
        table.add_row("Deployment", module.deployment_type)

        console.print(table)

    if warnings and verbose:
        console.print("\n[yellow]Warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  [yellow]⚠[/yellow] {warning}")

    if errors:
        raise typer.Exit(1)


@app.command("init")
def init_module(
    name: str = typer.Argument(..., help="Module name"),
    path: Path = typer.Option(Path.cwd(), "--path", "-p", help="Module directory"),
    tier: str = typer.Option("custom", "--tier", "-t", help="Module tier"),
    deployment: str = typer.Option(
        "kustomize", "--deployment", "-d", help="Deployment type"
    ),
    force: bool = typer.Option(False, "--force", "-f", help="Overwrite existing files"),
):
    """Initialize a new Orchestr8 module structure."""

    module_path = path / name if path.name != name else path
    o8_dir = module_path / ".o8"

    # Check if already exists
    if o8_dir.exists() and not force:
        console.print(f"[red]Module already initialized at {module_path}[/red]")
        console.print("Use --force to overwrite")
        raise typer.Exit(1)

    # Create directories
    console.print(f"[cyan]Initializing module:[/cyan] {name}")

    o8_dir.mkdir(parents=True, exist_ok=True)

    # Create module.yaml
    module_spec = {
        "apiVersion": "orchestr8.platform/v1alpha1",
        "kind": "ModuleSpecification",
        "metadata": {"name": name, "namespace": name},
        "spec": {
            "module": {
                "name": name,
                "version": "0.1.0",
                "tier": tier,
                "description": f"{name} module for Orchestr8 Platform",
                "maintainer": {
                    "name": "Your Organization",
                    "email": "support@example.com",
                },
            },
            "repository": {
                "url": f"https://github.com/your-org/{name}",
                "type": "github",
                "branch": "main",
                "path": "k8s" if deployment == "kustomize" else "helm",
            },
            "deployment": {
                "type": deployment,
                "path": "k8s" if deployment == "kustomize" else "helm",
                "multiTenant": False,
                "isolation": "namespace",
            },
            "testing": {
                "e2e": {
                    "framework": "stagehand",
                    "path": "tests/e2e",
                    "entrypoint": f"{name}.spec.ts",
                    "coverage": {"target": 70, "required": True},
                },
                "unit": {"path": "tests", "command": "pytest tests/"},
            },
            "requirements": {
                "authentication": {
                    "enabled": True,
                    "provider": "keycloak",
                    "clientId": name,
                },
                "monitoring": {
                    "metrics": {"enabled": True, "path": "/metrics", "port": 9090}
                },
                "networking": {
                    "ingress": True,
                    "serviceMesh": "istio",
                    "networkPolicies": True,
                },
            },
            "compliance": {
                "frameworks": ["SOC2"],
                "dataClassification": "internal",
                "encryption": {"atRest": True, "inTransit": True},
                "auditLogging": True,
            },
        },
    }

    spec_file = o8_dir / "module.yaml"
    with open(spec_file, "w") as f:
        yaml.dump(module_spec, f, default_flow_style=False, sort_keys=False)

    console.print("[green]✓[/green] Created .o8/module.yaml")

    # Create additional structure based on deployment type
    if deployment == "kustomize":
        # Create kustomize structure
        k8s_dir = module_path / "k8s"
        base_dir = k8s_dir / "base"
        base_dir.mkdir(parents=True, exist_ok=True)

        # Create basic kustomization.yaml
        kustomization = {
            "apiVersion": "kustomize.config.k8s.io/v1beta1",
            "kind": "Kustomization",
            "namespace": name,
            "resources": ["namespace.yaml", "deployment.yaml", "service.yaml"],
            "commonLabels": {"app": name, "module": name},
        }

        with open(base_dir / "kustomization.yaml", "w") as f:
            yaml.dump(kustomization, f, default_flow_style=False)

        console.print("[green]✓[/green] Created k8s/base/kustomization.yaml")

        # Create namespace
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": name,
                "labels": {"istio-injection": "enabled", "module": name},
            },
        }

        with open(base_dir / "namespace.yaml", "w") as f:
            yaml.dump(namespace, f, default_flow_style=False)

        console.print("[green]✓[/green] Created k8s/base/namespace.yaml")

    # Create test structure
    tests_dir = module_path / "tests"
    e2e_dir = tests_dir / "e2e"
    e2e_dir.mkdir(parents=True, exist_ok=True)

    # Create sample E2E test
    test_content = f"""import {{ Stagehand }} from '@browserbasehq/stagehand';

describe('{name} E2E Tests', () => {{
  let stagehand: Stagehand;

  beforeAll(async () => {{
    stagehand = new Stagehand({{
      env: 'LOCAL',
      verbose: true,
    }});
    await stagehand.init();
  }});

  afterAll(async () => {{
    await stagehand.close();
  }});

  test('Module health check', async () => {{
    await stagehand.page.goto('https://{name}.platform.local/health');
    const health = await stagehand.page.textContent('body');
    expect(JSON.parse(health).status).toBe('healthy');
  }});
}});
"""

    with open(e2e_dir / f"{name}.spec.ts", "w") as f:
        f.write(test_content)

    console.print(f"[green]✓[/green] Created tests/e2e/{name}.spec.ts")

    # Show summary
    console.print("\n[bold green]Module initialized successfully![/bold green]")
    console.print("\nNext steps:")
    console.print("  1. Update .o8/module.yaml with your module details")
    console.print(f"  2. Implement your module in {module_path}")
    console.print(f"  3. Validate with: [cyan]o8 module validate {module_path}[/cyan]")
    console.print(f"  4. Deploy with: [cyan]o8 module deploy {module_path}[/cyan]")


@app.command("list")
def list_modules(
    path: Path = typer.Option(
        None, "--path", "-p", help="Search path (defaults to parent projects directory)"
    ),
    json_output: bool = typer.Option(False, "--json", help="Output as JSON"),
):
    """List all Orchestr8 modules in a directory."""

    # Default to parent projects directory
    if path is None:
        # Go up from o8-cli to orchestr8 to projects
        search_path = (
            Path.cwd().parent.parent
            if "o8-cli" in str(Path.cwd())
            else Path.cwd().parent
        )
    else:
        search_path = path

    modules = []

    # Search recursively for modules with .o8 directories
    for o8_dir in search_path.rglob(".o8"):
        if o8_dir.is_dir():
            module_dir = o8_dir.parent
            module = ModuleSpec(module_dir)
            if module.is_valid:
                try:
                    rel_path = str(module_dir.relative_to(search_path))
                except ValueError:
                    rel_path = str(module_dir)

                modules.append(
                    {
                        "name": module.name,
                        "version": module.version,
                        "tier": module.tier,
                        "path": rel_path,
                        "deployment": module.deployment_type,
                    }
                )

    if json_output:
        console.print(json.dumps(modules, indent=2))
    else:
        if not modules:
            console.print("[yellow]No Orchestr8 modules found[/yellow]")
            return

        table = Table(title="Orchestr8 Modules")
        table.add_column("Name", style="cyan")
        table.add_column("Version", style="white")
        table.add_column("Tier", style="yellow")
        table.add_column("Deployment", style="green")
        table.add_column("Path", style="dim")

        for module in modules:
            table.add_row(
                module["name"],
                module["version"],
                module["tier"],
                module["deployment"],
                module["path"],
            )

        console.print(table)


@app.command("deploy")
def deploy_module(
    path: Path = typer.Argument(Path.cwd(), help="Module path"),
    environment: str = typer.Option("dev", "--env", "-e", help="Target environment"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be deployed"
    ),
    namespace: Optional[str] = typer.Option(
        None, "--namespace", "-n", help="Override namespace"
    ),
):
    """Deploy a module to the cluster."""

    module = ModuleSpec(path)

    if not module.is_valid:
        console.print("[red]Invalid module: missing .o8/module.yaml[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Deploying module:[/cyan] {module.name} v{module.version}")
    console.print(f"[cyan]Environment:[/cyan] {environment}")

    deployment = module.spec["spec"]["deployment"]
    deployment_type = deployment["type"]
    deployment_path = path / deployment.get("path", "k8s")

    # Use module namespace or override
    target_namespace = namespace or module.name

    if deployment_type == "kustomize":
        # Check for environment overlay
        overlay_path = deployment_path / "overlays" / environment
        if overlay_path.exists():
            console.print(f"[green]Using overlay:[/green] {overlay_path}")
            deploy_path = overlay_path
        else:
            console.print(f"[yellow]No overlay for {environment}, using base[/yellow]")
            # If deployment_path already ends with 'base', use it as is
            if deployment_path.name == "base":
                deploy_path = deployment_path
            else:
                deploy_path = deployment_path / "base"

        # Build kustomize command
        cmd = ["kubectl", "apply", "-k", str(deploy_path)]
        if dry_run:
            cmd.append("--dry-run=client")
            cmd.append("-o")
            cmd.append("yaml")

        console.print(f"\n[dim]Running: {' '.join(cmd)}[/dim]")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                if dry_run:
                    # Show the YAML that would be applied
                    syntax = Syntax(result.stdout, "yaml", theme="monokai")
                    console.print(syntax)
                else:
                    console.print("[green]✓ Module deployed successfully![/green]")
                    console.print(result.stdout)
            else:
                console.print(f"[red]Deployment failed:[/red]\n{result.stderr}")
                raise typer.Exit(1)
        except FileNotFoundError:
            console.print("[red]kubectl not found. Please install kubectl.[/red]")
            raise typer.Exit(1)

    elif deployment_type == "helm":
        # Helm deployment
        chart_path = deployment_path

        cmd = [
            "helm",
            "upgrade",
            "--install",
            module.name,
            str(chart_path),
            "--namespace",
            target_namespace,
            "--create-namespace",
        ]

        # Add values file if exists
        values_file = chart_path / f"values-{environment}.yaml"
        if values_file.exists():
            cmd.extend(["-f", str(values_file)])

        if dry_run:
            cmd.append("--dry-run")

        console.print(f"\n[dim]Running: {' '.join(cmd)}[/dim]")

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                console.print("[green]✓ Module deployed successfully![/green]")
                console.print(result.stdout)
            else:
                console.print(f"[red]Deployment failed:[/red]\n{result.stderr}")
                raise typer.Exit(1)
        except FileNotFoundError:
            console.print("[red]helm not found. Please install helm.[/red]")
            raise typer.Exit(1)

    else:
        console.print(f"[red]Unsupported deployment type: {deployment_type}[/red]")
        raise typer.Exit(1)

    # Show post-deployment info
    if not dry_run:
        console.print("\n[cyan]Check module status:[/cyan]")
        console.print(f"  kubectl get pods -n {target_namespace}")
        console.print(f"  kubectl get svc -n {target_namespace}")
        console.print(f"  o8 module status {path}")


@app.command("status")
def module_status(
    path: Path = typer.Argument(Path.cwd(), help="Module path"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch for changes"),
):
    """Check the status of a deployed module."""

    module = ModuleSpec(path)

    if not module.is_valid:
        console.print("[red]Invalid module: missing .o8/module.yaml[/red]")
        raise typer.Exit(1)

    namespace = module.name

    # Get pod status
    cmd = ["kubectl", "get", "pods", "-n", namespace, "-l", f"module={module.name}"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        console.print(f"[red]Failed to get status:[/red] {result.stderr}")
        raise typer.Exit(1)

    console.print(f"[bold cyan]Module Status: {module.name}[/bold cyan]\n")
    console.print(result.stdout)

    # Get service status
    cmd = ["kubectl", "get", "svc", "-n", namespace]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        console.print("\n[cyan]Services:[/cyan]")
        console.print(result.stdout)

    # Check health endpoint if configured
    requirements = module.spec.get("spec", {}).get("requirements", {})
    monitoring = requirements.get("monitoring", {})

    if monitoring.get("metrics", {}).get("enabled"):
        console.print("\n[cyan]Health Check:[/cyan]")
        # This would check the actual health endpoint
        console.print("  [dim]Would check /health endpoint[/dim]")

    if watch:
        console.print("\n[yellow]Watching for changes... (Ctrl+C to stop)[/yellow]")
        cmd = ["kubectl", "get", "pods", "-n", namespace, "-w"]
        subprocess.run(cmd)


@app.command("test")
def test_module(
    path: Path = typer.Argument(Path.cwd(), help="Module path"),
    test_type: str = typer.Option(
        "all", "--type", "-t", help="Test type: unit, e2e, integration, all"
    ),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run module tests."""

    module = ModuleSpec(path)

    if not module.is_valid:
        console.print("[red]Invalid module: missing .o8/module.yaml[/red]")
        raise typer.Exit(1)

    console.print(f"[cyan]Running tests for:[/cyan] {module.name}")

    testing = module.spec.get("spec", {}).get("testing", {})

    # Run unit tests
    if test_type in ["unit", "all"]:
        unit_config = testing.get("unit", {})
        if unit_config:
            console.print("\n[yellow]Running unit tests...[/yellow]")
            test_path = path / unit_config.get("path", "tests")
            test_cmd = unit_config.get("command", "pytest tests/")

            if test_path.exists():
                cmd = test_cmd.split()
                if verbose:
                    cmd.append("-v")

                result = subprocess.run(cmd, cwd=path, capture_output=True, text=True)
                if result.returncode == 0:
                    console.print("[green]✓ Unit tests passed[/green]")
                    if verbose:
                        console.print(result.stdout)
                else:
                    console.print("[red]✗ Unit tests failed[/red]")
                    console.print(result.stdout)
                    console.print(result.stderr)
            else:
                console.print(f"[yellow]Test path not found: {test_path}[/yellow]")

    # Run E2E tests
    if test_type in ["e2e", "all"]:
        e2e_config = testing.get("e2e", {})
        if e2e_config:
            console.print("\n[yellow]Running E2E tests...[/yellow]")
            test_path = path / e2e_config.get("path", "tests/e2e")

            if test_path.exists():
                # Check for Stagehand
                if e2e_config.get("framework") == "stagehand":
                    console.print("[cyan]Using Stagehand framework[/cyan]")
                    cmd = ["npm", "run", "test:e2e"]
                    if verbose:
                        cmd.append("--verbose")

                    result = subprocess.run(
                        cmd, cwd=path, capture_output=True, text=True
                    )
                    if result.returncode == 0:
                        console.print("[green]✓ E2E tests passed[/green]")
                        if verbose:
                            console.print(result.stdout)
                    else:
                        console.print("[red]✗ E2E tests failed[/red]")
                        console.print(result.stdout)
            else:
                console.print(f"[yellow]E2E test path not found: {test_path}[/yellow]")

    console.print("\n[green]Test run complete![/green]")


if __name__ == "__main__":
    app()
