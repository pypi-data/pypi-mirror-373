"""Orchestr8 CLI."""

import asyncio
from typing import Optional
import sys
import subprocess

import typer
from rich.console import Console
from rich.table import Table

from . import __version__
from .core import Orchestrator, Config, CloudProvider
from .core.config import GitHubConfig, KeycloakConfig
from .auth import GitHubDeviceFlow
from .auth.keycloak_idp import KeycloakIdentityProviderManager, IdentityProviderType
from .commands import module as module_commands
from .commands import branch as branch_commands
from .commands import argocd as argocd_commands
from .commands import secrets as secrets_commands
from .commands import bootstrap as bootstrap_commands
from .commands import tenant as tenant_commands
from .commands import llama as llama_commands
import httpx
import json

# Enable UTF-8 encoding for Windows to support emojis
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

console = Console()


def version_callback(value: bool):
    """Show version and exit."""
    if value:
        console.print(f"Orchestr8 v{__version__}")
        raise typer.Exit()


app = typer.Typer(
    name="o8",
    help=f"Orchestr8 CLI v{__version__} - Manage your Kubernetes platform with ease",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: Optional[bool] = typer.Option(
        None,
        "--version",
        "-V",
        help="Show version and exit",
        callback=version_callback,
        is_eager=True,
    ),
):
    """Orchestr8 CLI - Enterprise GitOps platform management."""
    if ctx.invoked_subcommand is None:
        # No command provided, show status (which includes everything)
        status(validate_only=False)


