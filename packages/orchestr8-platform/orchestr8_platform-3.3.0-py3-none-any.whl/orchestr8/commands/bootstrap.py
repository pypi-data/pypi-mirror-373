"""Bootstrap Kubernetes clusters for Orchestr8."""

import subprocess
import json
import shutil
from typing import Optional, Dict, Any
from pathlib import Path
from enum import Enum

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..utils.azure_cli import run_azure_cli, check_azure_cli_auth

console = Console()
app = typer.Typer(help="Bootstrap Kubernetes clusters for Orchestr8")


class BootstrapProvider(str, Enum):
    """Supported bootstrap providers."""

    LOCAL = "local"
    GCP = "gcp"
    GCP_TERRAFORM = "gcp-terraform"  # Full Terraform-based provisioning
    AZURE = "azure"
    AZURE_TERRAFORM = "azure-terraform"  # Full Terraform-based provisioning


class KubernetesBootstrapper:
    """Base class for Kubernetes cluster bootstrapping."""

    def __init__(self, console: Console):
        self.console = console

    async def bootstrap(self, **kwargs) -> Dict[str, Any]:
        """Bootstrap the Kubernetes cluster."""
        raise NotImplementedError

    async def destroy(self, **kwargs) -> Dict[str, Any]:
        """Destroy the Kubernetes cluster."""
        raise NotImplementedError

    async def status(self) -> Dict[str, Any]:
        """Check cluster status."""
        raise NotImplementedError


