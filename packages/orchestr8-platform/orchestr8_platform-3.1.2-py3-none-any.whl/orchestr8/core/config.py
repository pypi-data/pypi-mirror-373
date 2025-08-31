"""Configuration models for Orchestr8."""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator


class CloudProvider(str, Enum):
    """Supported cloud providers."""

    AWS = "aws"
    GCP = "gcp"
    AZURE = "azure"
    LOCAL = "local"


class GitHubConfig(BaseModel):
    """GitHub configuration."""

    org: str = Field(..., description="GitHub organization")
    token: Optional[str] = Field(None, description="GitHub personal access token")


class KeycloakConfig(BaseModel):
    """Keycloak configuration."""

    admin_username: str = Field(default="admin", description="Admin username")
    admin_password: Optional[str] = Field(None, description="Admin password")
    realm: str = Field(default="platform", description="Keycloak realm")


class Config(BaseModel):
    """Main configuration for Orchestr8."""

    provider: CloudProvider = Field(..., description="Cloud provider")
    region: Optional[str] = Field(None, description="Cloud region")
    cluster_name: str = Field(..., description="Kubernetes cluster name")
    domain: str = Field(..., description="Platform domain")
    github: GitHubConfig = Field(..., description="GitHub configuration")
    keycloak: KeycloakConfig = Field(default_factory=KeycloakConfig)
    namespace: str = Field(default="platform", description="Platform namespace")

    # Infrastructure provisioning options
    provision_infrastructure: bool = Field(
        default=False, description="Provision cloud infrastructure with Terraform"
    )
    gcp_project_id: Optional[str] = Field(
        None, description="GCP Project ID for infrastructure provisioning"
    )
    environment: str = Field(
        default="dev", description="Environment (dev, staging, production)"
    )
    machine_type: Optional[str] = Field(
        default="e2-standard-4", description="Machine type for nodes"
    )
    node_count: int = Field(default=3, description="Number of nodes")

    @field_validator("cluster_name")
    def validate_cluster_name(cls, v: str) -> str:
        """Validate cluster name format."""
        import re

        if not re.match(r"^[a-z0-9-]+$", v):
            raise ValueError(
                "Cluster name must contain only lowercase letters, numbers, and hyphens"
            )
        return v

    @field_validator("domain")
    def validate_domain(cls, v: str) -> str:
        """Validate domain format."""
        import re

        if not re.match(r"^[a-z0-9.-]+$", v):
            raise ValueError("Domain must be a valid hostname")
        return v

    @property
    def is_local(self) -> bool:
        """Check if running in local mode."""
        return self.provider == CloudProvider.LOCAL

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return self.model_dump(exclude_none=True)