@app.command()
def setup(
    provider: CloudProvider = typer.Option(
        CloudProvider.LOCAL, "--provider", "-p", help="Cloud provider"
    ),
    cluster_name: str = typer.Option(
        "o8-cluster", "--cluster", "-c", help="Kubernetes cluster name"
    ),
    domain: str = typer.Option(
        None, "--domain", "-d", help="Platform domain (e.g., platform.example.com)"
    ),
    github_org: str = typer.Option(
        None, "--github-org", "-g", help="GitHub organization"
    ),
    github_token: Optional[str] = typer.Option(
        None,
        "--github-token",
        envvar="GITHUB_TOKEN",
        help="GitHub personal access token",
    ),
    region: Optional[str] = typer.Option(
        "us-east-1", "--region", "-r", help="Cloud region (for AWS/GCP/Azure)"
    ),
    non_interactive: bool = typer.Option(
        False, "--non-interactive", "-n", help="Run without prompts"
    ),
    auth_interactive: bool = typer.Option(
        False, "--auth-interactive", "-a", help="Use interactive OAuth authentication"
    ),
    provision_infrastructure: bool = typer.Option(
        False,
        "--provision-infrastructure",
        "-i",
        help="Provision cloud infrastructure with Terraform (GCP only currently)",
    ),
    gcp_project_id: Optional[str] = typer.Option(
        None,
        "--gcp-project-id",
        help="GCP Project ID (required when provisioning GCP infrastructure)",
    ),
    environment: str = typer.Option(
        "dev", "--environment", "-e", help="Environment (dev, staging, production)"
    ),
):
    """Set up a new Orchestr8 instance."""
    console.print("[bold cyan]🚀 Orchestr8 Setup[/bold cyan]\n")

    # Check if provisioning infrastructure
    if provision_infrastructure:
        if provider == CloudProvider.GCP and not gcp_project_id:
            gcp_project_id = typer.prompt("GCP Project ID")
        elif provider != CloudProvider.GCP:
            console.print(
                "[red]Infrastructure provisioning is currently only supported for GCP[/red]"
            )
            raise typer.Exit(1)

    # Interactive mode
    if not non_interactive:
        if not domain:
            domain = typer.prompt(
                "Platform domain",
                default="platform.local"
                if provider == CloudProvider.LOCAL
                else "platform.example.com",
            )

        if not github_org:
            github_org = typer.prompt("GitHub organization")

        # Check if repository is private
        repo_url = f"https://github.com/{github_org}/orchestr8"
        console.print(f"\n[dim]Checking repository: {repo_url}[/dim]")

        # GitHub authentication is required for private repositories
        if not github_token:
            console.print("\n[red]⚠️  GitHub authentication is required[/red]")
            console.print(
                "[yellow]ArgoCD needs access to the orchestr8 repository[/yellow]"
            )
            console.print("\nAuthentication options:")
            console.print("  1. OAuth Device Flow (recommended - secure & easy)")
            console.print("  2. Personal Access Token (manual setup)")

            auth_choice = typer.prompt(
                "\nChoose authentication method",
                type=int,
                default=1,
                show_default=True,
                show_choices=False,
            )

            if auth_choice not in [1, 2]:
                console.print("[red]Invalid choice. Please select 1 or 2.[/red]")
                raise typer.Exit(1)

            if auth_choice == 1:  # OAuth Device Flow
                console.print(
                    "\n[cyan]Starting GitHub OAuth device flow authentication...[/cyan]"
                )

                # Ask for client ID
                console.print(
                    "[dim]Note: OAuth App must have device flow enabled[/dim]"
                )
                oauth_client_id = typer.prompt(
                    "GitHub OAuth App Client ID", default="", show_default=False
                )

                if not oauth_client_id:
                    console.print(
                        "[red]OAuth App Client ID is required for device flow[/red]"
                    )
                    raise typer.Exit(1)

                # Perform OAuth authentication
                github_auth = GitHubDeviceFlow(console, client_id=oauth_client_id)
                auth_result = github_auth.authenticate(scopes="repo")

                if auth_result:
                    github_token = auth_result.access_token
                    console.print(
                        f"[green]✅ Authenticated successfully with '{auth_result.scope}' scope[/green]"
                    )
                else:
                    console.print(
                        "[red]❌ Authentication failed or was cancelled[/red]"
                    )
                    raise typer.Exit(1)

            else:  # auth_choice == 2 - Personal Access Token
                console.print("\n[cyan]To create a Personal Access Token:[/cyan]")
                console.print("1. Go to https://github.com/settings/tokens/new")
                console.print(
                    "2. Select scope: 'repo' (Full control of private repositories)"
                )
                console.print("3. Generate token and copy it\n")

                github_token = typer.prompt(
                    "GitHub personal access token", hide_input=True
                )

                if not github_token:
                    console.print("[red]❌ GitHub token is required[/red]")
                    raise typer.Exit(1)

                # Validate the token silently
                github_auth = GitHubDeviceFlow(console)
                github_auth.validate_token(github_token)

    # Validate required fields (only domain and github_org are truly required)
    if not all([domain, github_org]):
        console.print(
            "[red]Error: Missing required configuration (domain and GitHub org)[/red]"
        )
        raise typer.Exit(1)

    # Create configuration
    config = Config(
        provider=provider,
        region=region if provider != CloudProvider.LOCAL else None,
        cluster_name=cluster_name,
        domain=domain,
        github=GitHubConfig(org=github_org, token=github_token),
        keycloak=KeycloakConfig(),
        provision_infrastructure=provision_infrastructure,
        gcp_project_id=gcp_project_id,
        environment=environment,
    )

    # Show configuration
    console.print("\n[yellow]Configuration Summary:[/yellow]")
    table = Table(show_header=False, box=None)
    table.add_row("Provider:", config.provider.value)
    if config.region:
        table.add_row("Region:", config.region)
    table.add_row("Cluster:", config.cluster_name)
    table.add_row("Domain:", config.domain)
    table.add_row("GitHub Org:", config.github.org)
    if provision_infrastructure:
        table.add_row("Infrastructure:", "[green]Will provision with Terraform[/green]")
        if gcp_project_id:
            table.add_row("GCP Project:", gcp_project_id)
        table.add_row("Environment:", environment)
    console.print(table)

    if not non_interactive:
        if not typer.confirm("\nProceed with setup?", default=True):
            console.print("[yellow]⚠️ Setup cancelled[/yellow]")
            raise typer.Exit(0)

    # Run setup
    try:
        orchestrator = Orchestrator(config, console)
    except Exception as e:
        console.print(f"[red]Failed to initialize orchestrator: {e}[/red]")
        import traceback

        console.print(traceback.format_exc())
        raise

    try:
        if provision_infrastructure:
            results = asyncio.run(orchestrator.setup_with_infrastructure())
        else:
            results = asyncio.run(orchestrator.setup())

        console.print("\n[green]✅ Setup completed successfully![/green]")

        # Show access information
        if config.provider == CloudProvider.LOCAL:
            console.print("\n[cyan]🎯 Access your platform:[/cyan]")
            console.print("   ArgoCD:      http://localhost:30080  (GitOps Dashboard)")
            console.print(
                "   Keycloak:    http://localhost:30081  (Identity Management)"
            )
            console.print(
                "   Platform:    http://localhost:30082  (OAuth2 Entry Point)"
            )

            if results.get("local_access", {}).get("services"):
                console.print("\n[cyan]📱 Module UIs (behind Keycloak auth):[/cyan]")
                console.print("   VoiceFuse:   http://localhost:30083")
                console.print("   Langfuse:    http://localhost:30084")

            if "argocd" in results and results["argocd"].get("admin_password"):
                console.print(
                    f"\n[dim]   ArgoCD login: admin / {results['argocd']['admin_password']}[/dim]"
                )

            # Show ArgoCD API status if available
            if results.get("argocd_api", {}).get("ready"):
                console.print("\n[cyan]🛠️  ArgoCD Management Commands:[/cyan]")
                console.print("   o8 apps                    (List all applications)")
                console.print("   o8 sync <app>              (Sync an application)")
                console.print("   o8 repos                   (Configure repositories)")

            # Check if GitHub repo was configured
            if config.github.token:
                console.print("\n[green]✅ GitHub repository access configured[/green]")
            else:
                console.print("\n[yellow]⚠️  GitHub repository not configured[/yellow]")
                console.print(
                    "[dim]   ArgoCD won't be able to sync from private repos[/dim]"
                )
                console.print("[dim]   Run 'o8 auth' after setup to configure[/dim]")
        else:
            console.print("\n[cyan]Access Information:[/cyan]")
            info_table = Table(show_header=False, box=None)
            info_table.add_row("ArgoCD URL:", f"https://argocd.{config.domain}")
            info_table.add_row("Keycloak URL:", f"https://keycloak.{config.domain}")
            if "argocd" in results and results["argocd"].get("admin_password"):
                info_table.add_row(
                    "ArgoCD Password:", results["argocd"]["admin_password"]
                )
            console.print(info_table)

            console.print("\n[blue]📌 Next steps:[/blue]")
            console.print("1. Configure DNS for your domain")
            console.print("2. Access ArgoCD to monitor deployments")
            console.print("3. Set up GitHub/Google OAuth in Keycloak (optional)")

    except Exception as e:
        console.print(f"\n[red]❌ Setup failed: {e}[/red]")
        import traceback

        console.print("[dim]" + traceback.format_exc() + "[/dim]")
        raise typer.Exit(1)


