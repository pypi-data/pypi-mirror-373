"""Orchestr8 Secrets Management with Native Python SDKs - No CLI dependencies required"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum
import typer
from typer import Option, Argument
import bcrypt
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm

# AWS SDK
import boto3
from botocore.exceptions import ClientError, NoCredentialsError

# Google Cloud SDK
from google.cloud import secretmanager
from google.api_core import exceptions as gcp_exceptions
from google.oauth2 import service_account
import google.auth


console = Console()
secrets = typer.Typer(
    help="Manage secrets with AWS and GCP (SDK-based, no CLI required)"
)


class Provider(str, Enum):
    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    BOTH = "both"


# Global context for storing common parameters
class SecretsContext:
    def __init__(self):
        self.project: Optional[str] = None
        self.region: Optional[str] = None
        self.credentials: Optional[str] = None
        self.key_vault_name: Optional[str] = None

    def setup_gcp(self) -> str:
        """Setup GCP authentication and return project ID"""
        if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            if self.credentials and Path(self.credentials).exists():
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
                    Path(self.credentials).absolute()
                )
            else:
                default_creds = Path.home() / ".gcp" / "o8-secrets-key.json"
                if default_creds.exists():
                    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(default_creds)

        return self.project or os.getenv("GOOGLE_CLOUD_PROJECT")

    def get_manager(self, provider: Provider):
        """Get the appropriate manager with auto-setup"""
        if provider == Provider.AWS:
            return AWSSecretsManager(region=self.region)
        elif provider == Provider.GCP:
            project = self.setup_gcp()
            return GCPSecretsManager(project_id=project)
        elif provider == Provider.AZURE:
            return AzureSecretsManager(key_vault_name=self.key_vault_name)
        else:
            raise ValueError(f"Unsupported provider: {provider}")


# Create a context instance
ctx = SecretsContext()


@secrets.callback()
def secrets_callback(
    project: Optional[str] = Option(
        None, "--project", envvar="GOOGLE_CLOUD_PROJECT", help="GCP project ID"
    ),
    region: Optional[str] = Option(
        None, "--region", envvar="AWS_REGION", help="AWS region"
    ),
    key_vault_name: Optional[str] = Option(
        None, "--key-vault", envvar="AZURE_KEY_VAULT_NAME", help="Azure Key Vault name"
    ),
    credentials: Optional[str] = Option(
        None,
        "--credentials",
        envvar="GOOGLE_APPLICATION_CREDENTIALS",
        help="Path to credentials file",
    ),
):
    """Common options for all secrets commands"""
    ctx.project = project
    ctx.region = region
    ctx.key_vault_name = key_vault_name
    ctx.credentials = credentials


class AWSSecretsManager:
    """AWS Secrets Manager using boto3 SDK"""

    def __init__(self, region: str = None, profile: str = None):
        self.region = region or os.getenv("AWS_REGION", "us-east-1")
        self.profile = profile or os.getenv("AWS_PROFILE")
        self.prefix = "o8/"

        try:
            if self.profile:
                session = boto3.Session(
                    profile_name=self.profile, region_name=self.region
                )
            else:
                session = boto3.Session(region_name=self.region)
            self.client = session.client("secretsmanager")
            self.sts = session.client("sts")

            # Verify credentials
            self.account_id = self.sts.get_caller_identity()["Account"]
            console.print(
                f"[green]✓ Connected to AWS Account: {self.account_id}[/green]"
            )
        except NoCredentialsError:
            console.print("[red]AWS credentials not found. Please configure:[/red]")
            console.print(
                "  Option 1: Set environment variables AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY"
            )
            console.print("  Option 2: Run 'aws configure' if AWS CLI is installed")
            console.print("  Option 3: Use IAM role if running on EC2")
            raise
        except ClientError as e:
            console.print(f"[red]AWS Error: {e}[/red]")
            raise

    def create_secret(
        self, name: str, data: Dict[str, Any], description: str = None
    ) -> bool:
        """Create or update a secret in AWS Secrets Manager"""
        full_name = f"{self.prefix}{name}"
        secret_string = json.dumps(data)

        try:
            # Try to create new secret
            self.client.create_secret(
                Name=full_name,
                Description=description or f"Orchestr8 managed secret: {name}",
                SecretString=secret_string,
            )
            console.print(
                f"[green]✓ Created secret '{full_name}' in AWS Secrets Manager[/green]"
            )
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceExistsException":
                # Secret exists, update it
                try:
                    self.client.update_secret(
                        SecretId=full_name, SecretString=secret_string
                    )
                    console.print(
                        f"[green]✓ Updated secret '{full_name}' in AWS Secrets Manager[/green]"
                    )
                    return True
                except ClientError as update_error:
                    console.print(f"[red]Failed to update secret: {update_error}[/red]")
                    return False
            else:
                console.print(f"[red]Failed to create secret: {e}[/red]")
                return False

    def get_secret(self, name: str) -> Optional[Dict]:
        """Retrieve a secret from AWS Secrets Manager"""
        full_name = f"{self.prefix}{name}"

        try:
            response = self.client.get_secret_value(SecretId=full_name)
            return json.loads(response["SecretString"])
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                console.print(f"[red]Secret not found: {full_name}[/red]")
            else:
                console.print(f"[red]Error retrieving secret: {e}[/red]")
            return None

    def list_secrets(self, prefix: str = None) -> List[Dict]:
        """List all secrets with optional prefix filter"""
        search_prefix = self.prefix + (prefix or "")
        secrets = []

        try:
            paginator = self.client.get_paginator("list_secrets")
            for page in paginator.paginate():
                for secret in page.get("SecretList", []):
                    if secret["Name"].startswith(search_prefix):
                        secrets.append(
                            {
                                "name": secret["Name"].replace(self.prefix, ""),
                                "full_name": secret["Name"],
                                "description": secret.get("Description", ""),
                                "last_changed": str(secret.get("LastChangedDate", "")),
                            }
                        )
        except ClientError as e:
            console.print(f"[red]Error listing secrets: {e}[/red]")

        return secrets

    def delete_secret(self, name: str, force: bool = True) -> bool:
        """Delete a secret from AWS Secrets Manager"""
        full_name = f"{self.prefix}{name}"

        try:
            if force:
                self.client.delete_secret(
                    SecretId=full_name, ForceDeleteWithoutRecovery=True
                )
            else:
                self.client.delete_secret(SecretId=full_name, RecoveryWindowInDays=7)
            console.print(f"[green]✓ Deleted secret '{full_name}'[/green]")
            return True
        except ClientError as e:
            console.print(f"[red]Failed to delete secret: {e}[/red]")
            return False


class GCPSecretsManager:
    """GCP Secret Manager using google-cloud-secret-manager SDK"""

    def __init__(self, project_id: str = None, credentials_path: str = None):
        self.project_id = (
            project_id or os.getenv("GOOGLE_CLOUD_PROJECT") or os.getenv("GCP_PROJECT")
        )
        self.prefix = "o8-"

        if not self.project_id:
            # Try to get from default credentials
            try:
                _, project = google.auth.default()
                self.project_id = project
            except Exception:
                console.print(
                    "[yellow]No GCP project specified. Set GOOGLE_CLOUD_PROJECT or use --project[/yellow]"
                )
                self.project_id = Prompt.ask("Enter your GCP project ID")

        try:
            if credentials_path:
                credentials = service_account.Credentials.from_service_account_file(
                    credentials_path
                )
                self.client = secretmanager.SecretManagerServiceClient(
                    credentials=credentials
                )
            else:
                # Use default credentials (gcloud auth, service account, etc.)
                self.client = secretmanager.SecretManagerServiceClient()

            self.parent = f"projects/{self.project_id}"
            console.print(
                f"[green]✓ Connected to GCP Project: {self.project_id}[/green]"
            )
        except Exception as e:
            console.print(f"[red]GCP Authentication Error: {e}[/red]")
            console.print("[yellow]Please configure GCP credentials:[/yellow]")
            console.print(
                "  Option 1: Set GOOGLE_APPLICATION_CREDENTIALS to service account key file"
            )
            console.print(
                "  Option 2: Run 'gcloud auth application-default login' if gcloud is installed"
            )
            console.print("  Option 3: Use service account if running on GCE/GKE")
            raise

    def create_secret(
        self, name: str, data: Dict[str, Any], description: str = None
    ) -> bool:
        """Create or update a secret in GCP Secret Manager"""
        full_name = f"{self.prefix}{name}"
        secret_id = full_name
        secret_data = json.dumps(data).encode("UTF-8")

        try:
            # Try to create the secret
            secret = self.client.create_secret(
                request={
                    "parent": self.parent,
                    "secret_id": secret_id,
                    "secret": {
                        "replication": {"automatic": {}},
                        "labels": {
                            "managed-by": "orchestr8",
                            "description": (description or "")[:63],
                        },
                    },
                }
            )

            # Add the secret version
            self.client.add_secret_version(
                request={"parent": secret.name, "payload": {"data": secret_data}}
            )
            console.print(
                f"[green]✓ Created secret '{secret_id}' in GCP Secret Manager[/green]"
            )
            return True

        except gcp_exceptions.AlreadyExists:
            # Secret exists, add new version
            try:
                secret_name = f"{self.parent}/secrets/{secret_id}"
                self.client.add_secret_version(
                    request={"parent": secret_name, "payload": {"data": secret_data}}
                )
                console.print(
                    f"[green]✓ Updated secret '{secret_id}' in GCP Secret Manager[/green]"
                )
                return True
            except Exception as e:
                console.print(f"[red]Failed to update secret: {e}[/red]")
                return False
        except Exception as e:
            console.print(f"[red]Failed to create secret: {e}[/red]")
            return False

    def get_secret(self, name: str, version: str = "latest") -> Optional[Dict]:
        """Retrieve a secret from GCP Secret Manager"""
        full_name = f"{self.prefix}{name}"
        secret_name = f"{self.parent}/secrets/{full_name}/versions/{version}"

        try:
            response = self.client.access_secret_version(request={"name": secret_name})
            secret_data = response.payload.data.decode("UTF-8")
            return json.loads(secret_data)
        except gcp_exceptions.NotFound:
            console.print(f"[red]Secret not found: {full_name}[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Error retrieving secret: {e}[/red]")
            return None

    def list_secrets(self, prefix: str = None) -> List[Dict]:
        """List all secrets with optional prefix filter"""
        search_prefix = self.prefix + (prefix or "")
        secrets = []

        try:
            for secret in self.client.list_secrets(request={"parent": self.parent}):
                secret_id = secret.name.split("/")[-1]
                if secret_id.startswith(search_prefix):
                    secrets.append(
                        {
                            "name": secret_id.replace(self.prefix, ""),
                            "full_name": secret_id,
                            "description": secret.labels.get("description", ""),
                            "create_time": str(secret.create_time),
                            "labels": dict(secret.labels),
                        }
                    )
        except Exception as e:
            console.print(f"[red]Error listing secrets: {e}[/red]")

        return secrets

    def delete_secret(self, name: str) -> bool:
        """Delete a secret from GCP Secret Manager"""
        full_name = f"{self.prefix}{name}"
        secret_name = f"{self.parent}/secrets/{full_name}"

        try:
            self.client.delete_secret(request={"name": secret_name})
            console.print(f"[green]✓ Deleted secret '{full_name}'[/green]")
            return True
        except Exception as e:
            console.print(f"[red]Failed to delete secret: {e}[/red]")
            return False


class AzureSecretsManager:
    """Azure Key Vault Secrets Manager using azure-keyvault-secrets SDK"""

    def __init__(self, key_vault_name: str = None):
        try:
            from azure.identity import DefaultAzureCredential
            from azure.keyvault.secrets import SecretClient
            # Import Azure exceptions for error handling (used in exception handling paths)
        except ImportError:
            console.print(
                "[red]Azure SDK not installed. Run: pip install azure-keyvault-secrets azure-identity[/red]"
            )
            raise

        self.key_vault_name = key_vault_name or os.getenv(
            "AZURE_KEY_VAULT_NAME", "o8-kv"
        )
        self.vault_url = f"https://{self.key_vault_name}.vault.azure.net/"
        self.prefix = "o8-"

        # Initialize Azure client with DefaultAzureCredential
        # This supports multiple authentication methods:
        # 1. Environment variables (service principal)
        # 2. Azure CLI
        # 3. Managed Identity
        # 4. Visual Studio Code
        try:
            self.credential = DefaultAzureCredential()
            self.client = SecretClient(
                vault_url=self.vault_url, credential=self.credential
            )

            # Test connection
            try:
                # Try to list secrets to verify access
                next(self.client.list_properties_of_secrets(), None)
                console.print(
                    f"[green]✓ Connected to Azure Key Vault: {self.key_vault_name}[/green]"
                )
            except StopIteration:
                # No secrets exist yet, but connection is valid
                console.print(
                    f"[green]✓ Connected to Azure Key Vault: {self.key_vault_name}[/green]"
                )
        except Exception as e:
            console.print(f"[red]Failed to connect to Azure Key Vault: {e}[/red]")
            console.print(
                "[yellow]Ensure you're authenticated with Azure CLI: az login[/yellow]"
            )
            raise

    def create_secret(self, name: str, value: str, **kwargs) -> Dict[str, Any]:
        """Create or update a secret in Azure Key Vault"""
        from azure.core.exceptions import HttpResponseError

        full_name = f"{self.prefix}{name}".replace(
            "_", "-"
        )  # Azure Key Vault requires hyphens

        try:
            # Set the secret
            secret = self.client.set_secret(full_name, value)

            console.print(
                f"[green]✓ Created/updated secret '{full_name}' in Azure Key Vault[/green]"
            )

            return {
                "name": secret.name,
                "version": secret.properties.version,
                "created_on": secret.properties.created_on.isoformat()
                if secret.properties.created_on
                else None,
                "updated_on": secret.properties.updated_on.isoformat()
                if secret.properties.updated_on
                else None,
            }
        except HttpResponseError as e:
            console.print(f"[red]Failed to create secret: {e}[/red]")
            raise

    def get_secret(self, name: str, version: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret from Azure Key Vault"""
        from azure.core.exceptions import ResourceNotFoundError

        full_name = f"{self.prefix}{name}".replace("_", "-")

        try:
            secret = self.client.get_secret(full_name, version=version)
            return secret.value
        except ResourceNotFoundError:
            console.print(f"[red]Secret '{full_name}' not found[/red]")
            return None
        except Exception as e:
            console.print(f"[red]Failed to get secret: {e}[/red]")
            return None

    def list_secrets(self) -> List[Dict[str, Any]]:
        """List all secrets in Azure Key Vault"""
        secrets = []

        try:
            # List all secrets
            for secret_properties in self.client.list_properties_of_secrets():
                if secret_properties.name.startswith(self.prefix):
                    secrets.append(
                        {
                            "name": secret_properties.name[len(self.prefix) :],
                            "full_name": secret_properties.name,
                            "enabled": secret_properties.enabled,
                            "created_on": secret_properties.created_on.isoformat()
                            if secret_properties.created_on
                            else None,
                            "updated_on": secret_properties.updated_on.isoformat()
                            if secret_properties.updated_on
                            else None,
                        }
                    )
        except Exception as e:
            console.print(f"[red]Failed to list secrets: {e}[/red]")

        return secrets

    def delete_secret(self, name: str) -> bool:
        """Delete a secret from Azure Key Vault (soft delete)"""
        from azure.core.exceptions import ResourceNotFoundError

        full_name = f"{self.prefix}{name}".replace("_", "-")

        try:
            # Begin deletion (soft delete)
            poller = self.client.begin_delete_secret(full_name)
            poller.result()

            console.print(
                f"[green]✓ Deleted secret '{full_name}' (soft delete)[/green]"
            )
            console.print(
                "[yellow]Note: Secret will be permanently deleted after retention period[/yellow]"
            )
            return True
        except ResourceNotFoundError:
            console.print(f"[red]Secret '{full_name}' not found[/red]")
            return False
        except Exception as e:
            console.print(f"[red]Failed to delete secret: {e}[/red]")
            return False


