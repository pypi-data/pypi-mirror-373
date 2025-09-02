"""Orchestr8 Llama-Stack AI workload management commands."""

import json
import os
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
from llama_stack_client import LlamaStackClient as LlamaStackSDK

from ..core.validator import ModuleValidator

app = typer.Typer(help="Llama-Stack AI workload management commands")
console = Console()


class LlamaStackClient:
    """Enhanced client for interacting with Llama-Stack deployments using both SDK and kubectl."""
    
    def __init__(self, base_url: str = None, api_key: Optional[str] = None):
        # Auto-detect local vs cluster deployment
        if base_url is None:
            base_url = self._detect_base_url()
        self.base_url = base_url
        self.api_key = api_key or os.getenv("LLAMA_STACK_API_KEY")
        
        # Initialize the official Llama Stack SDK client
        try:
            self.sdk_client = LlamaStackSDK(
                base_url=base_url,
                api_key=self.api_key
            )
        except Exception as e:
            console.print(f"[yellow]Warning: Could not initialize SDK client: {e}[/yellow]")
            self.sdk_client = None
        
    def _detect_base_url(self) -> str:
        """Detect the best available Llama Stack URL."""
        # Priority order:
        # 1. Local NodePort (Docker Desktop) if Llama Stack is deployed
        # 2. Cluster service if Llama Stack is deployed
        # 3. Default cluster service (will fail gracefully)
        
        try:
            # Check if Llama Stack is deployed in the cluster
            result = subprocess.run([
                "kubectl", "get", "service", "llama-stack", "-n", "llama-stack", 
                "--no-headers", "-o", "custom-columns=TYPE:.spec.type,PORT:.spec.ports[0].nodePort"
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if lines and lines[0]:
                    service_type, node_port = lines[0].split()
                    if service_type == "NodePort" and node_port != "<none>":
                        # Try NodePort first (for local development)
                        return f"http://localhost:{node_port}"
                    else:
                        # Use cluster service
                        return "http://llama-stack.llama-stack.svc.cluster.local:8080"
        except Exception:
            pass
            
        # Default to cluster service URL (commands will show helpful error if not available)
        return "http://llama-stack.llama-stack.svc.cluster.local:8080"

    def health_check(self) -> bool:
        """Check if Llama-Stack is healthy using SDK first, fallback to kubectl."""
        # Try SDK health check first
        if self.sdk_client:
            try:
                # Use the inspect endpoint to check health
                response = self.sdk_client.inspect.list_routes()
                return response is not None
            except Exception:
                pass
        
        # Fallback to kubectl-based health check
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
        """Get list of available models using SDK first, fallback to kubectl."""
        # Try SDK first
        if self.sdk_client:
            try:
                models_response = self.sdk_client.models.list()
                return [model.model_dump() for model in models_response]
            except Exception as e:
                console.print(f"[dim]SDK models call failed: {e}, falling back to kubectl[/dim]")
        
        # Fallback to kubectl-based approach
        try:
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
        """Get configured providers using SDK first, fallback to kubectl."""
        # Try SDK first
        if self.sdk_client:
            try:
                providers_response = self.sdk_client.providers.list()
                # Convert to dict format expected by the UI
                providers_dict = {}
                for provider in providers_response:
                    provider_data = provider.model_dump()
                    provider_type = provider_data.get('provider_type', 'unknown')
                    if provider_type not in providers_dict:
                        providers_dict[provider_type] = []
                    providers_dict[provider_type].append(provider_data)
                return providers_dict
            except Exception as e:
                console.print(f"[dim]SDK providers call failed: {e}, falling back to kubectl[/dim]")
        
        # Fallback to kubectl-based approach
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
    
    def get_vector_dbs(self) -> List[Dict[str, Any]]:
        """Get list of available vector databases."""
        if self.sdk_client:
            try:
                vector_dbs = self.sdk_client.vector_dbs.list()
                return [vdb.model_dump() for vdb in vector_dbs]
            except Exception as e:
                console.print(f"[dim]SDK vector_dbs call failed: {e}[/dim]")
        return []
    
    def run_inference(self, model: str, messages: List[Dict[str, str]]) -> Optional[str]:
        """Run inference using the SDK."""
        if not self.sdk_client:
            return None
            
        try:
            response = self.sdk_client.inference.chat_completion(
                model=model,
                messages=messages
            )
            return response.choices[0].message.content if response.choices else None
        except Exception as e:
            console.print(f"[red]Inference failed: {e}[/red]")
            return None


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


@app.command("inference")
def run_inference(
    message: str = typer.Argument(..., help="Message to send to the model"),
    model: Optional[str] = typer.Option(None, "--model", "-m", help="Model to use for inference"),
    base_url: str = typer.Option(None, "--url", help="Llama-Stack URL (auto-detected if not provided)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key for authentication"),
):
    """Run inference against Llama-Stack using the SDK."""
    
    client = LlamaStackClient(base_url=base_url, api_key=api_key)
    
    # Check if Llama Stack is actually available first
    if not client.health_check():
        console.print("[red]❌ Llama Stack is not available[/red]")
        console.print(f"[dim]Tried to connect to: {client.base_url}[/dim]")
        console.print("[yellow]💡 To deploy Llama Stack:[/yellow]")
        console.print("   [cyan]o8 setup --provider local[/cyan]  # For local development")
        console.print("   [cyan]o8 llama deploy[/cyan]           # Deploy to existing cluster")
        return
    
    console.print(f"[cyan]Running inference:[/cyan] {message[:50]}{'...' if len(message) > 50 else ''}")
    console.print(f"[dim]Using Llama Stack at: {client.base_url}[/dim]")
    
    if not client.sdk_client:
        console.print("[red]Error: Could not initialize SDK client. Check connection and API key.[/red]")
        raise typer.Exit(1)
    
    # Get available models if none specified
    if not model:
        console.print("[dim]No model specified, fetching available models...[/dim]")
        models = client.get_models()
        if not models:
            console.print("[red]Error: No models available[/red]")
            raise typer.Exit(1)
        
        # Use the first available model
        model = models[0].get('model_id') or models[0].get('name', 'default')
        console.print(f"[dim]Using model: {model}[/dim]")
    
    # Prepare messages in the expected format
    messages = [
        {"role": "user", "content": message}
    ]
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("Running inference...", total=1)
        
        response = client.run_inference(model, messages)
        progress.advance(task)
        
    if response:
        console.print("\n[green]Response:[/green]")
        console.print(Panel(response, title="AI Response", border_style="green"))
    else:
        console.print("[red]No response received[/red]")
        raise typer.Exit(1)


@app.command("vector-dbs")
def list_vector_dbs(
    base_url: str = typer.Option(None, "--url", help="Llama-Stack URL (auto-detected if not provided)"),
    api_key: Optional[str] = typer.Option(None, "--api-key", help="API key for authentication"),
):
    """List available vector databases."""
    
    client = LlamaStackClient(base_url=base_url, api_key=api_key)
    
    # Check if Llama Stack is actually available first
    if not client.health_check():
        console.print("[red]❌ Llama Stack is not available[/red]")
        console.print(f"[dim]Tried to connect to: {client.base_url}[/dim]")
        console.print("[yellow]💡 To deploy Llama Stack:[/yellow]")
        console.print("   [cyan]o8 setup --provider local[/cyan]  # For local development")
        console.print("   [cyan]o8 llama deploy[/cyan]           # Deploy to existing cluster")
        return
        
    console.print(f"[cyan]Listing vector databases from:[/cyan] {client.base_url}")
    
    vector_dbs = client.get_vector_dbs()
    
    if not vector_dbs:
        console.print("[yellow]No vector databases found[/yellow]")
        console.print("[dim]This is normal for a fresh installation[/dim]")
        return
        
    table = Table(title="Available Vector Databases")
    table.add_column("Database ID")
    table.add_column("Type")
    table.add_column("Status")
    
    for vdb in vector_dbs:
        table.add_row(
            vdb.get("database_id", "N/A"),
            vdb.get("database_type", "N/A"),
            vdb.get("status", "unknown")
        )
        
    console.print(table)


# Helper functions

def _create_rag_template(name: str, path: Path, provider: str):
    """Create RAG application template."""
    # Create module.yaml with RAG-specific configuration
    module_spec = {
        "apiVersion": "orchestr8.dev/v1",
        "kind": "Module",
        "metadata": {
            "name": name,
            "version": "1.0.0",
        },
        "spec": {
            "description": f"RAG application: {name}",
            "category": "ai-ml",
            "dependencies": [
                {"name": "llama-stack", "version": ">=1.0.0"},
                {"name": "chromadb", "version": ">=0.4.0", "optional": True}
            ],
            "requirements": {
                "compute": {
                    "cpu": "500m",
                    "memory": "2Gi",
                    "gpu": {"enabled": False, "count": 0}
                },
                "storage": {
                    "documents": {"size": "10Gi", "type": "ReadWriteOnce"},
                    "embeddings": {"size": "20Gi", "type": "ReadWriteOnce"}
                }
            },
            "networking": {
                "ports": [{"name": "http", "port": 8080, "protocol": "TCP"}],
                "ingress": {"enabled": True, "host": f"{name}.{{{{.Values.global.domain}}}}"}
            },
            "security": {"authentication": "oauth2", "rbac": True},
            "aiSpecific": {
                "workloadType": "rag",
                "providers": {
                    "llm": [provider],
                    "embeddings": [provider],
                    "vector_store": ["chromadb"]
                },
                "capabilities": ["document_ingestion", "semantic_search", "question_answering"],
                "models": {
                    "llm": f"{provider}/gpt-3.5-turbo" if provider == "openai" else f"{provider}/claude-3-sonnet",
                    "embeddings": f"{provider}/text-embedding-ada-002" if provider == "openai" else "sentence-transformers/all-MiniLM-L6-v2"
                }
            }
        }
    }
    
    # Write module spec
    with open(path / ".o8" / "module.yaml", "w") as f:
        yaml.dump(module_spec, f, default_flow_style=False)
    
    # Create basic kustomization
    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "namespace": name,
        "resources": [
            "namespace.yaml",
            "deployment.yaml", 
            "service.yaml",
            "configmap.yaml"
        ],
        "commonLabels": {
            "app.kubernetes.io/name": name,
            "app.kubernetes.io/component": "rag-application",
            "app.kubernetes.io/part-of": "orchestr8",
            "module": name
        }
    }
    
    with open(path / "base" / "kustomization.yaml", "w") as f:
        yaml.dump(kustomization, f, default_flow_style=False)
        
    # Create basic deployment
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment", 
        "metadata": {"name": name, "namespace": name},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app.kubernetes.io/name": name}},
            "template": {
                "metadata": {"labels": {"app.kubernetes.io/name": name}},
                "spec": {
                    "containers": [{
                        "name": "rag-app",
                        "image": f"orchestr8/{name}:latest",
                        "ports": [{"containerPort": 8080, "name": "http"}],
                        "env": [
                            {"name": "LLAMA_STACK_URL", "value": "http://llama-stack.llama-stack.svc.cluster.local:8080"},
                            {"name": "VECTOR_STORE_URL", "value": "http://chromadb.chromadb.svc.cluster.local:8000"}
                        ],
                        "resources": {
                            "requests": {"cpu": "250m", "memory": "1Gi"},
                            "limits": {"cpu": "500m", "memory": "2Gi"}
                        }
                    }]
                }
            }
        }
    }
    
    with open(path / "base" / "deployment.yaml", "w") as f:
        yaml.dump(deployment, f, default_flow_style=False)