@app.command()
def status(
    validate_only: bool = typer.Option(
        False,
        "--validate",
        help="Only validate prerequisites without checking deployment status",
    ),
):
    """Check Orchestr8 status and validate prerequisites."""
    console.print(f"[bold cyan]📊 Orchestr8 v{__version__}[/bold cyan]\n")

    if validate_only:
        # Run doctor check for prerequisites validation
        from .commands.doctor import check

        check(verbose=True, fix=False)
        return

    # Try to detect cluster name and project from context
    cluster_name = None
    project_id = None
    region = None
    try:
        result = subprocess.run(
            ["kubectl", "config", "current-context"], capture_output=True, text=True
        )
        if result.returncode == 0 and result.stdout:
            context = result.stdout.strip()
            # Extract info from GKE context format: gke_PROJECT_REGION_CLUSTER
            if "gke_" in context:
                parts = context.split("_")
                if len(parts) >= 4:
                    project_id = parts[1]
                    region = parts[2]
                    cluster_name = parts[3]
    except Exception:
        pass

    # Check for infrastructure
    from orchestr8.core.terraform import TerraformManager

    tf_manager = TerraformManager(console)
    infra_status = None
    if cluster_name:
        infra_status = tf_manager.get_infrastructure_status(cluster_name)

    try:
        # Create a minimal config for status check
        config = Config(
            provider=CloudProvider.LOCAL,
            cluster_name=cluster_name or "unknown",
            domain="unknown",
            github=GitHubConfig(org="unknown"),
        )

        orchestrator = Orchestrator(config, console)
        status = asyncio.run(orchestrator.get_status())

        # Infrastructure status (if GCP)
        if infra_status and infra_status.get("provisioned"):
            console.print("[bold]☁️  Infrastructure (GCP)[/bold]")
            console.print("   Status: [green]Provisioned[/green]")
            console.print(f"   Cluster: [cyan]{cluster_name}[/cyan]")
            console.print(f"   Project: [cyan]{project_id}[/cyan]")
            console.print(
                f"   Region: [cyan]{infra_status.get('location', region or 'unknown')}[/cyan]"
            )

            # Get more GKE details if available
            if project_id and cluster_name:
                try:
                    result = subprocess.run(
                        [
                            "gcloud",
                            "container",
                            "clusters",
                            "describe",
                            cluster_name,
                            "--region",
                            region or "us-central1",
                            "--project",
                            project_id,
                            "--format=json",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0:
                        import json

                        cluster_info = json.loads(result.stdout)
                        console.print(
                            f"   K8s Version: [cyan]{cluster_info.get('currentMasterVersion', 'unknown')}[/cyan]"
                        )

                        # Count total nodes across all pools
                        total_nodes = cluster_info.get("currentNodeCount", 0)
                        console.print(f"   Nodes: [cyan]{total_nodes}[/cyan]")

                        # Check cluster status
                        cluster_status = cluster_info.get("status", "unknown")
                        status_color = (
                            "green" if cluster_status == "RUNNING" else "yellow"
                        )
                        console.print(
                            f"   Cluster Status: [{status_color}]{cluster_status}[/{status_color}]"
                        )

                        # Show endpoint
                        endpoint = cluster_info.get("endpoint", "unknown")
                        console.print(f"   Endpoint: [dim]{endpoint}[/dim]")
                except Exception:
                    pass
            console.print("")
        elif infra_status and infra_status.get("exists"):
            console.print("[bold]☁️  Infrastructure[/bold]")
            console.print(
                "   Status: [yellow]Configuration exists but not provisioned[/yellow]\n"
            )
        elif cluster_name and "gke_" in (
            status.get("kubernetes", {}).get("context", "")
        ):
            # GKE cluster but no Terraform state
            console.print("[bold]☁️  Infrastructure (GCP)[/bold]")
            console.print(
                "   Status: [yellow]Cluster exists but not managed by O8[/yellow]"
            )
            console.print(
                "   [dim]Run 'o8 setup --provision-infrastructure' to manage with Terraform[/dim]\n"
            )

        # Kubernetes status
        k8s_status = (
            "[green]Connected[/green]"
            if status["kubernetes"]["connected"]
            else "[red]Not connected[/red]"
        )
        k8s_context = status["kubernetes"].get("context", "Unknown")
        console.print("[bold]☸️  Kubernetes[/bold]")
        console.print(f"   Status: {k8s_status}")
        console.print(f"   Context: [cyan]{k8s_context}[/cyan]")

        # ArgoCD status
        argo_status = (
            "[green]Installed[/green]"
            if status["argocd"]["installed"]
            else "[red]Not installed[/red]"
        )
        argo_url = "http://localhost:30080" if status["argocd"]["installed"] else ""
        console.print("\n[bold]🚀 ArgoCD[/bold]")
        console.print(f"   Status: {argo_status}")
        if argo_url:
            console.print(f"   URL: [link={argo_url}]{argo_url}[/link]")
            # Get ArgoCD password if available
            argo_password = status.get("argocd", {}).get("admin_password")
            if argo_password:
                console.print(f"   Login: admin / {argo_password}")

        # Platform status
        platform_status = (
            "[green]Deployed[/green]"
            if status["platform"]["deployed"]
            else "[red]Not deployed[/red]"
        )
        console.print(f"\n📦 Platform: {platform_status}")

        # Keycloak status if platform is deployed
        keycloak_info = status.get("keycloak", {})
        if keycloak_info.get("installed"):
            console.print("\n🔐 Keycloak: [green]Running[/green]")
            keycloak_url = (
                "http://localhost:30081"
                if config.provider == CloudProvider.LOCAL
                else f"https://keycloak.{config.domain}"
            )
            console.print(f"   URL: [link={keycloak_url}]{keycloak_url}[/link]")
            keycloak_password = keycloak_info.get("admin_password")
            if keycloak_password:
                console.print(f"   Login: admin / {keycloak_password}")

        # Repository status (local vs remote)
        repo_type = "Local" if config.provider == CloudProvider.LOCAL else "Remote"
        repo_connected = status.get("github", {}).get("connected")
        if repo_type == "Local":
            console.print("\n📁 Repository: [cyan]Local Development[/cyan]")
            console.print("   [dim]No external repository authentication needed[/dim]")
        else:
            repo_status = (
                "[green]Connected[/green]"
                if repo_connected
                else "[yellow]Not connected[/yellow]"
            )
            console.print(f"\n🔗 Repository: {repo_status}")
            if not repo_connected:
                console.print(
                    "   [dim]Run 'o8 auth' to connect to private repositories[/dim]"
                )

        # Check ArgoCD sync status if available
        if status.get("argocd_apps"):
            console.print("\n[yellow]ArgoCD Applications:[/yellow]")
            for app_name, app_status in status["argocd_apps"].items():
                sync = app_status.get("sync", "Unknown")
                health = app_status.get("health", "Unknown")

                # Color code the statuses
                if sync == "Synced":
                    sync_display = f"[green]{sync}[/green]"
                elif sync == "OutOfSync":
                    sync_display = f"[yellow]{sync}[/yellow]"
                else:
                    sync_display = f"[red]{sync}[/red]"

                if health == "Healthy":
                    health_display = f"[green]{health}[/green]"
                elif health == "Progressing":
                    health_display = f"[yellow]{health}[/yellow]"
                else:
                    health_display = f"[red]{health}[/red]"

                console.print(
                    f"  {app_name}: Sync: {sync_display}, Health: {health_display}"
                )

    except Exception as e:
        console.print(f"[red]Error checking status: {e}[/red]")
        raise typer.Exit(1)


@app.command()
def teardown(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force teardown without confirmation"
    ),
    cluster_name: str = typer.Option(
        None, "--cluster", help="Cluster name to teardown"
    ),
    keep_infrastructure: bool = typer.Option(
        False,
        "--keep-infrastructure",
        help="Keep the underlying cloud infrastructure (GKE cluster, etc.) - only remove O8 platform",
    ),
):
    """Teardown Orchestr8 platform and optionally infrastructure."""
    console.print("[bold red]⚠️  Orchestr8 Teardown[/bold red]\n")

    # Check if we have Terraform-managed infrastructure
    from orchestr8.core.terraform import TerraformManager

    tf_manager = TerraformManager(console)

    # Try to detect cluster name from context if not provided
    if not cluster_name:
        try:
            result = subprocess.run(
                ["kubectl", "config", "current-context"], capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout:
                context = result.stdout.strip()
                # Extract cluster name from GKE context format: gke_PROJECT_REGION_CLUSTER
                if "gke_" in context:
                    parts = context.split("_")
                    if len(parts) >= 4:
                        cluster_name = parts[3]
                        console.print(
                            f"[cyan]Detected cluster: {cluster_name}[/cyan]\n"
                        )
        except Exception:
            pass

    # Check if infrastructure exists for this cluster
    infrastructure_exists = False
    if cluster_name:
        infra_status = tf_manager.get_infrastructure_status(cluster_name)
        infrastructure_exists = infra_status.get("provisioned", False)

    console.print("[yellow]This will remove:[/yellow]")
    console.print("  • ArgoCD and all applications")
    console.print("  • Istio service mesh")
    console.print("  • Keycloak authentication")
    console.print("  • All platform namespaces")
    console.print("  • Custom Resource Definitions (CRDs)")

    if infrastructure_exists and not keep_infrastructure:
        console.print(
            "\n[bold red]⚠️  INFRASTRUCTURE WILL ALSO BE DESTROYED:[/bold red]"
        )
        console.print("  • GKE cluster and all node pools")
        console.print("  • VPC network and subnets")
        console.print("  • Service accounts and IAM bindings")
        console.print("  • All data and persistent volumes")
        console.print(
            "\n[yellow]To keep infrastructure, use --keep-infrastructure[/yellow]"
        )
    elif infrastructure_exists and keep_infrastructure:
        console.print("\n[green]✓ Infrastructure will be preserved[/green]")
        console.print("[dim]You can redeploy O8 later with 'o8 setup'[/dim]")
    elif not infrastructure_exists and not keep_infrastructure:
        console.print(
            "\n[dim]No Terraform-managed infrastructure found for this cluster[/dim]"
        )

    console.print("")

    if not force:
        if infrastructure_exists and not keep_infrastructure:
            console.print(
                "[red]⚠️  This will permanently destroy all infrastructure![/red]"
            )
            confirm = typer.confirm(
                "Are you absolutely sure you want to destroy everything?", default=False
            )
            if not confirm:
                console.print("[yellow]Teardown cancelled[/yellow]")
                raise typer.Exit(0)

            # Double confirmation for infrastructure
            console.print(
                f"\n[red]Type the cluster name '{cluster_name}' to confirm infrastructure destruction:[/red]"
            )
            confirmation = typer.prompt("Cluster name")
            if confirmation != cluster_name:
                console.print(
                    "[yellow]Confirmation failed - teardown cancelled[/yellow]"
                )
                raise typer.Exit(0)
        else:
            confirm = typer.confirm("Continue with platform teardown?", default=False)
            if not confirm:
                console.print("[yellow]Teardown cancelled[/yellow]")
                raise typer.Exit(0)

    # Create config for orchestrator
    config = Config(
        provider=CloudProvider.LOCAL,
        cluster_name=cluster_name or "unknown",
        domain="unknown",
        github=GitHubConfig(org="unknown"),
    )

    orchestrator = Orchestrator(config, console)

    try:
        # First teardown platform components
        console.print("\n[cyan]Removing O8 platform components...[/cyan]")
        result = asyncio.run(orchestrator.teardown())

        if result["success"]:
            console.print("\n[green]✅ Platform teardown completed![/green]")

            # Handle infrastructure if needed
            if infrastructure_exists and not keep_infrastructure:
                console.print("\n[yellow]Destroying cloud infrastructure...[/yellow]")
                console.print("[dim]This may take 10-15 minutes...[/dim]")

                infra_result = asyncio.run(
                    tf_manager.destroy_infrastructure(cluster_name)
                )

                if infra_result["success"]:
                    console.print(
                        "\n[green]✅ Infrastructure destroyed successfully![/green]"
                    )
                    console.print("[dim]All cloud resources have been removed.[/dim]")
                else:
                    console.print(
                        f"\n[red]❌ Infrastructure teardown failed: {infra_result.get('error')}[/red]"
                    )
                    console.print(
                        "[yellow]Platform components were removed but infrastructure may still exist[/yellow]"
                    )
                    console.print(
                        f"[yellow]Try manually: cd ~/.orchestr8/terraform/modules/bootstrap && terraform destroy -var-file=~/.orchestr8/terraform/{cluster_name}.tfvars[/yellow]"
                    )
                    raise typer.Exit(1)
            elif keep_infrastructure:
                console.print("\n[green]✅ Infrastructure preserved[/green]")
                console.print(
                    f"[dim]You can redeploy O8 with: o8 setup --cluster {cluster_name}[/dim]"
                )
        else:
            console.print(
                f"\n[red]❌ Platform teardown failed: {result.get('error')}[/red]"
            )
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"\n[red]❌ Teardown error: {e}[/red]")
        raise typer.Exit(1)


@app.command("validate")
def validate():
    """Validate prerequisites for Orchestr8."""
    console.print("[bold cyan]🔍 Validating Prerequisites[/bold cyan]\n")

    # Check for required commands
    commands = ["kubectl", "helm", "git"]
    all_good = True

    for cmd in commands:
        import shutil

        if shutil.which(cmd):
            console.print(f"✅ {cmd}")
        else:
            console.print(f"❌ {cmd} not found")
            all_good = False

    # Check Kubernetes connection
    try:
        result = subprocess.run(
            ["kubectl", "cluster-info"], capture_output=True, text=True
        )
        if result.returncode == 0:
            console.print("✅ Kubernetes cluster connected")
        else:
            console.print("❌ Cannot connect to Kubernetes cluster")
            all_good = False
    except Exception:
        console.print("❌ kubectl command failed")
        all_good = False

    if all_good:
        console.print("\n[green]All prerequisites satisfied! ✨[/green]")
    else:
        console.print(
            "\n[red]❌ Some prerequisites are missing. Please install them first.[/red]"
        )
        raise typer.Exit(1)


# Remove old placeholder secrets commands - now using the full implementation from secrets_commands


@app.command()
def auth(
    github_org: str = typer.Option(
        None, "--github-org", "-g", help="GitHub organization"
    ),
    token: str = typer.Option(
        None, "--token", "-t", help="GitHub personal access token"
    ),
):
    """Configure GitHub authentication for ArgoCD repository access."""
    console.print("[bold cyan]🔐 GitHub Authentication[/bold cyan]\n")

    # First check if ArgoCD is installed
    console.print("[yellow]Checking platform status...[/yellow]")
    try:
        result = subprocess.run(
            ["kubectl", "get", "namespace", "argocd"], capture_output=True, text=True
        )
        if result.returncode != 0:
            console.print("\n[red]❌ ArgoCD is not installed![/red]")
            console.print(
                "[yellow]Please run 'o8 setup' first to install the platform.[/yellow]"
            )
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error checking platform status: {e}[/red]")
        raise typer.Exit(1)

    console.print("[green]✅ ArgoCD found[/green]\n")

    # Get GitHub org if not provided
    if not github_org:
        github_org = typer.prompt("GitHub organization", default="killerapp")

    # Get token if not provided
    if not token:
        console.print("[cyan]To create a Personal Access Token:[/cyan]")
        console.print("1. Go to https://github.com/settings/tokens/new")
        console.print("2. Select scope: 'repo' (Full control of private repositories)")
        console.print("3. Generate token and copy it\n")

        token = typer.prompt("GitHub personal access token", hide_input=True)

        if not token:
            console.print("[red]❌ Token is required[/red]")
            raise typer.Exit(1)

    # Validate token silently
    github_auth = GitHubDeviceFlow(console)
    if not github_auth.validate_token(token):
        console.print("[yellow]⚠️  Could not validate token[/yellow]")

    # Create minimal config
    config = Config(
        provider=CloudProvider.LOCAL,
        cluster_name="unknown",
        domain="unknown",
        github=GitHubConfig(org=github_org, token=token),
    )

    # Configure ArgoCD
    orchestrator = Orchestrator(config, console)

    try:
        result = asyncio.run(orchestrator.configure_argocd_repo())
        if result.get("created") or result.get("updated"):
            # Trigger ArgoCD refresh
            subprocess.run(
                [
                    "kubectl",
                    "-n",
                    "argocd",
                    "patch",
                    "app",
                    "orchestr8-platform",
                    "--type",
                    "merge",
                    "-p",
                    '{"metadata": {"annotations": {"argocd.argoproj.io/refresh": "normal"}}}',
                ],
                capture_output=True,
            )

            console.print(
                f"\n[green]✅ Repository configured for {result.get('url')}[/green]"
            )
            console.print("[cyan]Check ArgoCD UI at http://localhost:30080[/cyan]")
        else:
            console.print(f"\n[red]❌ Failed: {result.get('error')}[/red]")
    except Exception as e:
        console.print(f"\n[red]❌ Error: {e}[/red]")


@app.command("repos")
def configure_repositories():
    """Configure ArgoCD Helm repositories for platform dependencies."""
    console.print("[bold cyan]🔧 Configuring ArgoCD Repositories[/bold cyan]\n")

    # Create minimal config for orchestrator
    config = Config(
        provider=CloudProvider.LOCAL,
        cluster_name="unknown",
        domain="unknown",
        github=GitHubConfig(org="killerapp"),
    )

    orchestrator = Orchestrator(config, console)

    try:
        result = asyncio.run(orchestrator.configure_argocd_helm_repos())

        console.print("\n[green]✅ Repository configuration complete![/green]")
        console.print(
            f"Configured {len(result['configured_repositories'])} of {result['total_repositories']} repositories"
        )

        if result["configured_repositories"]:
            console.print("\n[cyan]Configured repositories:[/cyan]")
            for repo in result["configured_repositories"]:
                console.print(f"  • {repo}")

            console.print(
                "\n[yellow]Note:[/yellow] ArgoCD repo server was restarted to pick up new repositories"
            )
            console.print(
                "[cyan]Refresh your platform applications in ArgoCD UI[/cyan]"
            )

    except Exception as e:
        console.print(f"\n[red]❌ Repository configuration failed: {e}[/red]")
        raise typer.Exit(1)


@app.command(name="idp")
def identity_provider(
    provider: IdentityProviderType = typer.Argument(
        ..., help="Identity provider to configure (github, google, microsoft)"
    ),
    non_interactive: bool = typer.Option(
        False,
        "--non-interactive",
        "-n",
        help="Use existing secret configuration without prompting",
    ),
):
    """Configure identity providers for Keycloak SSO."""
    console.print("[bold cyan]🔐 Identity Provider Configuration[/bold cyan]\n")

    # Check if platform is installed
    console.print("[yellow]Checking platform status...[/yellow]")
    try:
        result = subprocess.run(
            ["kubectl", "get", "namespace", "platform"], capture_output=True, text=True
        )
        if result.returncode != 0:
            console.print("\n[red]❌ Platform namespace not found![/red]")
            console.print(
                "[yellow]Please run 'o8 setup' first to install the platform.[/yellow]"
            )
            raise typer.Exit(1)
    except Exception as e:
        console.print(f"\n[red]❌ Error checking platform status: {e}[/red]")
        raise typer.Exit(1)

    # Configure the identity provider
    manager = KeycloakIdentityProviderManager(console)
    success = manager.configure_provider(provider, interactive=not non_interactive)

    if success:
        console.print(
            f"\n[green]✅ {provider.value.title()} identity provider configured successfully![/green]"
        )

        # Additional instructions for making users admins
        console.print(
            f"\n[cyan]📝 To grant admin access to a {provider.value} user:[/cyan]"
        )
        console.print(f"1. Have the user log in via {provider.value.title()} first")
        console.print("2. Access Keycloak Admin Console: http://localhost:30081")
        console.print("3. Login as admin/admin123")
        console.print("4. Select 'platform' realm (top-left dropdown)")
        console.print("5. Go to Users → View all users")
        console.print(f"6. Click on the {provider.value} user")
        console.print("7. Go to 'Role Mappings' tab")
        console.print("8. Assign 'platform-admin' role")
    else:
        console.print(
            f"\n[red]❌ Failed to configure {provider.value} identity provider[/red]"
        )
        raise typer.Exit(1)


def _get_argocd_auth_token() -> str:
    """Get ArgoCD authentication token (compatible with v3)."""
    import base64

    # Get the admin password from Kubernetes secret
    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "secret",
                "argocd-initial-admin-secret",
                "-n",
                "argocd",
                "-o",
                "jsonpath={.data.password}",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            # In ArgoCD v3, the password might not exist if it was reset
            # Try to use the default or a known password
            console.print(
                "[yellow]Warning: Could not get ArgoCD initial admin secret[/yellow]"
            )
            return ""

        if not result.stdout.strip():
            console.print("[yellow]Warning: ArgoCD admin secret is empty[/yellow]")
            return ""

        # Decode the base64 password
        try:
            password = base64.b64decode(result.stdout.strip()).decode("utf-8")
        except Exception as e:
            console.print(
                f"[yellow]Warning: Could not decode ArgoCD password: {e}[/yellow]"
            )
            return ""

        # Login to ArgoCD to get JWT token
        try:
            with httpx.Client(timeout=10) as client:
                login_response = client.post(
                    "http://localhost:30080/api/v1/session",
                    json={"username": "admin", "password": password},
                )

                if login_response.status_code == 200:
                    token = login_response.json().get("token", "")
                    if not token:
                        console.print(
                            "[yellow]Warning: ArgoCD login successful but no token received[/yellow]"
                        )
                    return token
                else:
                    # Password might be wrong or using old hash format
                    console.print(
                        f"[yellow]Warning: ArgoCD login failed (HTTP {login_response.status_code})[/yellow]"
                    )
                    console.print(
                        "[yellow]You may need to reset the password: o8 argocd reset-password[/yellow]"
                    )
                    return ""

        except httpx.ConnectError:
            console.print(
                "[yellow]Warning: Could not connect to ArgoCD API at localhost:30080[/yellow]"
            )
            return ""
        except Exception as e:
            console.print(f"[yellow]Warning: ArgoCD authentication error: {e}[/yellow]")
            return ""

    except Exception as e:
        # Fallback: don't use authentication for kubectl-based commands
        console.print(
            f"[yellow]Warning: Could not authenticate with ArgoCD API: {e}[/yellow]"
        )
        return ""


@app.command("sync")
def sync_application(
    name: str = typer.Argument(..., help="Application name to sync"),
    revision: str = typer.Option(
        "HEAD", "--revision", "-r", help="Git revision to sync to"
    ),
):
    """Sync an ArgoCD application using ArgoCD API."""
    try:
        console.print(f"[cyan]🔄 Syncing application: {name}[/cyan]")

        # Use kubectl patch for now (more reliable than API calls)
        result = subprocess.run(
            [
                "kubectl",
                "patch",
                "application",
                name,
                "-n",
                "argocd",
                "--type",
                "merge",
                "-p",
                f'{{"operation":{{"initiatedBy":{{"username":"o8"}},"sync":{{"revision":"{revision}"}}}}}}',
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            console.print(f"[green]✅ Successfully triggered sync for {name}[/green]")
        else:
            console.print(f"[red]❌ Failed to sync {name}: {result.stderr}[/red]")
            raise typer.Exit(1)

    except Exception as e:
        console.print(f"[red]❌ Failed to sync {name}: {e}[/red]")
        raise typer.Exit(1)


@app.command("apps")
def list_applications():
    """List all ArgoCD applications with status."""
    try:
        # Get applications using kubectl
        result = subprocess.run(
            ["kubectl", "get", "applications", "-n", "argocd", "-o", "json"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            console.print(f"[red]❌ Failed to get applications: {result.stderr}[/red]")
            raise typer.Exit(1)

        data = json.loads(result.stdout)
        apps = data.get("items", [])

        if not apps:
            console.print("[yellow]No applications found[/yellow]")
            return

        # Create a table
        table = Table(title="ArgoCD Applications")
        table.add_column("Name", style="cyan")
        table.add_column("Sync Status", style="blue")
        table.add_column("Health Status", style="green")
        table.add_column("Project", style="dim")

        for app in apps:
            name = app["metadata"]["name"]
            sync_status = app.get("status", {}).get("sync", {}).get("status", "Unknown")
            health_status = (
                app.get("status", {}).get("health", {}).get("status", "Unknown")
            )
            project = app.get("spec", {}).get("project", "default")

            table.add_row(name, sync_status, health_status, project)

        console.print(table)

    except Exception as e:
        console.print(f"[red]❌ Failed to list applications: {e}[/red]")
        raise typer.Exit(1)


# Module management commands - imported from cli.module
# The module commands are now in a separate file for better organization
# They provide full module management capabilities:
# - list: Show all deployed modules
# - deploy: Deploy a new module
# - status: Check module status
# - logs: View module logs
# - scale: Scale module replicas
# - rollback: Rollback to previous version
# - delete: Remove a module
# Register module commands
app.add_typer(module_commands.app, name="module")

# Register branch deployment commands
app.add_typer(branch_commands.app, name="branch")

# Register ArgoCD management commands
app.add_typer(argocd_commands.app, name="argocd")

# Register secrets management commands
app.add_typer(secrets_commands.secrets, name="secrets")

# Register bootstrap commands for Kubernetes cluster provisioning
app.add_typer(bootstrap_commands.app, name="bootstrap")
# Register tenant management commands
app.add_typer(tenant_commands.app, name="tenant")
# Register Llama-Stack AI workload management commands
app.add_typer(llama_commands.app, name="llama")


# Register doctor commands for diagnostics
# Special handling for doctor command - run check by default
@app.command(name="doctor")
def doctor_command(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
    fix: bool = typer.Option(False, "--fix", help="Show how to fix issues"),
):
    """Diagnose Orchestr8 environment and prerequisites."""
    # Import and call the check function directly
    from .commands.doctor import check

    check(verbose=verbose, fix=fix)


if __name__ == "__main__":
    app()
