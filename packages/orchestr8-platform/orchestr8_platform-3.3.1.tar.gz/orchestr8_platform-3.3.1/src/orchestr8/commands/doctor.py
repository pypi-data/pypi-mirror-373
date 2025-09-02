"""Orchestr8 Doctor - Diagnose and check prerequisites."""

import subprocess
import shutil
import platform
from typing import Dict, Any, List
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()
app = typer.Typer(help="Diagnose Orchestr8 environment and prerequisites")


def check_command(cmd: str) -> Dict[str, Any]:
    """Check if a command exists and get its version."""
    path = shutil.which(cmd)
    if not path:
        return {"installed": False, "path": None, "version": None}

    # Try to get version
    version = None
    try:
        # Different commands have different version flags
        version_flags = {
            "terraform": ["version", "-json"],
            "gcloud": ["version", "--format=json"],
            "kubectl": ["version", "--client", "--short"],
            "helm": ["version", "--short"],
            "docker": ["--version"],
            "git": ["--version"],
        }

        flag = version_flags.get(cmd, ["--version"])
        result = subprocess.run([cmd] + flag, capture_output=True, text=True, timeout=5)

        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
    except Exception:
        pass

    return {"installed": True, "path": path, "version": version}


def check_gcp_auth() -> Dict[str, Any]:
    """Check GCP authentication status."""
    try:
        result = subprocess.run(
            ["gcloud", "auth", "list", "--format=json"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            import json

            accounts = json.loads(result.stdout)
            if accounts:
                active = next(
                    (a for a in accounts if a.get("status") == "ACTIVE"), None
                )
                return {
                    "authenticated": True,
                    "account": active.get("account") if active else None,
                    "accounts": len(accounts),
                }
    except Exception:
        pass

    return {"authenticated": False, "account": None}


def check_aws_auth() -> Dict[str, Any]:
    """Check AWS authentication status."""
    try:
        result = subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            import json

            identity = json.loads(result.stdout)
            return {
                "authenticated": True,
                "account": identity.get("Account"),
                "user": identity.get("Arn", "").split("/")[-1],
            }
    except Exception:
        pass

    return {"authenticated": False, "account": None}


def check_kubernetes() -> Dict[str, Any]:
    """Check Kubernetes cluster connection."""
    try:
        # Get current context
        context_result = subprocess.run(
            ["kubectl", "config", "current-context"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        current_context = (
            context_result.stdout.strip() if context_result.returncode == 0 else None
        )

        # Check cluster info
        cluster_result = subprocess.run(
            ["kubectl", "cluster-info"], capture_output=True, text=True, timeout=5
        )

        connected = cluster_result.returncode == 0

        return {
            "connected": connected,
            "context": current_context,
            "cluster_info": cluster_result.stdout.strip() if connected else None,
        }
    except Exception:
        pass

    return {"connected": False, "context": None}


def check_docker() -> Dict[str, Any]:
    """Check Docker status."""
    try:
        result = subprocess.run(
            ["docker", "info", "--format", "json"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            import json

            info = json.loads(result.stdout)
            return {
                "running": True,
                "version": info.get("ServerVersion"),
                "os": info.get("OperatingSystem"),
                "kubernetes": "kubernetes" in info.get("Name", "").lower()
                or "desktop" in info.get("OperatingSystem", "").lower(),
            }
    except Exception:
        pass

    return {"running": False}


def check_ai_readiness() -> Dict[str, Any]:
    """Check AI/GPU readiness in the cluster."""
    try:
        # Check for GPU nodes
        gpu_result = subprocess.run([
            "kubectl", "get", "nodes", 
            "-l", "nvidia.com/gpu.present=true",
            "--no-headers", "-o", "custom-columns=NAME:.metadata.name"
        ], capture_output=True, text=True, timeout=10)
        
        gpu_nodes = []
        if gpu_result.returncode == 0 and gpu_result.stdout.strip():
            gpu_nodes = gpu_result.stdout.strip().split('\n')
            
        # Check for Llama-Stack deployment (both regular and local)
        llama_result = subprocess.run([
            "kubectl", "get", "deployment", "llama-stack", "-n", "llama-stack",
            "--no-headers", "-o", "custom-columns=NAME:.metadata.name"
        ], capture_output=True, text=True, timeout=10)
        
        llama_deployed = llama_result.returncode == 0 and "llama-stack" in llama_result.stdout
        
        # Check for local Ollama (for Docker Desktop development)
        ollama_available = False
        try:
            ollama_result = subprocess.run([
                "curl", "-s", "--connect-timeout", "3", "http://localhost:11434/api/tags"
            ], capture_output=True, text=True, timeout=5)
            ollama_available = ollama_result.returncode == 0
        except Exception:
            # If curl is not available, try with python's urllib
            try:
                import urllib.request
                urllib.request.urlopen("http://localhost:11434/api/tags", timeout=3)
                ollama_available = True
            except Exception:
                ollama_available = False
        
        # Check for AI secrets
        secrets_result = subprocess.run([
            "kubectl", "get", "secret", "llama-stack-api-keys", "-n", "llama-stack"
        ], capture_output=True, text=True, timeout=10)
        
        secrets_configured = secrets_result.returncode == 0
        
        # Check storage classes for AI workloads
        sc_result = subprocess.run([
            "kubectl", "get", "storageclass", "--no-headers", 
            "-o", "custom-columns=NAME:.metadata.name,PROVISIONER:.provisioner"
        ], capture_output=True, text=True, timeout=10)
        
        fast_storage = False
        if sc_result.returncode == 0:
            for line in sc_result.stdout.split('\n'):
                if 'fast' in line.lower() or 'ssd' in line.lower():
                    fast_storage = True
                    break
                    
        return {
            "gpu_nodes": gpu_nodes,
            "llama_deployed": llama_deployed,
            "ollama_available": ollama_available,
            "secrets_configured": secrets_configured,
            "fast_storage": fast_storage,
            "ai_ready": (len(gpu_nodes) > 0 and llama_deployed and secrets_configured) or 
                       (ollama_available and llama_deployed)  # Local dev with Ollama
        }
        
    except Exception:
        return {
            "gpu_nodes": [],
            "llama_deployed": False,
            "secrets_configured": False,
            "fast_storage": False,
            "ai_ready": False
        }


@app.command()
def check(
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Show detailed information"
    ),
    fix: bool = typer.Option(False, "--fix", help="Show how to fix issues"),
):
    """Check all Orchestr8 prerequisites and environment."""

    console.print(
        Panel.fit(
            "[bold cyan]Orchestr8 Doctor[/bold cyan]\n"
            "Checking your environment for Orchestr8 platform",
            border_style="cyan",
        )
    )

    # System Information
    console.print("\n[bold yellow]System Information[/bold yellow]")
    sys_table = Table(show_header=False, box=None)
    sys_table.add_row("OS:", platform.system())
    sys_table.add_row("Version:", platform.version())
    sys_table.add_row("Python:", platform.python_version())
    sys_table.add_row("Architecture:", platform.machine())
    console.print(sys_table)

    # Required Tools
    console.print("\n[bold yellow]Required Tools[/bold yellow]")
    tools = {
        "kubectl": {"required": True, "purpose": "Kubernetes management"},
        "helm": {"required": True, "purpose": "Package management"},
        "git": {"required": True, "purpose": "Version control"},
        "docker": {"required": False, "purpose": "Container runtime (for local)"},
        "terraform": {"required": False, "purpose": "Infrastructure provisioning"},
        "gcloud": {"required": False, "purpose": "GCP management"},
        "aws": {"required": False, "purpose": "AWS management"},
    }

    tools_table = Table(show_header=True)
    tools_table.add_column("Tool", style="cyan")
    tools_table.add_column("Status", style="green")
    tools_table.add_column("Version")
    tools_table.add_column("Purpose", style="dim")

    missing_required = []
    missing_optional = []

    for tool, info in tools.items():
        status = check_command(tool)

        if status["installed"]:
            status_icon = "✅"
            status_text = "Installed"
            version = status["version"] or "Unknown"
        else:
            if info["required"]:
                status_icon = "❌"
                status_text = "Missing"
                missing_required.append(tool)
            else:
                status_icon = "⚠️"
                status_text = "Not found"
                missing_optional.append(tool)
            version = "-"

        tools_table.add_row(
            f"{status_icon} {tool}",
            status_text,
            version[:40] if version != "-" else version,
            info["purpose"],
        )

    console.print(tools_table)

    # Kubernetes Status
    console.print("\n[bold yellow]Kubernetes Status[/bold yellow]")
    k8s_status = check_kubernetes()

    if k8s_status["connected"]:
        console.print(
            f"✅ Connected to cluster: [green]{k8s_status['context']}[/green]"
        )
        if verbose and k8s_status["cluster_info"]:
            console.print(f"   {k8s_status['cluster_info'][:100]}")
    else:
        console.print("❌ Not connected to any Kubernetes cluster")

    # Docker Status (for local development)
    console.print("\n[bold yellow]Docker Status[/bold yellow]")
    docker_status = check_docker()

    if docker_status["running"]:
        console.print("✅ Docker is running")
        if docker_status.get("kubernetes"):
            console.print("   [green]Kubernetes support detected[/green]")
    else:
        console.print("⚠️ Docker not running or not installed")

    # Cloud Provider Authentication
    console.print("\n[bold yellow]Cloud Provider Authentication[/bold yellow]")

    # GCP
    if check_command("gcloud")["installed"]:
        gcp_auth = check_gcp_auth()
        if gcp_auth["authenticated"]:
            console.print(
                f"✅ GCP: Authenticated as [green]{gcp_auth['account']}[/green]"
            )
        else:
            console.print("⚠️ GCP: Not authenticated (run: gcloud auth login)")
    else:
        console.print("⚠️ GCP: gcloud not installed")

    # AWS
    if check_command("aws")["installed"]:
        aws_auth = check_aws_auth()
        if aws_auth["authenticated"]:
            console.print(f"✅ AWS: Authenticated as [green]{aws_auth['user']}[/green]")
        else:
            console.print("⚠️ AWS: Not authenticated (configure with: aws configure)")
    else:
        console.print("⚠️ AWS: AWS CLI not installed")

    # AI/GPU Readiness
    console.print("\n[bold yellow]AI/GPU Readiness[/bold yellow]")
    ai_status = check_ai_readiness()
    
    if ai_status["ai_ready"]:
        console.print("✅ AI platform ready for workloads")
    else:
        console.print("⚠️ AI platform not fully configured")
        
    # GPU nodes
    if ai_status["gpu_nodes"]:
        console.print(f"✅ GPU nodes: {len(ai_status['gpu_nodes'])} available")
        if verbose:
            for node in ai_status["gpu_nodes"]:
                console.print(f"   • {node}")
    else:
        console.print("⚠️ No GPU nodes detected")
        
    # Llama-Stack deployment
    if ai_status["llama_deployed"]:
        console.print("✅ Llama-Stack deployed and running")
    else:
        console.print("⚠️ Llama-Stack not deployed (deploy with: o8 setup --provider local)")
        
    # Ollama availability (for local development)  
    if ai_status["ollama_available"]:
        console.print("✅ Ollama available on localhost:11434")
    else:
        console.print("⚠️ Ollama not detected (install from https://ollama.ai)")
        
    # AI secrets
    if ai_status["secrets_configured"]:
        console.print("✅ AI API secrets configured")
    else:
        console.print("⚠️ AI API secrets not configured")
        
    # Fast storage
    if ai_status["fast_storage"]:
        console.print("✅ Fast storage classes available for AI workloads")
    else:
        console.print("⚠️ No fast storage classes detected")

    # Orchestr8 Configuration
    console.print("\n[bold yellow]Orchestr8 Configuration[/bold yellow]")
    o8_dir = Path.home() / ".orchestr8"

    if o8_dir.exists():
        console.print(f"✅ Orchestr8 directory exists: {o8_dir}")

        # Check for terraform state
        tf_state = o8_dir / "terraform" / "terraform.tfstate"
        if tf_state.exists():
            console.print("   📦 Terraform state found")

        # Check for bootstrap config
        bootstrap_json = o8_dir / "bootstrap.json"
        if bootstrap_json.exists():
            console.print("   📋 Bootstrap configuration found")
    else:
        console.print(f"⚠️ Orchestr8 directory not found: {o8_dir}")

    # Summary and Recommendations
    console.print("\n" + "=" * 50)

    if not missing_required and not missing_optional:
        console.print("\n[green]✅ All prerequisites satisfied![/green]")
        console.print("You're ready to use Orchestr8!")
    else:
        if missing_required:
            console.print(
                f"\n[red]❌ Missing required tools: {', '.join(missing_required)}[/red]"
            )

        if missing_optional:
            console.print(
                f"\n[yellow]⚠️ Missing optional tools: {', '.join(missing_optional)}[/yellow]"
            )

        if fix:
            console.print("\n[cyan]📝 How to fix:[/cyan]")

            fixes = {
                "kubectl": {
                    "Windows": "choco install kubernetes-cli",
                    "Darwin": "brew install kubectl",
                    "Linux": "curl -LO https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl",
                },
                "helm": {
                    "Windows": "choco install kubernetes-helm",
                    "Darwin": "brew install helm",
                    "Linux": "curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash",
                },
                "terraform": {
                    "Windows": "choco install terraform",
                    "Darwin": "brew install terraform",
                    "Linux": "wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg",
                },
                "gcloud": {
                    "Windows": "Download from: https://cloud.google.com/sdk/docs/install",
                    "Darwin": "brew install google-cloud-sdk",
                    "Linux": "curl https://sdk.cloud.google.com | bash",
                },
                "docker": {
                    "Windows": "Download Docker Desktop: https://www.docker.com/products/docker-desktop",
                    "Darwin": "brew install --cask docker",
                    "Linux": "curl -fsSL https://get.docker.com | sh",
                },
                "aws": {
                    "Windows": "choco install awscli",
                    "Darwin": "brew install awscli",
                    "Linux": "pip install awscli",
                },
            }

            current_os = platform.system()

            for tool in missing_required + missing_optional:
                if tool in fixes and current_os in fixes[tool]:
                    console.print(f"\n{tool}:")
                    console.print(f"  {fixes[tool][current_os]}")

    # Quick start
    console.print("\n[bold cyan]Quick Start Commands:[/bold cyan]")
    console.print("1. Local development:  [yellow]o8 setup --provider local[/yellow]")
    console.print(
        "2. GCP with infra:     [yellow]o8 setup --provider gcp --provision-infrastructure --gcp-project-id PROJECT[/yellow]"
    )
    console.print("3. Check status:       [yellow]o8 status[/yellow]")


if __name__ == "__main__":
    app()