def _create_agent_template(name: str, path: Path, provider: str):
    """Create agentic workflow template."""
    # Create module.yaml with Agent-specific configuration
    module_spec = {
        "apiVersion": "orchestr8.dev/v1",
        "kind": "Module",
        "metadata": {
            "name": name,
            "version": "1.0.0",
        },
        "spec": {
            "description": f"Agentic workflow: {name}",
            "category": "ai-ml",
            "dependencies": [
                {"name": "llama-stack", "version": ">=1.0.0"},
                {"name": "redis", "version": ">=6.0", "optional": True}
            ],
            "requirements": {
                "compute": {
                    "cpu": "1000m",
                    "memory": "4Gi",
                    "gpu": {"enabled": True, "count": 1}
                },
                "storage": {
                    "workflow_state": {"size": "5Gi", "type": "ReadWriteOnce"},
                    "tool_cache": {"size": "10Gi", "type": "ReadWriteOnce"}
                }
            },
            "networking": {
                "ports": [
                    {"name": "http", "port": 8080, "protocol": "TCP"},
                    {"name": "grpc", "port": 9090, "protocol": "TCP"}
                ],
                "ingress": {"enabled": True, "host": f"{name}.{{{{.Values.global.domain}}}}"}
            },
            "security": {"authentication": "oauth2", "rbac": True},
            "aiSpecific": {
                "workloadType": "agent",
                "providers": {
                    "llm": [provider],
                    "safety": [provider],
                    "memory": ["redis"],
                    "tools": ["built-in"]
                },
                "capabilities": [
                    "multi_step_reasoning",
                    "tool_usage",
                    "memory_management", 
                    "safety_checks",
                    "workflow_execution"
                ],
                "models": {
                    "llm": f"{provider}/gpt-4" if provider == "openai" else f"{provider}/claude-3-opus",
                    "safety": f"{provider}/text-moderation-007" if provider == "openai" else "built-in"
                },
                "agentConfig": {
                    "maxSteps": 10,
                    "timeoutSeconds": 300,
                    "enabledTools": ["web_search", "calculator", "code_interpreter"],
                    "safetyLevel": "strict"
                }
            }
        }
    }
    
    # Write module spec
    with open(path / ".o8" / "module.yaml", "w") as f:
        yaml.dump(module_spec, f, default_flow_style=False)
    
    # Create basic kustomization
    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "namespace": name,
        "resources": [
            "namespace.yaml",
            "deployment.yaml", 
            "service.yaml",
            "configmap.yaml"
        ],
        "commonLabels": {
            "app.kubernetes.io/name": name,
            "app.kubernetes.io/component": "agent-workflow",
            "app.kubernetes.io/part-of": "orchestr8",
            "module": name
        }
    }
    
    with open(path / "base" / "kustomization.yaml", "w") as f:
        yaml.dump(kustomization, f, default_flow_style=False)
        
    # Create agent deployment with GPU support
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment", 
        "metadata": {"name": name, "namespace": name},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app.kubernetes.io/name": name}},
            "template": {
                "metadata": {"labels": {"app.kubernetes.io/name": name}},
                "spec": {
                    "nodeSelector": {"accelerator": "nvidia-tesla-gpu"},
                    "tolerations": [
                        {"key": "nvidia.com/gpu", "operator": "Exists", "effect": "NoSchedule"}
                    ],
                    "containers": [{
                        "name": "agent",
                        "image": f"orchestr8/{name}-agent:latest",
                        "ports": [
                            {"containerPort": 8080, "name": "http"},
                            {"containerPort": 9090, "name": "grpc"}
                        ],
                        "env": [
                            {"name": "LLAMA_STACK_URL", "value": "http://llama-stack.llama-stack.svc.cluster.local:8080"},
                            {"name": "REDIS_URL", "value": "redis://redis.redis.svc.cluster.local:6379"},
                            {"name": "AGENT_MODE", "value": "multi_step"},
                            {"name": "MAX_STEPS", "value": "10"}
                        ],
                        "resources": {
                            "requests": {
                                "cpu": "500m", 
                                "memory": "2Gi",
                                "nvidia.com/gpu": 1
                            },
                            "limits": {
                                "cpu": "1000m", 
                                "memory": "4Gi",
                                "nvidia.com/gpu": 1
                            }
                        }
                    }]
                }
            }
        }
    }
    
    with open(path / "base" / "deployment.yaml", "w") as f:
        yaml.dump(deployment, f, default_flow_style=False)