@secrets.command()
def init(
    provider: Provider = Option(
        Provider.AWS, "--provider", "-p", help="Cloud provider"
    ),
    project: Optional[str] = Option(None, "--project", help="GCP project ID"),
    region: Optional[str] = Option(None, "--region", help="AWS region"),
    key_vault_name: Optional[str] = Option(
        None, "--key-vault", help="Azure Key Vault name"
    ),
    credentials: Optional[str] = Option(
        None, "--credentials", help="Path to credentials file"
    ),
):
    """Initialize and test connection to secrets provider"""
    console.print(
        f"[bold]Initializing {provider.value.upper()} Secrets Manager...[/bold]"
    )

    try:
        if provider == Provider.AWS or provider == Provider.BOTH:
            AWSSecretsManager(region=region)
            console.print("[green]✓ AWS Secrets Manager ready[/green]")

        if provider == Provider.GCP or provider == Provider.BOTH:
            GCPSecretsManager(project_id=project, credentials_path=credentials)
            console.print("[green]✓ GCP Secret Manager ready[/green]")

        if provider == Provider.AZURE:
            AzureSecretsManager(key_vault_name=key_vault_name)
            console.print("[green]✓ Azure Key Vault ready[/green]")

        console.print(
            "\n[bold green]Secrets management initialized successfully![/bold green]"
        )
        console.print("\nYou can now use:")
        console.print("  o8 secrets create <name> --provider <aws|gcp|azure>")
        console.print("  o8 secrets list --provider <aws|gcp|azure>")
        console.print("  o8 secrets get <name> --provider <aws|gcp|azure>")

    except Exception as e:
        console.print(f"[red]Initialization failed: {e}[/red]")
        raise typer.Exit(1)


