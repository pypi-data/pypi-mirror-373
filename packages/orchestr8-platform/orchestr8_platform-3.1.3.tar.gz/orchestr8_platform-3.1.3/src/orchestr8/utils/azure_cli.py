"""Azure CLI helper utilities for Windows compatibility."""

import os
import platform
import subprocess
import shutil
from typing import List, Dict, Any


def get_azure_cli_path() -> str:
    """Get the correct path to Azure CLI executable."""
    if platform.system() == "Windows":
        # Common Azure CLI install locations on Windows
        possible_paths = [
            r"C:\Program Files\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
            r"C:\Program Files (x86)\Microsoft SDKs\Azure\CLI2\wbin\az.cmd",
            shutil.which("az.cmd"),
            shutil.which("az"),
        ]

        for path in possible_paths:
            if path and os.path.exists(path):
                return path

        # If not found in standard locations, try to find it
        az_path = shutil.which("az")
        if az_path:
            return az_path

        raise FileNotFoundError(
            "Azure CLI not found. Please install it from: "
            "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli-windows"
        )
    else:
        # On Linux/Mac, use standard which
        az_path = shutil.which("az")
        if not az_path:
            raise FileNotFoundError(
                "Azure CLI not found. Please install it from: "
                "https://docs.microsoft.com/en-us/cli/azure/install-azure-cli"
            )
        return az_path


def run_azure_cli(
    args: List[str],
    capture_output: bool = True,
    text: bool = True,
    check: bool = False,
    **kwargs,
) -> subprocess.CompletedProcess:
    """Run Azure CLI command with proper Windows compatibility.

    Args:
        args: List of arguments to pass to az CLI (without 'az' prefix)
        capture_output: Whether to capture stdout/stderr
        text: Whether to return output as text
        check: Whether to raise exception on non-zero return code
        **kwargs: Additional arguments to pass to subprocess.run

    Returns:
        CompletedProcess object with the result
    """
    az_path = get_azure_cli_path()

    # On Windows, if it's a .cmd file, we need to run it through cmd
    if platform.system() == "Windows" and az_path.endswith(".cmd"):
        # Use the cmd file directly
        full_command = [az_path] + args
    else:
        full_command = [az_path] + args

    # Add shell=True on Windows for .cmd files
    if platform.system() == "Windows" and az_path.endswith(".cmd"):
        # On Windows, we need to properly quote the command
        if platform.system() == "Windows":
            # Windows doesn't use shlex, just join with spaces
            full_command_str = " ".join(
                f'"{arg}"' if " " in arg else arg for arg in full_command
            )
            return subprocess.run(
                full_command_str,
                capture_output=capture_output,
                text=text,
                check=check,
                shell=True,  # nosec B602 - Required for Windows .cmd execution
                **kwargs,
            )

    return subprocess.run(
        full_command, capture_output=capture_output, text=text, check=check, **kwargs
    )


def check_azure_cli_auth() -> Dict[str, Any]:
    """Check if Azure CLI is authenticated.

    Returns:
        Dict with account information if authenticated

    Raises:
        RuntimeError: If not authenticated
    """
    import json

    try:
        result = run_azure_cli(
            ["account", "show", "--output", "json"],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        raise RuntimeError("Not authenticated with Azure CLI. Please run: az login")
    except json.JSONDecodeError as e:
        raise RuntimeError(f"Failed to parse Azure CLI output: {e}")
