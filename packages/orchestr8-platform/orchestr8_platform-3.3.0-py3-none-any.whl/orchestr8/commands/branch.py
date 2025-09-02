"""Orchestr8 Branch deployment management commands."""

import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import yaml

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

app = typer.Typer(help="Branch deployment management")
console = Console()


def get_argocd_app_path(module: str, environment: str) -> Path:
    """Get ArgoCD application path for module and environment."""
    base_path = Path("argocd-apps/modules")

    # Create environment-specific subdirectory if needed
    env_path = base_path / module
    env_path.mkdir(parents=True, exist_ok=True)

    return env_path / f"{module}-{environment}.yaml"


def create_branch_application(
    module: str,
    branch: str,
    environment: str = "dev",
    namespace_suffix: str = None,
    auto_sync: bool = True,
) -> Dict[str, Any]:
    """Create ArgoCD application spec for branch deployment."""

    namespace = f"{module}-{namespace_suffix or environment}"
    app_name = f"{module}-{namespace_suffix or environment}"

    return {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {
            "name": app_name,
            "namespace": "argocd",
            "labels": {
                "module": module,
                "environment": environment,
                "branch": branch.replace("/", "-"),
                "managed-by": "orchestr8",
            },
            "annotations": {
                "orchestr8.io/branch": branch,
                "orchestr8.io/environment": environment,
            },
        },
        "spec": {
            "project": f"{environment}-project"
            if environment != "prod"
            else "production-project",
            "source": {
                "repoURL": "https://github.com/killerapp/orchestr8",
                "targetRevision": branch,
                "path": f"modules/{module}/base",
            },
            "destination": {
                "server": "https://kubernetes.default.svc",
                "namespace": namespace,
            },
            "syncPolicy": {
                "automated": {
                    "prune": auto_sync and environment != "prod",
                    "selfHeal": auto_sync and environment != "prod",
                },
                "syncOptions": ["CreateNamespace=true"],
            },
        },
    }


@app.command("deploy")
def deploy_branch(
    module: str = typer.Argument(..., help="Module name (e.g., clickhouse, langfuse)"),
    branch: str = typer.Option("main", "--branch", "-b", help="Git branch to deploy"),
    environment: str = typer.Option(
        "dev", "--env", "-e", help="Environment (dev, staging, prod)"
    ),
    namespace_suffix: str = typer.Option(
        None, "--namespace", "-n", help="Custom namespace suffix"
    ),
    auto_sync: bool = typer.Option(
        True, "--auto-sync/--no-auto-sync", help="Enable automatic sync"
    ),
    apply: bool = typer.Option(
        False, "--apply", "-a", help="Apply to cluster immediately"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force overwrite existing application"
    ),
):
    """Deploy a module from a specific branch."""

    console.print(
        Panel.fit(
            f"[bold cyan]Branch Deployment Configuration[/bold cyan]\n\n"
            f"Module: [yellow]{module}[/yellow]\n"
            f"Branch: [green]{branch}[/green]\n"
            f"Environment: [blue]{environment}[/blue]\n"
            f"Namespace: [magenta]{module}-{namespace_suffix or environment}[/magenta]",
            title="Deployment Details",
        )
    )

    # Check if application already exists
    app_path = get_argocd_app_path(module, namespace_suffix or environment)

    if app_path.exists() and not force:
        console.print(
            f"\n[yellow]Warning:[/yellow] Application already exists at {app_path}"
        )
        console.print("Use --force to overwrite or choose a different namespace suffix")

        if not typer.confirm("Continue anyway?"):
            raise typer.Exit(0)

    # Create application spec
    app_spec = create_branch_application(
        module=module,
        branch=branch,
        environment=environment,
        namespace_suffix=namespace_suffix,
        auto_sync=auto_sync,
    )

    # Save application spec
    app_path.parent.mkdir(parents=True, exist_ok=True)
    with open(app_path, "w") as f:
        yaml.dump(app_spec, f, default_flow_style=False, sort_keys=False)

    console.print(f"\n[green]✓[/green] Created ArgoCD application at: {app_path}")

    # Show the generated YAML
    with open(app_path) as f:
        syntax = Syntax(f.read(), "yaml", theme="monokai", line_numbers=True)
        console.print("\n[bold]Generated Application:[/bold]")
        console.print(syntax)

    # Apply to cluster if requested
    if apply:
        console.print("\n[bold cyan]Applying to cluster...[/bold cyan]")
        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", str(app_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            console.print("[green]✓[/green] Application deployed successfully!")
            console.print(result.stdout)

            # Wait for app to appear in ArgoCD
            console.print("\n[dim]Waiting for ArgoCD to recognize application...[/dim]")
            subprocess.run(
                [
                    "kubectl",
                    "wait",
                    "--for=condition=Synced",
                    f"application/{module}-{namespace_suffix or environment}",
                    "-n",
                    "argocd",
                    "--timeout=60s",
                ],
                capture_output=True,
            )

            console.print(
                f"\n[bold green]Success![/bold green] Module deployed from branch [cyan]{branch}[/cyan]"
            )
            console.print("\nAccess ArgoCD UI: http://localhost:30080")
            console.print(f"Application: {module}-{namespace_suffix or environment}")

        except subprocess.CalledProcessError as e:
            console.print(f"[red]✗[/red] Failed to apply: {e.stderr}")
            raise typer.Exit(1)