@secrets.command()
def create(
    name: str = Argument(..., help="Secret name (without prefix)"),
    provider: Provider = Option(..., "--provider", "-p", help="Cloud provider"),
    data: Optional[str] = Option(
        None, "--data", "-d", help="JSON data or @filename or key=value,key2=value2"
    ),
    interactive: bool = Option(False, "--interactive", "-i", help="Interactive mode"),
    description: Optional[str] = Option(
        None, "--description", help="Secret description"
    ),
):
    """Create or update a secret"""
    if provider == Provider.BOTH:
        console.print("[red]Please specify either 'aws' or 'gcp'[/red]")
        raise typer.Exit(1)

    # Parse secret data
    secret_data = {}

    if interactive or (not data):
        console.print(
            "[cyan]Enter secret key-value pairs (empty key to finish):[/cyan]"
        )
        while True:
            key = Prompt.ask("Key", default="")
            if not key:
                break
            hide_input = (
                "password" in key.lower()
                or "secret" in key.lower()
                or "key" in key.lower()
            )
            value = Prompt.ask(f"Value for '{key}'", password=hide_input)
            secret_data[key] = value
    elif data:
        if data.startswith("@"):
            # Read from file
            file_path = Path(data[1:])
            if file_path.exists():
                with open(file_path, "r") as f:
                    secret_data = json.load(f)
            else:
                console.print(f"[red]File not found: {file_path}[/red]")
                raise typer.Exit(1)
        else:
            # Try parsing as JSON first
            try:
                secret_data = json.loads(data)
            except json.JSONDecodeError:
                # Try key=value format
                if "=" in data:
                    for pair in data.split(","):
                        if "=" in pair:
                            key, value = pair.strip().split("=", 1)
                            secret_data[key.strip()] = value.strip()
                else:
                    console.print(
                        "[red]Invalid data format. Use JSON, @filename, or key=value,key2=value2[/red]"
                    )
                    raise typer.Exit(1)

    if not secret_data:
        console.print("[red]No secret data provided[/red]")
        raise typer.Exit(1)

    # Handle password hashing
    if "password" in name.lower() or any("password" in k.lower() for k in secret_data):
        for key in list(secret_data.keys()):
            if "password" in key.lower() and not key.endswith("_hash"):
                if Confirm.ask(f"Hash password for '{key}'?", default=True):
                    hashed = bcrypt.hashpw(
                        secret_data[key].encode("utf-8"), bcrypt.gensalt()
                    )
                    secret_data[f"{key}_bcrypt"] = hashed.decode("utf-8")

    # Create the secret
    try:
        mgr = ctx.get_manager(provider)

        if mgr.create_secret(name, secret_data, description):
            console.print(
                f"\n[bold green]Secret '{name}' created successfully![/bold green]"
            )
    except Exception as e:
        console.print(f"[red]Failed to create secret: {e}[/red]")
        raise typer.Exit(1)


