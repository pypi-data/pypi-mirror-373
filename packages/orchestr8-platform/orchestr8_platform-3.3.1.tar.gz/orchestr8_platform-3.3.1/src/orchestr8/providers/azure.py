"""Azure provider for Orchestr8."""

import os
import json
import subprocess
from typing import Dict, Any, Optional, List
from rich.console import Console
from rich.table import Table

from ..core.config import Config

console = Console()


class AzureProvider:
    """Azure provider implementation for Orchestr8."""

    def __init__(self, config: Config):
        self.config = config
        self.subscription_id = os.getenv("AZURE_SUBSCRIPTION_ID")
        self.tenant_id = os.getenv("AZURE_TENANT_ID")
        self.client_id = os.getenv("AZURE_CLIENT_ID")
        self.client_secret = os.getenv("AZURE_CLIENT_SECRET")

    def validate_credentials(self) -> bool:
        """Validate Azure credentials."""
        # Check for Azure CLI authentication
        try:
            result = subprocess.run(
                ["az", "account", "show", "--output", "json"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                account = json.loads(result.stdout)
                console.print("[green]✓ Authenticated with Azure[/green]")
                console.print(f"  Subscription: {account['name']} ({account['id']})")
                console.print(f"  Tenant: {account['tenantId']}")
                return True
            else:
                console.print("[red]✗ Not authenticated with Azure[/red]")
                console.print("Run: az login")
                return False

        except FileNotFoundError:
            console.print("[red]✗ Azure CLI not installed[/red]")
            console.print(
                "Install from: https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
            )
            return False
        except Exception as e:
            console.print(f"[red]✗ Error checking Azure credentials: {e}[/red]")
            return False

    def ensure_resource_group(self, name: str, location: str) -> bool:
        """Ensure resource group exists."""
        try:
            # Check if resource group exists
            result = subprocess.run(
                ["az", "group", "show", "--name", name, "--output", "json"],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                console.print(f"[green]✓ Resource group '{name}' exists[/green]")
                return True

            # Create resource group
            console.print(f"Creating resource group '{name}' in {location}...")
            result = subprocess.run(
                [
                    "az",
                    "group",
                    "create",
                    "--name",
                    name,
                    "--location",
                    location,
                    "--tags",
                    "managed-by=orchestr8",
                    f"environment={self.config.environment}",
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                console.print(f"[green]✓ Created resource group '{name}'[/green]")
                return True
            else:
                console.print(
                    f"[red]✗ Failed to create resource group: {result.stderr}[/red]"
                )
                return False

        except Exception as e:
            console.print(f"[red]✗ Error managing resource group: {e}[/red]")
            return False

    def get_aks_credentials(self, cluster_name: str, resource_group: str) -> bool:
        """Get AKS cluster credentials."""
        try:
            console.print(f"Getting credentials for AKS cluster '{cluster_name}'...")

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
                timeout=30,
            )

            if result.returncode == 0:
                console.print("[green]✓ Retrieved AKS credentials[/green]")
                return True
            else:
                console.print(
                    f"[red]✗ Failed to get AKS credentials: {result.stderr}[/red]"
                )
                return False

        except Exception as e:
            console.print(f"[red]✗ Error getting AKS credentials: {e}[/red]")
            return False

    def list_aks_clusters(self) -> List[Dict[str, Any]]:
        """List all AKS clusters in the subscription."""
        try:
            result = subprocess.run(
                ["az", "aks", "list", "--output", "json"],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                clusters = json.loads(result.stdout)
                return clusters
            else:
                console.print(
                    f"[red]✗ Failed to list AKS clusters: {result.stderr}[/red]"
                )
                return []

        except Exception as e:
            console.print(f"[red]✗ Error listing AKS clusters: {e}[/red]")
            return []

    def create_storage_account(
        self, name: str, resource_group: str, location: str
    ) -> Optional[str]:
        """Create storage account for Terraform state."""
        try:
            # Check if storage account exists
            result = subprocess.run(
                [
                    "az",
                    "storage",
                    "account",
                    "show",
                    "--name",
                    name,
                    "--resource-group",
                    resource_group,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                console.print(f"[green]✓ Storage account '{name}' exists[/green]")
                return name

            # Create storage account
            console.print(f"Creating storage account '{name}'...")
            result = subprocess.run(
                [
                    "az",
                    "storage",
                    "account",
                    "create",
                    "--name",
                    name,
                    "--resource-group",
                    resource_group,
                    "--location",
                    location,
                    "--sku",
                    "Standard_LRS",
                    "--kind",
                    "StorageV2",
                    "--encryption-services",
                    "blob",
                    "--tags",
                    "managed-by=orchestr8",
                    f"environment={self.config.environment}",
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                console.print(f"[green]✓ Created storage account '{name}'[/green]")

                # Create container for Terraform state
                console.print("Creating container 'tfstate'...")
                result = subprocess.run(
                    [
                        "az",
                        "storage",
                        "container",
                        "create",
                        "--name",
                        "tfstate",
                        "--account-name",
                        name,
                        "--auth-mode",
                        "login",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    console.print("[green]✓ Created container 'tfstate'[/green]")
                    return name
                else:
                    console.print(
                        "[yellow]⚠ Storage account created but container creation failed[/yellow]"
                    )
                    return name
            else:
                console.print(
                    f"[red]✗ Failed to create storage account: {result.stderr}[/red]"
                )
                return None

        except Exception as e:
            console.print(f"[red]✗ Error creating storage account: {e}[/red]")
            return None

    def create_key_vault(
        self, name: str, resource_group: str, location: str
    ) -> Optional[str]:
        """Create Key Vault for secrets management."""
        try:
            # Check if Key Vault exists
            result = subprocess.run(
                [
                    "az",
                    "keyvault",
                    "show",
                    "--name",
                    name,
                    "--resource-group",
                    resource_group,
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            if result.returncode == 0:
                console.print(f"[green]✓ Key Vault '{name}' exists[/green]")
                return name

            # Create Key Vault
            console.print(f"Creating Key Vault '{name}'...")
            result = subprocess.run(
                [
                    "az",
                    "keyvault",
                    "create",
                    "--name",
                    name,
                    "--resource-group",
                    resource_group,
                    "--location",
                    location,
                    "--enable-rbac-authorization",
                    "true",
                    "--enable-soft-delete",
                    "true",
                    "--retention-days",
                    "7",
                    "--tags",
                    "managed-by=orchestr8",
                    f"environment={self.config.environment}",
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                console.print(f"[green]✓ Created Key Vault '{name}'[/green]")
                return name
            else:
                console.print(
                    f"[red]✗ Failed to create Key Vault: {result.stderr}[/red]"
                )
                return None

        except Exception as e:
            console.print(f"[red]✗ Error creating Key Vault: {e}[/red]")
            return None

    def setup_workload_identity(
        self,
        cluster_name: str,
        resource_group: str,
        namespace: str,
        service_account: str,
    ) -> Optional[Dict[str, str]]:
        """Set up Azure AD Workload Identity for a service account."""
        try:
            # Create managed identity
            identity_name = f"{cluster_name}-{namespace}-{service_account}"
            console.print(f"Creating managed identity '{identity_name}'...")

            result = subprocess.run(
                [
                    "az",
                    "identity",
                    "create",
                    "--name",
                    identity_name,
                    "--resource-group",
                    resource_group,
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                console.print(
                    f"[red]✗ Failed to create managed identity: {result.stderr}[/red]"
                )
                return None

            identity = json.loads(result.stdout)
            client_id = identity["clientId"]
            principal_id = identity["principalId"]

            console.print(
                f"[green]✓ Created managed identity with client ID: {client_id}[/green]"
            )

            # Get OIDC issuer URL
            result = subprocess.run(
                [
                    "az",
                    "aks",
                    "show",
                    "--name",
                    cluster_name,
                    "--resource-group",
                    resource_group,
                    "--query",
                    "oidcIssuerProfile.issuerUrl",
                    "--output",
                    "tsv",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                console.print(
                    f"[red]✗ Failed to get OIDC issuer URL: {result.stderr}[/red]"
                )
                return None

            issuer_url = result.stdout.strip()

            # Create federated credential
            console.print(
                f"Creating federated credential for {namespace}/{service_account}..."
            )

            federated_config = {
                "name": f"{namespace}-{service_account}",
                "issuer": issuer_url,
                "subject": f"system:serviceaccount:{namespace}:{service_account}",
                "audiences": ["api://AzureADTokenExchange"],
            }

            # Save config to temp file
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump(federated_config, f)
                config_file = f.name

            try:
                result = subprocess.run(
                    [
                        "az",
                        "identity",
                        "federated-credential",
                        "create",
                        "--name",
                        f"{namespace}-{service_account}",
                        "--identity-name",
                        identity_name,
                        "--resource-group",
                        resource_group,
                        "--subject",
                        f"system:serviceaccount:{namespace}:{service_account}",
                        "--issuer",
                        issuer_url,
                        "--audiences",
                        "api://AzureADTokenExchange",
                    ],
                    capture_output=True,
                    text=True,
                    timeout=30,
                )

                if result.returncode == 0:
                    console.print("[green]✓ Created federated credential[/green]")
                else:
                    console.print(
                        f"[yellow]⚠ Failed to create federated credential: {result.stderr}[/yellow]"
                    )
            finally:
                os.unlink(config_file)

            return {
                "identity_name": identity_name,
                "client_id": client_id,
                "principal_id": principal_id,
            }

        except Exception as e:
            console.print(f"[red]✗ Error setting up workload identity: {e}[/red]")
            return None

    def get_cluster_info(
        self, cluster_name: str, resource_group: str
    ) -> Optional[Dict[str, Any]]:
        """Get detailed information about an AKS cluster."""
        try:
            result = subprocess.run(
                [
                    "az",
                    "aks",
                    "show",
                    "--name",
                    cluster_name,
                    "--resource-group",
                    resource_group,
                    "--output",
                    "json",
                ],
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode == 0:
                return json.loads(result.stdout)
            else:
                console.print(
                    f"[red]✗ Failed to get cluster info: {result.stderr}[/red]"
                )
                return None

        except Exception as e:
            console.print(f"[red]✗ Error getting cluster info: {e}[/red]")
            return None

    def validate_environment(self) -> bool:
        """Validate Azure environment is ready for Orchestr8."""
        console.print("\n[bold]Validating Azure Environment[/bold]")

        checks = []

        # Check Azure CLI
        try:
            result = subprocess.run(
                ["az", "--version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                checks.append(("Azure CLI", True, "Installed"))
            else:
                checks.append(("Azure CLI", False, "Not installed"))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            checks.append(("Azure CLI", False, "Not installed"))

        # Check authentication
        if self.validate_credentials():
            checks.append(("Authentication", True, "Valid"))
        else:
            checks.append(("Authentication", False, "Not authenticated"))

        # Check kubectl
        try:
            result = subprocess.run(
                ["kubectl", "version", "--client"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                checks.append(("kubectl", True, "Installed"))
            else:
                checks.append(("kubectl", False, "Not installed"))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            checks.append(("kubectl", False, "Not installed"))

        # Check Terraform
        try:
            result = subprocess.run(
                ["terraform", "version"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                checks.append(("Terraform", True, "Installed"))
            else:
                checks.append(("Terraform", False, "Not installed"))
        except (FileNotFoundError, subprocess.TimeoutExpired):
            checks.append(("Terraform", False, "Not installed"))

        # Display results
        table = Table(title="Azure Environment Check")
        table.add_column("Component", style="cyan")
        table.add_column("Status", style="bold")
        table.add_column("Details")

        all_valid = True
        for component, status, details in checks:
            status_str = "[green]✓[/green]" if status else "[red]✗[/red]"
            table.add_row(component, status_str, details)
            if not status:
                all_valid = False

        console.print(table)

        return all_valid
