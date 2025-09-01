import pandas as pd
from typing import Optional, TYPE_CHECKING

from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric._credentials import with_credential

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


@with_credential
def list_gateways(credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    List all the Power BI gateways.

    Parameters
    ----------
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    =======
    pandas.DataFrame
        DataFrame with one row per gateway.
    """
    df = _PBIRestAPI().list_gateways()
    df = rename_and_validate_from_records(df, [
                            ("id",   "Gateway Id",    "str"),
                            ("name", "Gateway Name",  "str"),
                            ("type", "Gateway Type",  "str")])

    return df