@secrets.command("test")
def test_connection(
    provider: Provider = Option(..., "--provider", "-p", help="Cloud provider to test"),
):
    """Test connection to secrets provider"""
    try:
        mgr = ctx.get_manager(provider)

        if provider == Provider.AWS:
            console.print("[green]✓ Connected to AWS Secrets Manager[/green]")
            console.print(f"  Account: {mgr.account_id}")
            console.print(f"  Region: {mgr.region}")
        elif provider == Provider.GCP:
            console.print("[green]✓ Connected to GCP Secret Manager[/green]")
            console.print(f"  Project: {mgr.project_id}")

            # Try to list secrets to verify permissions
            secrets = mgr.list_secrets()
            console.print(f"  Secrets count: {len(secrets)}")
    except Exception as e:
        console.print(f"[red]Connection failed: {e}[/red]")
        raise typer.Exit(1)


@secrets.command("list")
def list_secrets(
    provider: Provider = Option(
        Provider.BOTH, "--provider", "-p", help="Cloud provider"
    ),
    prefix: Optional[str] = Option(None, "--prefix", help="Filter by prefix"),
):
    """List secrets from provider(s)"""

    table = Table(title="Orchestr8 Secrets")
    table.add_column("Provider", style="cyan")
    table.add_column("Name", style="green")
    table.add_column("Full Name", style="dim")
    table.add_column("Description", style="yellow")

    providers_to_check = []
    if provider == Provider.BOTH:
        providers_to_check = [Provider.AWS, Provider.GCP]
    else:
        providers_to_check = [provider]

    for prov in providers_to_check:
        try:
            mgr = ctx.get_manager(prov)

            secrets = mgr.list_secrets(prefix=prefix)
            for secret in secrets:
                table.add_row(
                    prov.value.upper(),
                    secret["name"],
                    secret["full_name"],
                    secret.get("description", "")[:50],
                )
        except Exception as e:
            console.print(f"[yellow]Could not list {prov.value} secrets: {e}[/yellow]")

    console.print(table)


