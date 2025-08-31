"""Orchestr8 Tenant management commands."""

import json
import yaml
from pathlib import Path
from typing import Optional, Dict, Any

import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

from ..core.cue_engine import CUEEngine, CUEEngineError

app = typer.Typer(help="Multi-tenant management commands")
console = Console()


def _generate_argocd_application(
    tenant_name: str, tenant_config: Dict[str, Any], bundle: Dict[str, Any]
) -> Dict[str, Any]:
    """Generate ArgoCD Application for tenant deployment."""
    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {
            "name": f"tenant-{tenant_name}",
            "namespace": "argocd",
            "finalizers": ["resources-finalizer.argocd.argoproj.io"],
        },
        "spec": {
            "project": "default",
            "source": {
                "repoURL": "https://github.com/killerapp/orchestr8",
                "targetRevision": "main",
                "path": f"tenants/{tenant_name}/generated",
            },
            "destination": {
                "server": "https://kubernetes.default.svc",
                "namespace": tenant_name,
            },
            "syncPolicy": {
                "automated": {"prune": True, "selfHeal": True},
                "syncOptions": ["CreateNamespace=true"],
                "retry": {
                    "limit": 3,
                    "backoff": {"duration": "5s", "factor": 2, "maxDuration": "1m"},
                },
            },
        },
    }


def _generate_module_argocd_application(
    tenant_name: str,
    module_name: str,
    namespace: str,
    tenant_config: Dict[str, Any],
    environment: str,
    auth_required: bool,
    roles: Optional[str],
    github_org: Optional[str],
    domain_prefix: str,
    source_path: str = None,
) -> Dict[str, Any]:
    """Generate ArgoCD Application for a tenant module."""

    # Parse roles
    role_list = roles.split(",") if roles else []

    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {
            "name": f"{tenant_name}-{module_name}",
            "namespace": "argocd",
            "labels": {
                "orchestr8.platform/tenant": tenant_name,
                "orchestr8.platform/module": module_name,
                "orchestr8.platform/environment": environment,
            },
            "annotations": {
                "orchestr8.platform/domain": f"{domain_prefix}.{tenant_config['metadata']['domain']}",
                "orchestr8.platform/auth-required": str(auth_required).lower(),
                "orchestr8.platform/github-org": github_org or "",
                "orchestr8.platform/required-roles": ",".join(role_list),
            },
            "finalizers": ["resources-finalizer.argocd.argoproj.io"],
        },
        "spec": {
            "project": "default",
            "source": {
                "repoURL": "https://github.com/killerapp/orchestr8",
                "targetRevision": "main",
                "path": source_path
                or f"modules/{module_name}/base",  # Use provided path or default to base
            },
            "destination": {
                "server": "https://kubernetes.default.svc",
                "namespace": namespace,
            },
            "syncPolicy": {
                "automated": {"prune": True, "selfHeal": True},
                "syncOptions": ["CreateNamespace=true", "ApplyOutOfSyncOnly=true"],
                "retry": {
                    "limit": 3,
                    "backoff": {"duration": "5s", "factor": 2, "maxDuration": "3m"},
                },
            },
            "info": [
                {
                    "name": "Description",
                    "value": f"{module_name.title()} module for {tenant_name} tenant",
                },
                {
                    "name": "URL",
                    "value": f"https://{domain_prefix}.{tenant_config['metadata']['domain']}",
                },
                {"name": "Environment", "value": environment},
            ],
        },
    }