def _create_inference_template(name: str, path: Path, provider: str):
    """Create inference service template."""
    # Create module.yaml with Inference-specific configuration
    module_spec = {
        "apiVersion": "orchestr8.dev/v1",
        "kind": "Module",
        "metadata": {
            "name": name,
            "version": "1.0.0",
        },
        "spec": {
            "description": f"Model inference service: {name}",
            "category": "ai-ml",
            "dependencies": [
                {"name": "llama-stack", "version": ">=1.0.0"}
            ],
            "requirements": {
                "compute": {
                    "cpu": "2000m",
                    "memory": "8Gi",
                    "gpu": {"enabled": True, "count": 1}
                },
                "storage": {
                    "model_cache": {"size": "50Gi", "type": "ReadWriteOnce"},
                    "inference_cache": {"size": "10Gi", "type": "ReadWriteOnce"}
                }
            },
            "networking": {
                "ports": [
                    {"name": "http", "port": 8080, "protocol": "TCP"},
                    {"name": "grpc", "port": 9090, "protocol": "TCP"},
                    {"name": "metrics", "port": 9091, "protocol": "TCP"}
                ],
                "ingress": {"enabled": True, "host": f"{name}.{{{{.Values.global.domain}}}}"}
            },
            "security": {"authentication": "api-key", "rbac": True},
            "aiSpecific": {
                "workloadType": "inference",
                "providers": {
                    "llm": [provider if provider != "local" else "huggingface"],
                    "inference": ["vllm", "transformers"]
                },
                "capabilities": [
                    "text_generation",
                    "completion",
                    "streaming",
                    "batch_processing",
                    "model_serving"
                ],
                "models": {
                    "primary": "meta-llama/Llama-2-7b-chat-hf" if provider == "local" else f"{provider}/gpt-3.5-turbo",
                    "fallback": "microsoft/DialoGPT-medium"
                },
                "inferenceConfig": {
                    "batchSize": 16,
                    "maxTokens": 2048,
                    "temperature": 0.7,
                    "enableStreaming": True,
                    "enableBatching": True,
                    "autoScaling": {
                        "enabled": True,
                        "minReplicas": 1,
                        "maxReplicas": 10,
                        "targetCPUUtilization": 70,
                        "targetGPUUtilization": 80
                    }
                }
            }
        }
    }
    
    # Write module spec
    with open(path / ".o8" / "module.yaml", "w") as f:
        yaml.dump(module_spec, f, default_flow_style=False)
    
    # Create basic kustomization
    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "namespace": name,
        "resources": [
            "namespace.yaml",
            "deployment.yaml", 
            "service.yaml",
            "configmap.yaml",
            "hpa.yaml"
        ],
        "commonLabels": {
            "app.kubernetes.io/name": name,
            "app.kubernetes.io/component": "inference-service",
            "app.kubernetes.io/part-of": "orchestr8",
            "module": name
        }
    }
    
    with open(path / "base" / "kustomization.yaml", "w") as f:
        yaml.dump(kustomization, f, default_flow_style=False)
        
    # Create inference deployment with GPU support and scaling
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment", 
        "metadata": {"name": name, "namespace": name},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app.kubernetes.io/name": name}},
            "template": {
                "metadata": {
                    "labels": {"app.kubernetes.io/name": name},
                    "annotations": {
                        "prometheus.io/scrape": "true",
                        "prometheus.io/port": "9091",
                        "prometheus.io/path": "/metrics"
                    }
                },
                "spec": {
                    "nodeSelector": {"accelerator": "nvidia-tesla-gpu"},
                    "tolerations": [
                        {"key": "nvidia.com/gpu", "operator": "Exists", "effect": "NoSchedule"}
                    ],
                    "containers": [{
                        "name": "inference-server",
                        "image": f"orchestr8/{name}-inference:latest",
                        "ports": [
                            {"containerPort": 8080, "name": "http"},
                            {"containerPort": 9090, "name": "grpc"},
                            {"containerPort": 9091, "name": "metrics"}
                        ],
                        "env": [
                            {"name": "LLAMA_STACK_URL", "value": "http://llama-stack.llama-stack.svc.cluster.local:8080"},
                            {"name": "MODEL_NAME", "value": "meta-llama/Llama-2-7b-chat-hf"},
                            {"name": "BATCH_SIZE", "value": "16"},
                            {"name": "MAX_TOKENS", "value": "2048"},
                            {"name": "ENABLE_STREAMING", "value": "true"},
                            {"name": "ENABLE_METRICS", "value": "true"}
                        ],
                        "resources": {
                            "requests": {
                                "cpu": "1000m", 
                                "memory": "4Gi",
                                "nvidia.com/gpu": 1
                            },
                            "limits": {
                                "cpu": "2000m", 
                                "memory": "8Gi",
                                "nvidia.com/gpu": 1
                            }
                        },
                        "readinessProbe": {
                            "httpGet": {"path": "/health", "port": 8080},
                            "initialDelaySeconds": 60,
                            "periodSeconds": 10
                        },
                        "livenessProbe": {
                            "httpGet": {"path": "/health", "port": 8080},
                            "initialDelaySeconds": 120,
                            "periodSeconds": 30
                        }
                    }]
                }
            }
        }
    }
    
    with open(path / "base" / "deployment.yaml", "w") as f:
        yaml.dump(deployment, f, default_flow_style=False)
        
    # Create HPA for autoscaling
    hpa = {
        "apiVersion": "autoscaling/v2",
        "kind": "HorizontalPodAutoscaler",
        "metadata": {"name": f"{name}-hpa", "namespace": name},
        "spec": {
            "scaleTargetRef": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "name": name
            },
            "minReplicas": 1,
            "maxReplicas": 10,
            "metrics": [
                {
                    "type": "Resource",
                    "resource": {"name": "cpu", "target": {"type": "Utilization", "averageUtilization": 70}}
                },
                {
                    "type": "Resource", 
                    "resource": {"name": "memory", "target": {"type": "Utilization", "averageUtilization": 80}}
                }
            ]
        }
    }
    
    with open(path / "base" / "hpa.yaml", "w") as f:
        yaml.dump(hpa, f, default_flow_style=False)

