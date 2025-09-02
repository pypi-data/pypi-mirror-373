"""Core orchestrator for Orchestr8 platform setup and management."""

import os
import subprocess
from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml

from kubernetes import client, config as k8s_config
from kubernetes.client.rest import ApiException
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .config import Config
from .secrets import SecretsManager
from .terraform import TerraformManager
from ..providers.github import GitHubProvider


class Orchestrator:
    """Core orchestrator that handles platform setup and management."""

    def _get_github_token(self) -> Optional[str]:
        """Get GitHub token from multiple sources (config, env, gh CLI)."""
        # 1. Try to get from config
        if self.config.github and self.config.github.token:
            return self.config.github.token

        # 2. Try to get from environment
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            return github_token

        # 3. Try to get from gh CLI
        try:
            result = subprocess.run(
                ["gh", "auth", "token"], capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def __init__(self, config: Config, console: Optional[Console] = None):
        self.config = config
        self.console = console or Console()
        self.secrets_manager = SecretsManager(config)

        try:
            self.terraform_manager = TerraformManager(console)
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Could not initialize Terraform manager: {e}[/yellow]"
            )
            self.terraform_manager = None

        self.github_provider = (
            GitHubProvider(config.github.token) if config.github.token else None
        )

        # Initialize Kubernetes client
        try:
            k8s_config.load_kube_config()
            self.k8s_api = client.CoreV1Api()
            self.k8s_apps_api = client.AppsV1Api()
        except Exception as e:
            self.console.print(
                f"[red]⚠️ Warning: Could not load Kubernetes config: {e}[/red]"
            )
            self.k8s_api = None
            self.k8s_apps_api = None

    async def setup_with_infrastructure(self) -> Dict[str, Any]:
        """Run complete setup including infrastructure provisioning."""
        results = {}

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,
        ) as progress:
            # Phase 1: Provision Infrastructure (if needed)
            if (
                self.config.provider.value == "gcp"
                and self.config.provision_infrastructure
            ):
                if not self.terraform_manager:
                    raise Exception(
                        "Terraform manager not initialized. Check Terraform installation."
                    )
                task = progress.add_task(
                    "Provisioning GCP infrastructure...", total=None
                )
                infra_result = await self.terraform_manager.provision_infrastructure(
                    provider="gcp",
                    project_id=self.config.gcp_project_id,
                    region=self.config.region,
                    cluster_name=self.config.cluster_name,
                    environment=self.config.environment,
                    github_org=self.config.github.org,
                    argocd_repo_url=f"https://github.com/{self.config.github.org}/orchestr8",
                )

                if not infra_result["success"]:
                    raise RuntimeError(
                        f"Infrastructure provisioning failed: {infra_result['error']}"
                    )

                progress.update(task, completed=True)
                results["infrastructure"] = infra_result

                # ArgoCD is already installed by Terraform
                results["argocd"] = {
                    "installed": True,
                    "admin_password": infra_result.get("argocd_password"),
                    "method": "terraform",
                }

                # Apply bootstrap ArgoCD app
                task = progress.add_task(
                    "Deploying Orchestr8 platform via ArgoCD...", total=None
                )
                subprocess.run(
                    [
                        "kubectl",
                        "apply",
                        "-f",
                        str(
                            Path(__file__).parent.parent.parent.parent.parent
                            / "argocd-apps"
                            / "bootstrap.yaml"
                        ),
                    ],
                    check=True,
                )
                progress.update(task, completed=True)

                results["platform"] = {"deployed": True, "method": "argocd-bootstrap"}
            else:
                # Traditional setup without infrastructure provisioning
                return await self.setup()

        return results

    async def setup(self) -> Dict[str, Any]:
        """Run the platform setup process (without infrastructure)."""
        results = {}

        # Show setup info
        if self.config.is_local:
            self.console.print(
                "[dim]→ Auto-generating secure passwords for local setup[/dim]"
            )
        else:
            self.console.print(
                f"[dim]→ Storing secrets in cloud secrets manager ({self.config.region})[/dim]"
            )

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,  # This makes the progress bar disappear after completion
        ) as progress:
            # Validate prerequisites
            task = progress.add_task("Validating prerequisites...", total=None)
            prereq_result = await self.validate_prerequisites()
            if not prereq_result["valid"]:
                raise RuntimeError(
                    f"Prerequisites validation failed: {prereq_result['errors']}"
                )
            progress.update(task, completed=True)
            results["prerequisites"] = prereq_result

            # Ensure secrets
            task = progress.add_task("Managing secrets...", total=None)
            secrets = await self.secrets_manager.ensure_all_secrets()
            progress.update(task, completed=True)
            results["secrets"] = {"count": len(secrets), "created": True}

            # Create namespaces
            task = progress.add_task("Creating namespaces...", total=None)
            namespaces = await self.create_namespaces()
            progress.update(task, completed=True)
            results["namespaces"] = namespaces

            # Create Kubernetes secrets
            task = progress.add_task("Creating Kubernetes secrets...", total=None)
            k8s_secrets = await self.create_kubernetes_secrets()
            progress.update(task, completed=True)
            results["kubernetes_secrets"] = k8s_secrets

            # Configure ArgoCD repository access if GitHub token provided
            if self.config.github.token:
                task = progress.add_task(
                    "Configuring ArgoCD repository access...", total=None
                )
                repo_config = await self.configure_argocd_repo()
                progress.update(task, completed=True)
                results["argocd_repo"] = repo_config

            # Install Istio
            task = progress.add_task("Installing Istio service mesh...", total=None)
            istio_result = await self.install_istio()
            progress.update(task, completed=True)
            results["istio"] = istio_result

            # Install ArgoCD
            task = progress.add_task("Installing ArgoCD...", total=None)
            argocd_result = await self.install_argocd()
            progress.update(task, completed=True)
            results["argocd"] = argocd_result

            # Configure ArgoCD repositories (essential for platform dependencies)
            task = progress.add_task(
                "Configuring ArgoCD Helm repositories...", total=None
            )
            repos_result = await self.configure_argocd_helm_repos()
            progress.update(task, completed=True)
            results["repositories"] = repos_result

            # Verify ArgoCD API access and bootstrap authentication
            task = progress.add_task("Verifying ArgoCD API access...", total=None)
            api_result = await self.bootstrap_argocd_api()
            progress.update(task, completed=True)
            results["argocd_api"] = api_result

            # Deploy platform
            task = progress.add_task("Deploying platform...", total=None)
            platform_result = await self.deploy_platform()
            progress.update(task, completed=True)
            results["platform"] = platform_result

            # Deploy Llama Stack AI runtime (local only)
            if self.config.is_local:
                task = progress.add_task("Deploying Llama Stack AI runtime...", total=None)
                llama_result = await self.deploy_llama_stack()
                progress.update(task, completed=True)
                results["llama_stack"] = llama_result

            # Configure local development access (Docker Desktop)
            if self.config.is_local:
                task = progress.add_task(
                    "Configuring local development access...", total=None
                )
                local_access = await self.configure_local_access()
                progress.update(task, completed=True)
                results["local_access"] = local_access

        return results

    async def validate_prerequisites(self) -> Dict[str, Any]:
        """Validate that all prerequisites are met."""
        errors = []
        warnings = []

        # Check kubectl
        if not self._command_exists("kubectl"):
            errors.append("kubectl not found in PATH")

        # Check helm
        if not self._command_exists("helm"):
            errors.append("helm not found in PATH")

        # Check Kubernetes connection
        if self.k8s_api:
            try:
                self.k8s_api.list_namespace()
            except Exception as e:
                errors.append(f"Cannot connect to Kubernetes cluster: {e}")
        else:
            errors.append("Kubernetes client not initialized")

        # Check GitHub token if provided
        if self.github_provider:
            try:
                await self.github_provider.validate_token()
            except Exception as e:
                warnings.append(f"GitHub token validation failed: {e}")

        return {"valid": len(errors) == 0, "errors": errors, "warnings": warnings}

    async def create_namespaces(self) -> List[str]:
        """Create required namespaces."""
        namespaces = [
            "argocd",
            "platform",
            "istio-system",
            "keycloak",
            "auth",
            "cert-manager",
        ]

        created = []
        for ns in namespaces:
            try:
                self.k8s_api.create_namespace(
                    client.V1Namespace(metadata=client.V1ObjectMeta(name=ns))
                )
                created.append(ns)
            except ApiException as e:
                if e.status == 409:  # Already exists
                    pass
                else:
                    raise

        return created

    async def create_kubernetes_secrets(self) -> Dict[str, bool]:
        """Create Kubernetes secrets from secrets manager."""
        k8s_secrets = await self.secrets_manager.export_kubernetes_secrets()
        results = {}

        for secret_name, secret_config in k8s_secrets.items():
            namespace = secret_config["namespace"]
            data = secret_config["data"]

            # Convert to base64
            import base64

            encoded_data = {
                k: base64.b64encode(v.encode()).decode() for k, v in data.items()
            }

            try:
                self.k8s_api.create_namespaced_secret(
                    namespace=namespace,
                    body=client.V1Secret(
                        metadata=client.V1ObjectMeta(name=secret_name),
                        type="Opaque",
                        data=encoded_data,
                    ),
                )
                results[f"{namespace}/{secret_name}"] = True
            except ApiException as e:
                if e.status == 409:  # Already exists
                    # Update it
                    self.k8s_api.patch_namespaced_secret(
                        name=secret_name,
                        namespace=namespace,
                        body=client.V1Secret(data=encoded_data),
                    )
                    results[f"{namespace}/{secret_name}"] = True
                else:
                    results[f"{namespace}/{secret_name}"] = False

        return results

    async def install_istio(self) -> Dict[str, Any]:
        """Install Istio service mesh."""
        # Add Istio Helm repo
        subprocess.run(
            [
                "helm",
                "repo",
                "add",
                "istio",
                "https://istio-release.storage.googleapis.com/charts",
            ],
            check=True,
        )
        subprocess.run(["helm", "repo", "update"], check=True)

        # Install Istio base (CRDs)
        subprocess.run(
            [
                "helm",
                "upgrade",
                "--install",
                "istio-base",
                "istio/base",
                "--namespace",
                "istio-system",
                "--create-namespace",
                "--version",
                "1.26.3",
                "--wait",
            ],
            check=True,
        )

        # Install Istiod (control plane)
        istio_values = {
            "pilot": {
                "autoscaleEnabled": False,
                "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}},
            }
        }

        # Write values to temp file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(istio_values, f)
            values_file = f.name

        try:
            subprocess.run(
                [
                    "helm",
                    "upgrade",
                    "--install",
                    "istiod",
                    "istio/istiod",
                    "--namespace",
                    "istio-system",
                    "--version",
                    "1.26.3",
                    "-f",
                    values_file,
                    "--wait",
                ],
                check=True,
            )

            # Optionally install ingress gateway for local development
            if self.config.is_local:
                gateway_values = {
                    "service": {
                        "type": "NodePort",
                        "ports": [
                            {
                                "port": 80,
                                "targetPort": 8080,
                                "nodePort": 30090,
                                "name": "http2",
                            },
                            {
                                "port": 443,
                                "targetPort": 8443,
                                "nodePort": 30443,
                                "name": "https",
                            },
                        ],
                    },
                    "resources": {"requests": {"cpu": "100m", "memory": "128Mi"}},
                }

                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".yaml", delete=False
                ) as f:
                    yaml.dump(gateway_values, f)
                    gateway_values_file = f.name

                try:
                    subprocess.run(
                        [
                            "helm",
                            "upgrade",
                            "--install",
                            "istio-ingressgateway",
                            "istio/gateway",
                            "--namespace",
                            "istio-system",
                            "--version",
                            "1.26.3",
                            "-f",
                            gateway_values_file,
                            "--wait",
                        ],
                        check=True,
                    )
                finally:
                    Path(gateway_values_file).unlink()

            return {"installed": True, "namespace": "istio-system", "version": "1.26.3"}
        finally:
            Path(values_file).unlink()

    async def install_argocd(self) -> Dict[str, Any]:
        """Install ArgoCD using Helm."""
        # Add Helm repo
        subprocess.run(
            ["helm", "repo", "add", "argo", "https://argoproj.github.io/argo-helm"],
            check=True,
        )
        subprocess.run(["helm", "repo", "update"], check=True)

        # Install ArgoCD
        # Get ArgoCD ports from environment or use defaults
        argocd_http_port = int(os.getenv("O8_ARGOCD_HTTP_PORT", "30080"))
        argocd_https_port = int(
            os.getenv("O8_ARGOCD_HTTPS_PORT", "30444")
        )  # Avoid conflict with Istio's 30443

        helm_values = {
            "server": {
                "service": {
                    "type": "NodePort" if self.config.is_local else "LoadBalancer",
                    "nodePortHttp": argocd_http_port if self.config.is_local else None,
                    "nodePortHttps": argocd_https_port
                    if self.config.is_local
                    else None,
                },
                "extraArgs": ["--insecure"],
            }
        }

        # Write values to temp file
        import tempfile

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(helm_values, f)
            values_file = f.name

        try:
            # Get ArgoCD version from environment or use latest stable
            argocd_version = os.getenv("O8_ARGOCD_VERSION", "8.2.5")

            subprocess.run(
                [
                    "helm",
                    "upgrade",
                    "--install",
                    "argocd",
                    "argo/argo-cd",
                    "--namespace",
                    "argocd",
                    "--version",
                    argocd_version,
                    "-f",
                    values_file,
                    "--wait",
                ],
                check=True,
            )

            # Get admin password
            result = subprocess.run(
                [
                    "kubectl",
                    "-n",
                    "argocd",
                    "get",
                    "secret",
                    "argocd-initial-admin-secret",
                    "-o",
                    "jsonpath={.data.password}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                import base64

                password = base64.b64decode(result.stdout).decode()
            else:
                password = None

            return {
                "installed": True,
                "admin_password": password,
                "url": f"http://localhost:{argocd_http_port}"
                if self.config.is_local
                else f"https://argocd.{self.config.domain}",
            }
        finally:
            Path(values_file).unlink()

    async def deploy_platform(self) -> Dict[str, Any]:
        """Deploy the Orchestr8 platform via ArgoCD."""
        # First, ensure platform Helm templates exist to disable default deployment
        await self._ensure_platform_templates()

        # Get GitHub token from multiple sources
        github_token = self._get_github_token()
        if github_token:
            self.console.print("[green]✓[/green] GitHub token found")

        # Only create repository secret if we have a token
        if github_token:
            repo_secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": "orchestr8-repo",
                    "namespace": "argocd",
                    "labels": {"argocd.argoproj.io/secret-type": "repository"},
                },
                "stringData": {
                    "type": "git",
                    "url": "https://github.com/killerapp/orchestr8.git",
                    "username": "not-used",  # GitHub token auth doesn't use username
                    "password": github_token,
                },
            }

            # Apply repository secret
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                yaml.dump(repo_secret, f)
                repo_file = f.name

            try:
                result = subprocess.run(
                    ["kubectl", "apply", "-f", repo_file],
                    capture_output=True,
                    text=True,
                )

                # If validation fails due to API server issues, try with bypass
                if result.returncode != 0 and (
                    "TLS handshake timeout" in result.stderr
                    or "connection refused" in result.stderr
                ):
                    self.console.print(
                        "[yellow]⚠ API server connectivity issue, retrying with validation bypass...[/yellow]"
                    )
                    result = subprocess.run(
                        ["kubectl", "apply", "-f", repo_file, "--validate=false"],
                        capture_output=True,
                        text=True,
                    )

                if result.returncode == 0:
                    self.console.print("[green]✓[/green] Repository secret configured")
                else:
                    raise subprocess.CalledProcessError(
                        result.returncode, "kubectl apply", result.stderr
                    )
            finally:
                Path(repo_file).unlink()
        else:
            self.console.print(
                "[yellow]⚠[/yellow] No GitHub token found - repository may be inaccessible if private"
            )
            self.console.print(
                "  Configure with: [cyan]o8 auth --github-org killerapp[/cyan]"
            )
            self.console.print("  Or: [cyan]gh auth login[/cyan]")

        # Create platform application
        platform_app = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {"name": "orchestr8-platform", "namespace": "argocd"},
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": "https://github.com/killerapp/orchestr8",
                    "targetRevision": "main",
                    "path": "platform",
                    "helm": {
                        "valueFiles": [
                            "values.yaml",
                            "values-local.yaml"
                            if self.config.is_local
                            else "values-production.yaml",
                        ]
                    },
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": "platform",
                },
                "syncPolicy": {
                    "automated": {"prune": False, "selfHeal": False},
                    "syncOptions": ["CreateNamespace=true", "ServerSideApply=true"],
                },
            },
        }

        # Apply platform application
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(platform_app, f)
            app_file = f.name

        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", app_file], capture_output=True, text=True
            )

            # If validation fails due to API server issues, try with bypass
            if result.returncode != 0 and (
                "TLS handshake timeout" in result.stderr
                or "connection refused" in result.stderr
            ):
                self.console.print(
                    "[yellow]⚠ API server connectivity issue, retrying with validation bypass...[/yellow]"
                )
                result = subprocess.run(
                    ["kubectl", "apply", "-f", app_file, "--validate=false"],
                    capture_output=True,
                    text=True,
                )

            if result.returncode == 0:
                return {"deployed": True, "application": "orchestr8-platform"}
            else:
                raise subprocess.CalledProcessError(
                    result.returncode, "kubectl apply", result.stderr
                )
        finally:
            Path(app_file).unlink()

    async def deploy_llama_stack(self) -> Dict[str, Any]:
        """Deploy Llama Stack AI runtime for local development."""
        import tempfile
        
        # Only deploy for local environments
        if not self.config.is_local:
            return {"deployed": False, "reason": "Llama Stack only deployed for local environments"}
        
        # Create Llama Stack application with local overlay
        llama_stack_app = {
            "apiVersion": "argoproj.io/v1alpha1",
            "kind": "Application",
            "metadata": {
                "name": "llama-stack-local",
                "namespace": "argocd",
                "labels": {
                    "app.kubernetes.io/name": "llama-stack",
                    "app.kubernetes.io/part-of": "orchestr8",
                    "category": "ai-infrastructure"
                },
                "annotations": {
                    "argocd.argoproj.io/sync-wave": "20",
                    "orchestr8.platform/mode": "local",
                    "orchestr8.platform/description": "Local Llama Stack deployment for Docker Desktop"
                },
                "finalizers": ["resources-finalizer.argocd.argoproj.io"]
            },
            "spec": {
                "project": "default",
                "source": {
                    "repoURL": "https://github.com/killerapp/orchestr8",
                    "targetRevision": "main",
                    "path": "modules/llama-stack/overlays/local"
                },
                "destination": {
                    "server": "https://kubernetes.default.svc",
                    "namespace": "llama-stack"
                },
                "syncPolicy": {
                    "automated": {"prune": True, "selfHeal": True, "allowEmpty": False},
                    "syncOptions": [
                        "CreateNamespace=true", 
                        "ApplyOutOfSyncOnly=true",
                        "PrunePropagationPolicy=foreground",
                        "PruneLast=true"
                    ],
                    "retry": {
                        "limit": 3,
                        "backoff": {
                            "duration": "5s",
                            "factor": 2,
                            "maxDuration": "3m"
                        }
                    }
                }
            }
        }

        # Apply Llama Stack application
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            yaml.dump(llama_stack_app, f)
            app_file = f.name

        try:
            result = subprocess.run(
                ["kubectl", "apply", "-f", app_file], capture_output=True, text=True
            )

            # If validation fails due to API server issues, try with bypass
            if result.returncode != 0 and (
                "TLS handshake timeout" in result.stderr
                or "connection refused" in result.stderr
            ):
                self.console.print(
                    "[yellow]⚠ API server connectivity issue, retrying with validation bypass...[/yellow]"
                )
                result = subprocess.run(
                    ["kubectl", "apply", "-f", app_file, "--validate=false"],
                    capture_output=True,
                    text=True,
                )

            if result.returncode == 0:
                return {"deployed": True, "application": "llama-stack-local"}
            else:
                # Don't fail the entire setup if Llama Stack deployment fails
                self.console.print(
                    f"[yellow]⚠ Llama Stack deployment failed (continuing setup): {result.stderr}[/yellow]"
                )
                return {"deployed": False, "error": result.stderr}
        except Exception as e:
            self.console.print(
                f"[yellow]⚠ Llama Stack deployment error (continuing setup): {str(e)}[/yellow]"
            )
            return {"deployed": False, "error": str(e)}
        finally:
            Path(app_file).unlink()

    async def configure_argocd_helm_repos(self) -> Dict[str, Any]:
        """Configure ArgoCD Helm repositories for platform dependencies."""
        # Standard Helm repositories needed by the platform
        repositories = [
            {"name": "bitnami", "url": "https://charts.bitnami.com/bitnami"},
            {"name": "oauth2-proxy", "url": "https://oauth2-proxy.github.io/manifests"},
            {"name": "jetstack", "url": "https://charts.jetstack.io"},
            {
                "name": "prometheus-community",
                "url": "https://prometheus-community.github.io/helm-charts",
            },
            {
                "name": "cloudnative-pg",
                "url": "https://cloudnative-pg.github.io/charts",
            },
            {"name": "argoproj", "url": "https://argoproj.github.io/argo-helm"},
            {
                "name": "istio",
                "url": "https://istio-release.storage.googleapis.com/charts",
            },
        ]

        created_repos = []

        for repo in repositories:
            repo_secret = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {
                    "name": f"{repo['name']}-repo",
                    "namespace": "argocd",
                    "labels": {"argocd.argoproj.io/secret-type": "repository"},
                },
                "stringData": {
                    "type": "helm",
                    "name": repo["name"],
                    "url": repo["url"],
                },
            }

            # Apply repository secret
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                yaml.dump(repo_secret, f)
                repo_file = f.name

            try:
                # Try with validation first
                result = subprocess.run(
                    ["kubectl", "apply", "-f", repo_file],
                    capture_output=True,
                    text=True,
                )

                # If validation fails due to API server issues, try with bypass
                if result.returncode != 0 and (
                    "TLS handshake timeout" in result.stderr
                    or "connection refused" in result.stderr
                ):
                    self.console.print(
                        "[yellow]⚠[/yellow] API server connectivity issue, retrying with validation bypass..."
                    )
                    result = subprocess.run(
                        [
                            "kubectl",
                            "apply",
                            "-f",
                            repo_file,
                            "--validate=false",
                            "--dry-run=client",
                        ],
                        capture_output=True,
                        text=True,
                    )

                    # If dry-run succeeds, apply without validation
                    if result.returncode == 0:
                        result = subprocess.run(
                            ["kubectl", "apply", "-f", repo_file, "--validate=false"],
                            capture_output=True,
                            text=True,
                        )

                if result.returncode == 0:
                    created_repos.append(repo["name"])
                    self.console.print(
                        f"[green]✓[/green] Configured {repo['name']} repository"
                    )
                else:
                    self.console.print(
                        f"[yellow]⚠[/yellow] Failed to configure {repo['name']}: {result.stderr}"
                    )
            finally:
                Path(repo_file).unlink()

        # Restart repo server if any repos were added
        if created_repos:
            self.console.print("[cyan]Restarting ArgoCD repo server...[/cyan]")
            result = subprocess.run(
                [
                    "kubectl",
                    "rollout",
                    "restart",
                    "deployment",
                    "argocd-repo-server",
                    "-n",
                    "argocd",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0:
                self.console.print("[green]✓[/green] ArgoCD repo server restarted")

        return {
            "configured_repositories": created_repos,
            "total_repositories": len(repositories),
        }

    async def bootstrap_argocd_api(self) -> Dict[str, Any]:
        """Bootstrap ArgoCD API access and verify authentication works."""
        import base64
        import time

        # Wait for ArgoCD to be fully ready
        max_retries = 30
        for attempt in range(max_retries):
            try:
                # Check if ArgoCD server is responsive
                result = subprocess.run(
                    [
                        "kubectl",
                        "get",
                        "deployment",
                        "argocd-server",
                        "-n",
                        "argocd",
                        "-o",
                        "jsonpath={.status.readyReplicas}",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout.strip() == "1":
                    break

            except Exception:
                pass

            if attempt < max_retries - 1:
                time.sleep(5)
            else:
                return {
                    "ready": False,
                    "error": "ArgoCD server not ready after 150 seconds",
                }

        try:
            # Get the admin password
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
            )

            if result.returncode != 0:
                return {
                    "ready": False,
                    "error": "Could not retrieve ArgoCD admin password",
                }

            password = base64.b64decode(result.stdout).decode("utf-8")

            # Test API connectivity by trying to list applications
            api_test = subprocess.run(
                ["kubectl", "get", "applications", "-n", "argocd", "--timeout=10s"],
                capture_output=True,
                text=True,
            )

            if api_test.returncode != 0:
                return {
                    "ready": False,
                    "error": f"ArgoCD API not accessible: {api_test.stderr}",
                }

            # Configure ArgoCD for insecure mode (local development)
            insecure_config = subprocess.run(
                [
                    "kubectl",
                    "patch",
                    "configmap",
                    "argocd-cmd-params-cm",
                    "-n",
                    "argocd",
                    "--type",
                    "merge",
                    "-p",
                    '{"data":{"server.insecure":"true"}}',
                ],
                capture_output=True,
                text=True,
            )

            if insecure_config.returncode == 0:
                # Restart ArgoCD server to apply insecure config
                subprocess.run(
                    [
                        "kubectl",
                        "rollout",
                        "restart",
                        "deployment",
                        "argocd-server",
                        "-n",
                        "argocd",
                    ],
                    capture_output=True,
                    text=True,
                )

            return {
                "ready": True,
                "api_accessible": True,
                "admin_password": password,
                "api_url": "http://localhost:30080",
                "insecure_mode": insecure_config.returncode == 0,
                "message": "ArgoCD API ready for Orchestr8 CLI commands (o8 apps, o8 sync)",
            }

        except Exception as e:
            return {"ready": False, "error": f"ArgoCD API bootstrap failed: {str(e)}"}

    async def configure_argocd_repo(self) -> Dict[str, bool]:
        """Configure ArgoCD repository access with GitHub credentials."""
        # First check if ArgoCD namespace exists
        try:
            self.k8s_api.read_namespace(name="argocd")
        except ApiException as e:
            if e.status == 404:
                return {
                    "created": False,
                    "updated": False,
                    "error": "ArgoCD is not installed. Run 'o8 setup' first.",
                }
            raise

        # Get GitHub token from multiple sources
        github_token = self._get_github_token()
        if not github_token:
            return {
                "created": False,
                "updated": False,
                "error": "No GitHub token found. Run 'gh auth login' or set GITHUB_TOKEN environment variable.",
            }

        repo_url = f"https://github.com/{self.config.github.org}/orchestr8.git"
        secret_name = "orchestr8-repo"

        # Create repository secret with proper ArgoCD labels
        secret_data = {
            "type": "git",
            "url": repo_url,
            "username": "not-used",  # GitHub token auth doesn't use username  # pragma: allowlist secret
            "password": github_token,
        }

        # Convert to base64
        import base64

        encoded_data = {
            k: base64.b64encode(v.encode()).decode() for k, v in secret_data.items()
        }

        try:
            # Check if secret exists
            try:
                existing = self.k8s_api.read_namespaced_secret(
                    name=secret_name, namespace="argocd"
                )
                # Update existing secret
                existing.data = encoded_data
                self.k8s_api.patch_namespaced_secret(
                    name=secret_name, namespace="argocd", body=existing
                )
                return {"created": False, "updated": True, "url": repo_url}
            except ApiException as e:
                if e.status == 404:
                    # Create new secret
                    secret = client.V1Secret(
                        metadata=client.V1ObjectMeta(
                            name=secret_name,
                            namespace="argocd",
                            labels={"argocd.argoproj.io/secret-type": "repository"},
                        ),
                        type="Opaque",
                        data=encoded_data,
                    )
                    self.k8s_api.create_namespaced_secret(
                        namespace="argocd", body=secret
                    )
                    return {"created": True, "updated": False, "url": repo_url}
                else:
                    raise
        except Exception as e:
            self.console.print(
                f"[yellow]Warning: Could not configure ArgoCD repository: {e}[/yellow]"
            )
            return {"created": False, "updated": False, "error": str(e)}

    def _command_exists(self, command: str) -> bool:
        """Check if a command exists in PATH."""
        import shutil

        return shutil.which(command) is not None

    async def _ensure_platform_templates(self):
        """Ensure platform Helm templates exist to disable default deployment."""
        templates_dir = Path("platform/templates")

        # Check if we're in the right directory
        if not Path("platform/Chart.yaml").exists():
            self.console.print(
                "[yellow]Warning: Not in orchestr8 root directory[/yellow]"
            )
            return

        # Create templates directory if it doesn't exist
        templates_dir.mkdir(exist_ok=True)

        # Create _helpers.tpl if it doesn't exist
        helpers_file = templates_dir / "_helpers.tpl"
        if not helpers_file.exists():
            helpers_content = """{{/*
Expand the name of the chart.
*/}}
{{- define "orchestr8.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "orchestr8.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "orchestr8.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "orchestr8.labels" -}}
helm.sh/chart: {{ include "orchestr8.chart" . }}
{{ include "orchestr8.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "orchestr8.selectorLabels" -}}
app.kubernetes.io/name: {{ include "orchestr8.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}"""
            helpers_file.write_text(helpers_content)

        # Create deployment.yaml to disable default deployment
        deployment_file = templates_dir / "deployment.yaml"
        if not deployment_file.exists():
            deployment_content = """# Disable the default deployment - Orchestr8 is a platform
# composed of multiple services (ArgoCD, Keycloak, Istio, etc.) not a single app
{{- if .Values.deployment.enabled }}
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ include "orchestr8.fullname" . }}
  labels:
    {{- include "orchestr8.labels" . | nindent 4 }}
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      {{- include "orchestr8.selectorLabels" . | nindent 6 }}
  template:
    metadata:
      labels:
        {{- include "orchestr8.selectorLabels" . | nindent 8 }}
    spec:
      containers:
      - name: {{ .Chart.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag | default .Chart.AppVersion }}"
        imagePullPolicy: {{ .Values.image.pullPolicy }}
        ports:
        - name: http
          containerPort: 8080
          protocol: TCP
{{- end }}"""
            deployment_file.write_text(deployment_content)

        # Create service.yaml
        service_file = templates_dir / "service.yaml"
        if not service_file.exists():
            service_content = """# Disable the default service - Orchestr8 services are provided
# by the individual components (ArgoCD, Keycloak, Istio, etc.)
{{- if .Values.deployment.enabled }}
apiVersion: v1
kind: Service
metadata:
  name: {{ include "orchestr8.fullname" . }}
  labels:
    {{- include "orchestr8.labels" . | nindent 4 }}
spec:
  type: {{ .Values.service.type }}
  ports:
    - port: {{ .Values.service.port }}
      targetPort: http
      protocol: TCP
      name: http
  selector:
    {{- include "orchestr8.selectorLabels" . | nindent 4 }}
{{- end }}"""
            service_file.write_text(service_content)

        # Create hpa.yaml
        hpa_file = templates_dir / "hpa.yaml"
        if not hpa_file.exists():
            hpa_content = """# Disable the default HPA - Orchestr8 components manage their own scaling
{{- if and .Values.deployment.enabled .Values.autoscaling.enabled }}
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {{ include "orchestr8.fullname" . }}
  labels:
    {{- include "orchestr8.labels" . | nindent 4 }}
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: {{ include "orchestr8.fullname" . }}
  minReplicas: {{ .Values.autoscaling.minReplicas }}
  maxReplicas: {{ .Values.autoscaling.maxReplicas }}
  metrics:
    {{- if .Values.autoscaling.targetCPUUtilizationPercentage }}
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetCPUUtilizationPercentage }}
    {{- end }}
    {{- if .Values.autoscaling.targetMemoryUtilizationPercentage }}
    - type: Resource
      resource:
        name: memory
        target:
          type: Utilization
          averageUtilization: {{ .Values.autoscaling.targetMemoryUtilizationPercentage }}
    {{- end }}
{{- end }}"""
            hpa_file.write_text(hpa_content)

        # Update values.yaml to disable deployment
        values_file = Path("platform/values.yaml")
        if values_file.exists():
            values_content = values_file.read_text()
            if "deployment:" not in values_content:
                # Add deployment config at the beginning after the header comments
                lines = values_content.split("\n")
                insert_idx = 0
                for i, line in enumerate(lines):
                    if line.strip() and not line.strip().startswith("#"):
                        insert_idx = i
                        break

                deployment_config = """# Disable default deployment - Orchestr8 is a platform, not a single app
deployment:
  enabled: false

# Default values that would normally configure the deployment
image:
  repository: nginx
  pullPolicy: IfNotPresent
  tag: ""

replicaCount: 1

service:
  type: ClusterIP
  port: 80

autoscaling:
  enabled: false
  minReplicas: 1
  maxReplicas: 100
  targetCPUUtilizationPercentage: 80

"""
                lines.insert(insert_idx, deployment_config)
                values_file.write_text("\n".join(lines))

    async def get_status(self) -> Dict[str, Any]:
        """Get current platform status."""
        status = {
            "config": self.config.to_dict(),
            "kubernetes": {"connected": False, "context": None, "cluster": None},
            "argocd": {"installed": False},
            "platform": {"deployed": False},
            "github": {"connected": False},
            "argocd_apps": {},
        }

        # Get current kubectl context
        try:
            result = subprocess.run(
                ["kubectl", "config", "current-context"], capture_output=True, text=True
            )
            if result.returncode == 0:
                status["kubernetes"]["context"] = result.stdout.strip()

            # Get cluster info
            result = subprocess.run(
                [
                    "kubectl",
                    "config",
                    "view",
                    "--minify",
                    "-o",
                    "jsonpath={.clusters[0].name}",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                status["kubernetes"]["cluster"] = result.stdout.strip()
        except Exception:
            pass

        # Check Kubernetes connection
        if self.k8s_api:
            try:
                self.k8s_api.list_namespace()
                status["kubernetes"]["connected"] = True
            except Exception:
                pass

        # Check ArgoCD
        try:
            result = subprocess.run(
                ["kubectl", "get", "deployment", "argocd-server", "-n", "argocd"],
                capture_output=True,
            )
            if result.returncode == 0:
                status["argocd"]["installed"] = True

                # Get ArgoCD admin password
                try:
                    result = subprocess.run(
                        [
                            "kubectl",
                            "-n",
                            "argocd",
                            "get",
                            "secret",
                            "argocd-initial-admin-secret",
                            "-o",
                            "jsonpath={.data.password}",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0 and result.stdout:
                        import base64

                        password = base64.b64decode(result.stdout).decode()
                        status["argocd"]["admin_password"] = password
                except Exception:
                    pass
        except Exception:
            pass

        # Check GitHub repository connection
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "secret",
                    "github-repo-creds",
                    "-n",
                    "argocd",
                    "-o",
                    "jsonpath={.metadata.name}",
                ],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0 and result.stdout.strip() == "github-repo-creds":
                status["github"]["connected"] = True
        except Exception:
            pass

        # Check ArgoCD applications
        if status["argocd"]["installed"]:
            try:
                result = subprocess.run(
                    [
                        "kubectl",
                        "get",
                        "applications",
                        "-n",
                        "argocd",
                        "-o",
                        "jsonpath={range .items[*]}{.metadata.name}{'|'}{.status.sync.status}{'|'}{.status.health.status}{'\\n'}{end}",
                    ],
                    capture_output=True,
                    text=True,
                )

                if result.returncode == 0 and result.stdout:
                    for line in result.stdout.strip().split("\n"):
                        if line:
                            parts = line.split("|")
                            if len(parts) >= 3:
                                app_name = parts[0]
                                status["argocd_apps"][app_name] = {
                                    "sync": parts[1],
                                    "health": parts[2],
                                }
            except Exception:
                pass

        # Check platform application
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "application",
                    "orchestr8-platform",
                    "-n",
                    "argocd",
                ],
                capture_output=True,
            )
            if result.returncode == 0:
                status["platform"]["deployed"] = True

                # Get Keycloak admin password if platform is deployed
                try:
                    result = subprocess.run(
                        [
                            "kubectl",
                            "-n",
                            "platform",
                            "get",
                            "secret",
                            "keycloak-admin-creds",
                            "-o",
                            "jsonpath={.data.admin-password}",
                        ],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0 and result.stdout:
                        import base64

                        password = base64.b64decode(result.stdout).decode()
                        status["keycloak"] = {
                            "installed": True,
                            "admin_password": password,
                        }
                    elif result.returncode != 0:
                        # Secret doesn't exist yet or platform namespace missing
                        status["keycloak"] = {
                            "installed": False,
                            "error": "Secret not found",
                        }
                except Exception as e:
                    status["keycloak"] = {"installed": False, "error": str(e)}
        except Exception:
            pass

        return status

    async def configure_local_access(self) -> Dict[str, bool]:
        """Configure LoadBalancer services for local Docker Desktop access."""
        services = []

        # Define LoadBalancer services for local development
        lb_services = [
            {
                "name": "argocd-server-local",
                "namespace": "argocd",
                "selector": {"app.kubernetes.io/name": "argocd-server"},
                "port": 30080,
                "targetPort": 8080,
                "description": "ArgoCD UI",
            },
            {
                "name": "keycloak-local",
                "namespace": "platform",
                "selector": {
                    "app.kubernetes.io/component": "keycloak",
                    "app.kubernetes.io/instance": "orchestr8-platform",
                    "app.kubernetes.io/name": "keycloak",
                },
                "port": 30081,
                "targetPort": 8080,
                "description": "Keycloak Admin",
            },
            {
                "name": "oauth2-proxy-local",
                "namespace": "auth",
                "selector": {"app": "oauth2-proxy"},
                "port": 30082,
                "targetPort": 4180,
                "description": "OAuth2 Proxy (Platform Entry)",
            },
            {
                "name": "voicefuse-local",
                "namespace": "voicefuse",
                "selector": {"app": "voicefuse"},
                "port": 30083,
                "targetPort": 8080,
                "description": "VoiceFuse UI",
            },
            {
                "name": "langfuse-local",
                "namespace": "langfuse",
                "selector": {"app": "langfuse"},
                "port": 30084,
                "targetPort": 3000,
                "description": "Langfuse UI",
            },
        ]

        for svc in lb_services:
            try:
                # Check if namespace exists first
                try:
                    self.k8s_api.read_namespace(name=svc["namespace"])
                except ApiException as e:
                    if e.status == 404:
                        # Skip if namespace doesn't exist yet
                        continue

                # Create LoadBalancer service
                service = client.V1Service(
                    metadata=client.V1ObjectMeta(
                        name=svc["name"],
                        namespace=svc["namespace"],
                        labels={
                            "app.kubernetes.io/managed-by": "orchestr8",
                            "orchestr8.platform/service-type": "local-access",
                        },
                    ),
                    spec=client.V1ServiceSpec(
                        type="LoadBalancer",
                        selector=svc["selector"],
                        ports=[
                            client.V1ServicePort(
                                name="http",
                                port=svc["port"],
                                target_port=svc["targetPort"],
                                protocol="TCP",
                            )
                        ],
                    ),
                )

                try:
                    self.k8s_api.create_namespaced_service(
                        namespace=svc["namespace"], body=service
                    )
                    services.append(
                        {
                            "name": svc["name"],
                            "port": svc["port"],
                            "description": svc["description"],
                            "created": True,
                        }
                    )
                except ApiException as e:
                    if e.status == 409:  # Already exists
                        # Update existing service
                        self.k8s_api.patch_namespaced_service(
                            name=svc["name"], namespace=svc["namespace"], body=service
                        )
                        services.append(
                            {
                                "name": svc["name"],
                                "port": svc["port"],
                                "description": svc["description"],
                                "updated": True,
                            }
                        )
                    else:
                        self.console.print(
                            f"[yellow]Warning: Could not create service {svc['name']}: {e}[/yellow]"
                        )

            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Error with service {svc['name']}: {e}[/yellow]"
                )

        return {"services": services}

    async def teardown(self) -> Dict[str, Any]:
        """Teardown the Orchestr8 platform."""
        results = {
            "success": True,
            "deleted": {
                "helm_releases": [],
                "applications": [],
                "namespaces": [],
                "crds": [],
            },
        }

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=self.console,
            transient=True,  # This makes the progress bar disappear after completion
        ) as progress:
            # Delete Helm releases first
            task = progress.add_task("Deleting Helm releases...", total=None)
            try:
                # Get all Helm releases across all namespaces
                result = subprocess.run(
                    ["helm", "list", "-A", "-o", "json"], capture_output=True, text=True
                )
                if result.returncode == 0 and result.stdout:
                    import json

                    releases = json.loads(result.stdout)

                    # Uninstall each release
                    for release in releases:
                        # Skip releases not managed by Orchestr8 based on configurable labels
                        if release.get("namespace") in [
                            "kube-system",
                            "kube-public",
                            "kube-node-lease",
                            "default",
                            "local-path-storage",
                        ]:
                            continue

                        try:
                            uninstall_result = subprocess.run(
                                [
                                    "helm",
                                    "uninstall",
                                    release["name"],
                                    "-n",
                                    release["namespace"],
                                ],
                                capture_output=True,
                                text=True,
                            )
                            if uninstall_result.returncode == 0:
                                results["deleted"]["helm_releases"].append(
                                    f"{release['name']} in {release['namespace']}"
                                )
                        except Exception as e:
                            self.console.print(
                                f"[yellow]Warning: Could not uninstall {release['name']}: {e}[/yellow]"
                            )
                progress.update(task, completed=True)
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not list Helm releases: {e}[/yellow]"
                )

            # Delete ArgoCD applications first
            task = progress.add_task("Deleting ArgoCD applications...", total=None)
            try:
                result = subprocess.run(
                    [
                        "kubectl",
                        "delete",
                        "applications",
                        "--all",
                        "-n",
                        "argocd",
                        "--ignore-not-found=true",
                    ],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and result.stdout:
                    # Parse deleted applications
                    for line in result.stdout.strip().split("\n"):
                        if "deleted" in line:
                            app_name = (
                                line.split('"')[1] if '"' in line else line.split()[0]
                            )
                            results["deleted"]["applications"].append(app_name)
                progress.update(task, completed=True)
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not delete applications: {e}[/yellow]"
                )

            # Delete namespaces dynamically based on labels
            task = progress.add_task("Deleting namespaces...", total=None)

            # Get namespaces with Orchestr8 labels or created by Orchestr8
            orchestr8_namespace_labels = os.getenv(
                "O8_NAMESPACE_LABELS",
                "app.kubernetes.io/part-of=orchestr8,managed-by=orchestr8",
            ).split(",")

            namespaces_to_delete = set()

            # Get namespaces by labels
            for label in orchestr8_namespace_labels:
                try:
                    result = subprocess.run(
                        ["kubectl", "get", "namespaces", "-l", label, "-o", "name"],
                        capture_output=True,
                        text=True,
                    )
                    if result.returncode == 0 and result.stdout:
                        for ns in result.stdout.strip().split("\n"):
                            if ns:
                                namespaces_to_delete.add(ns.replace("namespace/", ""))
                except Exception as e:
                    self.console.print(
                        f"[yellow]Warning: Could not get namespaces with label {label}: {e}[/yellow]"
                    )

            # Also include known Orchestr8 namespaces from environment or defaults
            default_namespaces = os.getenv(
                "O8_NAMESPACES",
                "argocd,istio-system,istio-ingress,keycloak,auth,cert-manager,monitoring,platform",
            ).split(",")
            namespaces_to_delete.update(default_namespaces)

            # Get all module namespaces (they typically have module label)
            try:
                result = subprocess.run(
                    ["kubectl", "get", "namespaces", "-l", "module", "-o", "name"],
                    capture_output=True,
                    text=True,
                )
                if result.returncode == 0 and result.stdout:
                    for ns in result.stdout.strip().split("\n"):
                        if ns:
                            namespaces_to_delete.add(ns.replace("namespace/", ""))
            except Exception as e:
                self.console.print(
                    f"[yellow]Warning: Could not get module namespaces: {e}[/yellow]"
                )

            # Start all namespace deletions in parallel
            import concurrent.futures

            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:

                def delete_namespace(ns):
                    try:
                        result = subprocess.run(
                            [
                                "kubectl",
                                "delete",
                                "namespace",
                                ns,
                                "--ignore-not-found=true",
                            ],
                            capture_output=True,
                            text=True,
                        )
                        if result.returncode == 0 and "deleted" in result.stdout:
                            return ns, True
                        return ns, False
                    except Exception as e:
                        self.console.print(
                            f"[yellow]Warning: Could not delete namespace {ns}: {e}[/yellow]"
                        )
                        return ns, False

                # Submit all deletions
                futures = {
                    executor.submit(delete_namespace, ns): ns
                    for ns in namespaces_to_delete
                }

                # Collect results as they complete
                for future in concurrent.futures.as_completed(futures):
                    ns, success = future.result()
                    if success:
                        results["deleted"]["namespaces"].append(ns)

            progress.update(task, completed=True)

            # Delete CRDs in parallel
            task = progress.add_task(
                "Deleting Custom Resource Definitions...", total=None
            )
            crd_labels = [
                "app.kubernetes.io/part-of=argocd",
                "app=istio",
                "app.kubernetes.io/name=cert-manager",
            ]

            # Delete CRDs in parallel
            with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:

                def delete_crds_by_label(label):
                    try:
                        result = subprocess.run(
                            [
                                "kubectl",
                                "delete",
                                "crd",
                                "-l",
                                label,
                                "--ignore-not-found=true",
                            ],
                            capture_output=True,
                            text=True,
                        )
                        deleted_crds = []
                        if result.returncode == 0 and result.stdout:
                            # Parse deleted CRDs
                            for line in result.stdout.strip().split("\n"):
                                if "deleted" in line:
                                    crd_name = (
                                        line.split('"')[1]
                                        if '"' in line
                                        else line.split()[0]
                                    )
                                    deleted_crds.append(crd_name)
                        return deleted_crds
                    except Exception as e:
                        self.console.print(
                            f"[yellow]Warning: Could not delete CRDs with label {label}: {e}[/yellow]"
                        )
                        return []

                # Submit all CRD deletions
                futures = [
                    executor.submit(delete_crds_by_label, label) for label in crd_labels
                ]

                # Collect results
                for future in concurrent.futures.as_completed(futures):
                    deleted_crds = future.result()
                    results["deleted"]["crds"].extend(deleted_crds)

            progress.update(task, completed=True)

        # Summary
        self.console.print(
            f"\n[dim]Deleted {len(results['deleted']['helm_releases'])} Helm releases[/dim]"
        )
        self.console.print(
            f"[dim]Deleted {len(results['deleted']['applications'])} applications[/dim]"
        )
        self.console.print(
            f"[dim]Deleted {len(results['deleted']['namespaces'])} namespaces[/dim]"
        )
        self.console.print(f"[dim]Deleted {len(results['deleted']['crds'])} CRDs[/dim]")

        return results
