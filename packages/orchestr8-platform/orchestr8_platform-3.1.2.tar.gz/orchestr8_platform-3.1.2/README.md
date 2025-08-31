# Orchestr8

A unified SDK and CLI for automated Kubernetes platform management using GitOps principles.

## Features

- 🚀 **Zero-touch cluster bootstrapping** - Automated setup with minimal manual steps
- 🔐 **Integrated secrets management** - AWS/GCP Secrets Manager support with automatic generation
- 🤖 **Multiple interfaces** - Use as CLI or SDK for programmatic access
- ☁️ **Multi-cloud ready** - Support for AWS, GCP, Azure, and local development
- 🔄 **GitOps native** - Built on ArgoCD with the app-of-apps pattern
- 🩺 **Built-in diagnostics** - Auto-running health checks and environment validation

## Installation

```bash
# Install from PyPI
uv tool install orchestr8-platform

# Or add to your project
uv add orchestr8-platform
```

## Quick Start

### CLI Usage

```bash
# Interactive setup
o8 setup

# Non-interactive setup
o8 setup \
  --provider aws \
  --cluster my-cluster \
  --domain platform.example.com \
  --github-org my-org \
  --region us-east-1

# Check status and validate environment
o8 status
o8 doctor

# Validate prerequisites
o8 validate
```

### SDK Usage

```python
from orchestr8 import Orchestr8SDK, Config, CloudProvider
from orchestr8.core.config import GitHubConfig

# Create configuration
config = Config(
    provider=CloudProvider.AWS,
    region="us-east-1",
    cluster_name="my-cluster",
    domain="platform.example.com",
    github=GitHubConfig(
        org="my-org",
        token="ghp_..."
    )
)

# Initialize SDK
sdk = Orchestr8SDK(config)

# Run setup
await sdk.setup()

# Check status
status = await sdk.get_status()
```

## Architecture

Orchestr8 sets up:

- **ArgoCD** - GitOps continuous delivery
- **Istio** - Service mesh for traffic management
- **Keycloak** - Identity and access management
- **Prometheus/Grafana** - Monitoring and observability
- **Cert-Manager** - Automatic TLS certificate management

## Development

```bash
# Clone the repository
git clone https://github.com/killerapp/orchestr8
cd orchestr8/o8-cli

# Install dependencies
uv sync

# Run tests
uv run pytest

# Run CLI in development
uv run python -m orchestr8.cli
```

## Publishing to PyPI

```bash
# Build the package
uv build

# Publish to PyPI
uv publish
```

## License

MIT