def _create_custom_template(name: str, path: Path, provider: str):
    """Create custom AI workload template."""
    # Create module.yaml with minimal custom configuration
    module_spec = {
        "apiVersion": "orchestr8.dev/v1",
        "kind": "Module",
        "metadata": {
            "name": name,
            "version": "1.0.0",
        },
        "spec": {
            "description": f"Custom AI workload: {name}",
            "category": "ai-ml",
            "dependencies": [
                {"name": "llama-stack", "version": ">=1.0.0", "optional": True}
            ],
            "requirements": {
                "compute": {
                    "cpu": "500m",
                    "memory": "2Gi",
                    "gpu": {"enabled": False, "count": 0}
                },
                "storage": {
                    "data": {"size": "10Gi", "type": "ReadWriteOnce"},
                    "cache": {"size": "5Gi", "type": "ReadWriteOnce"}
                }
            },
            "networking": {
                "ports": [{"name": "http", "port": 8080, "protocol": "TCP"}],
                "ingress": {"enabled": True, "host": f"{name}.{{{{.Values.global.domain}}}}"}
            },
            "security": {"authentication": "oauth2", "rbac": True},
            "aiSpecific": {
                "workloadType": "custom",
                "providers": {
                    "llm": [provider],
                    "custom": ["built-in"]
                },
                "capabilities": [
                    "custom_processing",
                    "api_integration",
                    "data_processing"
                ],
                "models": {
                    "primary": "configurable"
                },
                "customConfig": {
                    "enabledFeatures": [],
                    "configurationOptions": {},
                    "scalingPolicy": "manual"
                }
            }
        }
    }
    
    # Write module spec
    with open(path / ".o8" / "module.yaml", "w") as f:
        yaml.dump(module_spec, f, default_flow_style=False)
    
    # Create basic kustomization
    kustomization = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "namespace": name,
        "resources": [
            "namespace.yaml",
            "deployment.yaml", 
            "service.yaml",
            "configmap.yaml"
        ],
        "commonLabels": {
            "app.kubernetes.io/name": name,
            "app.kubernetes.io/component": "custom-workload",
            "app.kubernetes.io/part-of": "orchestr8",
            "module": name
        }
    }
    
    with open(path / "base" / "kustomization.yaml", "w") as f:
        yaml.dump(kustomization, f, default_flow_style=False)
        
    # Create basic custom deployment
    deployment = {
        "apiVersion": "apps/v1",
        "kind": "Deployment", 
        "metadata": {"name": name, "namespace": name},
        "spec": {
            "replicas": 1,
            "selector": {"matchLabels": {"app.kubernetes.io/name": name}},
            "template": {
                "metadata": {"labels": {"app.kubernetes.io/name": name}},
                "spec": {
                    "containers": [{
                        "name": "custom-app",
                        "image": f"orchestr8/{name}:latest",
                        "ports": [{"containerPort": 8080, "name": "http"}],
                        "env": [
                            {"name": "LLAMA_STACK_URL", "value": "http://llama-stack.llama-stack.svc.cluster.local:8080"},
                            {"name": "WORKLOAD_TYPE", "value": "custom"},
                            {"name": "LOG_LEVEL", "value": "info"}
                        ],
                        "resources": {
                            "requests": {"cpu": "250m", "memory": "1Gi"},
                            "limits": {"cpu": "500m", "memory": "2Gi"}
                        },
                        "readinessProbe": {
                            "httpGet": {"path": "/health", "port": 8080},
                            "initialDelaySeconds": 30,
                            "periodSeconds": 10
                        },
                        "livenessProbe": {
                            "httpGet": {"path": "/health", "port": 8080},
                            "initialDelaySeconds": 60,
                            "periodSeconds": 30
                        }
                    }]
                }
            }
        }
    }
    
    with open(path / "base" / "deployment.yaml", "w") as f:
        yaml.dump(deployment, f, default_flow_style=False)
    
    # Create README for the custom template
    readme_content = f"""# {name}

Custom AI workload created with Orchestr8 Llama-Stack integration.

## Getting Started

This is a custom AI workload template. You can modify the configuration to suit your specific needs.

### Configuration

Edit the following files to customize your workload:
- `.o8/module.yaml` - Module specification and AI configuration
- `base/deployment.yaml` - Kubernetes deployment configuration
- `base/kustomization.yaml` - Kustomize configuration

### Environment Variables

The following environment variables are available:
- `LLAMA_STACK_URL` - URL to the Llama-Stack service
- `WORKLOAD_TYPE` - Type of AI workload (custom)
- `LOG_LEVEL` - Logging level (debug, info, warn, error)

### Deployment

To deploy this workload:

```bash
o8 llama validate .
o8 llama deploy . --environment dev
```

### Monitoring

Check the status with:
```bash
o8 llama status --namespace {name}
```

View logs with:
```bash
o8 llama logs --namespace {name}
```
"""
    
    with open(path / "README.md", "w") as f:
        f.write(readme_content)

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