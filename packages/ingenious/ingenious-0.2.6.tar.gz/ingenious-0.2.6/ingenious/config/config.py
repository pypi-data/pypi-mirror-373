import os

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

from ingenious.config import IngeniousSettings
from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)


def get_kv_secret(secretName: str) -> str:
    # check if the key vault name is set in the environment variables
    if "KEY_VAULT_NAME" in os.environ:
        keyVaultName = os.environ["KEY_VAULT_NAME"]
        KVUri = f"https://{keyVaultName}.vault.azure.net"
        credential = DefaultAzureCredential()
        client = SecretClient(vault_url=KVUri, credential=credential)
        secret = client.get_secret(secretName)
        return secret.value or ""
    else:
        raise ValueError("KEY_VAULT_NAME environment variable not set")


def get_config(project_path: str = "") -> IngeniousSettings:
    """
    Get configuration using pydantic-settings system.

    This function provides configuration management that:
    - Automatically loads environment variables
    - Supports .env files
    - Provides validation with helpful error messages
    - Uses nested configuration models

    Args:
        project_path: Optional project path (for backward compatibility)

    Returns:
        IngeniousSettings: The loaded and validated configuration
    """
    try:
        settings = IngeniousSettings()
        settings.validate_configuration()
        return settings
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        raise
