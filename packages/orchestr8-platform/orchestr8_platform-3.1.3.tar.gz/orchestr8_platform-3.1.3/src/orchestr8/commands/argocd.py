"""ArgoCD management commands with v3 authentication support."""

import subprocess
import base64
import json
from typing import Optional, Dict, Any
import sys
import os

import typer
from rich.console import Console
import httpx
import bcrypt

# Enable UTF-8 encoding for Windows to support Unicode characters
if sys.platform == "win32":
    # Set UTF-8 mode environment variable
    if os.environ.get("PYTHONUTF8") != "1":
        os.environ["PYTHONUTF8"] = "1"

    # Reconfigure stdout/stderr for UTF-8 if available (Python 3.7+)
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

# Configuration from environment variables
ARGOCD_URL = os.environ.get("ARGOCD_URL", "http://localhost:30080")
ARGOCD_NAMESPACE = os.environ.get("ARGOCD_NAMESPACE", "argocd")
ARGOCD_TIMEOUT = int(os.environ.get("ARGOCD_TIMEOUT", "60"))

app = typer.Typer(help="ArgoCD management commands")
# Create console with forced encoding for Windows compatibility
console = Console(force_terminal=True if sys.platform == "win32" else None)


def generate_bcrypt_hash(password: str) -> str:
    """Generate bcrypt hash compatible with ArgoCD v3."""
    # ArgoCD v3 requires bcrypt with cost factor 10
    salt = bcrypt.gensalt(rounds=10)
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def get_argocd_secret() -> Dict[str, Any]:
    """Get ArgoCD secret data."""
    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "secret",
                "argocd-secret",
                "-n",
                ARGOCD_NAMESPACE,
                "-o",
                "json",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)
    except subprocess.CalledProcessError:
        return None


