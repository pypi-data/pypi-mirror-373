"""CUE Configuration Engine for Orchestr8.

This module provides the core CUE integration for Orchestr8, enabling:
- Type-safe configuration validation
- Template-free resource generation
- Multi-tenant configuration management
- Kubernetes resource generation from tenant specifications
"""

import json
import subprocess
import tempfile
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import shutil
import os

from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ..exceptions import Orchestr8Error


class CUEEngineError(Orchestr8Error):
    """Error in CUE configuration processing."""

    pass


@dataclass
class CUEValidationResult:
    """Result of CUE validation."""

    valid: bool
    errors: List[str]
    warnings: List[str]
    data: Optional[Dict[str, Any]] = None


@dataclass
class TenantResources:
    """Generated resources for a tenant."""

    namespace: Dict[str, Any]
    resource_quota: Dict[str, Any]
    limit_range: Dict[str, Any]
    network_policies: List[Dict[str, Any]]
    rbac: Dict[str, Any]
    secrets: Dict[str, Any]
    keycloak_realm: Dict[str, Any]
    istio_resources: Dict[str, Any] = None
    module_resources: List[Dict[str, Any]] = None
    istio_resources: Dict[str, Any]
    module_resources: List[Dict[str, Any]]


class CUEEngine:
    """CUE configuration engine for Orchestr8."""

    def __init__(
        self, schema_path: Optional[Path] = None, console: Optional[Console] = None
    ):
        """Initialize CUE engine.

        Args:
            schema_path: Path to CUE schemas directory
            console: Rich console for output
        """
        self.console = console or Console()

        # Determine schema path
        if schema_path:
            self.schema_path = schema_path
        else:
            # Default to schemas directory relative to project root
            project_root = Path(__file__).parent.parent.parent.parent.parent
            self.schema_path = project_root / "schemas"

        if not self.schema_path.exists():
            raise CUEEngineError(f"CUE schema path does not exist: {self.schema_path}")

        # Check if CUE CLI is available
        self._check_cue_cli()

        # Initialize CUE module paths
        self._init_module_paths()

    def _check_cue_cli(self):
        """Check if CUE CLI is available."""
        if not shutil.which("cue"):
            raise CUEEngineError(
                "CUE CLI not found. Please install CUE: https://cuelang.org/docs/introduction/installation"
            )

    def _init_module_paths(self):
        """Initialize CUE module paths."""
        # Key schema paths
        self.tenant_schema_path = self.schema_path / "tenant" / "tenant.cue"
        self.keycloak_schema_path = self.schema_path / "keycloak" / "keycloak.cue"
        self.k8s_schema_path = self.schema_path / "kubernetes" / "kubernetes.cue"

        # Verify schema files exist
        for name, path in {
            "tenant": self.tenant_schema_path,
            "keycloak": self.keycloak_schema_path,
            "kubernetes": self.k8s_schema_path,
        }.items():
            if not path.exists():
                raise CUEEngineError(f"{name.title()} schema not found: {path}")

    def _run_cue_command(
        self,
        args: List[str],
        input_data: Optional[str] = None,
        cwd: Optional[Path] = None,
    ) -> subprocess.CompletedProcess:
        """Run a CUE command and return the result.

        Args:
            args: CUE command arguments
            input_data: Optional input data to pipe to CUE
            cwd: Working directory for command

        Returns:
            CompletedProcess with stdout, stderr, and return code
        """
        cmd = ["cue"] + args

        try:
            result = subprocess.run(
                cmd,
                input=input_data,
                text=True,
                capture_output=True,
                cwd=cwd or self.schema_path.parent,
                check=False,
            )
            return result
        except Exception as e:
            raise CUEEngineError(
                f"Failed to run CUE command {' '.join(cmd)}: {e}"
            ) from e

    def validate_tenant_config(
        self, tenant_config: Dict[str, Any]
    ) -> CUEValidationResult:
        """Validate tenant configuration against CUE schema.

        Args:
            tenant_config: Tenant configuration to validate

        Returns:
            Validation result with errors and processed data
        """
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True,
            ) as progress:
                task = progress.add_task(
                    "Validating tenant configuration...", total=None
                )

                # Create temporary file with tenant config
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".yaml", delete=False
                ) as f:
                    yaml.dump(tenant_config, f, default_flow_style=False)
                    temp_config_path = Path(f.name)

                try:
                    # Run CUE validation
                    result = self._run_cue_command(
                        ["vet", str(self.tenant_schema_path), str(temp_config_path)]
                    )

                    errors = []
                    warnings = []

                    if result.returncode != 0:
                        # Parse CUE error output
                        if result.stderr:
                            errors.extend(result.stderr.strip().split("\n"))
                        if result.stdout:
                            errors.extend(result.stdout.strip().split("\n"))

                        return CUEValidationResult(
                            valid=False,
                            errors=[e for e in errors if e.strip()],
                            warnings=warnings,
                        )

                    # If validation passes, try to get the unified data
                    export_result = self._run_cue_command(
                        [
                            "export",
                            "--out",
                            "json",
                            str(self.tenant_schema_path),
                            str(temp_config_path),
                        ]
                    )

                    validated_data = tenant_config  # Default to original config
                    if export_result.returncode == 0 and export_result.stdout:
                        try:
                            # Use the CUE-processed data if available
                            validated_data = json.loads(export_result.stdout)
                        except json.JSONDecodeError:
                            warnings.append(
                                "Could not parse CUE export as JSON, using original config"
                            )
                    else:
                        warnings.append("CUE export failed, using original config")

                    progress.update(task, completed=True)

                    return CUEValidationResult(
                        valid=True, errors=[], warnings=warnings, data=validated_data
                    )

                finally:
                    # Clean up temporary file
                    try:
                        os.unlink(temp_config_path)
                    except OSError:
                        pass

        except CUEEngineError:
            raise
        except Exception as e:
            return CUEValidationResult(
                valid=False, errors=[f"Internal validation error: {e}"], warnings=[]
            )

    def generate_keycloak_realm(self, tenant_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate Keycloak realm configuration from tenant config.

        Args:
            tenant_config: Validated tenant configuration

        Returns:
            Keycloak realm configuration
        """
        # For now, create a simple realm config directly from tenant config
        # This avoids complex CUE embedding issues while proving the system works
        metadata = tenant_config.get("metadata", {})
        auth_config = tenant_config.get("authentication", {})
        realm_config = auth_config.get("realm", {})

        return {
            "id": metadata.get("name"),
            "realm": metadata.get("name"),
            "displayName": metadata.get("displayName"),
            "displayNameHtml": f"<div class='kc-logo-text'><span>{metadata.get('displayName')}</span></div>",
            "enabled": True,
            "registrationAllowed": realm_config.get("registrationAllowed", False),
            "registrationEmailAsUsername": True,
            "editUsernameAllowed": False,
            "resetPasswordAllowed": True,
            "rememberMe": realm_config.get("rememberMe", True),
            "verifyEmail": realm_config.get("verifyEmail", True),
            "loginWithEmailAllowed": True,
            "duplicateEmailsAllowed": False,
            "sslRequired": "external",
            "loginTheme": realm_config.get("loginTheme", "orchestr8"),
            "accountTheme": realm_config.get("accountTheme", "orchestr8"),
            "adminTheme": realm_config.get("adminTheme", "orchestr8"),
            "emailTheme": realm_config.get("emailTheme", "orchestr8"),
            "accessTokenLifespan": realm_config.get("sessions", {}).get(
                "accessTokenLifespan", 5
            )
            * 60,
            "accessTokenLifespanForImplicitFlow": 900,
            "ssoSessionIdleTimeout": realm_config.get("sessions", {}).get(
                "ssoSessionIdleTimeout", 60
            )
            * 60,
            "ssoSessionMaxLifespan": realm_config.get("sessions", {}).get(
                "ssoSessionMaxLifespan", 720
            )
            * 60,
            "refreshTokenMaxReuse": realm_config.get("sessions", {}).get(
                "refreshTokenMaxReuse", 0
            ),
            "bruteForceProtected": realm_config.get("bruteForceProtection", {}).get(
                "enabled", True
            ),
            "permanentLockout": realm_config.get("bruteForceProtection", {}).get(
                "permanentLockout", False
            ),
            "maxFailureWaitSeconds": realm_config.get("bruteForceProtection", {}).get(
                "maxFailureWaitSeconds", 900
            ),
            "minimumQuickLoginWaitSeconds": realm_config.get(
                "bruteForceProtection", {}
            ).get("minimumQuickLoginWaitSeconds", 60),
            "waitIncrementSeconds": realm_config.get("bruteForceProtection", {}).get(
                "waitIncrementSeconds", 60
            ),
            "quickLoginCheckMilliSeconds": realm_config.get(
                "bruteForceProtection", {}
            ).get("quickLoginCheckMilliSeconds", 1000),
            "maxDeltaTimeSeconds": realm_config.get("bruteForceProtection", {}).get(
                "maxDeltaTimeSeconds", 43200
            ),
            "failureFactor": realm_config.get("bruteForceProtection", {}).get(
                "failureFactor", 30
            ),
            "passwordPolicy": self._generate_password_policy(
                realm_config.get("passwordPolicy", {})
            ),
            "clients": auth_config.get("clients", []),
            "users": [],
            "groups": [],
            "roles": {
                "realm": [
                    {
                        "name": "default-roles-" + metadata.get("name"),
                        "description": "Default role for "
                        + metadata.get("displayName"),
                        "composite": True,
                        "composites": {
                            "realm": ["offline_access", "uma_authorization"]
                        },
                    }
                ]
            },
            "identityProviders": list(
                auth_config.get("identityProviders", {}).values()
            ),
            "internationalizationEnabled": True,
            "supportedLocales": ["en", "de", "fr", "es"],
            "defaultLocale": "en",
        }

    def _generate_password_policy(self, policy_config: Dict[str, Any]) -> str:
        """Generate Keycloak password policy string."""
        policies = []

        if policy_config.get("minLength", 8):
            policies.append(f"length({policy_config.get('minLength', 8)})")

        if policy_config.get("requireUppercase", True):
            policies.append("upperCase(1)")

        if policy_config.get("requireLowercase", True):
            policies.append("lowerCase(1)")

        if policy_config.get("requireNumbers", True):
            policies.append("digits(1)")

        if policy_config.get("requireSpecialChars", False):
            policies.append("specialChars(1)")

        if policy_config.get("notRecentPasswords", 3):
            policies.append(
                f"notUsername() and passwordHistory({policy_config.get('notRecentPasswords', 3)})"
            )

        return " and ".join(policies)

    def generate_kubernetes_resources(
        self, tenant_config: Dict[str, Any]
    ) -> TenantResources:
        """Generate Kubernetes resources from tenant configuration.

        Args:
            tenant_config: Validated tenant configuration

        Returns:
            Generated Kubernetes resources for the tenant
        """
        # Generate basic Kubernetes resources directly from tenant config
        metadata = tenant_config.get("metadata", {})
        tenant_name = metadata.get("name")
        resources_config = tenant_config.get("resources", {})
        security_config = tenant_config.get("security", {})

        # Create namespace
        namespace = {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": tenant_name,
                "labels": {
                    "orchestr8.platform/tenant": tenant_name,
                    "orchestr8.platform/managed": "true",
                    **metadata.get("labels", {}),
                },
                "annotations": metadata.get("annotations", {}),
            },
        }

        # Create resource quota
        quota_config = resources_config.get("namespaceQuota", {})
        resource_quota = {
            "apiVersion": "v1",
            "kind": "ResourceQuota",
            "metadata": {"name": f"{tenant_name}-quota", "namespace": tenant_name},
            "spec": {
                "hard": {
                    "requests.cpu": quota_config.get("compute", {}).get(
                        "requestsCpu", "10"
                    ),
                    "requests.memory": quota_config.get("compute", {}).get(
                        "requestsMemory", "20Gi"
                    ),
                    "limits.cpu": quota_config.get("compute", {}).get(
                        "limitsCpu", "20"
                    ),
                    "limits.memory": quota_config.get("compute", {}).get(
                        "limitsMemory", "40Gi"
                    ),
                    "requests.storage": quota_config.get("compute", {}).get(
                        "requestsStorage", "100Gi"
                    ),
                    "pods": str(quota_config.get("objects", {}).get("pods", 50)),
                    "services": str(
                        quota_config.get("objects", {}).get("services", 20)
                    ),
                    "count/ingresses.networking.k8s.io": str(
                        quota_config.get("objects", {}).get("ingresses", 10)
                    ),
                    "persistentvolumeclaims": str(
                        quota_config.get("objects", {}).get(
                            "persistentVolumeClaims", 10
                        )
                    ),
                    "configmaps": str(
                        quota_config.get("objects", {}).get("configMaps", 50)
                    ),
                    "secrets": str(quota_config.get("objects", {}).get("secrets", 50)),
                }
            },
        }

        # Create limit range
        limit_config = resources_config.get("limitRanges", {})
        limit_range = {
            "apiVersion": "v1",
            "kind": "LimitRange",
            "metadata": {"name": f"{tenant_name}-limits", "namespace": tenant_name},
            "spec": {
                "limits": [
                    {
                        "type": "Pod",
                        "max": {
                            "cpu": limit_config.get("maxPod", {}).get("cpu", "2"),
                            "memory": limit_config.get("maxPod", {}).get(
                                "memory", "4Gi"
                            ),
                        },
                        "min": {
                            "cpu": limit_config.get("minPod", {}).get("cpu", "10m"),
                            "memory": limit_config.get("minPod", {}).get(
                                "memory", "32Mi"
                            ),
                        },
                    },
                    {
                        "type": "Container",
                        "max": {
                            "cpu": limit_config.get("maxContainer", {}).get("cpu", "2"),
                            "memory": limit_config.get("maxContainer", {}).get(
                                "memory", "4Gi"
                            ),
                        },
                        "min": {
                            "cpu": limit_config.get("minContainer", {}).get(
                                "cpu", "10m"
                            ),
                            "memory": limit_config.get("minContainer", {}).get(
                                "memory", "32Mi"
                            ),
                        },
                    },
                ]
            },
        }

        # Create basic network policy (default deny)
        network_policy = {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "NetworkPolicy",
            "metadata": {
                "name": f"{tenant_name}-default-deny",
                "namespace": tenant_name,
            },
            "spec": {
                "podSelector": {},
                "policyTypes": ["Ingress", "Egress"],
                "ingress": [],
                "egress": [],
            },
        }

        # Create service account
        rbac_config = security_config.get("rbac", {})
        service_account = {
            "apiVersion": "v1",
            "kind": "ServiceAccount",
            "metadata": {
                "name": f"{tenant_name}-sa",
                "namespace": tenant_name,
                "labels": rbac_config.get("serviceAccount", {}).get("labels", {}),
                "annotations": rbac_config.get("serviceAccount", {}).get(
                    "annotations", {}
                ),
            },
            "automountServiceAccountToken": rbac_config.get("serviceAccount", {}).get(
                "automountToken", False
            ),
        }

        return TenantResources(
            namespace=namespace,
            resource_quota=resource_quota,
            limit_range=limit_range,
            network_policies=[network_policy],
            rbac=service_account,
            secrets={},
            keycloak_realm={},
            istio_resources={},
            module_resources=[],
        )

    def generate_tenant_module_resources(
        self, tenant_config: Dict[str, Any], module_name: str, target_namespace: str
    ) -> Dict[str, Any]:
        """Generate Kubernetes resources for a specific module within a tenant.

        Args:
            tenant_config: Tenant configuration
            module_name: Name of the module to generate resources for
            target_namespace: Target Kubernetes namespace

        Returns:
            Generated Kubernetes resources for the module
        """
        # Generate module-specific resources based on tenant configuration and module type
        if module_name == "langfuse":
            return self._generate_langfuse_resources(tenant_config, target_namespace)
        elif module_name == "clickhouse":
            return self._generate_clickhouse_resources(tenant_config, target_namespace)
        else:
            return self._generate_generic_module_resources(
                tenant_config, module_name, target_namespace
            )

    def _generate_langfuse_resources(
        self, tenant_config: Dict[str, Any], namespace: str
    ) -> Dict[str, Any]:
        """Generate Langfuse-specific resources for a tenant."""
        metadata = tenant_config.get("metadata", {})
        tenant_name = metadata.get("name")
        domain = metadata.get("domain")

        return {
            "namespace": {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": namespace,
                    "labels": {
                        "orchestr8.platform/tenant": tenant_name,
                        "orchestr8.platform/module": "langfuse",
                        "orchestr8.platform/managed": "true",
                    },
                },
            },
            "deployment": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "langfuse",
                    "namespace": namespace,
                    "labels": {
                        "app": "langfuse",
                        "orchestr8.platform/tenant": tenant_name,
                        "orchestr8.platform/module": "langfuse",
                    },
                },
                "spec": {
                    "replicas": 1,
                    "selector": {"matchLabels": {"app": "langfuse"}},
                    "template": {
                        "metadata": {"labels": {"app": "langfuse"}},
                        "spec": {
                            "containers": [
                                {
                                    "name": "langfuse",
                                    "image": "langfuse/langfuse:2.89.0",
                                    "ports": [{"containerPort": 3000, "name": "http"}],
                                    "env": [
                                        {
                                            "name": "DATABASE_URL",
                                            "value": "postgresql://langfuse:password@postgres:5432/langfuse",
                                        },
                                        {
                                            "name": "NEXTAUTH_SECRET",
                                            "value": "your-secret-key",
                                        },
                                        {
                                            "name": "NEXTAUTH_URL",
                                            "value": f"https://langfuse.{domain}",
                                        },
                                        {"name": "TELEMETRY_ENABLED", "value": "false"},
                                    ],
                                    "resources": {
                                        "requests": {"cpu": "200m", "memory": "512Mi"},
                                        "limits": {"cpu": "1000m", "memory": "1Gi"},
                                    },
                                }
                            ]
                        },
                    },
                },
            },
            "service": {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "langfuse",
                    "namespace": namespace,
                    "labels": {
                        "app": "langfuse",
                        "orchestr8.platform/tenant": tenant_name,
                        "orchestr8.platform/module": "langfuse",
                        "orchestr8.platform/managed": "true",
                    },
                },
                "spec": {
                    "selector": {"app": "langfuse"},
                    "ports": [
                        {
                            "port": 3000,
                            "targetPort": 3000,
                            "protocol": "TCP",
                            "name": "http",
                        }
                    ],
                    "type": "ClusterIP",
                },
            },
        }

    def _generate_clickhouse_resources(
        self, tenant_config: Dict[str, Any], namespace: str
    ) -> Dict[str, Any]:
        """Generate ClickHouse-specific resources for a tenant."""
        metadata = tenant_config.get("metadata", {})
        tenant_name = metadata.get("name")

        return {
            "namespace": {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": namespace,
                    "labels": {
                        "orchestr8.platform/tenant": tenant_name,
                        "orchestr8.platform/module": "clickhouse",
                        "orchestr8.platform/managed": "true",
                    },
                },
            },
            "deployment": {
                "apiVersion": "apps/v1",
                "kind": "Deployment",
                "metadata": {
                    "name": "clickhouse",
                    "namespace": namespace,
                    "labels": {
                        "app": "clickhouse",
                        "orchestr8.platform/tenant": tenant_name,
                        "orchestr8.platform/module": "clickhouse",
                    },
                },
                "spec": {
                    "replicas": 1,
                    "selector": {"matchLabels": {"app": "clickhouse"}},
                    "template": {
                        "metadata": {"labels": {"app": "clickhouse"}},
                        "spec": {
                            "containers": [
                                {
                                    "name": "clickhouse",
                                    "image": "clickhouse/clickhouse-server:24.8.5.115",
                                    "ports": [
                                        {"containerPort": 8123, "name": "http"},
                                        {"containerPort": 9000, "name": "tcp"},
                                    ],
                                    "resources": {
                                        "requests": {"cpu": "500m", "memory": "1Gi"},
                                        "limits": {"cpu": "2000m", "memory": "4Gi"},
                                    },
                                }
                            ]
                        },
                    },
                },
            },
            "service": {
                "apiVersion": "v1",
                "kind": "Service",
                "metadata": {
                    "name": "clickhouse",
                    "namespace": namespace,
                    "labels": {
                        "app": "clickhouse",
                        "orchestr8.platform/tenant": tenant_name,
                        "orchestr8.platform/module": "clickhouse",
                        "orchestr8.platform/managed": "true",
                    },
                },
                "spec": {
                    "selector": {"app": "clickhouse"},
                    "ports": [
                        {
                            "port": 8123,
                            "targetPort": 8123,
                            "protocol": "TCP",
                            "name": "http",
                        },
                        {
                            "port": 9000,
                            "targetPort": 9000,
                            "protocol": "TCP",
                            "name": "tcp",
                        },
                    ],
                    "type": "ClusterIP",
                },
            },
        }

    def _generate_generic_module_resources(
        self, tenant_config: Dict[str, Any], module_name: str, namespace: str
    ) -> Dict[str, Any]:
        """Generate generic resources for unknown modules."""
        metadata = tenant_config.get("metadata", {})
        tenant_name = metadata.get("name")

        return {
            "namespace": {
                "apiVersion": "v1",
                "kind": "Namespace",
                "metadata": {
                    "name": namespace,
                    "labels": {
                        "orchestr8.platform/tenant": tenant_name,
                        "orchestr8.platform/module": module_name,
                        "orchestr8.platform/managed": "true",
                    },
                },
            }
        }

    def validate_module_config(
        self,
        module_config: Dict[str, Any],
        tenant_context: Optional[Dict[str, Any]] = None,
    ) -> CUEValidationResult:
        """Validate module configuration against tenant constraints.

        Args:
            module_config: Module configuration to validate
            tenant_context: Tenant context for validation

        Returns:
            Validation result
        """
        try:
            # Create validation input
            validation_input = {"module": module_config}

            if tenant_context:
                validation_input["tenant"] = tenant_context

            # Create temporary file with validation input
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", delete=False
            ) as f:
                yaml.dump(validation_input, f, default_flow_style=False)
                temp_input_path = Path(f.name)

            try:
                # Use CUE to validate module schema from tenant schema
                result = self._run_cue_command(
                    [
                        "vet",
                        str(self.tenant_schema_path),
                        str(temp_input_path),
                        "-d",
                        "#Module",  # Specify module definition
                        "-c",  # Strict mode
                    ]
                )

                errors = []
                warnings = []

                if result.returncode != 0:
                    # Parse CUE error output
                    if result.stderr:
                        errors.extend(result.stderr.strip().split("\n"))
                    if result.stdout:
                        errors.extend(result.stdout.strip().split("\n"))

                    return CUEValidationResult(
                        valid=False,
                        errors=[e for e in errors if e.strip()],
                        warnings=warnings,
                    )

                # Try to export the validated module data
                export_result = self._run_cue_command(
                    [
                        "export",
                        "--out",
                        "json",
                        "-e",
                        "module",
                        str(self.tenant_schema_path),
                        str(temp_input_path),
                    ]
                )

                validated_data = None
                if export_result.returncode == 0 and export_result.stdout:
                    try:
                        validated_data = json.loads(export_result.stdout)
                    except json.JSONDecodeError:
                        warnings.append("Could not parse validated module data as JSON")

                return CUEValidationResult(
                    valid=True, errors=[], warnings=warnings, data=validated_data
                )

            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_input_path)
                except OSError:
                    pass

        except CUEEngineError:
            raise
        except Exception as e:
            return CUEValidationResult(
                valid=False, errors=[f"Module validation failed: {e}"], warnings=[]
            )

    def export_to_yaml(self, data: Dict[str, Any], output_path: Path):
        """Export CUE-generated data to YAML files.

        Args:
            data: Generated data to export
            output_path: Directory to write YAML files
        """
        try:
            output_path.mkdir(parents=True, exist_ok=True)

            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
                transient=True,
            ) as progress:
                task = progress.add_task("Exporting to YAML...", total=len(data))

                for name, resource in data.items():
                    if isinstance(resource, dict) and resource.get("kind"):
                        # Single Kubernetes resource
                        filename = f"{name.replace('_', '-')}.yaml"
                        filepath = output_path / filename

                        with open(filepath, "w") as f:
                            yaml.dump(resource, f, default_flow_style=False, indent=2)

                    elif isinstance(resource, list):
                        # Multiple resources
                        filename = f"{name.replace('_', '-')}.yaml"
                        filepath = output_path / filename

                        with open(filepath, "w") as f:
                            yaml.dump_all(
                                resource, f, default_flow_style=False, indent=2
                            )

                    elif isinstance(resource, dict):
                        # Nested structure - create subdirectory
                        subdir = output_path / name.replace("_", "-")
                        subdir.mkdir(exist_ok=True)
                        self.export_to_yaml(resource, subdir)

                    progress.advance(task)

        except Exception as e:
            raise CUEEngineError(f"Failed to export to YAML: {e}") from e

    def export_to_json(self, data: Dict[str, Any], output_path: Path):
        """Export CUE-generated data to JSON files.

        Args:
            data: Generated data to export
            output_path: Directory to write JSON files
        """
        try:
            output_path.mkdir(parents=True, exist_ok=True)

            for name, resource in data.items():
                filename = f"{name.replace('_', '-')}.json"
                filepath = output_path / filename

                with open(filepath, "w") as f:
                    json.dump(resource, f, indent=2)

        except Exception as e:
            raise CUEEngineError(f"Failed to export to JSON: {e}") from e

    def compile_tenant_bundle(self, tenant_config: Dict[str, Any]) -> Dict[str, Any]:
        """Compile complete tenant bundle with all resources.

        Args:
            tenant_config: Tenant configuration

        Returns:
            Complete bundle with all generated resources
        """
        try:
            self.console.print("[bold cyan]🏗️  Compiling tenant bundle...[/bold cyan]")

            # Validate tenant configuration
            validation = self.validate_tenant_config(tenant_config)
            if not validation.valid:
                raise CUEEngineError(f"Tenant validation failed: {validation.errors}")

            validated_config = validation.data

            # Generate Keycloak realm
            keycloak_realm = self.generate_keycloak_realm(validated_config)

            # Generate Kubernetes resources
            k8s_resources = self.generate_kubernetes_resources(validated_config)

            # Compile complete bundle
            bundle = {
                "tenant": validated_config,
                "keycloak": {"realm": keycloak_realm},
                "kubernetes": {
                    "namespace": k8s_resources.namespace,
                    "resourceQuota": k8s_resources.resource_quota,
                    "limitRange": k8s_resources.limit_range,
                    "networkPolicies": list(k8s_resources.network_policies),
                    "rbac": k8s_resources.rbac,
                    "secrets": k8s_resources.secrets,
                    "keycloakRealm": k8s_resources.keycloak_realm,
                    "istio": k8s_resources.istio_resources,
                    "modules": k8s_resources.module_resources,
                },
            }

            self.console.print("[green]✅ Tenant bundle compiled successfully[/green]")

            return bundle

        except Exception as e:
            raise CUEEngineError(f"Failed to compile tenant bundle: {e}") from e

    def get_tenant_schema(self) -> Dict[str, Any]:
        """Get the tenant schema definition.

        Returns:
            Tenant schema as dictionary
        """
        try:
            # Export tenant schema definition using CUE CLI
            result = self._run_cue_command(
                [
                    "export",
                    "--out",
                    "json",
                    "-e",
                    "#Tenant",
                    str(self.tenant_schema_path),
                ]
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown CUE error"
                raise CUEEngineError(f"Failed to export tenant schema: {error_msg}")

            if not result.stdout:
                raise CUEEngineError("CUE export produced no schema output")

            try:
                schema_def = json.loads(result.stdout)
                return schema_def
            except json.JSONDecodeError as e:
                raise CUEEngineError(f"Failed to parse tenant schema JSON: {e}")

        except CUEEngineError:
            raise
        except Exception as e:
            raise CUEEngineError(f"Failed to get tenant schema: {e}") from e

    def get_module_schema(self) -> Dict[str, Any]:
        """Get the module schema definition.

        Returns:
            Module schema as dictionary
        """
        try:
            # Export module schema definition using CUE CLI
            result = self._run_cue_command(
                [
                    "export",
                    "--out",
                    "json",
                    "-e",
                    "#Module",
                    str(self.tenant_schema_path),
                ]
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown CUE error"
                raise CUEEngineError(f"Failed to export module schema: {error_msg}")

            if not result.stdout:
                raise CUEEngineError("CUE export produced no schema output")

            try:
                schema_def = json.loads(result.stdout)
                return schema_def
            except json.JSONDecodeError as e:
                raise CUEEngineError(f"Failed to parse module schema JSON: {e}")

        except CUEEngineError:
            raise
        except Exception as e:
            raise CUEEngineError(f"Failed to get module schema: {e}") from e

    def format_cue_file(self, file_path: Path):
        """Format a CUE file using cue fmt.

        Args:
            file_path: Path to CUE file to format
        """
        try:
            result = subprocess.run(
                ["cue", "fmt", str(file_path)],
                capture_output=True,
                text=True,
                check=True,
            )

            # Write formatted content back to file
            with open(file_path, "w") as f:
                f.write(result.stdout)

        except subprocess.CalledProcessError as e:
            raise CUEEngineError(f"CUE formatting failed: {e.stderr}") from e
        except FileNotFoundError:
            self.console.print(
                "[yellow]⚠️  CUE CLI not found. Install from https://cuelang.org/[/yellow]"
            )

    def validate_cue_syntax(self, file_path: Path) -> CUEValidationResult:
        """Validate CUE file syntax using cue vet.

        Args:
            file_path: Path to CUE file to validate

        Returns:
            Validation result
        """
        try:
            result = subprocess.run(
                ["cue", "vet", str(file_path)], capture_output=True, text=True
            )

            if result.returncode == 0:
                return CUEValidationResult(valid=True, errors=[], warnings=[])
            else:
                return CUEValidationResult(
                    valid=False, errors=[result.stderr.strip()], warnings=[]
                )

        except FileNotFoundError:
            return CUEValidationResult(
                valid=False,
                errors=["CUE CLI not found. Install from https://cuelang.org/"],
                warnings=[],
            )

    @staticmethod
    def create_default_tenant(
        name: str,
        display_name: str,
        domain: str,
        organization: str,
        modules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Create a default tenant configuration.

        Args:
            name: Tenant identifier
            display_name: Human-readable name
            domain: Primary domain
            organization: Organization name
            modules: List of module names to include

        Returns:
            Default tenant configuration
        """
        modules = modules or ["web-app"]

        return {
            "metadata": {
                "name": name,
                "displayName": display_name,
                "domain": domain,
                "organization": {"name": organization},
                "environment": "dev",
                "labels": {},
                "annotations": {},
                "version": "1.0.0",
            },
            "authentication": {
                "realm": {
                    "registrationAllowed": False,
                    "verifyEmail": True,
                    "rememberMe": True,
                    "loginTheme": "orchestr8",
                    "accountTheme": "orchestr8",
                    "adminTheme": "orchestr8",
                    "emailTheme": "orchestr8",
                    "sessions": {
                        "ssoSessionIdleTimeout": 60,
                        "ssoSessionMaxLifespan": 720,
                        "accessTokenLifespan": 5,
                        "refreshTokenMaxReuse": 0,
                    },
                    "passwordPolicy": {
                        "minLength": 8,
                        "requireUppercase": True,
                        "requireLowercase": True,
                        "requireNumbers": True,
                        "requireSpecialChars": False,
                        "notRecentPasswords": 3,
                    },
                    "bruteForceProtection": {
                        "enabled": True,
                        "permanentLockout": False,
                        "maxFailureWaitSeconds": 900,
                        "minimumQuickLoginWaitSeconds": 60,
                        "waitIncrementSeconds": 60,
                        "quickLoginCheckMilliSeconds": 1000,
                        "maxDeltaTimeSeconds": 43200,
                        "failureFactor": 30,
                    },
                },
                "identityProviders": {},
                "clients": [],
                "users": {
                    "defaultGroups": [],
                    "defaultRoles": [],
                    "userProfileAttributes": [],
                    "emailSettings": {
                        "emailAsUsername": True,
                        "loginWithEmailAllowed": True,
                        "duplicateEmailsAllowed": False,
                    },
                    "accountSettings": {
                        "editUsernameAllowed": False,
                        "userManagedAccessAllowed": False,
                        "socialAccountLinking": True,
                    },
                },
            },
            "modules": [
                {
                    "name": module_name,
                    "category": "web-app",
                    "config": {},
                    "resources": {
                        "requests": {"cpu": "100m", "memory": "128Mi"},
                        "limits": {"cpu": "1000m", "memory": "1Gi"},
                        "replicas": {"min": 1, "max": 10, "target": 1},
                        "autoscaling": {"enabled": False, "targetCPUUtilization": 80},
                    },
                    "networking": {
                        "ports": [{"name": "http", "port": 8080, "protocol": "TCP"}],
                        "ingress": {
                            "enabled": True,
                            "className": "istio",
                            "path": "/",
                            "pathType": "Prefix",
                            "tls": {"enabled": True},
                            "annotations": {},
                        },
                        "serviceMesh": {
                            "enabled": True,
                            "mTLS": True,
                            "trafficPolicy": {"loadBalancer": "ROUND_ROBIN"},
                            "circuitBreaker": {
                                "enabled": False,
                                "consecutiveErrors": 5,
                                "interval": "30s",
                                "baseEjectionTime": "30s",
                                "maxEjectionPercent": 50,
                            },
                        },
                    },
                    "security": {
                        "authentication": {
                            "required": True,
                            "type": "oauth2",
                            "requiredRoles": [],
                            "requiredGroups": [],
                        },
                        "podSecurityContext": {
                            "runAsNonRoot": True,
                            "runAsUser": 1000,
                            "runAsGroup": 1000,
                            "fsGroup": 1000,
                            "seccompProfile": {"type": "RuntimeDefault"},
                        },
                        "containerSecurityContext": {
                            "allowPrivilegeEscalation": False,
                            "readOnlyRootFilesystem": True,
                            "capabilities": {"drop": ["ALL"]},
                            "seccompProfile": {"type": "RuntimeDefault"},
                        },
                        "networkPolicies": {
                            "enabled": True,
                            "ingress": [
                                {
                                    "from": [
                                        {
                                            "namespaceSelector": {
                                                "matchLabels": {"name": "istio-system"}
                                            }
                                        }
                                    ]
                                }
                            ],
                            "egress": [
                                {
                                    "to": [
                                        {
                                            "namespaceSelector": {
                                                "matchLabels": {
                                                    "orchestr8.platform/tenant": name
                                                }
                                            }
                                        }
                                    ]
                                }
                            ],
                        },
                    },
                }
                for module_name in modules
            ],
            "networking": {
                "domain": domain,
                "subdomainStrategy": "module-prefix",
                "tls": {
                    "enabled": True,
                    "issuer": "letsencrypt-prod",
                    "wildcardCert": False,
                },
                "loadBalancer": {
                    "type": "istio",
                    "rateLimiting": {
                        "enabled": False,
                        "requestsPerMinute": 100,
                        "burstSize": 10,
                    },
                    "timeouts": {"request": "60s", "idle": "180s", "keepAlive": "75s"},
                },
                "externalAccess": {"enabled": True},
            },
            "security": {
                "network": {
                    "defaultDeny": True,
                    "crossTenantAccess": False,
                    "internetAccess": {"allowed": False},
                },
                "podSecurity": {
                    "enforce": "restricted",
                    "audit": "restricted",
                    "warn": "restricted",
                    "version": "latest",
                },
                "rbac": {
                    "serviceAccount": {
                        "create": True,
                        "automountToken": False,
                        "annotations": {},
                        "labels": {},
                    },
                    "clusterRoles": [],
                    "roles": [],
                },
                "secrets": {
                    "externalSecrets": {
                        "enabled": False,
                        "provider": "vault",
                        "providerConfig": {},
                    },
                    "sealedSecrets": {"enabled": True, "scope": "namespace-wide"},
                    "rotation": {"enabled": False, "schedule": "0 2 * * 0"},
                },
                "images": {
                    "allowedRegistries": ["gcr.io", "docker.io", "ghcr.io"],
                    "requireSigning": False,
                    "vulnerabilityScanning": {
                        "enabled": True,
                        "severity": "HIGH",
                        "blockOnViolation": False,
                    },
                    "blockLatestTag": False,
                },
                "admission": {
                    "policies": [],
                    "enforceResourceLimits": True,
                    "requiredLabels": {
                        "orchestr8.platform/tenant": name,
                        "orchestr8.platform/managed": "true",
                    },
                    "requiredAnnotations": {},
                },
                "monitoring": {
                    "securityEvents": {
                        "enabled": True,
                        "policyViolations": True,
                        "privilegeEscalation": True,
                        "networkPolicyViolations": True,
                    },
                    "auditLogging": {
                        "enabled": True,
                        "retention": "90d",
                        "logLevel": "moderate",
                    },
                },
                "compliance": {
                    "frameworks": [],
                    "dataResidency": {"enabled": False},
                    "encryption": {
                        "atRest": True,
                        "inTransit": True,
                        "keyRotation": False,
                    },
                    "retention": {
                        "logs": "90d",
                        "metrics": "30d",
                        "traces": "7d",
                        "backups": "1y",
                    },
                },
            },
            "resources": {
                "namespaceQuota": {
                    "compute": {
                        "requestsCpu": "10",
                        "requestsMemory": "20Gi",
                        "limitsCpu": "20",
                        "limitsMemory": "40Gi",
                        "requestsStorage": "100Gi",
                    },
                    "objects": {
                        "pods": 50,
                        "services": 20,
                        "ingresses": 10,
                        "persistentVolumeClaims": 10,
                        "configMaps": 50,
                        "secrets": 50,
                    },
                    "services": {"nodeports": 0, "loadbalancers": 5},
                },
                "limitRanges": {
                    "defaultPod": {"cpu": "100m", "memory": "128Mi"},
                    "defaultRequestPod": {"cpu": "50m", "memory": "64Mi"},
                    "maxContainer": {"cpu": "2", "memory": "4Gi"},
                    "minContainer": {"cpu": "10m", "memory": "32Mi"},
                },
                "priorityClasses": {
                    "default": "tenant-normal",
                    "high": "tenant-high",
                    "low": "tenant-low",
                },
                "storageClasses": {
                    "default": "orchestr8-ssd",
                    "fast": "orchestr8-nvme",
                    "backup": "orchestr8-hdd",
                },
            },
        }
