"""Context module for handling configuration loading and management."""

import os
from datetime import datetime
from typing import Dict, Any, Optional

import bugsnag
import jwt
import requests
import yaml

from cerebrium import env
from cerebrium.utils.logging import cerebrium_log

DEFAULT_CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".cerebrium", "config.yaml")
CONFIG_PATH = os.getenv("CEREBRIUM_CONFIG_PATH", DEFAULT_CONFIG_PATH)

environment = os.getenv("CEREBRIUM_ENV", "prod")


class CLIContext:
    """Global CLI context to store service account token and verbose mode."""

    def __init__(self):
        self.service_account_token: Optional[str] = None
        self.verbose: bool = False


cli_context = CLIContext()


class InvalidProjectIDError(Exception):
    """Raised when a project ID is invalid"""

    pass


def _get_env_key(key: str) -> str:
    """
    Get the environment-specific key for config storage.

    Args:
        key: The base key name

    Returns:
        str: The environment-prefixed key
    """
    prefix = "" if environment == "prod" else f"{environment}-"
    return f"{prefix}{key}"


def load_config() -> Dict[str, Any]:
    """
    Load configuration from the YAML config file.

    Returns:
        Dict[str, Any]: The loaded configuration dictionary, or empty dict if file doesn't exist
    """
    if not os.path.exists(CONFIG_PATH):
        return {}

    with open(CONFIG_PATH, "r") as f:
        config = yaml.safe_load(f) or {}

    return config


def save_config(config: Dict[str, Any]) -> None:
    """
    Save configuration to the YAML config file.

    Args:
        config: The configuration dictionary to save
    """
    # Ensure the directory exists
    config_dir = os.path.dirname(CONFIG_PATH)
    os.makedirs(config_dir, exist_ok=True)

    with open(CONFIG_PATH, "w", newline="\n") as f:
        yaml.safe_dump(config, f)


def get_config_value(key: str) -> Optional[Any]:
    """
    Get a configuration value for the current environment.

    Args:
        key: The configuration key (without environment prefix)

    Returns:
        The configuration value or None if not found
    """
    config = load_config()
    return config.get(_get_env_key(key))


def set_config_value(key: str, value: Any) -> None:
    """
    Set a configuration value for the current environment.

    Args:
        key: The configuration key (without environment prefix)
        value: The value to set
    """
    config = load_config()
    config[_get_env_key(key)] = value
    save_config(config)


def get_token_from_config() -> tuple[Optional[str], Optional[str]]:
    """
    Get JWT and refresh tokens from the config for the current environment.

    Checks for both service account tokens and regular access tokens.

    Returns:
        tuple: (jwt_token, refresh_token) - both can be None if not found
    """
    # First check for service account token (from save-auth-config with JWT)
    jwt_token = get_config_value("serviceAccountToken")
    if jwt_token:
        # Service account tokens don't have refresh tokens
        return jwt_token, None

    # Fall back to regular access token
    jwt_token = get_config_value("accessToken")
    refresh_token = get_config_value("refreshToken")
    return jwt_token, refresh_token


def update_token_in_config(jwt_token: str) -> None:
    """
    Update the JWT token in the config for the current environment.

    Args:
        jwt_token: The new JWT token
    """
    set_config_value("accessToken", jwt_token)


def get_service_account_token() -> Optional[str]:
    if cli_context.service_account_token:
        return cli_context.service_account_token

    service_account_token = os.getenv("CEREBRIUM_SERVICE_ACCOUNT_TOKEN")
    if service_account_token and validate_service_account_token(service_account_token):
        return service_account_token

    # 3. Check stored service account token (from save-auth-config with JWT)
    service_account_token = get_config_value("serviceAccountToken")
    if service_account_token and validate_service_account_token(service_account_token):
        return service_account_token
    return None