@secrets.command("get")
def get_secret(
    name: str = Argument(..., help="Secret name"),
    provider: Provider = Option(..., "--provider", "-p", help="Cloud provider"),
    show_values: bool = Option(False, "--show-values", help="Display values"),
    output: Optional[str] = Option(
        None, "--output", "-o", help="Output format (json, yaml)"
    ),
):
    """Retrieve and display a secret"""
    if provider == Provider.BOTH:
        console.print("[red]Please specify either 'aws' or 'gcp'[/red]")
        raise typer.Exit(1)

    try:
        mgr = ctx.get_manager(provider)

        secret = mgr.get_secret(name)

        if secret:
            if output == "json":
                console.print(json.dumps(secret, indent=2))
            elif output == "yaml":
                import yaml

                console.print(yaml.dump(secret, default_flow_style=False))
            else:
                console.print(f"\n[bold]Secret: {name}[/bold]")
                console.print(f"Provider: {provider.value.upper()}")
                console.print(f"Keys: {', '.join(secret.keys())}")

                if show_values:
                    console.print("\n[yellow]Values:[/yellow]")
                    for key, value in secret.items():
                        # Mask sensitive values
                        if any(
                            sensitive in key.lower()
                            for sensitive in ["password", "secret", "key", "token"]
                        ):
                            if len(str(value)) > 10:
                                masked = (
                                    str(value)[:3]
                                    + "*" * (len(str(value)) - 6)
                                    + str(value)[-3:]
                                )
                            else:
                                masked = "*" * len(str(value))
                            console.print(f"  {key}: {masked}")
                        else:
                            console.print(f"  {key}: {value}")
        else:
            console.print(f"[red]Secret not found: {name}[/red]")

    except Exception as e:
        console.print(f"[red]Failed to get secret: {e}[/red]")
        raise typer.Exit(1)


