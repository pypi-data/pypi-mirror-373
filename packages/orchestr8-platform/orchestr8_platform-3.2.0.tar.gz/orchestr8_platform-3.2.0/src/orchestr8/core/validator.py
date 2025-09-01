"""Module validation utilities for Orchestr8."""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a validation check."""

    passed: bool
    message: str
    severity: str = "error"  # error, warning, info
    details: Optional[Dict[str, Any]] = None


class ModuleValidator:
    """Validates Orchestr8 module specifications."""

    def __init__(self):
        """Initialize the validator."""
        self.errors: List[ValidationResult] = []
        self.warnings: List[ValidationResult] = []

    def validate_spec(self, spec_path: Path) -> Tuple[bool, List[ValidationResult]]:
        """Validate a module specification file.

        Args:
            spec_path: Path to the module.yaml file

        Returns:
            Tuple of (is_valid, results)
        """
        results = []

        # Load spec
        try:
            with open(spec_path) as f:
                spec = yaml.safe_load(f)
        except Exception as e:
            results.append(
                ValidationResult(
                    passed=False, message=f"Failed to parse YAML: {e}", severity="error"
                )
            )
            return False, results

        # Validate structure
        results.extend(self._validate_structure(spec))

        # Validate module metadata
        results.extend(self._validate_module_metadata(spec))

        # Validate deployment config
        results.extend(self._validate_deployment(spec))

        # Validate testing config
        results.extend(self._validate_testing(spec))

        # Validate requirements
        results.extend(self._validate_requirements(spec))

        # Validate security configuration
        results.extend(self._validate_security(spec))

        # Validate compliance
        results.extend(self._validate_compliance(spec))

        # Check if all critical validations passed
        has_errors = any(r.severity == "error" and not r.passed for r in results)

        return not has_errors, results

    def _validate_structure(self, spec: Dict) -> List[ValidationResult]:
        """Validate basic structure of the spec."""
        results = []

        # Check required top-level fields
        required_fields = ["apiVersion", "kind", "metadata", "spec"]
        for field in required_fields:
            if field not in spec:
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"Missing required field: {field}",
                        severity="error",
                    )
                )

        # Check API version
        if spec.get("apiVersion") != "orchestr8.platform/v1alpha1":
            results.append(
                ValidationResult(
                    passed=False,
                    message=f"Invalid apiVersion: {spec.get('apiVersion')}",
                    severity="error",
                    details={"expected": "orchestr8.platform/v1alpha1"},
                )
            )

        # Check kind
        if spec.get("kind") != "ModuleSpecification":
            results.append(
                ValidationResult(
                    passed=False,
                    message=f"Invalid kind: {spec.get('kind')}",
                    severity="error",
                    details={"expected": "ModuleSpecification"},
                )
            )

        return results

    def _validate_module_metadata(self, spec: Dict) -> List[ValidationResult]:
        """Validate module metadata section."""
        results = []

        module = spec.get("spec", {}).get("module", {})

        # Required fields
        required = ["name", "version", "tier"]
        for field in required:
            if not module.get(field):
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"Missing required module field: {field}",
                        severity="error",
                    )
                )

        # Validate tier
        valid_tiers = ["core", "standard", "custom", "experimental"]
        if module.get("tier") and module["tier"] not in valid_tiers:
            results.append(
                ValidationResult(
                    passed=False,
                    message=f"Invalid tier: {module['tier']}",
                    severity="warning",
                    details={"valid_tiers": valid_tiers},
                )
            )

        # Validate version format (semantic versioning)
        import re

        version = module.get("version", "")
        if version and not re.match(r"^v?\d+\.\d+\.\d+(-[\w.]+)?$", version):
            results.append(
                ValidationResult(
                    passed=False,
                    message=f"Invalid version format: {version}",
                    severity="warning",
                    details={"expected": "Semantic versioning (e.g., 1.0.0)"},
                )
            )

        return results

    def _validate_deployment(self, spec: Dict) -> List[ValidationResult]:
        """Validate deployment configuration."""
        results = []

        deployment = spec.get("spec", {}).get("deployment", {})

        if not deployment:
            results.append(
                ValidationResult(
                    passed=False,
                    message="Missing deployment configuration",
                    severity="error",
                )
            )
            return results

        # Check deployment type
        valid_types = ["helm", "kustomize", "raw", "operator"]
        if deployment.get("type") not in valid_types:
            results.append(
                ValidationResult(
                    passed=False,
                    message=f"Invalid deployment type: {deployment.get('type')}",
                    severity="error",
                    details={"valid_types": valid_types},
                )
            )

        # Check path
        if not deployment.get("path"):
            results.append(
                ValidationResult(
                    passed=False, message="Missing deployment path", severity="error"
                )
            )

        return results

    def _validate_testing(self, spec: Dict) -> List[ValidationResult]:
        """Validate testing configuration."""
        results = []

        testing = spec.get("spec", {}).get("testing", {})

        if not testing:
            results.append(
                ValidationResult(
                    passed=False,
                    message="Missing testing configuration",
                    severity="warning",
                )
            )
            return results

        # Check E2E tests (required)
        if not testing.get("e2e"):
            results.append(
                ValidationResult(
                    passed=False,
                    message="E2E testing configuration is required",
                    severity="error",
                )
            )
        else:
            e2e = testing["e2e"]
            if e2e.get("framework") != "stagehand":
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"Non-standard E2E framework: {e2e.get('framework')}",
                        severity="warning",
                        details={"recommended": "stagehand"},
                    )
                )

            if not e2e.get("path"):
                results.append(
                    ValidationResult(
                        passed=False,
                        message="E2E test path not specified",
                        severity="warning",
                    )
                )

        return results

    def _validate_requirements(self, spec: Dict) -> List[ValidationResult]:
        """Validate module requirements."""
        results = []

        requirements = spec.get("spec", {}).get("requirements", {})

        if not requirements:
            results.append(
                ValidationResult(
                    passed=False,
                    message="Missing requirements section",
                    severity="warning",
                )
            )
            return results

        # Check authentication
        auth = requirements.get("authentication", {})
        if auth.get("enabled", True) and not auth.get("clientId"):
            results.append(
                ValidationResult(
                    passed=False,
                    message="Authentication enabled but clientId not specified",
                    severity="warning",
                )
            )

        # Check monitoring
        monitoring = requirements.get("monitoring", {})
        if monitoring.get("metrics", {}).get("enabled", True):
            if not monitoring.get("metrics", {}).get("path"):
                results.append(
                    ValidationResult(
                        passed=False,
                        message="Metrics enabled but path not specified",
                        severity="info",
                        details={"default": "/metrics"},
                    )
                )

        # Check networking
        networking = requirements.get("networking", {})
        if networking.get("networkPolicies", True):
            results.append(
                ValidationResult(
                    passed=True,
                    message="NetworkPolicies enabled (good security practice)",
                    severity="info",
                )
            )
        else:
            results.append(
                ValidationResult(
                    passed=False,
                    message="NetworkPolicies disabled - not recommended for production",
                    severity="warning",
                )
            )

        return results

    def _validate_security(self, spec: Dict) -> List[ValidationResult]:
        """Validate security configuration."""
        results = []

        security = spec.get("spec", {}).get("security", {})

        # If no security section, warn about defaults
        if not security:
            results.append(
                ValidationResult(
                    passed=False,
                    message="No security configuration found - using platform defaults",
                    severity="warning",
                    details={"recommendation": "Define explicit security settings"},
                )
            )
            return results

        # Check pod security context
        pod_context = security.get("podSecurityContext", {})
        if not pod_context.get("runAsNonRoot", True):
            results.append(
                ValidationResult(
                    passed=False,
                    message="Pod configured to run as root - security risk",
                    severity="error",
                )
            )

        # Check container security context
        container_context = security.get("containerSecurityContext", {})
        if container_context.get("allowPrivilegeEscalation", False):
            results.append(
                ValidationResult(
                    passed=False,
                    message="Privilege escalation allowed - security risk",
                    severity="error",
                )
            )

        if not container_context.get("readOnlyRootFilesystem", True):
            results.append(
                ValidationResult(
                    passed=False,
                    message="Root filesystem is writable - consider read-only",
                    severity="warning",
                )
            )

        # Check capabilities
        capabilities = container_context.get("capabilities", {})
        if "ALL" not in capabilities.get("drop", []):
            results.append(
                ValidationResult(
                    passed=False,
                    message="Not dropping ALL capabilities - security risk",
                    severity="warning",
                )
            )

        # Check service account
        sa = security.get("serviceAccount", {})
        if sa.get("automountToken", False):
            results.append(
                ValidationResult(
                    passed=False,
                    message="Service account token automount enabled - security risk",
                    severity="warning",
                    details={"recommendation": "Disable unless required"},
                )
            )

        # Check image registry
        if not security.get("imageRegistry"):
            results.append(
                ValidationResult(
                    passed=False,
                    message="No approved image registry specified",
                    severity="info",
                    details={
                        "recommendation": "Specify approved registry for production"
                    },
                )
            )

        # Check secrets management
        secrets = security.get("secrets", {})
        if secrets.get("provider") == "manual":
            results.append(
                ValidationResult(
                    passed=False,
                    message="Manual secret management - consider using sealed-secrets or external-secrets",
                    severity="warning",
                )
            )

        return results

    def _validate_compliance(self, spec: Dict) -> List[ValidationResult]:
        """Validate compliance configuration."""
        results = []

        compliance = spec.get("spec", {}).get("compliance", {})

        if not compliance:
            results.append(
                ValidationResult(
                    passed=False,
                    message="No compliance configuration found",
                    severity="info",
                    details={
                        "recommendation": "Define compliance requirements for production"
                    },
                )
            )
            return results

        # Check data classification
        classification = compliance.get("dataClassification", "internal")
        if classification in ["confidential", "restricted"]:
            # Stricter checks for sensitive data
            spec.get("spec", {}).get("security", {})

            if not compliance.get("encryption", {}).get("atRest", True):
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"Encryption at rest disabled for {classification} data",
                        severity="error",
                    )
                )

            if not compliance.get("encryption", {}).get("inTransit", True):
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"Encryption in transit disabled for {classification} data",
                        severity="error",
                    )
                )

            if not compliance.get("auditLogging", True):
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"Audit logging disabled for {classification} data",
                        severity="error",
                    )
                )

        # Check frameworks
        frameworks = compliance.get("frameworks", [])
        if frameworks:
            results.append(
                ValidationResult(
                    passed=True,
                    message=f"Compliance frameworks configured: {', '.join(frameworks)}",
                    severity="info",
                )
            )

        # Check security scanning
        scanning = compliance.get("securityScanning", {})
        if not scanning.get("enabled", True):
            results.append(
                ValidationResult(
                    passed=False,
                    message="Security scanning disabled",
                    severity="warning",
                )
            )

        return results

    def validate_deployment_files(
        self, module_path: Path, spec: Dict
    ) -> List[ValidationResult]:
        """Validate that deployment files exist."""
        results = []

        deployment = spec.get("spec", {}).get("deployment", {})
        deployment_type = deployment.get("type")
        deployment_path = module_path / deployment.get("path", "k8s")

        if deployment_type == "kustomize":
            # Check for kustomization.yaml
            kustomization_file = deployment_path / "base" / "kustomization.yaml"
            if not kustomization_file.exists():
                # Try without base subdirectory
                kustomization_file = deployment_path / "kustomization.yaml"
                if not kustomization_file.exists():
                    results.append(
                        ValidationResult(
                            passed=False,
                            message=f"Kustomization file not found at {deployment_path}",
                            severity="error",
                        )
                    )

        elif deployment_type == "helm":
            # Check for Chart.yaml
            chart_file = deployment_path / "Chart.yaml"
            if not chart_file.exists():
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"Helm Chart.yaml not found at {deployment_path}",
                        severity="error",
                    )
                )

        return results

    def validate_test_files(
        self, module_path: Path, spec: Dict
    ) -> List[ValidationResult]:
        """Validate that test files exist."""
        results = []

        testing = spec.get("spec", {}).get("testing", {})

        # Check E2E tests
        if testing.get("e2e"):
            e2e_path = module_path / testing["e2e"].get("path", "tests/e2e")
            if not e2e_path.exists():
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"E2E test directory not found: {e2e_path}",
                        severity="warning",
                    )
                )
            else:
                # Check for entrypoint
                entrypoint = testing["e2e"].get("entrypoint")
                if entrypoint:
                    entrypoint_file = e2e_path / entrypoint
                    if not entrypoint_file.exists():
                        results.append(
                            ValidationResult(
                                passed=False,
                                message=f"E2E entrypoint not found: {entrypoint_file}",
                                severity="warning",
                            )
                        )

        # Check unit tests
        if testing.get("unit"):
            unit_path = module_path / testing["unit"].get("path", "tests")
            if not unit_path.exists():
                results.append(
                    ValidationResult(
                        passed=False,
                        message=f"Unit test directory not found: {unit_path}",
                        severity="info",
                    )
                )

        return results