@app.command("init")
def init_tenant(
    name: str = typer.Argument(..., help="Tenant name (must be DNS-compatible)"),
    display_name: Optional[str] = typer.Option(
        None, "--display-name", "-d", help="Human-readable display name"
    ),
    domain: Optional[str] = typer.Option(
        None, "--domain", help="Primary domain for tenant"
    ),
    organization: Optional[str] = typer.Option(None, "--org", help="Organization name"),
    modules: Optional[str] = typer.Option(
        None, "--modules", help="Comma-separated list of initial modules"
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", "-o", help="Output directory for tenant configuration"
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--non-interactive", help="Run in interactive mode"
    ),
):
    """Initialize a new tenant configuration."""

    console.print(f"[bold cyan]🏢 Initializing tenant: {name}[/bold cyan]\n")

    # Validate tenant name (DNS-compatible)
    import re

    if not re.match(r"^[a-z][a-z0-9-]*[a-z0-9]$", name):
        console.print(
            "[red]❌ Tenant name must be DNS-compatible (lowercase, alphanumeric, hyphens)[/red]"
        )
        raise typer.Exit(1)

    try:
        # Initialize CUE engine
        cue_engine = CUEEngine(console=console)

        # Gather configuration interactively or from parameters
        if interactive:
            config = _interactive_tenant_setup(
                name, display_name, domain, organization, modules
            )
        else:
            config = _non_interactive_tenant_setup(
                name, display_name, domain, organization, modules
            )

        # Validate configuration using CUE
        console.print("🔍 Validating tenant configuration...")
        validation = cue_engine.validate_tenant_config(config)

        if not validation.valid:
            console.print("[red]❌ Tenant configuration validation failed:[/red]")
            for error in validation.errors:
                console.print(f"   • {error}")
            raise typer.Exit(1)

        # Use validated configuration
        config = validation.data
        console.print("[green]✅ Tenant configuration validated successfully[/green]")

        # Determine output path
        if not output:
            output = Path.cwd() / "tenants" / name

        output.mkdir(parents=True, exist_ok=True)

        # Save tenant configuration
        config_file = output / "tenant.yaml"
        with open(config_file, "w") as f:
            yaml.dump(config, f, default_flow_style=False, indent=2)

        console.print(f"[green]✅ Tenant configuration saved to: {config_file}[/green]")

        # Generate resources
        console.print("🏗️  Generating tenant resources...")

        # Generate Keycloak realm
        keycloak_realm = cue_engine.generate_keycloak_realm(config)
        keycloak_file = output / "keycloak-realm.json"
        with open(keycloak_file, "w") as f:
            json.dump(keycloak_realm, f, indent=2)

        # Generate Kubernetes resources
        k8s_resources = cue_engine.generate_kubernetes_resources(config)
        k8s_dir = output / "kubernetes"
        # Convert dataclass to dict for export
        from dataclasses import asdict

        cue_engine.export_to_yaml(asdict(k8s_resources), k8s_dir)

        # Generate complete bundle
        bundle = cue_engine.compile_tenant_bundle(config)
        bundle_file = output / "tenant-bundle.json"
        with open(bundle_file, "w") as f:
            json.dump(bundle, f, indent=2)

        # Summary
        console.print(
            f"\n[bold green]🎉 Tenant '{name}' initialized successfully![/bold green]"
        )
        console.print(f"Configuration: {config_file}")
        console.print(f"Keycloak realm: {keycloak_file}")
        console.print(f"Kubernetes resources: {k8s_dir}")
        console.print(f"Complete bundle: {bundle_file}")

        # Generate ArgoCD application for tenant
        argocd_app = _generate_argocd_application(name, config, bundle)
        project_root = Path(__file__).parent.parent.parent.parent.parent
        argocd_file = project_root / "argocd-apps" / "tenants" / f"tenant-{name}.yaml"
        argocd_file.parent.mkdir(parents=True, exist_ok=True)

        with open(argocd_file, "w") as f:
            yaml.dump(argocd_app, f, default_flow_style=False, indent=2)

        console.print("\n[bold]Next steps:[/bold]")
        console.print(
            f"1. Review configuration: [cyan]o8 tenant validate {config_file}[/cyan]"
        )
        console.print(f"2. Deploy tenant: [cyan]o8 tenant deploy {config_file}[/cyan]")
        console.print(f"3. ArgoCD Application: [cyan]{argocd_file}[/cyan]")
        console.print(
            f"4. Configure identity providers: [cyan]o8 tenant auth {name}[/cyan]"
        )

    except CUEEngineError as e:
        console.print(f"[red]❌ CUE engine error: {e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Failed to initialize tenant: {e}[/red]")
        raise typer.Exit(1)


