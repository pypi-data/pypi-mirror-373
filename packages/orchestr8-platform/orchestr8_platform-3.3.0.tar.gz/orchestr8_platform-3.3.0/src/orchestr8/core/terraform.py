"""Terraform infrastructure provisioning for Orchestr8."""

import os
import json
import subprocess
import tempfile
import shutil
import zipfile
import urllib.request
from pathlib import Path
from typing import Dict, Any, Optional
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn


class TerraformManager:
    """Manages Terraform operations for Orchestr8 infrastructure."""

    def __init__(self, console: Optional[Console] = None):
        self.console = console or Console()
        self.state_dir = Path.home() / ".orchestr8" / "terraform"
        self.state_dir.mkdir(parents=True, exist_ok=True)

        # Set up Terraform directory in .orchestr8
        self.terraform_dir = self.state_dir / "modules" / "bootstrap"

        # Check if we need to download Terraform files
        try:
            if not self._check_terraform_files():
                self._download_terraform_files()
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Could not set up Terraform files: {e}[/yellow]"
            )

    def _check_terraform_files(self) -> bool:
        """Check if Terraform files exist locally."""
        required_files = ["main.tf", "variables.tf", "outputs.tf"]
        if not self.terraform_dir.exists():
            return False

        for file in required_files:
            if not (self.terraform_dir / file).exists():
                return False

        return True

    def _download_terraform_files(self):
        """Download Terraform files from GitHub repository."""
        self.console.print("[cyan]Downloading Terraform modules from GitHub...[/cyan]")

        # First, try to use local files if in development
        local_terraform = (
            Path(__file__).resolve().parent.parent.parent.parent.parent / "terraform"
        )
        if local_terraform.exists():
            # Copy local terraform files
            terraform_dest = self.state_dir / "modules"
            if terraform_dest.exists():
                shutil.rmtree(terraform_dest)
            shutil.copytree(local_terraform, terraform_dest)
            self.console.print(
                f"[green]✓ Using local Terraform modules from {local_terraform}[/green]"
            )
            return

        # Otherwise download from GitHub
        repo_url = "https://api.github.com/repos/killerapp/orchestr8/zipball/main"

        try:
            # Create temp directory
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir = Path(tmpdir)
                zip_path = tmpdir / "repo.zip"

                # Download the repository
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=self.console,
                    transient=True,
                ) as progress:
                    task = progress.add_task("Downloading repository...", total=None)

                    urllib.request.urlretrieve(repo_url, zip_path)
                    progress.update(task, completed=True)

                # Extract the zip file
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(tmpdir)

                # Find the terraform directory in the extracted content
                # GitHub zipball creates a directory with format: owner-repo-hash
                extracted_dirs = [
                    d
                    for d in tmpdir.iterdir()
                    if d.is_dir() and d.name.startswith("killerapp-orchestr8")
                ]
                if not extracted_dirs:
                    raise FileNotFoundError("Could not find extracted repository")

                extracted_dir = extracted_dirs[0]
                terraform_src = extracted_dir / "terraform"

                if not terraform_src.exists():
                    raise FileNotFoundError(
                        "Terraform directory not found in repository"
                    )

                # Copy terraform files to local .orchestr8 directory
                terraform_dest = self.state_dir / "modules"
                if terraform_dest.exists():
                    shutil.rmtree(terraform_dest)

                shutil.copytree(terraform_src, terraform_dest)

                self.console.print(
                    f"[green]✓ Terraform modules downloaded to {terraform_dest}[/green]"
                )

        except Exception as e:
            self.console.print(f"[red]Failed to download Terraform files: {e}[/red]")
            raise

    def check_prerequisites(self) -> Dict[str, bool]:
        """Check if required tools are installed."""
        tools = {
            "terraform": self._check_command("terraform"),
            "gcloud": self._check_command("gcloud"),
            "kubectl": self._check_command("kubectl"),
        }
        return tools

    def _check_command(self, cmd: str) -> bool:
        """Check if a command exists."""
        return shutil.which(cmd) is not None

    async def provision_infrastructure(
        self,
        provider: str,
        project_id: str,
        region: str = "us-central1",
        cluster_name: str = "orchestr8-cluster",
        environment: str = "dev",
        **kwargs,
    ) -> Dict[str, Any]:
        """Provision cloud infrastructure using Terraform."""

        if provider != "gcp":
            return {
                "success": False,
                "error": f"Provider {provider} not yet supported for Terraform provisioning",
            }

        # Check prerequisites
        prereqs = self.check_prerequisites()
        if not all(prereqs.values()):
            missing = [tool for tool, exists in prereqs.items() if not exists]
            return {
                "success": False,
                "error": f"Missing required tools: {', '.join(missing)}",
            }

        # Check GCP authentication
        if not self._check_gcp_auth():
            return {
                "success": False,
                "error": "Not authenticated with GCP. Run: gcloud auth login",
            }

        # Set up shell usage for Windows
        import platform

        use_shell = platform.system() == "Windows"

        # Set GCP project
        subprocess.run(
            ["gcloud", "config", "set", "project", project_id],
            capture_output=True,
            shell=use_shell,
        )

        # Enable required APIs
        self.console.print("[yellow]Enabling required GCP APIs...[/yellow]")
        apis = [
            "container.googleapis.com",
            "compute.googleapis.com",
            "iam.googleapis.com",
            "cloudresourcemanager.googleapis.com",
            "secretmanager.googleapis.com",
        ]

        for api in apis:
            subprocess.run(
                ["gcloud", "services", "enable", api, "--quiet"],
                capture_output=True,
                shell=use_shell,
            )

        # Create tfvars file
        tfvars_content = self._create_tfvars(
            project_id=project_id,
            region=region,
            cluster_name=cluster_name,
            environment=environment,
            **kwargs,
        )

        tfvars_path = self.state_dir / f"{cluster_name}.tfvars"
        tfvars_path.write_text(tfvars_content)

        # Initialize Terraform
        self.console.print("[cyan]Initializing Terraform...[/cyan]")
        self.console.print(f"[dim]Working directory: {self.terraform_dir}[/dim]")

        # Ensure Terraform files are available
        if not self._check_terraform_files():
            self._download_terraform_files()

        # Use shell=True on Windows for better command handling
        import platform

        use_shell = platform.system() == "Windows"

        # Set up environment with proper credentials
        env = os.environ.copy()
        if platform.system() == "Windows":
            # On Windows, ensure we use ADC credentials
            adc_path = (
                Path.home()
                / "AppData"
                / "Roaming"
                / "gcloud"
                / "application_default_credentials.json"
            )
            if adc_path.exists():
                env["GOOGLE_APPLICATION_CREDENTIALS"] = str(adc_path)

        try:
            result = subprocess.run(
                [
                    "terraform",
                    "init",
                    "-backend-config",
                    f"path={self.state_dir / 'terraform.tfstate'}",
                ],
                cwd=str(self.terraform_dir),  # Convert Path to string for Windows
                capture_output=True,
                text=True,
                shell=use_shell,
                env=env,
            )
        except Exception as e:
            return {"success": False, "error": f"Failed to run terraform init: {e}"}

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Terraform init failed: {result.stderr}",
            }

        # Run Terraform plan
        self.console.print("[cyan]Planning infrastructure changes...[/cyan]")
        result = subprocess.run(
            ["terraform", "plan", "-var-file", str(tfvars_path), "-out", "tfplan"],
            cwd=str(self.terraform_dir),
            capture_output=True,
            text=True,
            shell=use_shell,
            env=env,
        )

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Terraform plan failed: {result.stderr}",
            }

        # Apply Terraform
        self.console.print(
            "[cyan]Creating infrastructure (this may take 10-15 minutes)...[/cyan]"
        )
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            task = progress.add_task(
                "Provisioning GKE cluster and resources...", total=None
            )

            result = subprocess.run(
                ["terraform", "apply", "-auto-approve", "-var-file", str(tfvars_path)],
                cwd=str(self.terraform_dir),
                capture_output=True,
                text=True,
                shell=use_shell,
                env=env,
            )

            progress.update(task, completed=True)

        if result.returncode != 0:
            return {
                "success": False,
                "error": f"Terraform apply failed: {result.stderr}",
            }

        # Get outputs
        outputs = self._get_terraform_outputs()

        # Configure kubectl
        self.console.print("[cyan]Configuring kubectl...[/cyan]")
        subprocess.run(
            [
                "gcloud",
                "container",
                "clusters",
                "get-credentials",
                cluster_name,
                "--region",
                region,
                "--project",
                project_id,
            ],
            capture_output=True,
            shell=use_shell,
        )

        return {
            "success": True,
            "cluster_name": outputs.get("cluster_name", {}).get("value"),
            "cluster_endpoint": outputs.get("cluster_endpoint", {}).get("value"),
            "argocd_password": outputs.get("argocd_admin_password", {}).get("value"),
            "kubeconfig_command": outputs.get("kubeconfig_command", {}).get("value"),
            "outputs": outputs,
        }

    def _check_gcp_auth(self) -> bool:
        """Check if authenticated with GCP."""
        import platform

        use_shell = platform.system() == "Windows"

        result = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=json"],
            capture_output=True,
            text=True,
            shell=use_shell,
        )

        if result.returncode == 0:
            try:
                accounts = json.loads(result.stdout)
                return len(accounts) > 0
            except json.JSONDecodeError:
                return False
        return False

    def _create_tfvars(
        self,
        project_id: str,
        region: str,
        cluster_name: str,
        environment: str,
        node_count: int = 2,
        machine_type: str = "e2-standard-2",
        **kwargs,
    ) -> str:
        """Create terraform.tfvars content."""

        # Use preemptible nodes for dev/test to save costs
        use_preemptible = environment in ["dev", "test"]

        # Try to get GitHub token from multiple sources
        github_token = ""

        # 1. Check gh CLI
        try:
            result = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True
            )
            if result.returncode == 0 and result.stdout.strip():
                github_token = result.stdout.strip()
        except Exception:
            pass

        # 2. Check environment variable
        if not github_token:
            github_token = os.environ.get("GITHUB_TOKEN", "")

        tfvars = f"""# Auto-generated by Orchestr8
project_id = "{project_id}"
region     = "{region}"
cluster_name = "{cluster_name}"
environment = "{environment}"

# Node configuration
node_count = {node_count}
min_node_count = {kwargs.get("min_node_count", 1)}
max_node_count = {kwargs.get("max_node_count", 3)}
machine_type = "{machine_type}"
disk_size_gb = {kwargs.get("disk_size_gb", 100)}
use_preemptible_nodes = {str(use_preemptible).lower()}

# Network configuration
enable_private_cluster = {str(kwargs.get("enable_private_cluster", False)).lower()}

# ArgoCD
argocd_version = "{kwargs.get("argocd_version", "5.51.6")}"
argocd_repo_url = "{kwargs.get("argocd_repo_url", "https://github.com/killerapp/orchestr8")}"
"""

        # Add GitHub token if available
        if github_token:
            tfvars += f'github_token = "{github_token}"\n'
            self.console.print(
                "[green]✓ GitHub token found for repository access[/green]"
            )
        else:
            self.console.print(
                "[yellow]⚠ No GitHub token found - repository access may fail[/yellow]"
            )

        tfvars += f"""
# External Secrets
install_external_secrets = {str(kwargs.get("install_external_secrets", True)).lower()}

# Tags
tags = {{
  managed_by = "orchestr8"
  owner = "{kwargs.get("owner", "platform-team")}"
}}
"""
        return tfvars

    def _get_terraform_outputs(self) -> Dict[str, Any]:
        """Get Terraform outputs."""
        import platform

        use_shell = platform.system() == "Windows"

        result = subprocess.run(
            ["terraform", "output", "-json"],
            cwd=str(self.terraform_dir),
            capture_output=True,
            text=True,
            shell=use_shell,
        )

        if result.returncode == 0:
            try:
                return json.loads(result.stdout)
            except json.JSONDecodeError:
                return {}
        return {}

    async def destroy_infrastructure(self, cluster_name: str) -> Dict[str, Any]:
        """Destroy Terraform-managed infrastructure."""
        import platform

        use_shell = platform.system() == "Windows"

        tfvars_path = self.state_dir / f"{cluster_name}.tfvars"
        if not tfvars_path.exists():
            return {
                "success": False,
                "error": f"No configuration found for cluster {cluster_name}",
            }

        self.console.print("[red]Destroying infrastructure...[/red]")

        result = subprocess.run(
            ["terraform", "destroy", "-auto-approve", "-var-file", str(tfvars_path)],
            cwd=str(self.terraform_dir),
            capture_output=True,
            text=True,
            shell=use_shell,
        )

        if result.returncode == 0:
            # Clean up tfvars file
            tfvars_path.unlink()
            return {
                "success": True,
                "message": f"Infrastructure for {cluster_name} destroyed",
            }
        else:
            return {
                "success": False,
                "error": f"Terraform destroy failed: {result.stderr}",
            }

    def get_infrastructure_status(self, cluster_name: str) -> Dict[str, Any]:
        """Get status of Terraform-managed infrastructure."""
        import platform

        use_shell = platform.system() == "Windows"

        tfvars_path = self.state_dir / f"{cluster_name}.tfvars"
        if not tfvars_path.exists():
            return {
                "exists": False,
                "message": f"No infrastructure configuration found for {cluster_name}",
            }

        # Check Terraform state
        result = subprocess.run(
            ["terraform", "show", "-json"],
            cwd=str(self.terraform_dir),
            capture_output=True,
            text=True,
            shell=use_shell,
        )

        if result.returncode == 0:
            try:
                state = json.loads(result.stdout)
                resources = (
                    state.get("values", {}).get("root_module", {}).get("resources", [])
                )

                # Look for the GKE cluster
                cluster_resource = next(
                    (r for r in resources if r["type"] == "google_container_cluster"),
                    None,
                )

                if cluster_resource:
                    return {
                        "exists": True,
                        "provisioned": True,
                        "cluster_name": cluster_resource["values"]["name"],
                        "location": cluster_resource["values"]["location"],
                        "status": "running",
                    }
                else:
                    return {
                        "exists": True,
                        "provisioned": False,
                        "message": "Infrastructure configuration exists but not yet provisioned",
                    }
            except json.JSONDecodeError:
                pass

        return {
            "exists": True,
            "provisioned": False,
            "message": "Unable to read infrastructure state",
        }
