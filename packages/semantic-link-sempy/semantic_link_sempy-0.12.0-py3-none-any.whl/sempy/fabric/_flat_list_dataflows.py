from typing import Any, Dict, List, Literal, Optional, Tuple, Union, TYPE_CHECKING
from uuid import UUID

import pandas as pd

from sempy._utils._log import log
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy.fabric._credentials import with_credential

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


@log
@with_credential
def list_dataflows(workspace: Optional[Union[str, UUID]] = None,
                   endpoint: Literal["powerbi", "fabric"] = "powerbi",
                   credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    List all the Fabric dataflows.

    Please see `Dataflows - Get Dataflows <https://learn.microsoft.com/en-us/rest/api/fabric/core/dataflows/list-dataflows>`_
    for more details.

    Parameters
    ----------
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    endpoint : Literal["powerbi", "fabric"], default="powerbi"
        The endpoint to use for listing dataflows. Supported values are "powerbi" and "fabric".
        See `PowerBI List Dataflows <https://learn.microsoft.com/en-us/rest/api/power-bi/dataflows/get-dataflows>`__ for using "powerbi"
        and `Fabric List Dataflows <https://learn.microsoft.com/en-us/rest/api/fabric/dataflow/items/list-dataflows>`__ for using "fabric".
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per data flow.
    """
    payload: List[Dict[str, Any]]
    transform: List[Tuple[str, str, str]]
    workspace_client = _get_or_create_workspace_client(workspace)

    if endpoint == "powerbi":
        payload = workspace_client._pbi_rest_api.list_dataflows(
            workspace_client.get_workspace_name(),
            workspace_client.get_workspace_id())
        transform = [
            ("objectId",     "Dataflow Id",   "str"),
            ("name",         "Dataflow Name", "str"),
            ("description",  "Description",   "str"),
            ("configuredBy", "Configured By", "str?")
        ]
    elif endpoint == "fabric":
        payload = workspace_client._fabric_rest_api.list_dataflows(workspace_client.get_workspace_id())
        transform = [
            ("id",           "Dataflow Id",        "str"),
            ("displayName",  "Dataflow Name",      "str"),
            ("description",  "Description",        "str"),
            ("folderId",     "Dataflow Folder Id", "str?")
        ]
    else:
        raise ValueError(f"Unsupported endpoint: {endpoint}. Supported endpoints are \"powerbi\" and \"fabric\".")

    df = rename_and_validate_from_records(payload, transform, replace_na=True)
    return df


@log
@with_credential
def list_dataflow_storage_accounts(credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    List a list of dataflow storage accounts that the user has access to.

    Please see `Dataflow Storage Accounts - Get Dataflow Storage Accounts <https://learn.microsoft.com/en-us/rest/api/power-bi/dataflow-storage-accounts/get-dataflow-storage-accounts>`_
    for more details.

    Parameters
    ----------
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per dataflow storage account.
    """
    client = _PBIRestAPI()
    payload = client.list_dataflow_storage_accounts()
    df = rename_and_validate_from_records(payload, [
        ("id",        "Dataflow Storage Account Id",   "str"),
        ("name",      "Dataflow Storage Account Name", "str"),
        ("isEnabled", "Is Enabled",                    "bool")])

    return df
