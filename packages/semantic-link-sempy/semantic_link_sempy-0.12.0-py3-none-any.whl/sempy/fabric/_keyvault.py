import base64
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


def get_key_vault_secret(
    vault: str,
    secret: str,
    credential: Optional["TokenCredential"] = None
) -> str:
    """
    Get a secret from Azure Key Vault.

    Parameters
    ----------
    vault : str
        Name or URL of the Key Vault.
    secret : str
        Name of the secret in the target Key Vault to be retrieved.
    credential : azure.core.credentials.TokenCredential, default=None
        Token credential to use for authentication. If None, the default
        credential will be used.

    Returns
    -------
    str
        The value of the secret.
    """
    vault = vault if vault.startswith("https://") else f"https://{vault}.vault.azure.net"

    from azure.keyvault.secrets import SecretClient

    if credential is None:
        from fabric.analytics.environment.credentials import \
            FabricAnalyticsTokenCredentials
        credential = FabricAnalyticsTokenCredentials()

    client = SecretClient(vault_url=vault, credential=credential)
    secret_value = client.get_secret(secret)
    return secret_value.value or ""


def get_key_vault_certificate(
    vault: str,
    certificate: str,
    credential: Optional["TokenCredential"] = None
) -> bytes:
    """
    Get a certificate from Azure Key Vault.

    Parameters
    ----------
    vault : str
        URL of the Key Vault.
    certificate : str
        Name of the certificate in the target Key Vault to be retrieved.
    credential : azure.core.credentials.TokenCredential, default=None
        Token credential to use for authentication. If None, the default
        credential will be used.

    Returns
    -------
    bytes
        The content bytes of the certificate.
    """
    return base64.b64decode(
        get_key_vault_secret(vault, certificate, credential=credential)
    )