@app.command("validate")
def validate_tenant(
    config_file: Path = typer.Argument(..., help="Path to tenant configuration file"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed validation output"
    ),
):
    """Validate tenant configuration."""

    console.print(
        f"[bold cyan]🔍 Validating tenant configuration: {config_file}[/bold cyan]\n"
    )

    if not config_file.exists():
        console.print(f"[red]❌ Configuration file not found: {config_file}[/red]")
        raise typer.Exit(1)

    try:
        # Load configuration
        with open(config_file) as f:
            if config_file.suffix.lower() in [".yaml", ".yml"]:
                config = yaml.safe_load(f)
            elif config_file.suffix.lower() == ".json":
                config = json.load(f)
            else:
                console.print("[red]❌ Configuration file must be YAML or JSON[/red]")
                raise typer.Exit(1)

        # Initialize CUE engine
        cue_engine = CUEEngine(console=console)

        # Validate configuration
        validation = cue_engine.validate_tenant_config(config)

        if validation.valid:
            console.print("[green]✅ Tenant configuration is valid[/green]")

            if verbose and validation.data:
                console.print("\n[bold]Validated Configuration:[/bold]")
                syntax = Syntax(
                    yaml.dump(validation.data, default_flow_style=False, indent=2),
                    "yaml",
                )
                console.print(syntax)

        else:
            console.print("[red]❌ Tenant configuration validation failed:[/red]")
            for error in validation.errors:
                console.print(f"   • {error}")
            raise typer.Exit(1)

        if validation.warnings:
            console.print("\n[yellow]⚠️  Validation warnings:[/yellow]")
            for warning in validation.warnings:
                console.print(f"   • {warning}")

    except Exception as e:
        console.print(f"[red]❌ Validation failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("deploy")
def deploy_tenant(
    config_file: Path = typer.Argument(..., help="Path to tenant configuration file"),
    dry_run: bool = typer.Option(
        False, "--dry-run", help="Show what would be deployed without applying"
    ),
    wait: bool = typer.Option(
        True, "--wait/--no-wait", help="Wait for deployment to complete"
    ),
):
    """Deploy tenant to Kubernetes cluster."""

    console.print(f"[bold cyan]🚀 Deploying tenant: {config_file}[/bold cyan]\n")

    if not config_file.exists():
        console.print(f"[red]❌ Configuration file not found: {config_file}[/red]")
        raise typer.Exit(1)

    try:
        # Load configuration
        with open(config_file) as f:
            if config_file.suffix.lower() in [".yaml", ".yml"]:
                config = yaml.safe_load(f)
            elif config_file.suffix.lower() == ".json":
                config = json.load(f)
            else:
                console.print("[red]❌ Configuration file must be YAML or JSON[/red]")
                raise typer.Exit(1)

        # Initialize CUE engine
        cue_engine = CUEEngine(console=console)

        # Validate and compile
        bundle = cue_engine.compile_tenant_bundle(config)
        tenant_name = bundle["tenant"]["metadata"]["name"]

        if dry_run:
            console.print(
                "[yellow]🔍 Dry run - showing resources that would be created:[/yellow]\n"
            )

            # Show Kubernetes resources
            k8s_resources = bundle["kubernetes"]
            for resource_type, resource_data in k8s_resources.items():
                if isinstance(resource_data, dict) and resource_data.get("kind"):
                    console.print(
                        f"[cyan]{resource_data['kind']}: {resource_data['metadata']['name']}[/cyan]"
                    )
                elif isinstance(resource_data, list):
                    for resource in resource_data:
                        if isinstance(resource, dict) and resource.get("kind"):
                            console.print(
                                f"[cyan]{resource['kind']}: {resource['metadata']['name']}[/cyan]"
                            )

            console.print("\n[yellow]Use --dry-run=false to apply changes[/yellow]")
            return

        # Confirm deployment
        if not Confirm.ask(
            f"Deploy tenant '{tenant_name}' to current Kubernetes cluster?"
        ):
            console.print("Deployment cancelled.")
            return

        # Deploy resources
        _deploy_tenant_resources(bundle, wait)

        console.print(
            f"\n[bold green]🎉 Tenant '{tenant_name}' deployed successfully![/bold green]"
        )
        console.print("\n[bold]Access Information:[/bold]")
        console.print(
            f"Keycloak Admin: https://auth.{config['networking']['domain']}/admin/"
        )
        console.print(
            f"Tenant Realm: https://auth.{config['networking']['domain']}/realms/{tenant_name}"
        )

        for module in config.get("modules", []):
            module_name = module["name"]
            module_url = f"https://{module_name}.{config['networking']['domain']}"
            console.print(f"{module_name.title()}: {module_url}")

    except Exception as e:
        console.print(f"[red]❌ Deployment failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("add-module")
def add_module_to_tenant(
    tenant_name: str = typer.Argument(..., help="Tenant name"),
    module_name: str = typer.Argument(
        ..., help="Module name (langfuse, clickhouse, etc.)"
    ),
    namespace: Optional[str] = typer.Option(
        None, "--namespace", "-n", help="Target namespace (defaults to tenant-module)"
    ),
    environment: str = typer.Option(
        "dev", "--environment", "-e", help="Environment (dev, staging, prod)"
    ),
    auth_required: bool = typer.Option(
        True, "--auth/--no-auth", help="Enable OAuth2 authentication"
    ),
    roles: Optional[str] = typer.Option(
        None, "--roles", help="Comma-separated list of required roles"
    ),
    github_org: Optional[str] = typer.Option(
        None, "--github-org", help="GitHub organization for authentication"
    ),
    domain_prefix: Optional[str] = typer.Option(
        None, "--domain", help="Custom domain prefix (defaults to module name)"
    ),
):
    """Add a module to an existing tenant."""

    console.print(
        f"[bold cyan]🧩 Adding module '{module_name}' to tenant '{tenant_name}'[/bold cyan]\n"
    )

    try:
        # Validate tenant exists
        tenant_dir = Path.cwd() / "tenants" / tenant_name
        if not tenant_dir.exists():
            console.print(
                f"[red]❌ Tenant '{tenant_name}' not found. Run 'o8 tenant init {tenant_name}' first.[/red]"
            )
            raise typer.Exit(1)

        # Load tenant configuration
        tenant_config_file = tenant_dir / "tenant.yaml"
        if not tenant_config_file.exists():
            console.print(
                f"[red]❌ Tenant configuration not found: {tenant_config_file}[/red]"
            )
            raise typer.Exit(1)

        with open(tenant_config_file) as f:
            tenant_config = yaml.safe_load(f)

        # Validate module exists
        modules_dir = Path(__file__).parent.parent.parent.parent.parent / "modules"
        module_dir = modules_dir / module_name
        if not module_dir.exists():
            available_modules = [
                d.name
                for d in modules_dir.iterdir()
                if d.is_dir() and not d.name.startswith(".")
            ]
            console.print(f"[red]❌ Module '{module_name}' not found.[/red]")
            console.print(f"Available modules: {', '.join(available_modules)}")
            raise typer.Exit(1)

        # Determine target namespace
        target_namespace = namespace or f"{tenant_name}-{module_name}"
        domain_prefix = domain_prefix or module_name

        console.print(f"📦 Module: {module_name}")
        console.print(f"🏢 Tenant: {tenant_name}")
        console.print(f"🎯 Namespace: {target_namespace}")
        console.print(
            f"🌐 URL: https://{domain_prefix}.{tenant_config['metadata']['domain']}"
        )

        if not Confirm.ask(f"Deploy module '{module_name}' to tenant '{tenant_name}'?"):
            console.print("Module deployment cancelled.")
            return

        # Initialize CUE engine for resource generation
        from ..core.cue_engine import CUEEngine

        cue_engine = CUEEngine(console=console)

        # Generate module resources using CUE
        console.print("🏗️  Generating module resources with CUE...")
        module_resources = cue_engine.generate_tenant_module_resources(
            tenant_config, module_name, target_namespace
        )

        # Save generated Kubernetes resources
        project_root = Path(__file__).parent.parent.parent.parent.parent
        module_output_dir = (
            project_root / "tenants" / tenant_name / "modules" / module_name
        )
        module_output_dir.mkdir(parents=True, exist_ok=True)

        # Export resources to YAML files
        cue_engine.export_to_yaml(module_resources, module_output_dir)

        # Generate module-specific ArgoCD application pointing to generated resources
        argocd_app = _generate_module_argocd_application(
            tenant_name,
            module_name,
            target_namespace,
            tenant_config,
            environment,
            auth_required,
            roles,
            github_org,
            domain_prefix,
            f"tenants/{tenant_name}/modules/{module_name}",  # Point to generated resources
        )

        # Save ArgoCD application
        argocd_file = (
            project_root
            / "argocd-apps"
            / "tenants"
            / f"{tenant_name}-{module_name}.yaml"
        )
        argocd_file.parent.mkdir(parents=True, exist_ok=True)

        with open(argocd_file, "w") as f:
            yaml.dump(argocd_app, f, default_flow_style=False, indent=2)

        console.print(
            f"\n[bold green]🎉 Module '{module_name}' added to tenant '{tenant_name}'![/bold green]"
        )
        console.print("\n[bold]Next steps:[/bold]")
        console.print(
            f"1. Apply ArgoCD application: [cyan]kubectl apply -f {argocd_file}[/cyan]"
        )
        console.print(
            f"2. Check deployment: [cyan]kubectl get pods -n {target_namespace}[/cyan]"
        )
        console.print(
            f"3. Access application: [cyan]https://{domain_prefix}.{tenant_config['metadata']['domain']}[/cyan]"
        )

        # Add port forwarding info for local development
        if environment == "dev":
            console.print(
                f"4. Port forward for local testing: [cyan]kubectl port-forward -n {target_namespace} svc/{module_name} 8080:8080[/cyan]"
            )
            console.print("5. Local access: [cyan]http://localhost:8080[/cyan]")

    except Exception as e:
        console.print(f"[red]❌ Failed to add module: {e}[/red]")
        raise typer.Exit(1)


@app.command("list-modules")
def list_available_modules(
    category: Optional[str] = typer.Option(
        None, "--category", "-c", help="Filter by category"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, yaml"
    ),
):
    """List available modules that can be added to tenants."""

    console.print("[bold cyan]📦 Available Modules[/bold cyan]\n")

    try:
        modules_dir = Path(__file__).parent.parent.parent.parent.parent / "modules"
        if not modules_dir.exists():
            console.print("[red]❌ Modules directory not found[/red]")
            raise typer.Exit(1)

        modules = []
        for module_path in modules_dir.iterdir():
            if (
                module_path.is_dir()
                and not module_path.name.startswith(".")
                and module_path.name not in ["templates", "CLAUDE.md", "README.md"]
            ):
                module_info = {
                    "name": module_path.name,
                    "path": str(module_path),
                    "description": "Available module",
                    "category": "general",
                }

                # Try to read module metadata if available
                metadata_file = module_path / ".o8" / "module.yaml"
                if metadata_file.exists():
                    try:
                        with open(metadata_file) as f:
                            metadata = yaml.safe_load(f)
                            module_info["description"] = metadata.get("spec", {}).get(
                                "description", module_info["description"]
                            )
                            module_info["category"] = metadata.get("spec", {}).get(
                                "category", module_info["category"]
                            )
                    except Exception:
                        pass

                # Check if kustomization exists
                kustomization_files = list(module_path.glob("**/kustomization.yaml"))
                module_info["kustomize_ready"] = len(kustomization_files) > 0

                if not category or module_info["category"] == category:
                    modules.append(module_info)

        if output == "table":
            from rich.table import Table

            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Module", style="cyan", width=15)
            table.add_column("Category", style="green", width=12)
            table.add_column("Status", style="yellow", width=10)
            table.add_column("Description", style="white")

            for module in sorted(modules, key=lambda x: x["name"]):
                status = "✅ Ready" if module["kustomize_ready"] else "⚠️ Basic"
                table.add_row(
                    module["name"], module["category"], status, module["description"]
                )

            console.print(table)
            console.print(f"\n[dim]Found {len(modules)} modules[/dim]")

        elif output == "json":
            import json

            console.print(json.dumps(modules, indent=2))

        elif output == "yaml":
            console.print(yaml.dump(modules, default_flow_style=False))

        console.print("\n[bold]Usage:[/bold]")
        console.print("[cyan]o8 tenant add-module <tenant-name> <module-name>[/cyan]")
        console.print("\n[bold]Examples:[/bold]")
        console.print("[dim]o8 tenant add-module test-company langfuse[/dim]")
        console.print(
            "[dim]o8 tenant add-module test-company clickhouse --no-auth[/dim]"
        )

    except Exception as e:
        console.print(f"[red]❌ Failed to list modules: {e}[/red]")
        raise typer.Exit(1)


@app.command("list")
def list_tenants(
    namespace: Optional[str] = typer.Option(
        None, "--namespace", "-n", help="Namespace to search (default: all)"
    ),
    output: str = typer.Option(
        "table", "--output", "-o", help="Output format: table, json, yaml"
    ),
):
    """List all tenants in the cluster."""

    console.print("[bold cyan]🏢 Listing tenants...[/bold cyan]\n")

    try:
        import subprocess

        # Get namespaces with tenant label
        cmd = [
            "kubectl",
            "get",
            "namespace",
            "-l",
            "orchestr8.platform/tenant",
            "-o",
            "json",
        ]
        if namespace:
            cmd.extend(["-n", namespace])

        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        namespaces_data = json.loads(result.stdout)

        tenants = []
        for ns in namespaces_data.get("items", []):
            tenant_info = {
                "name": ns["metadata"]["labels"].get(
                    "orchestr8.platform/tenant", "unknown"
                ),
                "namespace": ns["metadata"]["name"],
                "environment": ns["metadata"]["labels"].get(
                    "orchestr8.platform/environment", "unknown"
                ),
                "created": ns["metadata"].get("creationTimestamp", "unknown"),
                "status": ns["status"]["phase"],
            }
            tenants.append(tenant_info)

        if output == "json":
            console.print(json.dumps(tenants, indent=2))
        elif output == "yaml":
            console.print(yaml.dump(tenants, default_flow_style=False, indent=2))
        else:
            # Table output
            table = Table(title="Orchestr8 Tenants")
            table.add_column("Name", style="cyan")
            table.add_column("Namespace", style="blue")
            table.add_column("Environment", style="green")
            table.add_column("Created", style="dim")
            table.add_column("Status", style="yellow")

            for tenant in tenants:
                table.add_row(
                    tenant["name"],
                    tenant["namespace"],
                    tenant["environment"],
                    tenant["created"],
                    tenant["status"],
                )

            console.print(table)

            if not tenants:
                console.print("[yellow]No tenants found in the cluster.[/yellow]")
                console.print("Create one with: [cyan]o8 tenant init <name>[/cyan]")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to list tenants: {e.stderr}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error listing tenants: {e}[/red]")
        raise typer.Exit(1)


@app.command("delete")
def delete_tenant(
    name: str = typer.Argument(..., help="Tenant name to delete"),
    force: bool = typer.Option(False, "--force", help="Skip confirmation prompt"),
):
    """Delete a tenant and all its resources."""

    console.print(f"[bold red]🗑️  Deleting tenant: {name}[/bold red]\n")

    try:
        import subprocess

        # Check if ANY tenant resources exist (namespace, ArgoCD apps, or files)
        tenant_exists = False

        # Check if main tenant namespace exists
        result = subprocess.run(
            ["kubectl", "get", "namespace", name, "-o", "json"],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            ns_data = json.loads(result.stdout)
            if ns_data["metadata"]["labels"].get("orchestr8.platform/tenant"):
                tenant_exists = True

        # Check if any ArgoCD applications exist for this tenant
        result = subprocess.run(
            ["kubectl", "get", "applications", "-n", "argocd", "-o", "json"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            all_apps = json.loads(result.stdout)
            for app in all_apps.get("items", []):
                app_name = app["metadata"]["name"]
                if (
                    app_name == f"tenant-{name}"
                    or app_name.startswith(f"{name}-")
                    or app_name.startswith(f"tenant-{name}-")
                ):
                    tenant_exists = True
                    break

        # Check if tenant directory exists
        project_root = Path(__file__).parent.parent.parent.parent.parent
        if (project_root / "tenants" / name).exists():
            tenant_exists = True

        # Check if any module namespaces exist
        result = subprocess.run(
            ["kubectl", "get", "namespaces", "-o", "json"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            all_ns = json.loads(result.stdout)
            for ns in all_ns.get("items", []):
                ns_name = ns["metadata"]["name"]
                if ns_name.startswith(f"{name}-"):
                    tenant_exists = True
                    break

        if not tenant_exists:
            console.print(f"[red]❌ No resources found for tenant '{name}'[/red]")
            raise typer.Exit(1)

        # Confirm deletion
        if not force:
            console.print(
                f"[yellow]⚠️  This will permanently delete tenant '{name}' and all its resources![/yellow]"
            )
            if not Confirm.ask("Are you sure you want to continue?"):
                console.print("Deletion cancelled.")
                return

        # Find all tenant-related namespaces
        console.print("Finding tenant-related resources...")
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "namespaces",
                "-l",
                f"orchestr8.platform/tenant={name}",
                "-o",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        tenant_namespaces = []
        if result.stdout.strip():
            ns_data = json.loads(result.stdout)
            tenant_namespaces = [
                ns["metadata"]["name"] for ns in ns_data.get("items", [])
            ]

        # Also check for module namespaces with naming pattern
        result = subprocess.run(
            ["kubectl", "get", "namespaces", "-o", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        all_ns_data = json.loads(result.stdout)
        for ns in all_ns_data.get("items", []):
            ns_name = ns["metadata"]["name"]
            if ns_name.startswith(f"{name}-") and ns_name not in tenant_namespaces:
                tenant_namespaces.append(ns_name)

        # Delete ArgoCD applications for this tenant
        console.print("Removing ArgoCD applications...")

        # First, get applications by label
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "applications",
                "-n",
                "argocd",
                "-l",
                f"orchestr8.platform/tenant={name}",
                "-o",
                "json",
            ],
            capture_output=True,
            text=True,
        )
        apps_to_delete = set()
        if result.returncode == 0 and result.stdout.strip():
            app_data = json.loads(result.stdout)
            for app in app_data.get("items", []):
                apps_to_delete.add(app["metadata"]["name"])

        # Also get ALL applications and check by naming pattern
        result = subprocess.run(
            ["kubectl", "get", "applications", "-n", "argocd", "-o", "json"],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            all_apps = json.loads(result.stdout)
            for app in all_apps.get("items", []):
                app_name = app["metadata"]["name"]
                # Check if app name matches tenant patterns
                if (
                    app_name == f"tenant-{name}"
                    or app_name.startswith(f"{name}-")
                    or app_name.startswith(f"tenant-{name}-")
                ):
                    apps_to_delete.add(app_name)

        # Delete all identified applications
        for app_name in apps_to_delete:
            console.print(f"Deleting ArgoCD application: {app_name}")
            subprocess.run(
                [
                    "kubectl",
                    "delete",
                    "application",
                    app_name,
                    "-n",
                    "argocd",
                    "--timeout=30s",
                ],
                capture_output=True,
            )

        # Delete all tenant namespaces
        for ns_name in tenant_namespaces:
            console.print(f"Deleting namespace: {ns_name}")
            subprocess.run(
                ["kubectl", "delete", "namespace", ns_name, "--timeout=60s"], check=True
            )

        # Delete Keycloak realm ConfigMap
        console.print("Removing Keycloak realm configuration...")
        subprocess.run(
            [
                "kubectl",
                "delete",
                "configmap",
                f"keycloak-realm-{name}",
                "-n",
                "platform",
            ],
            capture_output=True,  # Don't fail if ConfigMap doesn't exist
        )

        # Clean up tenant directory from git repo
        project_root = Path(__file__).parent.parent.parent.parent.parent
        tenant_dir = project_root / "tenants" / name
        if tenant_dir.exists():
            console.print(f"Removing tenant directory: {tenant_dir}")
            import shutil

            shutil.rmtree(tenant_dir)

        # Clean up ArgoCD application files
        argocd_apps_dir = project_root / "argocd-apps" / "tenants"
        if argocd_apps_dir.exists():
            # Remove module application files
            for app_file in argocd_apps_dir.glob(f"{name}-*.yaml"):
                console.print(f"Removing ArgoCD application file: {app_file}")
                app_file.unlink()

            # Also remove main tenant application file
            tenant_app_file = argocd_apps_dir / f"tenant-{name}.yaml"
            if tenant_app_file.exists():
                console.print(f"Removing ArgoCD application file: {tenant_app_file}")
                tenant_app_file.unlink()

        console.print(f"[green]✅ Tenant '{name}' deleted successfully[/green]")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]❌ Failed to delete tenant: {e.stderr or e}[/red]")
        raise typer.Exit(1)
    except Exception as e:
        console.print(f"[red]❌ Error deleting tenant: {e}[/red]")
        raise typer.Exit(1)


@app.command("auth")
def configure_tenant_auth(
    name: str = typer.Argument(..., help="Tenant name"),
    provider: str = typer.Option(
        "github",
        "--provider",
        "-p",
        help="Identity provider: github, google, microsoft",
    ),
    interactive: bool = typer.Option(
        True, "--interactive/--non-interactive", help="Interactive configuration"
    ),
):
    """Configure identity providers for a tenant."""

    console.print(
        f"[bold cyan]🔐 Configuring authentication for tenant: {name}[/bold cyan]\n"
    )

    try:
        # TODO: Implement identity provider configuration
        # This would integrate with the existing Keycloak IDP manager

        console.print(
            "[yellow]⚠️  Identity provider configuration not yet implemented[/yellow]"
        )
        console.print("This feature will be added in the next version.")
        console.print(
            "For now, configure identity providers manually in Keycloak admin console."
        )

    except Exception as e:
        console.print(f"[red]❌ Authentication configuration failed: {e}[/red]")
        raise typer.Exit(1)


@app.command("schema")
def show_tenant_schema(
    output: str = typer.Option(
        "yaml", "--output", "-o", help="Output format: yaml, json"
    ),
):
    """Show the tenant configuration schema."""

    console.print("[bold cyan]📋 Tenant Configuration Schema[/bold cyan]\n")

    try:
        cue_engine = CUEEngine(console=console)
        schema = cue_engine.get_tenant_schema()

        if output == "json":
            console.print(json.dumps(schema, indent=2))
        else:
            console.print(yaml.dump(schema, default_flow_style=False, indent=2))

    except Exception as e:
        console.print(f"[red]❌ Failed to get schema: {e}[/red]")
        raise typer.Exit(1)


def _interactive_tenant_setup(
    name: str,
    display_name: Optional[str],
    domain: Optional[str],
    organization: Optional[str],
    modules: Optional[str],
) -> Dict[str, Any]:
    """Interactively gather tenant configuration."""

    console.print("[bold]Let's configure your tenant:[/bold]\n")

    # Basic information
    display_name = display_name or Prompt.ask("Display name", default=name.title())
    domain = domain or Prompt.ask("Primary domain", default=f"{name}.platform.local")
    organization = organization or Prompt.ask(
        "Organization name", default="My Organization"
    )

    # Modules
    if modules:
        module_list = [m.strip() for m in modules.split(",")]
    else:
        default_modules = "web-app"
        modules_input = Prompt.ask(
            "Initial modules (comma-separated)", default=default_modules
        )
        module_list = [m.strip() for m in modules_input.split(",")]

    # Environment
    environment = Prompt.ask(
        "Environment", choices=["dev", "staging", "prod"], default="dev"
    )

    # Security settings
    console.print("\n[bold]Security Configuration:[/bold]")
    internet_access = Confirm.ask("Allow internet access for modules?", default=False)
    cross_tenant = Confirm.ask("Allow cross-tenant communication?", default=False)

    # Identity providers
    console.print("\n[bold]Identity Providers:[/bold]")
    github_enabled = Confirm.ask("Enable GitHub OAuth?", default=True)
    google_enabled = Confirm.ask("Enable Google OAuth?", default=False)
    microsoft_enabled = Confirm.ask("Enable Microsoft OAuth?", default=False)

    # Build identity providers config
    identity_providers = {}

    if github_enabled:
        github_client_id = Prompt.ask("GitHub OAuth Client ID")
        github_org = Prompt.ask("GitHub Organization (optional)", default="")

        identity_providers["github"] = {
            "enabled": True,
            "clientId": github_client_id,
            "organization": github_org if github_org else None,
            "scopes": ["user:email"],
            "trustEmail": True,
            "storeToken": False,
            "addReadTokenRoleOnCreate": False,
            "attributeMapping": {
                "username": "login",
                "email": "email",
                "firstName": "name",
                "lastName": "",
            },
        }

    if google_enabled:
        google_client_id = Prompt.ask("Google OAuth Client ID")
        hosted_domain = Prompt.ask("G Suite hosted domain (optional)", default="")

        identity_providers["google"] = {
            "enabled": True,
            "clientId": google_client_id,
            "hostedDomain": hosted_domain if hosted_domain else None,
            "offlineAccess": False,
            "scopes": ["openid", "profile", "email"],
            "trustEmail": True,
            "storeToken": False,
            "addReadTokenRoleOnCreate": False,
        }

    if microsoft_enabled:
        microsoft_client_id = Prompt.ask("Microsoft OAuth Client ID")
        tenant_id = Prompt.ask("Azure AD Tenant ID", default="common")

        identity_providers["microsoft"] = {
            "enabled": True,
            "clientId": microsoft_client_id,
            "tenantId": tenant_id,
            "scopes": ["openid", "profile", "email"],
            "trustEmail": True,
            "storeToken": False,
            "addReadTokenRoleOnCreate": False,
        }

    # Create configuration using the CUE engine's default tenant factory
    from ..core.cue_engine import CUEEngine

    config = CUEEngine.create_default_tenant(
        name, display_name, domain, organization, module_list
    )

    # Update with interactive choices
    config["metadata"]["environment"] = environment
    config["authentication"]["identityProviders"] = identity_providers
    config["security"]["network"]["internetAccess"]["allowed"] = internet_access
    config["security"]["network"]["crossTenantAccess"] = cross_tenant

    return config


def _non_interactive_tenant_setup(
    name: str,
    display_name: Optional[str],
    domain: Optional[str],
    organization: Optional[str],
    modules: Optional[str],
) -> Dict[str, Any]:
    """Create tenant configuration from command line parameters."""

    display_name = display_name or name.title()
    domain = domain or f"{name}.platform.local"
    organization = organization or "My Organization"
    module_list = modules.split(",") if modules else ["web-app"]

    from ..core.cue_engine import CUEEngine

    return CUEEngine.create_default_tenant(
        name, display_name, domain, organization, module_list
    )


def _deploy_tenant_resources(bundle: Dict[str, Any], wait: bool = True):
    """Deploy tenant resources to Kubernetes."""
    import subprocess
    import tempfile

    k8s_resources = bundle["kubernetes"]
    tenant_name = bundle["tenant"]["metadata"]["name"]

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Write all resources to temporary files
        resource_files = []

        for resource_type, resource_data in k8s_resources.items():
            if isinstance(resource_data, dict) and resource_data.get("kind"):
                # Single resource
                resource_file = temp_path / f"{resource_type}.yaml"
                with open(resource_file, "w") as f:
                    yaml.dump(resource_data, f, default_flow_style=False, indent=2)
                resource_files.append(resource_file)

            elif isinstance(resource_data, list):
                # Multiple resources
                resource_file = temp_path / f"{resource_type}.yaml"
                with open(resource_file, "w") as f:
                    yaml.dump_all(resource_data, f, default_flow_style=False, indent=2)
                resource_files.append(resource_file)

            elif isinstance(resource_data, dict):
                # Nested resources
                for sub_name, sub_data in resource_data.items():
                    if isinstance(sub_data, dict) and sub_data.get("kind"):
                        resource_file = temp_path / f"{resource_type}-{sub_name}.yaml"
                        with open(resource_file, "w") as f:
                            yaml.dump(sub_data, f, default_flow_style=False, indent=2)
                        resource_files.append(resource_file)

        # Apply resources in order
        console.print("📦 Creating Kubernetes resources...")

        for resource_file in resource_files:
            console.print(f"   Applying {resource_file.name}...")

            cmd = ["kubectl", "apply", "-f", str(resource_file)]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                console.print(
                    f"[red]❌ Failed to apply {resource_file.name}: {result.stderr}[/red]"
                )
                raise Exception(f"Resource application failed: {result.stderr}")

        # Wait for namespace to be ready
        if wait:
            console.print(f"⏳ Waiting for namespace {tenant_name} to be ready...")

            cmd = [
                "kubectl",
                "wait",
                "--for=condition=Ready",
                f"namespace/{tenant_name}",
                "--timeout=60s",
            ]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                console.print(f"[green]✅ Namespace {tenant_name} is ready[/green]")
            else:
                console.print(
                    f"[yellow]⚠️  Timeout waiting for namespace {tenant_name}[/yellow]"
                )


if __name__ == "__main__":
    app()