def get_or_refresh_token() -> Optional[str]:
    """
    Get the current JWT token, refreshing it if expired.

    This function checks if a user's JWT token has expired. If it has, it makes a request
    to Cognito with the refresh token to generate a new one.

    Token precedence:
    1. service_account_token from CLI flag (--service-account-token)
    2. CEREBRIUM_SERVICE_ACCOUNT_TOKEN environment variable
    3. Stored service account token (from save-auth-config with JWT)
    4. Stored session token (from login)

    Returns:
        str: A valid JWT token, or None if authentication fails.
    """
    service_account_token = get_service_account_token()
    if service_account_token:
        return service_account_token

    # 4. Fall back to stored session token
    # Assuming the JWT token is stored in a config file
    if not os.path.exists(CONFIG_PATH):
        cerebrium_log(
            level="ERROR",
            message="You must log in or provide a service account to use this functionality. Please run 'cerebrium login' or see CI/CD docs for more information.",
            prefix="",
        )
        bugsnag.notify(Exception("User not logged in"), severity="warning")
        return None

    jwt_token, refresh_token = get_token_from_config()
    if not jwt_token:
        cerebrium_log(
            level="ERROR",
            message="You must log in to use this functionality. Please run 'cerebrium login'",
            prefix="",
        )
        bugsnag.notify(Exception("User not logged in"), severity="warning")
        return None

    # Decode the JWT token without verification to check the expiration time
    try:
        payload = jwt.decode(jwt_token, options={"verify_signature": False})
    except Exception as e:
        cerebrium_log(level="ERROR", message=f"Failed to decode JWT token: {str(e)}", prefix="")
        bugsnag.notify(Exception("Failed to decode JWT token."), severity="warning")
        return None

    # Check if the token has expired
    # Service account tokens (no refresh_token) cannot be refreshed
    if datetime.fromtimestamp(payload["exp"]) < datetime.now():
        if not refresh_token:
            cerebrium_log(
                level="ERROR",
                message="Service account token has expired. Please generate a new one.",
                prefix="",
            )
            bugsnag.notify(Exception("Service account token expired"), severity="warning")
            return None
        # Token has expired, request a new one using the refresh token
        response = requests.post(
            env.values()["auth_url"],
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "refresh_token",
                "client_id": env.values()["client_id"],
                "refresh_token": refresh_token,
            },
            timeout=30,
        )
        if response.status_code == 200:
            new_jwt_token = response.json()["access_token"]
            # Update the config file with the new JWT token
            update_token_in_config(new_jwt_token)
            return new_jwt_token
        else:
            cerebrium_log(
                level="ERROR",
                message="Failed to refresh JWT token. Please login again.",
                prefix="",
            )
            bugsnag.notify(Exception("Failed to refresh JWT token."), severity="warning")
            return None
    else:
        # Token has not expired, return the current JWT token
        return jwt_token


def validate_service_account_token(service_account_token: str):
    # Decode the JWT token without verification to check the expiration time
    try:
        payload = jwt.decode(service_account_token, options={"verify_signature": False})
    except Exception as e:
        cerebrium_log(level="ERROR", message=f"Failed to decode JWT token: {str(e)}", prefix="")
        bugsnag.notify(Exception("Failed to decode JWT token."), severity="warning")
        return False

    # Check if the token has expired
    # Service account tokens (no refresh_token) cannot be refreshed
    if "exp" in payload and datetime.fromtimestamp(payload["exp"]) < datetime.now():
        cerebrium_log(
            level="ERROR",
            message="Service account token has expired. Please generate a new one.",
            prefix="",
        )
        bugsnag.notify(Exception("Service account token expired"), severity="warning")
        return False
    return True


def is_valid_project_id(project_id: str) -> bool:
    """
    Validate that the project ID starts with 'p-' or 'dev-p-'
    """
    return project_id.startswith(("p-", "dev-p-"))


def get_current_project() -> Optional[str]:
    """
    Get the current project context and project name
    """
    if environment == "test":
        return "test-project"

    try:
        project_id = get_config_value("project")

        if project_id:
            if is_valid_project_id(project_id):
                return project_id
            else:
                raise InvalidProjectIDError(f"Invalid project ID: {project_id}")

        service_account_token = get_service_account_token()
        if service_account_token:
            project_id = extract_project_id_from_jwt(service_account_token)
            if project_id:
                return project_id
            else:
                raise InvalidProjectIDError(f"Invalid project ID: {project_id}")

        return None
    except Exception as e:
        bugsnag.notify(e, severity="error")
        raise


def get_default_region() -> str:
    """
    Get the default region for the current environment.

    Returns:
        str: The default region, defaults to 'us-east-1' if not set
    """
    region = get_config_value("defaultRegion")
    return region if region else "us-east-1"


def set_default_region(region: str) -> None:
    """
    Set the default region for the current environment.

    Args:
        region: The region to set as default (e.g., 'us-east-1', 'eu-west-1')
    """
    set_config_value("defaultRegion", region)


def extract_project_id_from_jwt(jwt_token: str) -> Optional[str]:
    """
    Extract project ID from a JWT token.
    Args:
        jwt_token: The JWT token to extract project ID from
    Returns:
        str: The extracted project ID, or None if not found
    """
    try:
        # Decode JWT without verification to extract claims
        decoded = jwt.decode(jwt_token, options={"verify_signature": False})

        # Try to extract project_id from JWT
        # Common claim names for project_id
        for claim in ["project_id", "projectId", "sub", "project"]:
            if claim in decoded and is_valid_project_id(decoded[claim]):
                return decoded[claim]

        # Check custom claims if still no project_id
        if "custom" in decoded:
            custom_claims = decoded["custom"]
            for claim in ["project_id", "projectId", "project"]:
                if claim in custom_claims and is_valid_project_id(decoded[claim]):
                    return custom_claims[claim]

        return None
    except Exception as e:
        return None