class LocalKubernetesBootstrapper(KubernetesBootstrapper):
    """Bootstrap local Kubernetes using Docker Desktop or Minikube."""

    def detect_local_k8s(self) -> Optional[str]:
        """Detect available local Kubernetes runtime."""
        # Check Docker Desktop
        if shutil.which("docker"):
            try:
                result = subprocess.run(
                    ["docker", "system", "info", "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    info = json.loads(result.stdout)
                    # Check if Docker Desktop with Kubernetes is available
                    if "desktop" in info.get("OperatingSystem", "").lower():
                        # Check if Kubernetes is enabled
                        kubectl_result = subprocess.run(
                            ["kubectl", "config", "get-contexts"],
                            capture_output=True,
                            text=True,
                            timeout=5,
                        )
                        if (
                            kubectl_result.returncode == 0
                            and "docker-desktop" in kubectl_result.stdout
                        ):
                            return "docker-desktop"
            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                pass

        # Check Minikube
        if shutil.which("minikube"):
            try:
                result = subprocess.run(
                    ["minikube", "status", "--format", "json"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    status = json.loads(result.stdout)
                    if status.get("Host") == "Running":
                        return "minikube"
            except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
                pass

        # Check Kind
        if shutil.which("kind"):
            try:
                result = subprocess.run(
                    ["kind", "get", "clusters"],
                    capture_output=True,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0 and result.stdout.strip():
                    return "kind"
            except (subprocess.TimeoutExpired, FileNotFoundError):
                pass

        return None

    async def bootstrap(
        self, runtime: Optional[str] = None, **kwargs
    ) -> Dict[str, Any]:
        """Bootstrap local Kubernetes cluster."""
        # Auto-detect if not specified
        if not runtime:
            runtime = self.detect_local_k8s()
            if runtime:
                self.console.print(f"[green]✓[/green] Detected {runtime} Kubernetes")
            else:
                self.console.print("[yellow]No local Kubernetes detected[/yellow]")
                return await self._setup_kind()

        if runtime == "docker-desktop":
            return await self._setup_docker_desktop()
        elif runtime == "minikube":
            return await self._setup_minikube()
        elif runtime == "kind":
            return await self._setup_kind()
        else:
            raise ValueError(f"Unsupported runtime: {runtime}")

    async def _setup_docker_desktop(self) -> Dict[str, Any]:
        """Setup Docker Desktop Kubernetes."""
        self.console.print("[cyan]Using Docker Desktop Kubernetes[/cyan]")

        # Switch context to docker-desktop
        result = subprocess.run(
            ["kubectl", "config", "use-context", "docker-desktop"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Failed to switch to docker-desktop context: {result.stderr}"
            )

        # Verify cluster is running
        result = subprocess.run(
            ["kubectl", "cluster-info"], capture_output=True, text=True
        )

        if result.returncode != 0:
            self.console.print("[red]Docker Desktop Kubernetes is not running[/red]")
            self.console.print("Please enable Kubernetes in Docker Desktop settings")
            raise RuntimeError("Docker Desktop Kubernetes not available")

        return {
            "provider": "docker-desktop",
            "status": "ready",
            "context": "docker-desktop",
            "message": "Docker Desktop Kubernetes is ready",
        }

    async def _setup_minikube(self) -> Dict[str, Any]:
        """Setup Minikube cluster."""
        self.console.print("[cyan]Setting up Minikube cluster[/cyan]")

        # Check if minikube is already running
        result = subprocess.run(
            ["minikube", "status", "--format", "json"], capture_output=True, text=True
        )

        if result.returncode == 0:
            status = json.loads(result.stdout)
            if status.get("Host") == "Running":
                self.console.print("[green]✓[/green] Minikube is already running")
            else:
                # Start minikube
                self.console.print("Starting Minikube...")
                result = subprocess.run(
                    ["minikube", "start", "--memory=4096", "--cpus=2"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode != 0:
                    raise RuntimeError(f"Failed to start Minikube: {result.stderr}")
        else:
            # Install and start minikube
            self.console.print("Starting new Minikube cluster...")
            result = subprocess.run(
                ["minikube", "start", "--memory=4096", "--cpus=2"],
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise RuntimeError(f"Failed to start Minikube: {result.stderr}")

        # Enable ingress addon
        subprocess.run(["minikube", "addons", "enable", "ingress"], capture_output=True)

        return {
            "provider": "minikube",
            "status": "ready",
            "context": "minikube",
            "message": "Minikube cluster is ready",
        }

    async def _setup_kind(self) -> Dict[str, Any]:
        """Setup Kind cluster."""
        self.console.print("[cyan]Setting up Kind cluster[/cyan]")

        cluster_name = "o8-local"

        # Check if cluster exists
        result = subprocess.run(
            ["kind", "get", "clusters"], capture_output=True, text=True
        )

        if result.returncode == 0 and cluster_name in result.stdout:
            self.console.print(
                f"[green]✓[/green] Kind cluster '{cluster_name}' already exists"
            )
        else:
            # Create Kind cluster with ingress support
            config_content = """
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  kubeadmConfigPatches:
  - |
    kind: InitConfiguration
    nodeRegistration:
      kubeletExtraArgs:
        node-labels: "ingress-ready=true"
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
  - containerPort: 30080
    hostPort: 30080
    protocol: TCP
  - containerPort: 30081
    hostPort: 30081
    protocol: TCP
  - containerPort: 30082
    hostPort: 30082
    protocol: TCP
  - containerPort: 30083
    hostPort: 30083
    protocol: TCP
  - containerPort: 30084
    hostPort: 30084
    protocol: TCP
"""
            # Write config to temp file
            config_path = Path.home() / ".orchestr8" / "kind-config.yaml"
            config_path.parent.mkdir(parents=True, exist_ok=True)
            config_path.write_text(config_content)

            self.console.print(f"Creating Kind cluster '{cluster_name}'...")
            result = subprocess.run(
                [
                    "kind",
                    "create",
                    "cluster",
                    "--name",
                    cluster_name,
                    "--config",
                    str(config_path),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                raise RuntimeError(f"Failed to create Kind cluster: {result.stderr}")

        # Set kubectl context
        subprocess.run(
            ["kubectl", "config", "use-context", f"kind-{cluster_name}"],
            capture_output=True,
        )

        return {
            "provider": "kind",
            "status": "ready",
            "context": f"kind-{cluster_name}",
            "cluster_name": cluster_name,
            "message": f"Kind cluster '{cluster_name}' is ready",
        }

    async def destroy(self, runtime: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        """Destroy local Kubernetes cluster."""
        if not runtime:
            runtime = self.detect_local_k8s()

        if runtime == "kind":
            cluster_name = kwargs.get("cluster_name", "o8-local")
            result = subprocess.run(
                ["kind", "delete", "cluster", "--name", cluster_name],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                return {
                    "destroyed": True,
                    "message": f"Kind cluster '{cluster_name}' destroyed",
                }
            else:
                return {"destroyed": False, "error": result.stderr}
        elif runtime == "minikube":
            result = subprocess.run(
                ["minikube", "delete"], capture_output=True, text=True
            )
            if result.returncode == 0:
                return {"destroyed": True, "message": "Minikube cluster destroyed"}
            else:
                return {"destroyed": False, "error": result.stderr}
        else:
            return {
                "destroyed": False,
                "message": f"Cannot destroy {runtime} cluster (managed externally)",
            }

    async def status(self) -> Dict[str, Any]:
        """Check local cluster status."""
        runtime = self.detect_local_k8s()

        if not runtime:
            return {
                "available": False,
                "message": "No local Kubernetes runtime detected",
            }

        # Check kubectl connection
        result = subprocess.run(
            ["kubectl", "cluster-info"], capture_output=True, text=True
        )

        connected = result.returncode == 0

        # Get current context
        context_result = subprocess.run(
            ["kubectl", "config", "current-context"], capture_output=True, text=True
        )

        current_context = (
            context_result.stdout.strip()
            if context_result.returncode == 0
            else "unknown"
        )

        return {
            "available": True,
            "connected": connected,
            "runtime": runtime,
            "context": current_context,
            "message": f"Using {runtime}"
            if connected
            else f"{runtime} detected but not connected",
        }


class GCPKubernetesBootstrapper(KubernetesBootstrapper):
    """Bootstrap GKE cluster using Terraform."""

    def __init__(self, console: Console):
        super().__init__(console)
        self.terraform_dir = Path.home() / ".orchestr8" / "terraform" / "gcp"

    def _ensure_terraform(self) -> bool:
        """Ensure Terraform is installed."""
        if not shutil.which("terraform"):
            self.console.print("[red]Terraform is not installed[/red]")
            self.console.print(
                "Please install Terraform: https://www.terraform.io/downloads"
            )
            return False
        return True

    def _ensure_gcloud(self) -> bool:
        """Ensure gcloud CLI is installed and configured."""
        if not shutil.which("gcloud"):
            self.console.print("[red]gcloud CLI is not installed[/red]")
            self.console.print(
                "Please install gcloud: https://cloud.google.com/sdk/docs/install"
            )
            return False

        # Check authentication
        result = subprocess.run(
            ["gcloud", "auth", "list", "--filter=status:ACTIVE", "--format=json"],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0 or not json.loads(result.stdout):
            self.console.print("[red]Not authenticated with GCP[/red]")
            self.console.print("Please run: gcloud auth login")
            return False

        return True

    def _create_terraform_config(
        self, project_id: str, region: str, cluster_name: str
    ) -> None:
        """Create Terraform configuration for GKE."""
        self.terraform_dir.mkdir(parents=True, exist_ok=True)

        # Main Terraform configuration
        main_tf = """
terraform {
  required_version = ">= 1.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

variable "project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "region" {
  description = "GCP Region"
  type        = string
}

variable "cluster_name" {
  description = "GKE Cluster Name"
  type        = string
}

variable "zone" {
  description = "GCP Zone"
  type        = string
  default     = ""
}

locals {
  zone = var.zone != "" ? var.zone : "${var.region}-a"
}

resource "google_container_cluster" "o8_cluster" {
  name     = var.cluster_name
  location = local.zone

  # Start with minimal node pool
  initial_node_count = 1
  remove_default_node_pool = true

  # Network configuration
  network    = "default"
  subnetwork = "default"

  # Workload Identity
  workload_identity_config {
    workload_pool = "${var.project_id}.svc.id.goog"
  }

  # Security
  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }

  # Addons
  addons_config {
    http_load_balancing {
      disabled = false
    }
    horizontal_pod_autoscaling {
      disabled = false
    }
    network_policy_config {
      disabled = false
    }
  }

  # Maintenance window
  maintenance_policy {
    daily_maintenance_window {
      start_time = "03:00"
    }
  }
}

resource "google_container_node_pool" "o8_nodes" {
  name       = "${var.cluster_name}-pool"
  cluster    = google_container_cluster.o8_cluster.id
  location   = local.zone
  node_count = 3

  autoscaling {
    min_node_count = 2
    max_node_count = 6
  }

  management {
    auto_repair  = true
    auto_upgrade = true
  }

  node_config {
    preemptible  = false
    machine_type = "e2-standard-4"
    disk_size_gb = 50
    disk_type    = "pd-standard"

    # Google recommends custom service accounts
    service_account = google_service_account.o8_nodes.email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]

    # Workload Identity
    workload_metadata_config {
      mode = "GKE_METADATA"
    }

    labels = {
      managed_by = "orchestr8"
      cluster    = var.cluster_name
    }

    tags = ["o8-cluster", var.cluster_name]
  }
}

resource "google_service_account" "o8_nodes" {
  account_id   = "${var.cluster_name}-nodes"
  display_name = "Orchestr8 GKE Nodes Service Account"
  project      = var.project_id
}

# IAM roles for the node service account
resource "google_project_iam_member" "node_log_writer" {
  project = var.project_id
  role    = "roles/logging.logWriter"
  member  = "serviceAccount:${google_service_account.o8_nodes.email}"
}

resource "google_project_iam_member" "node_metric_writer" {
  project = var.project_id
  role    = "roles/monitoring.metricWriter"
  member  = "serviceAccount:${google_service_account.o8_nodes.email}"
}

resource "google_project_iam_member" "node_monitoring_viewer" {
  project = var.project_id
  role    = "roles/monitoring.viewer"
  member  = "serviceAccount:${google_service_account.o8_nodes.email}"
}

output "cluster_name" {
  value = google_container_cluster.o8_cluster.name
}

output "cluster_endpoint" {
  value     = google_container_cluster.o8_cluster.endpoint
  sensitive = true
}

output "cluster_ca_certificate" {
  value     = google_container_cluster.o8_cluster.master_auth[0].cluster_ca_certificate
  sensitive = true
}

output "region" {
  value = var.region
}

output "zone" {
  value = local.zone
}
"""

        (self.terraform_dir / "main.tf").write_text(main_tf)

        # Terraform variables file
        tfvars = f"""
project_id   = "{project_id}"
region       = "{region}"
cluster_name = "{cluster_name}"
"""
        (self.terraform_dir / "terraform.tfvars").write_text(tfvars)

    async def bootstrap(
        self,
        project_id: str,
        region: str = "us-central1",
        cluster_name: str = "o8-cluster",
        **kwargs,
    ) -> Dict[str, Any]:
        """Bootstrap GKE cluster."""
        # Check prerequisites
        if not self._ensure_terraform() or not self._ensure_gcloud():
            raise RuntimeError("Prerequisites not met")

        # Set the project
        subprocess.run(
            ["gcloud", "config", "set", "project", project_id], capture_output=True
        )

        # Enable required APIs
        self.console.print("[cyan]Enabling required GCP APIs...[/cyan]")
        apis = [
            "container.googleapis.com",
            "compute.googleapis.com",
            "iam.googleapis.com",
            "cloudresourcemanager.googleapis.com",
        ]

        for api in apis:
            result = subprocess.run(
                ["gcloud", "services", "enable", api], capture_output=True, text=True
            )
            if result.returncode != 0:
                self.console.print(
                    f"[yellow]Warning: Could not enable {api}: {result.stderr}[/yellow]"
                )

        # Create Terraform configuration
        self.console.print("[cyan]Creating Terraform configuration...[/cyan]")
        self._create_terraform_config(project_id, region, cluster_name)

        # Initialize Terraform
        self.console.print("[cyan]Initializing Terraform...[/cyan]")
        result = subprocess.run(
            ["terraform", "init"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Terraform init failed: {result.stderr}")

        # Plan Terraform
        self.console.print("[cyan]Planning GKE cluster creation...[/cyan]")
        result = subprocess.run(
            ["terraform", "plan", "-out=tfplan"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Terraform plan failed: {result.stderr}")

        # Apply Terraform
        self.console.print(
            "[cyan]Creating GKE cluster (this may take 10-15 minutes)...[/cyan]"
        )
        result = subprocess.run(
            ["terraform", "apply", "tfplan"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Terraform apply failed: {result.stderr}")

        # Get cluster credentials
        self.console.print("[cyan]Configuring kubectl...[/cyan]")
        zone_result = subprocess.run(
            ["terraform", "output", "-raw", "zone"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )
        zone = (
            zone_result.stdout.strip() if zone_result.returncode == 0 else f"{region}-a"
        )

        result = subprocess.run(
            [
                "gcloud",
                "container",
                "clusters",
                "get-credentials",
                cluster_name,
                "--zone",
                zone,
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to get cluster credentials: {result.stderr}")

        return {
            "provider": "gcp",
            "status": "ready",
            "cluster_name": cluster_name,
            "project_id": project_id,
            "region": region,
            "zone": zone,
            "context": f"gke_{project_id}_{zone}_{cluster_name}",
            "message": f"GKE cluster '{cluster_name}' is ready in {zone}",
        }

    async def destroy(self, **kwargs) -> Dict[str, Any]:
        """Destroy GKE cluster."""
        if not self.terraform_dir.exists():
            return {"destroyed": False, "message": "No Terraform configuration found"}

        if not self._ensure_terraform():
            raise RuntimeError("Terraform not installed")

        self.console.print("[cyan]Destroying GKE cluster...[/cyan]")
        result = subprocess.run(
            ["terraform", "destroy", "-auto-approve"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Clean up Terraform files
            shutil.rmtree(self.terraform_dir)
            return {"destroyed": True, "message": "GKE cluster destroyed"}
        else:
            return {"destroyed": False, "error": result.stderr}

    async def status(self) -> Dict[str, Any]:
        """Check GKE cluster status."""
        if not self.terraform_dir.exists():
            return {"available": False, "message": "No GKE cluster configuration found"}

        if not self._ensure_terraform():
            return {"available": False, "message": "Terraform not installed"}

        # Check Terraform state
        result = subprocess.run(
            ["terraform", "show", "-json"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return {"available": False, "message": "Could not read Terraform state"}

        try:
            state = json.loads(result.stdout)
            if state.get("values") and state["values"].get("root_module"):
                resources = state["values"]["root_module"].get("resources", [])
                cluster_resource = next(
                    (r for r in resources if r["type"] == "google_container_cluster"),
                    None,
                )

                if cluster_resource:
                    cluster_name = cluster_resource["values"]["name"]
                    location = cluster_resource["values"]["location"]

                    # Check kubectl connection
                    kubectl_result = subprocess.run(
                        ["kubectl", "cluster-info"], capture_output=True, text=True
                    )

                    connected = kubectl_result.returncode == 0

                    return {
                        "available": True,
                        "connected": connected,
                        "cluster_name": cluster_name,
                        "location": location,
                        "message": f"GKE cluster '{cluster_name}' in {location}",
                    }
        except json.JSONDecodeError:
            pass

        return {"available": False, "message": "No active GKE cluster found"}


class AzureKubernetesBootstrapper(KubernetesBootstrapper):
    """Bootstrap AKS cluster using Terraform."""

    def __init__(self, console: Console):
        super().__init__(console)
        self.terraform_dir = Path.home() / ".orchestr8" / "terraform" / "azure"

    def _ensure_terraform(self) -> bool:
        """Ensure Terraform is installed."""
        if not shutil.which("terraform"):
            self.console.print("[red]Terraform is not installed[/red]")
            self.console.print(
                "Please install Terraform: https://www.terraform.io/downloads"
            )
            return False
        return True

    def _ensure_azure_cli(self) -> bool:
        """Ensure Azure CLI is installed and configured."""
        try:
            # Check if Azure CLI is available
            from ..utils.azure_cli import get_azure_cli_path

            get_azure_cli_path()
        except FileNotFoundError as e:
            self.console.print(f"[red]{e}[/red]")
            return False

        # Check authentication
        try:
            account = check_azure_cli_auth()
            self.console.print("[green]✓ Authenticated to Azure[/green]")
            self.console.print(f"  Subscription: {account['name']}")
            return True
        except RuntimeError as e:
            self.console.print(f"[red]{e}[/red]")
            return False

    def _create_terraform_config(
        self,
        subscription_id: str,
        resource_group: str,
        location: str,
        cluster_name: str,
    ) -> None:
        """Create Terraform configuration for AKS."""
        self.terraform_dir.mkdir(parents=True, exist_ok=True)

        # Main Terraform configuration
        main_tf = """
terraform {
  required_version = ">= 1.3.0"

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.85"
    }
    azuread = {
      source  = "hashicorp/azuread"
      version = "~> 2.47"
    }
  }

  backend "local" {
    path = "terraform.tfstate"
  }
}

provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
}

provider "azuread" {}

variable "subscription_id" {
  description = "Azure Subscription ID"
  type        = string
}

variable "resource_group_name" {
  description = "Resource Group Name"
  type        = string
}

variable "location" {
  description = "Azure Region"
  type        = string
}

variable "cluster_name" {
  description = "AKS Cluster Name"
  type        = string
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location

  tags = {
    managed_by  = "orchestr8"
    environment = "dev"
  }
}

# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "${var.cluster_name}-vnet"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  address_space       = ["10.0.0.0/16"]
}

# Subnet for AKS
resource "azurerm_subnet" "aks" {
  name                 = "${var.cluster_name}-subnet"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.0.0/22"]

  service_endpoints = [
    "Microsoft.ContainerRegistry",
    "Microsoft.KeyVault",
    "Microsoft.Storage"
  ]
}

# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = var.cluster_name
  location            = azurerm_resource_group.main.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = var.cluster_name
  kubernetes_version  = "1.30"

  default_node_pool {
    name                = "system"
    node_count          = 2
    vm_size            = "Standard_D2s_v3"
    os_disk_size_gb    = 128
    type               = "VirtualMachineScaleSets"
    enable_auto_scaling = true
    min_count          = 2
    max_count          = 4
    vnet_subnet_id     = azurerm_subnet.aks.id
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin     = "azure"
    network_policy     = "calico"
    dns_service_ip     = "10.1.0.10"
    service_cidr       = "10.1.0.0/16"
    load_balancer_sku  = "standard"
  }

  # Enable RBAC
  azure_active_directory_role_based_access_control {
    managed            = true
    azure_rbac_enabled = true
  }

  # Enable Workload Identity
  oidc_issuer_enabled       = true
  workload_identity_enabled = true

  tags = {
    managed_by  = "orchestr8"
    environment = "dev"
  }
}

# User node pool
resource "azurerm_kubernetes_cluster_node_pool" "user" {
  name                  = "user"
  kubernetes_cluster_id = azurerm_kubernetes_cluster.main.id
  vm_size              = "Standard_D2s_v3"
  node_count           = 2
  vnet_subnet_id       = azurerm_subnet.aks.id

  enable_auto_scaling = true
  min_count          = 1
  max_count          = 4

  zones = ["1", "2"]

  node_labels = {
    "node-type" = "user"
    "workload"  = "general"
  }

  tags = {
    managed_by = "orchestr8"
  }
}

# Key Vault for secrets
resource "azurerm_key_vault" "main" {
  name                = "${substr(var.cluster_name, 0, 17)}-o8-kv"
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku_name           = "standard"
  tenant_id          = data.azurerm_client_config.current.tenant_id

  soft_delete_retention_days = 7
  purge_protection_enabled   = true
  enable_rbac_authorization = true

  tags = {
    managed_by = "orchestr8"
  }
}

# Container Registry
resource "azurerm_container_registry" "main" {
  name                = replace("${var.cluster_name}o8", "-", "")
  resource_group_name = azurerm_resource_group.main.name
  location            = azurerm_resource_group.main.location
  sku                 = "Standard"
  admin_enabled       = false

  tags = {
    managed_by = "orchestr8"
  }
}

# Grant AKS pull access to ACR
resource "azurerm_role_assignment" "aks_acr_pull" {
  principal_id                     = azurerm_kubernetes_cluster.main.kubelet_identity[0].object_id
  role_definition_name             = "AcrPull"
  scope                           = azurerm_container_registry.main.id
  skip_service_principal_aad_check = true
}

data "azurerm_client_config" "current" {}

output "cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "resource_group" {
  value = azurerm_resource_group.main.name
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}
"""

        # Write main.tf
        (self.terraform_dir / "main.tf").write_text(main_tf)

        # Create terraform.tfvars
        tfvars = f"""
subscription_id      = "{subscription_id}"
resource_group_name  = "{resource_group}"
location            = "{location}"
cluster_name        = "{cluster_name}"
"""
        (self.terraform_dir / "terraform.tfvars").write_text(tfvars)

    async def bootstrap(self, **kwargs) -> Dict[str, Any]:
        """Bootstrap AKS cluster."""
        subscription_id = kwargs.get("subscription_id")
        resource_group = kwargs.get("resource_group", "o8-resources")
        location = kwargs.get("location", "eastus2")
        cluster_name = kwargs.get("cluster_name", "o8-cluster")

        # Ensure prerequisites
        if not self._ensure_terraform():
            raise RuntimeError("Terraform not installed")

        if not self._ensure_azure_cli():
            raise RuntimeError("Azure CLI not installed or not authenticated")

        # Get subscription ID if not provided
        if not subscription_id:
            result = run_azure_cli(
                ["account", "show", "--query", "id", "--output", "tsv"],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                subscription_id = result.stdout.strip()
            else:
                raise RuntimeError("Could not get Azure subscription ID")

        self.console.print(f"[cyan]Creating AKS cluster '{cluster_name}'...[/cyan]")
        self.console.print(f"  Subscription: {subscription_id}")
        self.console.print(f"  Resource Group: {resource_group}")
        self.console.print(f"  Location: {location}")

        # Create Terraform configuration
        self._create_terraform_config(
            subscription_id, resource_group, location, cluster_name
        )

        # Initialize Terraform
        self.console.print("[cyan]Initializing Terraform...[/cyan]")
        result = subprocess.run(
            ["terraform", "init"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Terraform init failed: {result.stderr}")

        # Plan deployment
        self.console.print("[cyan]Planning AKS deployment...[/cyan]")
        result = subprocess.run(
            ["terraform", "plan", "-out=tfplan"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Terraform plan failed: {result.stderr}")

        # Apply deployment
        self.console.print(
            "[cyan]Creating AKS cluster (this may take 10-15 minutes)...[/cyan]"
        )
        result = subprocess.run(
            ["terraform", "apply", "tfplan"],
            cwd=self.terraform_dir,
            capture_output=False,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError("Terraform apply failed")

        # Get cluster credentials
        self.console.print("[cyan]Getting AKS credentials...[/cyan]")
        result = subprocess.run(
            [
                "az",
                "aks",
                "get-credentials",
                "--name",
                cluster_name,
                "--resource-group",
                resource_group,
                "--overwrite-existing",
            ],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"Failed to get cluster credentials: {result.stderr}")

        return {
            "provider": "azure",
            "status": "ready",
            "cluster_name": cluster_name,
            "subscription_id": subscription_id,
            "resource_group": resource_group,
            "location": location,
            "context": f"{cluster_name}",
            "message": f"AKS cluster '{cluster_name}' is ready in {location}",
        }

    async def destroy(self, **kwargs) -> Dict[str, Any]:
        """Destroy AKS cluster."""
        if not self.terraform_dir.exists():
            return {"destroyed": False, "message": "No Terraform configuration found"}

        if not self._ensure_terraform():
            raise RuntimeError("Terraform not installed")

        self.console.print("[cyan]Destroying AKS cluster...[/cyan]")
        result = subprocess.run(
            ["terraform", "destroy", "-auto-approve"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            # Clean up Terraform files
            shutil.rmtree(self.terraform_dir)
            return {"destroyed": True, "message": "AKS cluster destroyed"}
        else:
            return {"destroyed": False, "error": result.stderr}

    async def status(self) -> Dict[str, Any]:
        """Check AKS cluster status."""
        if not self.terraform_dir.exists():
            return {"available": False, "message": "No AKS cluster configuration found"}

        if not self._ensure_terraform():
            return {"available": False, "message": "Terraform not installed"}

        # Check Terraform state
        result = subprocess.run(
            ["terraform", "show", "-json"],
            cwd=self.terraform_dir,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            return {"available": False, "message": "Could not read Terraform state"}

        try:
            state = json.loads(result.stdout)
            if state.get("values") and state["values"].get("root_module"):
                resources = state["values"]["root_module"].get("resources", [])
                cluster_resource = next(
                    (r for r in resources if r["type"] == "azurerm_kubernetes_cluster"),
                    None,
                )

                if cluster_resource:
                    cluster_name = cluster_resource["values"]["name"]
                    location = cluster_resource["values"]["location"]

                    # Check kubectl connection
                    kubectl_result = subprocess.run(
                        ["kubectl", "cluster-info"], capture_output=True, text=True
                    )

                    connected = kubectl_result.returncode == 0

                    return {
                        "available": True,
                        "connected": connected,
                        "cluster_name": cluster_name,
                        "location": location,
                        "message": f"AKS cluster '{cluster_name}' in {location}",
                    }
        except json.JSONDecodeError:
            pass

        return {"available": False, "message": "No active AKS cluster found"}


@app.command("create")
def create_cluster(
    provider: BootstrapProvider = typer.Argument(
        ..., help="Provider to use for bootstrapping (local, gcp, azure)"
    ),
    project_id: Optional[str] = typer.Option(
        None, "--project-id", "-p", help="GCP Project ID (required for GCP)"
    ),
    subscription_id: Optional[str] = typer.Option(
        None,
        "--subscription-id",
        "-s",
        help="Azure Subscription ID (optional for Azure)",
    ),
    resource_group: str = typer.Option(
        "o8-resources", "--resource-group", "-g", help="Azure Resource Group name"
    ),
    region: str = typer.Option(
        "us-central1", "--region", "-r", help="Cloud region (GCP/Azure)"
    ),
    location: str = typer.Option("eastus2", "--location", "-l", help="Azure location"),
    cluster_name: str = typer.Option(
        "o8-cluster", "--cluster-name", "-c", help="Cluster name"
    ),
    runtime: Optional[str] = typer.Option(
        None, "--runtime", help="Local runtime to use (docker-desktop, minikube, kind)"
    ),
):
    """Create a new Kubernetes cluster."""
    import asyncio

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        if provider == BootstrapProvider.LOCAL:
            task = progress.add_task("Setting up local Kubernetes...", total=None)
            bootstrapper = LocalKubernetesBootstrapper(console)
            result = asyncio.run(bootstrapper.bootstrap(runtime=runtime))
            progress.update(task, completed=True)

        elif provider == BootstrapProvider.GCP:
            if not project_id:
                console.print("[red]GCP Project ID is required for GKE[/red]")
                raise typer.Exit(1)

            task = progress.add_task("Creating GKE cluster...", total=None)
            bootstrapper = GCPKubernetesBootstrapper(console)
            result = asyncio.run(
                bootstrapper.bootstrap(
                    project_id=project_id, region=region, cluster_name=cluster_name
                )
            )
            progress.update(task, completed=True)

        elif provider == BootstrapProvider.AZURE:
            task = progress.add_task("Creating AKS cluster...", total=None)
            bootstrapper = AzureKubernetesBootstrapper(console)
            result = asyncio.run(
                bootstrapper.bootstrap(
                    subscription_id=subscription_id,
                    resource_group=resource_group,
                    location=location,
                    cluster_name=cluster_name,
                )
            )
            progress.update(task, completed=True)

        else:
            console.print(f"[red]Unsupported provider: {provider}[/red]")
            raise typer.Exit(1)

    console.print(f"\n[green]✅ {result['message']}[/green]")

    if provider == BootstrapProvider.LOCAL:
        console.print("\n[cyan]Next steps:[/cyan]")
        console.print("1. Run 'o8 setup' to install Orchestr8")
        console.print("2. Access ArgoCD at http://localhost:30080")
    elif provider == BootstrapProvider.GCP:
        console.print("\n[cyan]Cluster Details:[/cyan]")
        table = Table(show_header=False, box=None)
        table.add_row("Project:", result.get("project_id", ""))
        table.add_row("Region:", result.get("region", ""))
        table.add_row("Zone:", result.get("zone", ""))
        table.add_row("Context:", result.get("context", ""))
        console.print(table)

        console.print("\n[cyan]Next steps:[/cyan]")
        console.print(
            "1. Run 'o8 setup --provider gcp --domain your-domain.com' to install Orchestr8"
        )
        console.print("2. Configure DNS for your domain")
        console.print("3. Access ArgoCD at https://argocd.your-domain.com")
    elif provider == BootstrapProvider.AZURE:
        console.print("\n[cyan]Cluster Details:[/cyan]")
        table = Table(show_header=False, box=None)
        table.add_row("Subscription:", result.get("subscription_id", ""))
        table.add_row("Resource Group:", result.get("resource_group", ""))
        table.add_row("Location:", result.get("location", ""))
        table.add_row("Cluster Name:", result.get("cluster_name", ""))
        table.add_row("Context:", result.get("context", ""))
        console.print(table)

        console.print("\n[cyan]Next steps:[/cyan]")
        console.print(
            "1. Run 'o8 setup --provider azure --domain your-domain.com' to install Orchestr8"
        )
        console.print("2. Configure DNS for your domain")
        console.print("3. Access ArgoCD at https://argocd.your-domain.com")


@app.command("destroy")
def destroy_cluster(
    provider: BootstrapProvider = typer.Argument(
        ..., help="Provider of the cluster to destroy (local, gcp, azure)"
    ),
    cluster_name: str = typer.Option(
        "o8-cluster", "--cluster-name", "-c", help="Cluster name (for Kind clusters)"
    ),
    force: bool = typer.Option(
        False, "--force", "-f", help="Force destroy without confirmation"
    ),
):
    """Destroy a Kubernetes cluster."""
    import asyncio

    if not force:
        console.print(
            f"[red]⚠️  This will destroy the {provider} Kubernetes cluster[/red]"
        )
        if provider in [BootstrapProvider.GCP, BootstrapProvider.AZURE]:
            console.print(
                "[yellow]All data and resources in the cluster will be permanently deleted[/yellow]"
            )

        if not typer.confirm("Are you sure you want to continue?"):
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        if provider == BootstrapProvider.LOCAL:
            task = progress.add_task("Destroying local cluster...", total=None)
            bootstrapper = LocalKubernetesBootstrapper(console)
            result = asyncio.run(bootstrapper.destroy(cluster_name=cluster_name))
            progress.update(task, completed=True)

        elif provider == BootstrapProvider.GCP:
            task = progress.add_task("Destroying GKE cluster...", total=None)
            bootstrapper = GCPKubernetesBootstrapper(console)
            result = asyncio.run(bootstrapper.destroy())
            progress.update(task, completed=True)

        elif provider == BootstrapProvider.AZURE:
            task = progress.add_task("Destroying AKS cluster...", total=None)
            bootstrapper = AzureKubernetesBootstrapper(console)
            result = asyncio.run(bootstrapper.destroy())
            progress.update(task, completed=True)

        else:
            console.print(f"[red]Unsupported provider: {provider}[/red]")
            raise typer.Exit(1)

    if result.get("destroyed"):
        console.print(f"\n[green]✅ {result['message']}[/green]")
    else:
        console.print(
            f"\n[red]❌ {result.get('message', result.get('error', 'Unknown error'))}[/red]"
        )
        raise typer.Exit(1)


@app.command("status")
def cluster_status(
    provider: Optional[BootstrapProvider] = typer.Argument(
        None,
        help="Provider to check (local, gcp, azure). If not specified, checks all.",
    ),
):
    """Check Kubernetes cluster status."""
    import asyncio

    console.print("[bold cyan]🔍 Kubernetes Cluster Status[/bold cyan]\n")

    providers_to_check = (
        [provider]
        if provider
        else [BootstrapProvider.LOCAL, BootstrapProvider.GCP, BootstrapProvider.AZURE]
    )

    for prov in providers_to_check:
        if prov == BootstrapProvider.LOCAL:
            bootstrapper = LocalKubernetesBootstrapper(console)
            status = asyncio.run(bootstrapper.status())

            console.print("[cyan]Local Kubernetes:[/cyan]")
            if status["available"]:
                table = Table(show_header=False, box=None)
                table.add_row("Runtime:", status.get("runtime", "Unknown"))
                table.add_row("Context:", status.get("context", "Unknown"))
                table.add_row(
                    "Connected:",
                    "[green]Yes[/green]" if status["connected"] else "[red]No[/red]",
                )
                console.print(table)
            else:
                console.print(f"  {status['message']}")

        elif prov == BootstrapProvider.GCP:
            bootstrapper = GCPKubernetesBootstrapper(console)
            status = asyncio.run(bootstrapper.status())

            console.print("\n[cyan]GCP GKE:[/cyan]")
            if status["available"]:
                table = Table(show_header=False, box=None)
                table.add_row("Cluster:", status.get("cluster_name", "Unknown"))
                table.add_row("Location:", status.get("location", "Unknown"))
                table.add_row(
                    "Connected:",
                    "[green]Yes[/green]" if status["connected"] else "[red]No[/red]",
                )
                console.print(table)
            else:
                console.print(f"  {status['message']}")

        elif prov == BootstrapProvider.AZURE:
            bootstrapper = AzureKubernetesBootstrapper(console)
            status = asyncio.run(bootstrapper.status())

            console.print("\n[cyan]Azure AKS:[/cyan]")
            if status["available"]:
                table = Table(show_header=False, box=None)
                table.add_row("Cluster:", status.get("cluster_name", "Unknown"))
                table.add_row("Location:", status.get("location", "Unknown"))
                table.add_row(
                    "Connected:",
                    "[green]Yes[/green]" if status["connected"] else "[red]No[/red]",
                )
                console.print(table)
            else:
                console.print(f"  {status['message']}")

    # Also show general kubectl status
    console.print("\n[cyan]kubectl status:[/cyan]")
    result = subprocess.run(
        ["kubectl", "config", "current-context"], capture_output=True, text=True
    )

    if result.returncode == 0:
        current_context = result.stdout.strip()
        console.print(f"  Current context: {current_context}")

        # Try to get cluster info
        cluster_result = subprocess.run(
            ["kubectl", "cluster-info"], capture_output=True, text=True
        )

        if cluster_result.returncode == 0:
            console.print("  [green]✓[/green] Connected to cluster")
        else:
            console.print("  [red]✗[/red] Cannot connect to cluster")
    else:
        console.print("  [red]No kubectl context configured[/red]")


@app.command("clean")
def clean_bootstrap_files(
    force: bool = typer.Option(
        False, "--force", "-f", help="Force cleanup without confirmation"
    ),
):
    """Clean up bootstrap configuration files and state."""
    bootstrap_dir = Path.home() / ".orchestr8"

    if not bootstrap_dir.exists():
        console.print("[yellow]No bootstrap directory found[/yellow]")
        return

    # Find what needs to be cleaned
    items_to_clean = []

    # Check for Terraform files
    terraform_dir = bootstrap_dir / "terraform"
    if terraform_dir.exists():
        items_to_clean.append(("Terraform configurations", terraform_dir))

    # Check for Kind config
    kind_config = bootstrap_dir / "kind-config.yaml"
    if kind_config.exists():
        items_to_clean.append(("Kind configuration", kind_config))

    if not items_to_clean:
        console.print("[yellow]No bootstrap files to clean[/yellow]")
        return

    # Show what will be cleaned
    console.print("[cyan]The following items will be removed:[/cyan]")
    for item_name, item_path in items_to_clean:
        console.print(f"  • {item_name}: {item_path}")

    if not force:
        if not typer.confirm("\nProceed with cleanup?"):
            console.print("[yellow]Cleanup cancelled[/yellow]")
            raise typer.Exit(0)

    # Perform cleanup
    for item_name, item_path in items_to_clean:
        try:
            if item_path.is_dir():
                shutil.rmtree(item_path)
            else:
                item_path.unlink()
            console.print(f"[green]✓[/green] Removed {item_name}")
        except Exception as e:
            console.print(f"[red]✗[/red] Failed to remove {item_name}: {e}")

    # Clean up empty directories
    if bootstrap_dir.exists() and not any(bootstrap_dir.iterdir()):
        bootstrap_dir.rmdir()
        console.print("[green]✓[/green] Removed empty bootstrap directory")

    console.print("\n[green]✅ Bootstrap cleanup completed[/green]")


if __name__ == "__main__":
    app()
