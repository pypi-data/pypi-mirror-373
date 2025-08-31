"""Orchestr8 Exception Classes."""


class Orchestr8Error(Exception):
    """Base exception for all Orchestr8 errors."""

    pass


class ConfigurationError(Orchestr8Error):
    """Error in configuration or setup."""

    pass


class ValidationError(Orchestr8Error):
    """Error in data validation."""

    pass


class ProviderError(Orchestr8Error):
    """Error with cloud provider operations."""

    pass


class AuthenticationError(Orchestr8Error):
    """Error with authentication or authorization."""

    pass


class DeploymentError(Orchestr8Error):
    """Error during deployment operations."""

    pass