@secrets.command()
def delete(
    name: str = Argument(..., help="Secret name"),
    provider: Provider = Option(..., "--provider", "-p", help="Cloud provider"),
    yes: bool = Option(False, "--yes", "-y", help="Skip confirmation"),
):
    """Delete a secret"""
    if provider == Provider.BOTH:
        console.print("[red]Please specify either 'aws' or 'gcp'[/red]")
        raise typer.Exit(1)

    if not yes:
        if not Confirm.ask(f"Delete secret '{name}' from {provider.value.upper()}?"):
            raise typer.Abort()

    try:
        mgr = ctx.get_manager(provider)
        mgr.delete_secret(name)

    except Exception as e:
        console.print(f"[red]Failed to delete secret: {e}[/red]")
        raise typer.Exit(1)


@secrets.command()
def setup(
    provider: Provider = Option(
        ..., "--provider", "-p", help="Cloud provider to setup"
    ),
    project: Optional[str] = Option(None, "--project", help="GCP project ID"),
    key_file: Optional[str] = Option(
        None, "--key-file", help="Path to service account key file"
    ),
    auto_open: bool = Option(
        True, "--auto-open/--no-open", help="Auto-open browser for setup"
    ),
):
    """Quick setup for cloud provider authentication"""

    if provider == Provider.GCP:
        project_id = project

        # Quick auth check
        try:
            mgr = GCPSecretsManager(project_id=project_id)
            console.print(
                f"[green]✓ Already authenticated for project: {project_id}[/green]"
            )
            return
        except Exception:
            pass

        # If key file provided, just set it up
        if key_file:
            if Path(key_file).exists():
                os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
                    Path(key_file).absolute()
                )
                os.environ["GOOGLE_CLOUD_PROJECT"] = project_id

                # Test connection
                try:
                    mgr = GCPSecretsManager(project_id=project_id)
                    console.print(
                        f"[green]✓ Setup complete! Project: {project_id}[/green]"
                    )

                    # Save to user's .gcp directory
                    import platform

                    if platform.system() == "Windows":
                        dest_path = Path(
                            f"C:\\Users\\{os.environ.get('USERNAME')}\\.gcp\\o8-secrets-key.json"
                        )
                    else:
                        dest_path = Path.home() / ".gcp" / "o8-secrets-key.json"

                    dest_path.parent.mkdir(exist_ok=True)
                    import shutil

                    shutil.copy2(key_file, dest_path)
                    console.print(f"[dim]Key saved to: {dest_path}[/dim]")

                    # Set permanent env vars on Windows
                    if platform.system() == "Windows":
                        import subprocess

                        subprocess.run(
                            f'setx GOOGLE_APPLICATION_CREDENTIALS "{dest_path}"',
                            shell=True,
                            capture_output=True,
                        )
                        subprocess.run(
                            f'setx GOOGLE_CLOUD_PROJECT "{project_id}"',
                            shell=True,
                            capture_output=True,
                        )
                        console.print(
                            "[dim]Environment variables set (restart terminal to use)[/dim]"
                        )

                    return
                except Exception as e:
                    console.print(f"[red]Authentication failed: {e}[/red]")
            else:
                console.print(f"[red]Key file not found: {key_file}[/red]")
                raise typer.Exit(1)

        # Interactive setup
        console.print(f"[yellow]Setup GCP Secrets for project: {project_id}[/yellow]\n")

        if auto_open:
            import webbrowser

            url = f"https://console.cloud.google.com/iam-admin/serviceaccounts?project={project_id}"
            webbrowser.open(url)
            console.print("[green]✓ Opened GCP Console[/green]")

        console.print("\n1. Create service account: [cyan]o8-secrets-manager[/cyan]")
        console.print("2. Grant role: [cyan]Secret Manager Admin[/cyan]")
        console.print("3. Download JSON key")
        console.print(
            "\nThen run: [yellow]o8 secrets setup --provider gcp --key-file <path-to-key.json>[/yellow]"
        )

    elif provider == Provider.AWS:
        # Quick auth check
        try:
            mgr = AWSSecretsManager()
            console.print(
                f"[green]✓ Already authenticated! Account: {mgr.account_id}[/green]"
            )
            return
        except Exception:
            pass

        console.print("[yellow]AWS Setup Required[/yellow]")
        console.print("\nSet environment variables:")
        console.print("  export AWS_ACCESS_KEY_ID=<your-key>")
        console.print("  export AWS_SECRET_ACCESS_KEY=<your-secret>")
        console.print("  export AWS_REGION=us-east-1")
        console.print("\nThen run: [yellow]o8 secrets init --provider aws[/yellow]")


