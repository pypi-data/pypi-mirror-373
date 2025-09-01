"""Module management commands for Orchestr8 CLI."""

import asyncio
import json
from pathlib import Path
from typing import Optional

import click
import yaml
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

console = Console()


@click.group()
def module():
    """Manage Orchestr8 modules."""
    pass


@module.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["table", "json", "yaml"]),
    default="table",
    help="Output format",
)
async def list():
    """List all deployed modules."""
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Fetching modules...", total=None)

        try:
            # Get ArgoCD applications
            proc = await asyncio.create_subprocess_exec(
                "kubectl",
                "get",
                "applications",
                "-n",
                "argocd",
                "-o",
                "json",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await proc.communicate()

            if proc.returncode != 0:
                console.print(f"[red]Error: {stderr.decode()}[/red]")
                return

            apps = json.loads(stdout.decode())
            modules = []

            for app in apps.get("items", []):
                metadata = app.get("metadata", {})
                spec = app.get("spec", {})
                status = app.get("status", {})

                # Filter for module applications
                if metadata.get(
                    "namespace"
                ) == "argocd" and "platform" not in metadata.get("name", ""):
                    modules.append(
                        {
                            "name": metadata.get("name"),
                            "namespace": spec.get("destination", {}).get("namespace"),
                            "repo": spec.get("source", {}).get("repoURL"),
                            "path": spec.get("source", {}).get("path"),
                            "revision": spec.get("source", {}).get("targetRevision"),
                            "sync_status": status.get("sync", {}).get(
                                "status", "Unknown"
                            ),
                            "health_status": status.get("health", {}).get(
                                "status", "Unknown"
                            ),
                        }
                    )

            progress.update(task, completed=True)

            if format == "json":
                console.print_json(data=modules)
            elif format == "yaml":
                console.print(yaml.dump(modules, default_flow_style=False))
            else:
                table = Table(title="Deployed Modules")
                table.add_column("Name", style="cyan")
                table.add_column("Namespace", style="magenta")
                table.add_column("Repository")
                table.add_column("Revision")
                table.add_column("Sync", style="green")
                table.add_column("Health", style="yellow")

                for m in modules:
                    sync_color = "green" if m["sync_status"] == "Synced" else "red"
                    health_color = (
                        "green" if m["health_status"] == "Healthy" else "yellow"
                    )

                    table.add_row(
                        m["name"],
                        m["namespace"],
                        m["repo"].replace("https://github.com/", ""),
                        m["revision"],
                        f"[{sync_color}]{m['sync_status']}[/{sync_color}]",
                        f"[{health_color}]{m['health_status']}[/{health_color}]",
                    )

                console.print(table)

        except Exception as e:
            console.print(f"[red]Error listing modules: {e}[/red]")


@module.command()
@click.argument("module_name")
@click.option("--version", "-v", help="Module version/tag to deploy")
@click.option(
    "--values", "-f", type=click.Path(exists=True), help="Values file for Helm chart"
)
@click.option("--namespace", "-n", help="Target namespace (defaults to module name)")
@click.option("--repo", "-r", help="Git repository URL")
@click.option("--path", "-p", default="helm/chart", help="Path to Helm chart in repo")
async def deploy(
    module_name: str,
    version: Optional[str],
    values: Optional[str],
    namespace: Optional[str],
    repo: Optional[str],
    path: str,
):
    """Deploy a new module to the platform."""
    namespace = namespace or module_name
    version = version or "main"

    # Default repo pattern
    if not repo:
        repo = f"https://github.com/killerapp/{module_name}"

    console.print(f"[cyan]Deploying module {module_name}...[/cyan]")

    # Create ArgoCD application manifest
    app_manifest = {
        "apiVersion": "argoproj.io/v1alpha1",
        "kind": "Application",
        "metadata": {
            "name": module_name,
            "namespace": "argocd",
            "finalizers": ["resources-finalizer.argocd.argoproj.io"],
        },
        "spec": {
            "project": "default",
            "source": {
                "repoURL": repo,
                "targetRevision": version,
                "path": path,
            },
            "destination": {
                "server": "https://kubernetes.default.svc",
                "namespace": namespace,
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

    # Add values file if provided
    if values:
        with open(values, "r") as f:
            values_content = f.read()
            app_manifest["spec"]["source"]["helm"] = {"values": values_content}

    # Write manifest to temp file
    import tempfile

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(app_manifest, f)
        manifest_path = f.name

    try:
        # Apply the manifest
        proc = await asyncio.create_subprocess_exec(
            "kubectl",
            "apply",
            "-f",
            manifest_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode == 0:
            console.print(
                f"[green]✓ Module {module_name} deployed successfully![/green]"
            )
            console.print(
                f"[yellow]Run 'o8 module status {module_name}' to check deployment status[/yellow]"
            )
        else:
            console.print(f"[red]Error deploying module: {stderr.decode()}[/red]")

    finally:
        # Clean up temp file
        Path(manifest_path).unlink(missing_ok=True)


@module.command()
@click.argument("module_name")
@click.option("--watch", "-w", is_flag=True, help="Watch status continuously")
async def status(module_name: str, watch: bool):
    """Check status of a deployed module."""

    async def get_status():
        proc = await asyncio.create_subprocess_exec(
            "kubectl",
            "get",
            "application",
            module_name,
            "-n",
            "argocd",
            "-o",
            "json",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()

        if proc.returncode != 0:
            console.print(f"[red]Module {module_name} not found[/red]")
            return None

        app = json.loads(stdout.decode())
        status = app.get("status", {})

        return {
            "name": module_name,
            "sync": status.get("sync", {}).get("status", "Unknown"),
            "health": status.get("health", {}).get("status", "Unknown"),
            "message": status.get("conditions", [{}])[0].get("message", "")
            if status.get("conditions")
            else "",
            "resources": len(status.get("resources", [])),
        }

    if watch:
        console.print(
            f"[cyan]Watching status for {module_name} (Ctrl+C to stop)...[/cyan]"
        )
        while True:
            status_info = await get_status()
            if status_info:
                console.clear()
                console.print(f"[bold]Module: {status_info['name']}[/bold]")
                console.print(f"Sync Status: {status_info['sync']}")
                console.print(f"Health Status: {status_info['health']}")
                console.print(f"Resources: {status_info['resources']}")
                if status_info["message"]:
                    console.print(f"Message: {status_info['message']}")
            await asyncio.sleep(2)
    else:
        status_info = await get_status()
        if status_info:
            console.print(f"[bold]Module: {status_info['name']}[/bold]")
            console.print(f"Sync Status: {status_info['sync']}")
            console.print(f"Health Status: {status_info['health']}")
            console.print(f"Resources: {status_info['resources']}")
            if status_info["message"]:
                console.print(f"Message: {status_info['message']}")


@module.command()
@click.argument("module_name")
@click.option("--follow", "-f", is_flag=True, help="Follow log output")
@click.option("--tail", "-n", default=100, help="Number of lines to show")
@click.option("--container", "-c", help="Specific container to get logs from")
async def logs(module_name: str, follow: bool, tail: int, container: Optional[str]):
    """Get logs from a module's pods."""
    # Get pods in the module's namespace
    proc = await asyncio.create_subprocess_exec(
        "kubectl",
        "get",
        "pods",
        "-n",
        module_name,
        "-o",
        "json",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode != 0:
        console.print(f"[red]Error getting pods: {stderr.decode()}[/red]")
        return

    pods = json.loads(stdout.decode())
    pod_list = [p["metadata"]["name"] for p in pods.get("items", [])]

    if not pod_list:
        console.print(f"[yellow]No pods found in namespace {module_name}[/yellow]")
        return

    # Use the first pod or let user choose
    pod_name = pod_list[0]
    if len(pod_list) > 1:
        console.print(f"[cyan]Multiple pods found. Using: {pod_name}[/cyan]")

    # Build kubectl logs command
    cmd = ["kubectl", "logs", "-n", module_name, pod_name, f"--tail={tail}"]
    if follow:
        cmd.append("-f")
    if container:
        cmd.extend(["-c", container])

    # Stream logs
    proc = await asyncio.create_subprocess_exec(
        *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    try:
        if follow:
            console.print(
                f"[cyan]Following logs for {pod_name} (Ctrl+C to stop)...[/cyan]"
            )
            while True:
                line = await proc.stdout.readline()
                if not line:
                    break
                console.print(line.decode().rstrip())
        else:
            stdout, stderr = await proc.communicate()
            if proc.returncode == 0:
                console.print(stdout.decode())
            else:
                console.print(f"[red]Error: {stderr.decode()}[/red]")
    except KeyboardInterrupt:
        proc.terminate()
        console.print("\n[yellow]Log streaming stopped[/yellow]")


@module.command()
@click.argument("module_name")
@click.option("--replicas", "-r", type=int, required=True, help="Number of replicas")
async def scale(module_name: str, replicas: int):
    """Scale a module's deployment."""
    console.print(f"[cyan]Scaling {module_name} to {replicas} replicas...[/cyan]")

    # Scale the deployment
    proc = await asyncio.create_subprocess_exec(
        "kubectl",
        "scale",
        "deployment",
        "-n",
        module_name,
        "--replicas",
        str(replicas),
        "--all",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode == 0:
        console.print(
            f"[green]✓ Module {module_name} scaled to {replicas} replicas[/green]"
        )
    else:
        console.print(f"[red]Error scaling module: {stderr.decode()}[/red]")


@module.command()
@click.argument("module_name")
@click.option("--revision", type=int, help="Specific revision to rollback to")
async def rollback(module_name: str, revision: Optional[int]):
    """Rollback a module to a previous version."""
    if revision:
        console.print(
            f"[cyan]Rolling back {module_name} to revision {revision}...[/cyan]"
        )
        cmd = [
            "kubectl",
            "rollout",
            "undo",
            "deployment",
            "-n",
            module_name,
            "--to-revision",
            str(revision),
        ]
    else:
        console.print(f"[cyan]Rolling back {module_name} to previous version...[/cyan]")
        cmd = ["kubectl", "rollout", "undo", "deployment", "-n", module_name]

    proc = await asyncio.create_subprocess_exec(
        *cmd, "--all", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode == 0:
        console.print(f"[green]✓ Module {module_name} rolled back successfully[/green]")
    else:
        console.print(f"[red]Error rolling back module: {stderr.decode()}[/red]")


@module.command()
@click.argument("module_name")
@click.option("--force", "-f", is_flag=True, help="Force deletion without confirmation")
async def delete(module_name: str, force: bool):
    """Delete a module from the platform."""
    if not force:
        if not click.confirm(f"Are you sure you want to delete module {module_name}?"):
            console.print("[yellow]Deletion cancelled[/yellow]")
            return

    console.print(f"[cyan]Deleting module {module_name}...[/cyan]")

    # Delete ArgoCD application
    proc = await asyncio.create_subprocess_exec(
        "kubectl",
        "delete",
        "application",
        module_name,
        "-n",
        "argocd",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()

    if proc.returncode == 0:
        console.print(f"[green]✓ Module {module_name} deleted successfully[/green]")
    else:
        console.print(f"[red]Error deleting module: {stderr.decode()}[/red]")


# Make commands async-compatible
def run_async(func):
    """Wrapper to run async functions in click commands."""

    def wrapper(*args, **kwargs):
        return asyncio.run(func(*args, **kwargs))

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# Apply async wrapper to all commands
list = run_async(list)
deploy = run_async(deploy)
status = run_async(status)
logs = run_async(logs)
scale = run_async(scale)
rollback = run_async(rollback)
delete = run_async(delete)
