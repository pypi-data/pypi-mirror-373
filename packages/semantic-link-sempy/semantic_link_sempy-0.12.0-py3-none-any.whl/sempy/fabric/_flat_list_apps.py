import pandas as pd
from typing import Optional, TYPE_CHECKING

from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric._credentials import with_credential

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


@with_credential
def list_apps(credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    List all the Power BI apps.

    Parameters
    ----------
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    =======
    pandas.DataFrame
        DataFrame with one row per app.
    """
    df = _PBIRestAPI().list_apps()

    df = rename_and_validate_from_records(df, [
                            ("id",          "App Id",       "str"),
                            ("name",        "App Name",     "str"),
                            ("lastUpdate",  "Last Update",  "datetime64[ns]"),
                            ("description", "Description",  "str"),
                            ("publishedBy", "Published By", "str"),
                            ("workspaceId", "Workspace Id", "str")])

    return df
