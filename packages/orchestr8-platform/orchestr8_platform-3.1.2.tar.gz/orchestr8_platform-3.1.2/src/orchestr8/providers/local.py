"""Local provider for development and testing."""

import json
from pathlib import Path
from typing import Optional
import os


class LocalSecretsProvider:
    """Local file-based secrets provider for development."""

    def __init__(self, storage_path: Optional[Path] = None):
        if storage_path:
            self.storage_path = storage_path
        else:
            # Use user's home directory
            self.storage_path = Path.home() / ".orchestr8" / "secrets"

        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.secrets_file = self.storage_path / "secrets.json"

        # Load existing secrets
        self._load_secrets()

    def _load_secrets(self) -> None:
        """Load secrets from file."""
        if self.secrets_file.exists():
            with open(self.secrets_file, "r") as f:
                self.secrets = json.load(f)
        else:
            self.secrets = {}

    def _save_secrets(self) -> None:
        """Save secrets to file."""
        with open(self.secrets_file, "w") as f:
            json.dump(self.secrets, f, indent=2)

        # Set restrictive permissions (Unix-like systems)
        if os.name != "nt":
            os.chmod(self.secrets_file, 0o600)

    async def get_secret(self, key: str) -> Optional[str]:
        """Get a secret value."""
        return self.secrets.get(key)

    async def set_secret(
        self, key: str, value: str, description: Optional[str] = None
    ) -> None:
        """Set a secret value."""
        self.secrets[key] = value

        # Store metadata separately if needed
        if description:
            metadata_key = f"_metadata_{key}"
            self.secrets[metadata_key] = {"description": description}

        self._save_secrets()

    async def list_secrets(self) -> list[str]:
        """List all secrets."""
        return [k for k in self.secrets.keys() if not k.startswith("_metadata_")]

    async def delete_secret(self, key: str) -> None:
        """Delete a secret."""
        if key in self.secrets:
            del self.secrets[key]

            # Remove metadata if exists
            metadata_key = f"_metadata_{key}"
            if metadata_key in self.secrets:
                del self.secrets[metadata_key]

            self._save_secrets()
