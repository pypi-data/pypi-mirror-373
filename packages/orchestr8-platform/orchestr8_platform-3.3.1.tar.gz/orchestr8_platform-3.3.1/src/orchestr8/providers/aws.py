"""AWS provider implementations."""

import json
from typing import Optional
import boto3
from botocore.exceptions import ClientError


class AWSSecretsProvider:
    """AWS Secrets Manager provider for secret storage."""

    def __init__(self, region: str, cluster_name: str):
        self.region = region
        self.cluster_name = cluster_name
        self.client = boto3.client("secretsmanager", region_name=region)
        self.prefix = f"o8/{cluster_name}"

    def _get_secret_name(self, key: str) -> str:
        """Get full secret name with prefix."""
        return f"{self.prefix}/{key}"

    async def get_secret(self, key: str) -> Optional[str]:
        """Get a secret value."""
        try:
            response = self.client.get_secret_value(SecretId=self._get_secret_name(key))

            # Secrets Manager stores as JSON by default
            if "SecretString" in response:
                secret_data = json.loads(response["SecretString"])
                return secret_data.get("value")

            return None

        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                return None
            raise

    async def set_secret(
        self, key: str, value: str, description: Optional[str] = None
    ) -> None:
        """Set a secret value."""
        secret_name = self._get_secret_name(key)
        secret_data = json.dumps({"value": value})

        try:
            # Try to update existing secret
            self.client.put_secret_value(SecretId=secret_name, SecretString=secret_data)
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                # Create new secret
                self.client.create_secret(
                    Name=secret_name,
                    Description=description or f"Orchestr8 secret: {key}",
                    SecretString=secret_data,
                    Tags=[
                        {"Key": "ManagedBy", "Value": "Orchestr8"},
                        {"Key": "Cluster", "Value": self.cluster_name},
                    ],
                )
            else:
                raise

    async def list_secrets(self) -> list[str]:
        """List all secrets for this cluster."""
        secrets = []
        paginator = self.client.get_paginator("list_secrets")

        for page in paginator.paginate(
            Filters=[{"Key": "name", "Values": [self.prefix]}]
        ):
            for secret in page["SecretList"]:
                # Extract key from full name
                name = secret["Name"]
                if name.startswith(self.prefix + "/"):
                    key = name[len(self.prefix) + 1 :]
                    secrets.append(key)

        return secrets

    async def delete_secret(self, key: str) -> None:
        """Delete a secret."""
        try:
            self.client.delete_secret(
                SecretId=self._get_secret_name(key), ForceDeleteWithoutRecovery=True
            )
        except ClientError as e:
            if e.response["Error"]["Code"] != "ResourceNotFoundException":
                raise