def update_argocd_password(password: str) -> bool:
    """Update ArgoCD admin password with proper bcrypt hash."""
    try:
        # Generate bcrypt hash
        hashed = generate_bcrypt_hash(password)
        encoded_hash = base64.b64encode(hashed.encode("utf-8")).decode("utf-8")

        # Check if argocd-secret exists
        secret = get_argocd_secret()

        if secret:
            # Update existing secret
            patch_data = {
                "data": {
                    "admin.password": encoded_hash,
                    "admin.passwordMtime": base64.b64encode(
                        "2024-01-01T00:00:00Z".encode("utf-8")
                    ).decode("utf-8"),
                }
            }

            result = subprocess.run(
                [
                    "kubectl",
                    "patch",
                    "secret",
                    "argocd-secret",
                    "-n",
                    ARGOCD_NAMESPACE,
                    "--type",
                    "merge",
                    "-p",
                    json.dumps(patch_data),
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode != 0:
                console.print(f"[red]Failed to update secret: {result.stderr}[/red]")
                return False
        else:
            # Create new secret
            secret_manifest = {
                "apiVersion": "v1",
                "kind": "Secret",
                "metadata": {"name": "argocd-secret", "namespace": "argocd"},
                "type": "Opaque",
                "data": {
                    "admin.password": encoded_hash,
                    "admin.passwordMtime": base64.b64encode(
                        "2024-01-01T00:00:00Z".encode("utf-8")
                    ).decode("utf-8"),
                },
            }

            # Apply the secret
            process = subprocess.Popen(
                ["kubectl", "apply", "-f", "-"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
            stdout, stderr = process.communicate(input=json.dumps(secret_manifest))

            if process.returncode != 0:
                console.print(f"[red]Failed to create secret: {stderr}[/red]")
                return False

        # Update initial admin secret as well for consistency
        encoded_password = base64.b64encode(password.encode("utf-8")).decode("utf-8")
        subprocess.run(
            [
                "kubectl",
                "patch",
                "secret",
                "argocd-initial-admin-secret",
                "-n",
                ARGOCD_NAMESPACE,
                "--type",
                "merge",
                "-p",
                json.dumps({"data": {"password": encoded_password}}),
            ],
            capture_output=True,
            text=True,
        )

        # Restart ArgoCD server to pick up new password
        console.print("[yellow]Restarting ArgoCD server...[/yellow]")
        subprocess.run(
            [
                "kubectl",
                "rollout",
                "restart",
                "deployment/argocd-server",
                "-n",
                ARGOCD_NAMESPACE,
            ],
            capture_output=True,
        )

        # Wait for rollout to complete
        subprocess.run(
            [
                "kubectl",
                "rollout",
                "status",
                "deployment/argocd-server",
                "-n",
                ARGOCD_NAMESPACE,
                "--timeout=60s",
            ],
            capture_output=True,
        )

        return True

    except Exception as e:
        console.print(f"[red]Error updating password: {e}[/red]")
        return False


def verify_argocd_login(password: str) -> bool:
    """Verify ArgoCD login with new password."""
    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{ARGOCD_URL}/api/v1/session",
                json={"username": "admin", "password": password},
            )

            if response.status_code == 200:
                token = response.json().get("token")
                if token:
                    console.print(
                        "[green]✓ Successfully authenticated with ArgoCD[/green]"
                    )
                    return True
            else:
                console.print(
                    f"[red]Authentication failed: {response.status_code}[/red]"
                )
                return False

    except httpx.ConnectError:
        console.print(
            "[yellow]Cannot connect to ArgoCD. Ensure port-forward is active.[/yellow]"
        )
        console.print(
            "[dim]Run: kubectl port-forward svc/argocd-server -n argocd 30080:80[/dim]"
        )
        return False
    except Exception as e:
        console.print(f"[red]Login verification failed: {e}[/red]")
        return False


@app.command("reset-password")
def reset_password(
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="New password (will prompt if not provided, NOT RECOMMENDED - visible in shell history)",
    ),
    password_stdin: bool = typer.Option(
        False, "--password-stdin", help="Read password from stdin (more secure)"
    ),
    verify: bool = typer.Option(
        True, "--verify/--no-verify", help="Verify login after reset"
    ),
):
    """Reset ArgoCD admin password with v3 compatible bcrypt hash."""
    console.print("[bold cyan]ArgoCD Password Reset[/bold cyan]\n")

    # Check if ArgoCD is installed
    result = subprocess.run(
        ["kubectl", "get", "namespace", ARGOCD_NAMESPACE],
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        console.print(
            f"[red]ArgoCD namespace '{ARGOCD_NAMESPACE}' not found. Is ArgoCD installed?[/red]"
        )
        raise typer.Exit(1)

    # Get password from stdin if requested
    if password_stdin:
        console.print("[dim]Reading password from stdin...[/dim]")
        password = sys.stdin.read().strip()
        if not password:
            console.print("[red]No password provided via stdin[/red]")
            raise typer.Exit(1)
    # Get password if not provided
    elif not password:
        password = typer.prompt(
            "Enter new admin password", hide_input=True, confirmation_prompt=True
        )

    if len(password) < 8:
        console.print("[red]Password must be at least 8 characters long[/red]")
        raise typer.Exit(1)

    console.print("[yellow]Updating ArgoCD password...[/yellow]")

    if update_argocd_password(password):
        console.print("[green]✓ Password updated successfully[/green]")

        if verify:
            console.print("\n[yellow]Verifying login...[/yellow]")
            if verify_argocd_login(password):
                console.print("\n[green]Password reset complete![/green]")
                console.print(f"Login: admin / {password}")
            else:
                console.print(
                    "[yellow]Could not verify login. Password may still be updated.[/yellow]"
                )
                console.print(
                    "[dim]Try accessing ArgoCD UI at http://localhost:30080[/dim]"
                )
    else:
        console.print("[red]Failed to reset password[/red]")
        raise typer.Exit(1)


@app.command("login")
def login(
    password: Optional[str] = typer.Option(
        None,
        "--password",
        "-p",
        help="Admin password (NOT RECOMMENDED - visible in shell history)",
    ),
    password_stdin: bool = typer.Option(
        False, "--password-stdin", help="Read password from stdin (more secure)"
    ),
):
    """Test ArgoCD login and get authentication token."""
    console.print("[bold cyan]ArgoCD Login Test[/bold cyan]\n")

    # Get password from stdin if requested
    if password_stdin:
        console.print("[dim]Reading password from stdin...[/dim]")
        password = sys.stdin.read().strip()
        if not password:
            console.print("[red]No password provided via stdin[/red]")
            raise typer.Exit(1)
    # Get password if not provided
    elif not password:
        # Try to get from secret
        try:
            result = subprocess.run(
                [
                    "kubectl",
                    "get",
                    "secret",
                    "argocd-initial-admin-secret",
                    "-n",
                    ARGOCD_NAMESPACE,
                    "-o",
                    "jsonpath={.data.password}",
                ],
                capture_output=True,
                text=True,
            )

            if result.returncode == 0 and result.stdout:
                password = base64.b64decode(result.stdout).decode("utf-8")
                console.print(
                    "[dim]Using password from argocd-initial-admin-secret[/dim]"
                )
            else:
                password = typer.prompt("Enter admin password", hide_input=True)
        except Exception:
            password = typer.prompt("Enter admin password", hide_input=True)

    try:
        with httpx.Client(timeout=10.0) as client:
            response = client.post(
                f"{ARGOCD_URL}/api/v1/session",
                json={"username": "admin", "password": password},
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get("token")

                console.print("[green]✓ Login successful![/green]")

                # Test the token by getting version
                headers = {"Authorization": f"Bearer {token}"}
                version_response = client.get(
                    f"{ARGOCD_URL}/api/v1/version", headers=headers
                )

                if version_response.status_code == 200:
                    version_data = version_response.json()
                    console.print(
                        f"\n[cyan]ArgoCD Version:[/cyan] {version_data.get('Version', 'Unknown')}"
                    )

                # Only show token preview if explicitly requested (future feature)
                console.print(
                    "\n[dim]Authentication successful. Token generated.[/dim]"
                )
                console.print("[dim]Use this session for ArgoCD API operations.[/dim]")

                return token
            else:
                console.print(f"[red]Login failed: {response.status_code}[/red]")
                if response.text:
                    console.print(f"[dim]{response.text}[/dim]")

    except httpx.ConnectError:
        console.print("[red]Cannot connect to ArgoCD at http://localhost:30080[/red]")
        console.print("[yellow]Ensure ArgoCD is accessible:[/yellow]")
        console.print("  kubectl port-forward svc/argocd-server -n argocd 30080:80")
    except Exception as e:
        console.print(f"[red]Login error: {e}[/red]")

    raise typer.Exit(1)


@app.command("info")
def info():
    """Show ArgoCD server information and status."""
    console.print("[bold cyan]ArgoCD Server Information[/bold cyan]\n")

    # Check if namespace exists
    result = subprocess.run(
        ["kubectl", "get", "namespace", "argocd"], capture_output=True, text=True
    )

    if result.returncode != 0:
        console.print("[red]ArgoCD namespace not found[/red]")
        raise typer.Exit(1)

    # Get server deployment status
    result = subprocess.run(
        [
            "kubectl",
            "get",
            "deployment",
            "argocd-server",
            "-n",
            ARGOCD_NAMESPACE,
            "-o",
            "json",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        deployment = json.loads(result.stdout)
        status = deployment.get("status", {})

        ready = status.get("readyReplicas", 0)
        desired = status.get("replicas", 1)

        if ready == desired:
            console.print(f"[green]Server Status: Ready ({ready}/{desired})[/green]")
        else:
            console.print(
                f"[yellow]Server Status: Not Ready ({ready}/{desired})[/yellow]"
            )

    # Get ArgoCD version from image
    result = subprocess.run(
        [
            "kubectl",
            "get",
            "deployment",
            "argocd-server",
            "-n",
            ARGOCD_NAMESPACE,
            "-o",
            "jsonpath={.spec.template.spec.containers[0].image}",
        ],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        image = result.stdout
        version = image.split(":")[-1] if ":" in image else "latest"
        console.print(f"[cyan]Version:[/cyan] {version}")
        console.print(f"[dim]Image: {image}[/dim]")

    # Check for password secrets
    console.print("\n[cyan]Password Configuration:[/cyan]")

    secrets = ["argocd-initial-admin-secret", "argocd-secret"]
    for secret_name in secrets:
        result = subprocess.run(
            ["kubectl", "get", "secret", secret_name, "-n", ARGOCD_NAMESPACE],
            capture_output=True,
            text=True,
        )

        if result.returncode == 0:
            console.print(f"  ✓ {secret_name} exists")
        else:
            console.print(f"  ✗ {secret_name} not found")

    console.print("\n[cyan]Access URLs:[/cyan]")
    console.print(f"  Local: {ARGOCD_URL}")
    console.print(
        f"  Port-forward: kubectl port-forward svc/argocd-server -n {ARGOCD_NAMESPACE} 30080:80"
    )


if __name__ == "__main__":
    app()
