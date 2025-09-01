from __future__ import annotations

import datetime
from contextlib import contextmanager
from functools import wraps
from typing import TYPE_CHECKING, Optional, Tuple, Union, cast

import jwt
from azure.core.credentials import AccessToken

from sempy.fabric._keyvault import (get_key_vault_certificate,
                                    get_key_vault_secret)

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


@contextmanager
def set_service_principal(tenant_id: Union[str, Tuple[str, str]],
                          client_id: Union[str, Tuple[str, str]],
                          *,
                          client_secret: Optional[Union[str, Tuple[str, str]]] = None,
                          client_certificate: Optional[Union[bytes, Tuple[str, str]]] = None):
    """
    Set the service principal credentials as the default authentication using a context manager.

    Parameters
    ----------
    tenant_id : str or Tuple[str, str]
        The tenant ID, or a Key Vault reference as a pair of (Key Vault name or URI,
        secret name) which stores the tenant ID.
    client_id : str or Tuple[str, str]
        The client ID, or a Key Vault reference as a pair of (Key Vault name or URI,
        secret name) which stores the client ID.
    client_secret : str or Tuple[str, str], default=None
        The client secret, or a Key Vault reference as a pair of (Key Vault name or URI,
        secret name) which stores the client secret. You should provide either
        `client_secret` or `client_certificate` to authenticate the service
        principal. `client_secret` will be ignored if both are provided.
    client_certificate : bytes or Tuple[str, str], default=None
        The client certificate bytes, or a Key Vault reference as a pair of
        (Key Vault name or URI, secret name) which stores the client certificate. You
        should provide either `client_secret` or `client_certificate` to
        authenticate the service principal. `client_secret` will be ignored
        if both are provided.

    Yields
    ------
    None

    Examples
    --------
    >>> # Using direct values
    >>> import sempy.fabric as fabric
    >>> from sempy.fabric import set_service_principal
    >>> with set_service_principal(
    ...     tenant_id="abcd1234-...",
    ...     client_id="9876abcd-...",
    ...     client_secret="abcde..."
    ... ):
    ...     # Do something with the service principal credentials
    ...     fabric.list_workspaces()

    >>> # Using Key Vault name references
    >>> import sempy.fabric as fabric
    >>> from sempy.fabric import set_service_principal
    >>> with set_service_principal(
    ...     tenant_id=("my_vault", "tenant_id_kv"),
    ...     client_id=("my_vault", "client_id_kv"),
    ...     client_secret=("my_vault", "client_secret_kv")
    ... ):
    ...     # Do something with the service principal credentials
    ...     fabric.list_workspaces()

    >>> # Using Key Vault URI references
    >>> import sempy.fabric as fabric
    >>> from sempy.fabric import set_service_principal
    >>> with set_service_principal(
    ...     tenant_id=("https://myvault.vault.azure.net", "tenant_id_kv"),
    ...     client_id=("https://myvault.vault.azure.net", "client_id_kv"),
    ...     client_secret=("https://myvault.vault.azure.net", "client_secret_kv")
    ... ):
    ...     # Do something with the service principal credentials
    ...     fabric.list_workspaces()

    >>> # Using certificate authentication
    >>> import sempy.fabric as fabric
    >>> from sempy.fabric import set_service_principal
    >>> with set_service_principal(
    ...     tenant_id="abcd1234-...",
    ...     client_id="9876abcd-...",
    ...     client_certificate=b'<certficate data>'
    ... ):
    ...     # Do something with the service principal credentials
    ...     fabric.list_workspaces()
    """
    with set_default_credential(
        ServicePrincipalCredential(
            tenant_id,
            client_id,
            client_secret=client_secret,
            client_certificate=client_certificate
        )
    ):
        yield


def get_access_token(*scopes: str) -> AccessToken:
    """
    Get token of the specified scopes from Fabric token library.

    Parameters
    ----------
    scope : str, default=None
        Desired scopes for the access token. If none is provided, the default
        scope for Power BI is used.

    Returns
    -------
    AccessToken
        The access token for the specified audience.
    """

    if not scopes:
        from fabric.analytics.environment.constant import PBI_SCOPE
        scopes = (PBI_SCOPE,)

    from fabric.analytics.environment.credentials import \
        FabricAnalyticsTokenCredentials
    return (
        FabricAnalyticsTokenCredentials()
        .get_token(*scopes)
    )


def build_access_token(token: str) -> AccessToken:
    """
    Build an AccessToken from the token string. This is used to create a
    ConstantTokenCredential.

    Parameters
    ----------
    token : str
        The access token string.

    Returns
    -------
    AccessToken
        The AccessToken object.
    """
    exp = _get_token_expiry_raw_timestamp(token)
    return AccessToken(token, exp)


