from abc import ABC, abstractmethod
from typing import Literal
import warnings


class TokenProvider(ABC):
    """
    Abstract base class for logic that acquires auth tokens.

    .. deprecated::
        TokenProvider and its subclasses are deprecated and will be removed in a future version.
        Please migrate to `azure.core.credentials.TokenCredential` implementations
        such as `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`
        instead.
    """
    def __init__(self):
        warnings.warn(
            "TokenProvider and its subclasses are deprecated and will be removed in a future version. "
            "Please migrate to `azure.core.credentials.TokenCredential` implementations "
            "such as `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials` "
            "instead.",
            FutureWarning,
            stacklevel=2
        )

    @abstractmethod
    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi") -> str:
        """
        Get implementation specific token.

        Returns
        -------
        str
            Auth token.
        """
        raise NotImplementedError


class ConstantTokenProvider(TokenProvider):
    """
    Wrapper around a token that was externally acquired by the user.

    .. deprecated::
        ConstantTokenProvider is deprecated and will be removed in a future version.
        Please migrate to `azure.core.credentials.TokenCredential` implementations
        such as `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`
        instead.
    """
    def __init__(self, pbi_token, storage_token=None, sql_token=None):
        super().__init__()
        self.token_dict = {
            "pbi": pbi_token,
            "storage": storage_token,
            "sql": sql_token
        }

    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi"):
        """
        Get token.

        Returns
        -------
        str
            Fixed token provided by user during instantiation.
        """
        return self.token_dict.get(audience)


class SynapseTokenProvider(TokenProvider):
    """
    Acquire an auth token from within a Trident workspace.

    .. deprecated::
        SynapseTokenProvider is deprecated and will be removed in a future version.
        Please migrate to `azure.core.credentials.TokenCredential` implementations
        such as `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`
        instead.

    Examples
    --------
    >>> # Deprecated usage - do not use in new code
    >>> provider = SynapseTokenProvider()
    >>> token = provider(audience="pbi")

    >>> # Recommended alternative
    >>> from fabric.analytics.environment.credentials import FabricAnalyticsTokenCredentials
    >>> credentials = FabricAnalyticsTokenCredentials()
    >>> # Use shorthand scope
    >>> token = credentials.get_token("pbi")
    >>> # Use full scope URI
    >>> token = credentials.get_token("https://analysis.windows.net/powerbi/api/.default")
    """
    def __init__(self):
        super().__init__()

    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi"):
        """
        Get token from within a Trident workspace.

        Returns
        -------
        str
            Token acquired from Trident libraries.
        """
        return _get_token(audience=audience)


def _get_token(audience: Literal["pbi", "storage", "sql"]) -> str:
    """
    Get token of the specified audience from Fabric token library.

    Some old VHDs on Fabric may not have the latest `token_utils`, so we add
    a fallback try-catch to switch to the legacy method.

    We should remove getting from `PyTridentTokenLibrary` in the future.
    """
    if audience not in ("pbi", "storage", "sql"):
        raise ValueError(f"Invalid token audience: {audience}")
    try:
        # This is to patch token_utils to support sql token, which is not necessary in newer versions of token_utils.
        from synapse.ml.fabric.token_utils import TokenServiceClient
        TokenServiceClient.resource_mapping['sql'] = 'sql'

        from synapse.ml.fabric.token_utils import TokenUtils
        token_utils = TokenUtils()
        match audience:
            case "storage":
                return token_utils.get_storage_token()
            case "sql":
                return token_utils.get_access_token("sql")
            case "pbi":
                if hasattr(token_utils, "get_ml_aad_token"):
                    return token_utils.get_ml_aad_token()
                else:
                    return token_utils.get_aad_token()
    except ImportError:
        try:
            from trident_token_library_wrapper import PyTridentTokenLibrary
            return PyTridentTokenLibrary.get_access_token(audience)
        except ImportError:
            raise RuntimeError("No token_provider specified and unable to obtain token from the environment")