@secrets.command()
def rotate(
    name: str = Argument(..., help="Secret name to rotate"),
    provider: Provider = Option(None, "--provider", "-p", help="Cloud provider"),
):
    """Rotate a secret (coming soon)"""
    console.print(f"Rotating {name} coming soon!")


@secrets.command()
def configure(
    provider: Provider = Option(
        ..., "--provider", "-p", help="Cloud provider to configure"
    ),
):
    """Interactive configuration wizard for cloud providers"""
    console.print(
        f"[bold cyan]Configuring {provider.value.upper()} Secrets Management[/bold cyan]\n"
    )

    if provider == Provider.AWS:
        console.print("[yellow]AWS Configuration Options:[/yellow]")
        console.print("1. Use existing AWS CLI configuration")
        console.print("2. Set environment variables")
        console.print("3. Use IAM role (EC2/ECS/Lambda)")

        choice = Prompt.ask("Choose option", choices=["1", "2", "3"], default="1")

        if choice == "2":
            console.print("\n[cyan]Set these environment variables:[/cyan]")
            console.print("export AWS_ACCESS_KEY_ID=your-access-key")
            console.print("export AWS_SECRET_ACCESS_KEY=your-secret-key")
            console.print("export AWS_REGION=us-east-1")
        elif choice == "1":
            console.print("\n[cyan]Using AWS CLI configuration[/cyan]")
            console.print("Run: aws configure")
        else:
            console.print("\n[cyan]IAM role will be used automatically[/cyan]")

    elif provider == Provider.GCP:
        console.print("[yellow]GCP Configuration Options:[/yellow]")
        console.print("1. Use service account key file")
        console.print("2. Use gcloud default credentials")
        console.print("3. Use GCE/GKE metadata service")

        choice = Prompt.ask("Choose option", choices=["1", "2", "3"], default="1")

        if choice == "1":
            key_path = Prompt.ask("Path to service account key JSON file")
            if Path(key_path).exists():
                console.print("\n[cyan]Set environment variable:[/cyan]")
                console.print(f"export GOOGLE_APPLICATION_CREDENTIALS={key_path}")
            else:
                console.print(f"[red]File not found: {key_path}[/red]")
        elif choice == "2":
            console.print("\n[cyan]Using gcloud default credentials[/cyan]")
            console.print("Run: gcloud auth application-default login")
        else:
            console.print(
                "\n[cyan]GCE/GKE metadata service will be used automatically[/cyan]"
            )

    console.print("\n[green]Configuration complete! Test with:[/green]")
    console.print(f"o8 secrets init --provider {provider.value}")


if __name__ == "__main__":
    secrets()