@contextmanager
def set_default_credential(credential: Optional["TokenCredential"] = None):
    """
    Set the default credential for the current thread.

    Parameters
    ----------
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    if not credential:
        yield
        return

    from fabric.analytics.environment.credentials import \
        SetFabricAnalyticsDefaultTokenCredentials

    with SetFabricAnalyticsDefaultTokenCredentials(credential):
        yield


def with_credential(func):
    """
    A decorator to handle credentials for functions by setting the default
    credential using the `set_default_credential` context manager.

    This decorator automatically extracts a `credential` parameter from the
    wrapped function's keyword arguments and temporarily sets it as the default
    credential during function execution.

    Requirements
    ------------
    The wrapped function MUST include an optional `credential` parameter in its
    signature, typically as:

    ```python
    @with_credential
    def my_function(param1, param2, *, credential: Optional[TokenCredential] = None):
        # Function implementation
        pass
    ```

    Parameters
    ----------
    func : callable
        The function to be wrapped. Must accept an optional `credential` parameter.

    Returns
    -------
    callable
        The wrapped function that handles credential context automatically.

    Examples
    --------
    >>> @with_credential
    ... def list_datasets(workspace: str, *, credential: Optional[TokenCredential] = None):
    ...     # Function logic using default credential
    ...     pass
    ...
    >>> # Usage - credential is automatically handled
    >>> list_datasets("my_workspace", credential=my_credential)
    """
    import inspect

    # Validate that the function has a credential parameter
    sig = inspect.signature(func)
    if 'credential' not in sig.parameters:
        raise ValueError(
            f"Function '{func.__name__}' must have an optional 'credential' parameter "
            f"to use the @with_credential decorator. "
            f"Add '*, credential: Optional[TokenCredential] = None' to the function signature."
        )

    @wraps(func)
    def wrapped(*args, **kwargs):
        """
        Wrapper that extracts the credential parameter and sets it as the default
        credential context before calling the original function.
        """
        credential = kwargs.pop("credential", None)
        with set_default_credential(credential):
            return func(*args, **kwargs)

    return wrapped


def get_token_seconds_remaining(token: str) -> int:
    """
    Get the number of seconds remaining until the token expires.

    Parameters
    ----------
    token : str
        The access token.

    Returns
    -------
    int
        The number of seconds remaining until the token expires.
    """
    exp_time = _get_token_expiry_raw_timestamp(token)
    now_epoch = (datetime.datetime.now(tz=datetime.timezone.utc) - datetime.datetime(1970, 1, 1, tzinfo=datetime.timezone.utc)).total_seconds()
    return int(exp_time - now_epoch)


def get_token_expiry_utc(token: str) -> str:
    """
    Get the token expiry time in UTC format.

    Parameters
    ----------
    token : str
        The access token.

    Returns
    -------
    str
        The token expiry time in UTC format.
    """
    exp_time = _get_token_expiry_raw_timestamp(token)
    return str(datetime.datetime.fromtimestamp(exp_time, tz=datetime.timezone.utc))


def _get_token_expiry_raw_timestamp(token: str) -> int:
    """
    Get the raw expiry timestamp (in seconds) from the token. The value is
    decoded from the JWT token.

    Parameters
    ----------
    token : str
        The access token.

    Returns
    -------
    int
        The raw expiry timestamp value (in seconds).
    """
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload.get("exp", 0)
    except jwt.DecodeError:
        # Token is not a valid token (ex: using myToken in tests)
        return 0


class ConstantTokenCredential:
    """
    An implementation of `azure.core.credentials.TokenCredential` that built
    from an AccessToken and always returns the same one in subsequent calls.

    Parameters
    ----------
    token : AccessToken or str
        The access token or the token string to be built from and to be
        returned in the subsequent calls.
    """
    def __init__(self, token: Union[AccessToken, str]):
        if isinstance(token, str):
            self._token = build_access_token(token)
        elif isinstance(token, AccessToken):
            self._token = token
        else:
            raise TypeError("Input token must be either a string or an "
                            f"AccessToken, but got {type(token)}")

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        """
        Return the same access token which is used to initialize this instance.

        Parameters
        ----------
        scopes : tuple
            The scopes for which the token is requested. Will be ignored in
            this implementation.
        kwargs : dict
            Additional keyword arguments. Will be ignored in this
            implementation.

        Returns
        -------
        AccessToken
            The access token that was used to initialize this instance.
        """
        return self._token


class ServicePrincipalCredential:

    def __init__(self,
                 tenant_id: Union[str, Tuple[str, str]],
                 client_id: Union[str, Tuple[str, str]],
                 *,
                 client_secret: Optional[Union[str, Tuple[str, str]]] = None,
                 client_certificate: Optional[Union[bytes, Tuple[str, str]]] = None) -> None:

        self._token_credential: "TokenCredential"

        client_auth_count = sum([client_certificate is not None, client_secret is not None])
        if client_auth_count != 1:
            raise ValueError("Exactly one authentication parameter from "
                             "{`client_secret`, `client_certificate`} must be "
                             f"provided, but got {client_auth_count}")

        def _resolve_secret(secret, is_cert=False):
            if isinstance(secret, (str, bytes)):
                return secret

            kv_uri, kv_secret = secret
            kv_uri = kv_uri if kv_uri.startswith("https://") else f"https://{kv_uri}.vault.azure.net"
            if is_cert:
                return get_key_vault_certificate(kv_uri, kv_secret)
            return get_key_vault_secret(kv_uri, kv_secret)

        tenant_id = cast(str, _resolve_secret(tenant_id))
        client_id = cast(str, _resolve_secret(client_id))

        if client_secret is not None:
            from azure.identity import ClientSecretCredential  # type: ignore
            self._token_credential = ClientSecretCredential(
                tenant_id,
                client_id,
                _resolve_secret(client_secret)
            )

        else:
            from azure.identity import CertificateCredential  # type: ignore
            self._token_credential = CertificateCredential(
                tenant_id,
                client_id,
                certificate_data=_resolve_secret(client_certificate, is_cert=True)
            )

    def get_token(self, *scopes, **kwargs) -> AccessToken:
        """
        Get the access token for the specified scopes.

        Parameters
        ----------
        scopes : tuple
            The scopes for which the token is requested. Will be ignored in
            this implementation.
        kwargs : dict
            Additional keyword arguments. Will be ignored in this
            implementation.

        Returns
        -------
        AccessToken
            The access token that was used to initialize this instance.
        """
        return self._token_credential.get_token(*scopes, **kwargs)