@app.command("list")
def list_deployments(
    module: Optional[str] = typer.Option(
        None, "--module", "-m", help="Filter by module"
    ),
    environment: Optional[str] = typer.Option(
        None, "--env", "-e", help="Filter by environment"
    ),
):
    """List all branch deployments."""

    try:
        # Get all ArgoCD applications
        result = subprocess.run(
            ["kubectl", "get", "applications", "-n", "argocd", "-o", "json"],
            capture_output=True,
            text=True,
            check=True,
        )

        import json

        apps = json.loads(result.stdout).get("items", [])

        # Filter Orchestr8-managed apps
        o8_apps = []
        for app in apps:
            labels = app.get("metadata", {}).get("labels", {})
            if labels.get("managed-by") == "orchestr8":
                # Apply filters
                if module and labels.get("module") != module:
                    continue
                if environment and labels.get("environment") != environment:
                    continue

                o8_apps.append(
                    {
                        "name": app["metadata"]["name"],
                        "module": labels.get("module", ""),
                        "environment": labels.get("environment", ""),
                        "branch": app["metadata"]
                        .get("annotations", {})
                        .get("orchestr8.io/branch", ""),
                        "namespace": app["spec"]["destination"]["namespace"],
                        "sync": app.get("status", {})
                        .get("sync", {})
                        .get("status", "Unknown"),
                        "health": app.get("status", {})
                        .get("health", {})
                        .get("status", "Unknown"),
                    }
                )

        if not o8_apps:
            console.print("[yellow]No branch deployments found[/yellow]")
            return

        # Display table
        table = Table(title="Orchestr8 Branch Deployments")
        table.add_column("Module", style="cyan")
        table.add_column("Environment", style="blue")
        table.add_column("Branch", style="green")
        table.add_column("Namespace", style="magenta")
        table.add_column("Sync", style="yellow")
        table.add_column("Health")

        for app in o8_apps:
            health_style = "green" if app["health"] == "Healthy" else "red"
            sync_style = "green" if app["sync"] == "Synced" else "yellow"

            table.add_row(
                app["module"],
                app["environment"],
                app["branch"],
                app["namespace"],
                f"[{sync_style}]{app['sync']}[/{sync_style}]",
                f"[{health_style}]{app['health']}[/{health_style}]",
            )

        console.print(table)

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to list applications: {e.stderr}[/red]")
        raise typer.Exit(1)


@app.command("promote")
def promote_deployment(
    module: str = typer.Argument(..., help="Module name"),
    from_env: str = typer.Option("dev", "--from", help="Source environment"),
    to_env: str = typer.Option("staging", "--to", help="Target environment"),
    branch: Optional[str] = typer.Option(
        None, "--branch", "-b", help="Override target branch"
    ),
    apply: bool = typer.Option(False, "--apply", "-a", help="Apply immediately"),
):
    """Promote a module deployment to another environment."""

    console.print(
        Panel.fit(
            f"[bold cyan]Promotion Configuration[/bold cyan]\n\n"
            f"Module: [yellow]{module}[/yellow]\n"
            f"From: [red]{from_env}[/red] → To: [green]{to_env}[/green]\n"
            f"Branch: [blue]{branch or 'auto-detect'}[/blue]",
            title="Promotion Details",
        )
    )

    # Get source application
    source_app_path = get_argocd_app_path(module, from_env)

    if not source_app_path.exists():
        console.print(f"[red]Source application not found: {source_app_path}[/red]")
        raise typer.Exit(1)

    # Load source application
    with open(source_app_path) as f:
        source_app = yaml.safe_load(f)

    # Determine target branch
    if not branch:
        if to_env == "prod":
            branch = "main"
        elif to_env == "staging":
            branch = source_app["spec"]["source"]["targetRevision"]
        else:
            branch = source_app["spec"]["source"]["targetRevision"]

    # Create target application
    target_app = create_branch_application(
        module=module, branch=branch, environment=to_env, auto_sync=(to_env != "prod")
    )

    # Save target application
    target_app_path = get_argocd_app_path(module, to_env)
    with open(target_app_path, "w") as f:
        yaml.dump(target_app, f, default_flow_style=False, sort_keys=False)

    console.print(
        f"\n[green]✓[/green] Created promotion application at: {target_app_path}"
    )

    if apply:
        try:
            subprocess.run(
                ["kubectl", "apply", "-f", str(target_app_path)],
                capture_output=True,
                text=True,
                check=True,
            )
            console.print("[green]✓[/green] Promotion completed successfully!")

        except subprocess.CalledProcessError as e:
            console.print(f"[red]Failed to apply promotion: {e.stderr}[/red]")
            raise typer.Exit(1)


@app.command("cleanup")
def cleanup_deployment(
    module: str = typer.Argument(..., help="Module name"),
    environment: str = typer.Option(..., "--env", "-e", help="Environment to cleanup"),
    namespace_suffix: Optional[str] = typer.Option(
        None, "--namespace", "-n", help="Custom namespace suffix"
    ),
    confirm: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Remove a branch deployment."""

    app_name = f"{module}-{namespace_suffix or environment}"

    if not confirm:
        console.print(
            f"[yellow]Warning:[/yellow] This will delete the application [red]{app_name}[/red]"
        )
        if not typer.confirm("Continue?"):
            raise typer.Exit(0)

    try:
        # Delete ArgoCD application
        subprocess.run(
            ["kubectl", "delete", "application", app_name, "-n", "argocd"],
            capture_output=True,
            text=True,
            check=True,
        )
        console.print(f"[green]✓[/green] Deleted application: {app_name}")

        # Remove application file
        app_path = get_argocd_app_path(module, namespace_suffix or environment)
        if app_path.exists():
            app_path.unlink()
            console.print(f"[green]✓[/green] Removed application file: {app_path}")

    except subprocess.CalledProcessError as e:
        console.print(f"[red]Failed to cleanup: {e.stderr}[/red]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
