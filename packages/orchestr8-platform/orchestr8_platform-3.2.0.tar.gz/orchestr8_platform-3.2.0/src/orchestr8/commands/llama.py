"""Orchestr8 Llama-Stack AI workload management commands."""

import json
import subprocess
import time
from pathlib import Path
from typing import Optional, List, Dict, Any

import typer
import yaml
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.syntax import Syntax
from rich.panel import Panel

from ..core.validator import ModuleValidator

app = typer.Typer(help="Llama-Stack AI workload management commands")
console = Console()


class LlamaStackClient:
    """Client for interacting with Llama-Stack deployments."""
    
    def __init__(self, base_url: str = "http://llama-stack.llama-stack.svc.cluster.local:8080"):
        self.base_url = base_url
        
    def health_check(self) -> bool:
        """Check if Llama-Stack is healthy."""
        try:
            result = subprocess.run([
                "kubectl", "get", "pods", "-n", "llama-stack", 
                "-l", "app.kubernetes.io/name=llama-stack",
                "--no-headers"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return False
                
            pods = result.stdout.strip().split('\n')
            if not pods or pods == ['']:
                return False
                
            # Check if any pod is running
            for pod in pods:
                if 'Running' in pod:
                    return True
            return False
            
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
            return False
            
    def get_models(self) -> List[Dict[str, Any]]:
        """Get list of available models."""
        try:
            # Get models from configmap
            result = subprocess.run([
                "kubectl", "get", "configmap", "llama-stack-config",
                "-n", "llama-stack", "-o", "yaml"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return []
                
            config = yaml.safe_load(result.stdout)
            server_config = yaml.safe_load(config['data']['server.yaml'])
            return server_config.get('models', [])
            
        except Exception:
            return []
            
    def get_providers(self) -> Dict[str, Any]:
        """Get configured providers."""
        try:
            result = subprocess.run([
                "kubectl", "get", "configmap", "llama-stack-config",
                "-n", "llama-stack", "-o", "yaml"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode != 0:
                return {}
                
            config = yaml.safe_load(result.stdout)
            server_config = yaml.safe_load(config['data']['server.yaml'])
            return server_config.get('providers', {})
            
        except Exception:
            return {}


@app.command("init")
def init_ai_workload(
    name: str = typer.Argument(..., help="AI workload name"),
    template: str = typer.Option("rag", "--template", "-t", help="Workload template: rag, agent, inference, custom"),
    path: Path = typer.Option(Path.cwd(), "--path", "-p", help="Directory to create workload"),
    provider: str = typer.Option("openai", "--provider", help="AI provider: openai, anthropic, groq, local"),
):
    """Initialize a new AI workload module."""
    
    workload_path = path / name
    
    if workload_path.exists():
        console.print(f"[red]Error:[/red] Directory {workload_path} already exists")
        raise typer.Exit(1)
        
    console.print(f"[cyan]Creating AI workload:[/cyan] {name}")
    console.print(f"[dim]Template:[/dim] {template}")
    console.print(f"[dim]Provider:[/dim] {provider}")
    
    templates = {
        "rag": _create_rag_template,
        "agent": _create_agent_template,
        "inference": _create_inference_template,
        "custom": _create_custom_template
    }
    
    if template not in templates:
        console.print(f"[red]Error:[/red] Unknown template: {template}")
        console.print(f"[yellow]Available templates:[/yellow] {', '.join(templates.keys())}")
        raise typer.Exit(1)
        
    # Create workload structure
    workload_path.mkdir(parents=True)
    (workload_path / ".o8").mkdir()
    (workload_path / "base").mkdir()
    (workload_path / "overlays").mkdir()
    (workload_path / "tests").mkdir()
    
    # Generate template
    templates[template](name, workload_path, provider)
    
    console.print(f"[green]✓[/green] AI workload {name} created at {workload_path}")
    console.print(f"[yellow]Next steps:[/yellow]")
    console.print(f"  1. cd {workload_path}")
    console.print(f"  2. o8 llama validate")
    console.print(f"  3. o8 llama deploy --environment dev")


@app.command("validate")
def validate_ai_workload(
    path: Path = typer.Argument(Path.cwd(), help="Path to AI workload directory"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed validation"),
):
    """Validate an AI workload configuration."""
    
    console.print(f"[cyan]Validating AI workload at:[/cyan] {path}")
    
    # Check if it's a valid AI workload
    spec_file = path / ".o8" / "module.yaml"
    if not spec_file.exists():
        console.print("[red]Error:[/red] No .o8/module.yaml found")
        console.print("[yellow]Tip:[/yellow] Initialize with: [cyan]o8 llama init[/cyan]")
        raise typer.Exit(1)
        
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Validating AI workload...", total=8)
        
        errors = []
        warnings = []
        
        # 1. Parse YAML
        progress.update(task, description="Parsing configuration...")
        try:
            with open(spec_file) as f:
                spec = yaml.safe_load(f)
        except Exception as e:
            errors.append(f"Failed to parse YAML: {e}")
            spec = {}
        progress.advance(task)
        
        # 2. Check AI-specific fields
        progress.update(task, description="Checking AI configuration...")
        ai_config = spec.get("spec", {}).get("aiSpecific", {})
        if not ai_config:
            warnings.append("No aiSpecific configuration found")
        else:
            if not ai_config.get("providers"):
                warnings.append("No providers configured")
            if not ai_config.get("capabilities"):
                warnings.append("No capabilities specified")
        progress.advance(task)
        
        # 3. Check GPU requirements
        progress.update(task, description="Validating GPU requirements...")
        compute = spec.get("spec", {}).get("requirements", {}).get("compute", {})
        if compute.get("gpu", {}).get("enabled", False):
            progress.update(task, description="Checking GPU nodes...")
            gpu_nodes = _check_gpu_nodes()
            if not gpu_nodes:
                warnings.append("No GPU nodes detected in cluster")
            else:
                console.print(f"[dim]Found {len(gpu_nodes)} GPU nodes[/dim]")
        progress.advance(task)
        
        # 4. Check storage requirements
        progress.update(task, description="Validating storage...")
        storage = spec.get("spec", {}).get("requirements", {}).get("storage", {})
        total_storage = 0
        for storage_type, config in storage.items():
            if isinstance(config, dict) and "size" in config:
                size_str = config["size"]
                # Simple size parsing (assumes Gi units)
                if size_str.endswith("Gi"):
                    total_storage += int(size_str[:-2])
        
        if total_storage > 0:
            console.print(f"[dim]Total storage required: {total_storage}Gi[/dim]")
        progress.advance(task)
        
        # 5. Check provider secrets
        progress.update(task, description="Checking provider secrets...")
        providers = ai_config.get("providers", {})
        for provider_type, provider_list in providers.items():
            if provider_list and any(p in provider_list for p in ["openai", "anthropic", "groq"]):
                secret_check = _check_secret_exists("llama-stack-api-keys")
                if not secret_check:
                    warnings.append(f"API key secrets not found for {provider_type}")
        progress.advance(task)
        
        # 6. Validate base manifests
        progress.update(task, description="Checking Kubernetes manifests...")
        base_dir = path / "base"
        if base_dir.exists():
            kustomization_file = base_dir / "kustomization.yaml"
            if not kustomization_file.exists():
                errors.append("Missing base/kustomization.yaml")
            else:
                try:
                    with open(kustomization_file) as f:
                        kustomization = yaml.safe_load(f)
                    resources = kustomization.get("resources", [])
                    if not resources:
                        warnings.append("No resources defined in kustomization")
                except Exception as e:
                    errors.append(f"Invalid kustomization.yaml: {e}")
        progress.advance(task)
        
        # 7. Test kustomize build
        progress.update(task, description="Testing kustomize build...")
        try:
            result = subprocess.run([
                "kustomize", "build", str(base_dir)
            ], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                errors.append(f"Kustomize build failed: {result.stderr}")
        except subprocess.TimeoutExpired:
            warnings.append("Kustomize build timed out")
        except FileNotFoundError:
            warnings.append("kustomize not found in PATH")
        progress.advance(task)
        
        # 8. Final validation
        progress.update(task, description="Completing validation...")
        progress.advance(task)
    
    # Show results
    if errors:
        console.print("\n[red]❌ Validation failed with errors:[/red]")
        for error in errors:
            console.print(f"  • {error}")
            
    if warnings:
        console.print("\n[yellow]⚠️  Validation warnings:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")
            
    if not errors and not warnings:
        console.print("\n[green]✅ AI workload validation passed![/green]")
    elif not errors:
        console.print("\n[green]✅ AI workload validation passed with warnings[/green]")
    else:
        raise typer.Exit(1)


@app.command("deploy")
def deploy_ai_workload(
    path: Path = typer.Argument(Path.cwd(), help="AI workload path"),
    environment: str = typer.Option("dev", "--env", "-e", help="Target environment"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be deployed"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for deployment to complete"),
):
    """Deploy an AI workload to the cluster."""
    
    console.print(f"[cyan]Deploying AI workload from:[/cyan] {path}")
    console.print(f"[dim]Environment:[/dim] {environment}")
    
    # Validate first
    console.print("[dim]Running validation...[/dim]")
    try:
        validate_ai_workload(path, verbose=False)
    except typer.Exit:
        console.print("[red]Validation failed. Fix errors before deploying.[/red]")
        raise
    
    # Build manifests
    base_dir = path / "base"
    if not base_dir.exists():
        console.print("[red]Error:[/red] No base directory found")
        raise typer.Exit(1)
        
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # 1. Build kustomize
        task = progress.add_task("Building manifests...", total=4)
        try:
            result = subprocess.run([
                "kustomize", "build", str(base_dir)
            ], capture_output=True, text=True, timeout=60)
            
            if result.returncode != 0:
                console.print(f"[red]Kustomize build failed:[/red] {result.stderr}")
                raise typer.Exit(1)
                
            manifests = result.stdout
            
        except subprocess.TimeoutExpired:
            console.print("[red]Kustomize build timed out[/red]")
            raise typer.Exit(1)
        except FileNotFoundError:
            console.print("[red]kustomize not found. Please install kustomize.[/red]")
            raise typer.Exit(1)
            
        progress.advance(task)
        
        # 2. Show dry run if requested
        if dry_run:
            progress.update(task, description="Showing deployment preview...")
            console.print("\n[yellow]Deployment preview:[/yellow]")
            syntax = Syntax(manifests, "yaml", theme="monokai", line_numbers=True)
            console.print(Panel(syntax, title="Kubernetes Manifests"))
            progress.advance(task)
            return
            
        # 3. Apply manifests
        progress.update(task, description="Applying to cluster...")
        try:
            result = subprocess.run([
                "kubectl", "apply", "-f", "-"
            ], input=manifests, capture_output=True, text=True, timeout=120)
            
            if result.returncode != 0:
                console.print(f"[red]Deployment failed:[/red] {result.stderr}")
                raise typer.Exit(1)
                
            console.print(f"[green]Applied manifests:[/green]")
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    console.print(f"  • {line}")
                    
        except subprocess.TimeoutExpired:
            console.print("[red]Deployment timed out[/red]")
            raise typer.Exit(1)
            
        progress.advance(task)
        
        # 4. Wait for deployment
        if wait:
            progress.update(task, description="Waiting for deployment...")
            namespace = _get_namespace_from_manifests(manifests)
            if namespace:
                _wait_for_deployment(namespace, timeout=300)
            progress.advance(task)
        else:
            progress.advance(task)
    
    console.print("\n[green]✅ AI workload deployed successfully![/green]")
    console.print(f"[yellow]Check status with:[/yellow] o8 llama status")


@app.command("status")
def ai_workload_status(
    namespace: str = typer.Option("llama-stack", "--namespace", "-n", help="Kubernetes namespace"),
    watch: bool = typer.Option(False, "--watch", "-w", help="Watch for changes"),
):
    """Check the status of AI workloads."""
    
    console.print(f"[cyan]Checking AI workload status in namespace:[/cyan] {namespace}")
    
    # Get basic pod status
    try:
        result = subprocess.run([
            "kubectl", "get", "pods", "-n", namespace,
            "-l", "category=ai-workload",
            "-o", "wide"
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            console.print(f"[red]Failed to get pod status:[/red] {result.stderr}")
            raise typer.Exit(1)
            
        console.print("\n[yellow]AI Workload Pods:[/yellow]")
        console.print(result.stdout)
        
    except subprocess.TimeoutExpired:
        console.print("[red]Command timed out[/red]")
        raise typer.Exit(1)
    
    # Check Llama-Stack health
    client = LlamaStackClient()
    console.print(f"\n[cyan]Llama-Stack Health:[/cyan]")
    
    if client.health_check():
        console.print("[green]✅ Healthy[/green]")
        
        # Show models
        models = client.get_models()
        if models:
            table = Table(title="Available Models")
            table.add_column("Model ID")
            table.add_column("Provider")
            table.add_column("Type")
            
            for model in models:
                table.add_row(
                    model.get("model_id", "N/A"),
                    model.get("provider_id", "N/A"),
                    model.get("model_type", "N/A")
                )
            console.print(table)
            
        # Show providers
        providers = client.get_providers()
        if providers:
            console.print(f"\n[yellow]Configured Providers:[/yellow]")
            for provider_type, provider_list in providers.items():
                console.print(f"  • {provider_type}: {len(provider_list)} configured")
                
    else:
        console.print("[red]❌ Unhealthy[/red]")
        console.print("[yellow]Check logs with:[/yellow] kubectl logs -n llama-stack -l app.kubernetes.io/name=llama-stack")
    
    if watch:
        console.print("\n[dim]Watching for changes... (Ctrl+C to exit)[/dim]")
        try:
            subprocess.run([
                "kubectl", "get", "pods", "-n", namespace,
                "-l", "category=ai-workload", "-w"
            ])
        except KeyboardInterrupt:
            console.print("\n[dim]Stopped watching[/dim]")


@app.command("logs")
def ai_workload_logs(
    namespace: str = typer.Option("llama-stack", "--namespace", "-n", help="Kubernetes namespace"),
    follow: bool = typer.Option(False, "--follow", "-f", help="Follow log output"),
    tail: int = typer.Option(100, "--tail", help="Number of lines to show"),
):
    """View AI workload logs."""
    
    console.print(f"[cyan]Fetching logs from namespace:[/cyan] {namespace}")
    
    cmd = [
        "kubectl", "logs", "-n", namespace,
        "-l", "app.kubernetes.io/name=llama-stack",
        "--tail", str(tail)
    ]
    
    if follow:
        cmd.append("-f")
        
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        if follow:
            console.print("\n[dim]Stopped following logs[/dim]")


@app.command("providers")
def list_providers(
    namespace: str = typer.Option("llama-stack", "--namespace", "-n", help="Kubernetes namespace"),
    provider_type: Optional[str] = typer.Option(None, "--type", "-t", help="Filter by provider type"),
):
    """List and manage AI providers."""
    
    console.print(f"[cyan]AI Providers in namespace:[/cyan] {namespace}")
    
    client = LlamaStackClient()
    providers = client.get_providers()
    
    if not providers:
        console.print("[yellow]No providers configured[/yellow]")
        return
        
    for ptype, provider_list in providers.items():
        if provider_type and ptype != provider_type:
            continue
            
        console.print(f"\n[yellow]{ptype.title()} Providers:[/yellow]")
        
        if not provider_list:
            console.print("  [dim]None configured[/dim]")
            continue
            
        table = Table()
        table.add_column("Provider ID")
        table.add_column("Type") 
        table.add_column("Configuration")
        
        for provider in provider_list:
            config_summary = []
            config = provider.get("config", {})
            
            for key in ["url", "host", "region", "database"]:
                if key in config:
                    config_summary.append(f"{key}: {config[key]}")
                    
            table.add_row(
                provider.get("provider_id", "N/A"),
                provider.get("provider_type", "N/A"),
                ", ".join(config_summary) if config_summary else "default"
            )
            
        console.print(table)


# Helper functions

def _create_rag_template(name: str, path: Path, provider: str):
    """Create RAG application template."""
    # Implementation would create RAG-specific configuration
    pass

def _create_agent_template(name: str, path: Path, provider: str):
    """Create agentic workflow template."""
    # Implementation would create agent-specific configuration  
    pass

def _create_inference_template(name: str, path: Path, provider: str):
    """Create inference service template."""
    # Implementation would create inference-specific configuration
    pass

def _create_custom_template(name: str, path: Path, provider: str):
    """Create custom AI workload template."""
    # Implementation would create generic AI workload template
    pass

def _check_gpu_nodes() -> List[str]:
    """Check for GPU-enabled nodes in the cluster."""
    try:
        result = subprocess.run([
            "kubectl", "get", "nodes", 
            "-l", "nvidia.com/gpu.present=true",
            "--no-headers", "-o", "custom-columns=NAME:.metadata.name"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            return result.stdout.strip().split('\n') if result.stdout.strip() else []
        return []
        
    except Exception:
        return []

def _check_secret_exists(secret_name: str, namespace: str = "llama-stack") -> bool:
    """Check if a secret exists."""
    try:
        result = subprocess.run([
            "kubectl", "get", "secret", secret_name, "-n", namespace
        ], capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except Exception:
        return False

def _get_namespace_from_manifests(manifests: str) -> Optional[str]:
    """Extract namespace from manifests."""
    try:
        for doc in yaml.safe_load_all(manifests):
            if doc and doc.get("metadata", {}).get("namespace"):
                return doc["metadata"]["namespace"]
        return None
    except Exception:
        return None

def _wait_for_deployment(namespace: str, timeout: int = 300):
    """Wait for deployment to be ready."""
    try:
        subprocess.run([
            "kubectl", "wait", "--for=condition=ready", "pod",
            "-n", namespace, "-l", "category=ai-workload",
            f"--timeout={timeout}s"
        ], timeout=timeout + 10)
    except subprocess.TimeoutExpired:
        console.print("[yellow]Deployment is taking longer than expected...[/yellow]")
    except Exception:
        pass