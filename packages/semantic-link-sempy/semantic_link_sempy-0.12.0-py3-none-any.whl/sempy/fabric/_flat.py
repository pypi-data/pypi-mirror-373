import json
import graphviz
import pandas as pd
import datetime
import os
import warnings
from uuid import UUID

from sempy.fabric._credentials import with_credential
from sempy.fabric._dataframe._fabric_dataframe import FabricDataFrame
from sempy.fabric._client import DatasetXmlaClient, DatasetRestClient
from sempy.fabric._client._connection_mode import parse_connection_mode, ConnectionMode
from sempy.fabric._client._fabric_rest_api import _FabricRestAPI
from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy.fabric._client._refresh_execution_details import RefreshExecutionDetails
from sempy.fabric._client._utils import _create_tom_server
from sempy.fabric._cache import _get_or_create_workspace_client, _get_fabric_rest_api
from sempy.fabric._environment import _get_workspace_url, _on_jupyter, get_workspace_id
from sempy.fabric._client._utils import _build_adomd_connection_string
from sempy.fabric._trace._trace_connection import TraceConnection
from sempy.fabric._trace._trace import Trace
from sempy.fabric._utils import _get_relationships, dotnet_to_pandas_date, collection_to_dataframe, is_valid_uuid
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.relationships import plot_relationship_metadata
from sempy.relationships._utils import _to_dataframe_dict
from sempy.relationships._validate import _list_relationship_violations
from sempy._utils._log import log, log_error, log_tables
from typing import Any, cast, Dict, List, Optional, Union, Tuple, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


@log
@with_credential
def execute_tmsl(script: Union[Dict, str], refresh_tom_cache: bool = True,
                 workspace: Optional[Union[str, UUID]] = None,
                 credential: Optional["TokenCredential"] = None):
    """
    Execute TMSL script.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. If your TMSL script is specific to a semantic model, you must have at least **ReadWrite** permissions on it to proceed.

    Parameters
    ----------
    script : Dict or str
        The TMSL script json.
    refresh_tom_cache : bool, default=True
        Whether or not to refresh the dataset after executing the TMSL script.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    if isinstance(script, Dict):
        script = json.dumps(script)

    workspace_client = _get_or_create_workspace_client(workspace)
    workspace_client.execute_tmsl(script)

    if refresh_tom_cache:
        workspace_client.refresh_tom_cache()


@log
@with_credential
def refresh_tom_cache(workspace: Optional[Union[str, UUID]] = None,
                      credential: Optional["TokenCredential"] = None):
    """
    Refresh TOM cache in the notebook kernel.

    Parameters
    ----------
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    _get_or_create_workspace_client(workspace).refresh_tom_cache()


@log
@with_credential
def get_roles(
    dataset: Union[str, UUID],
    include_members: bool = False,
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    Retrieve all roles associated with the dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    include_members : bool, default=False
        Whether or not to include members for each role.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `role <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.role?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing roles and with their attributes.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    model = workspace_client.get_dataset(dataset).Model

    extraction_def = [
        ("Role",                  lambda r: r[0].Name,                                "str"),   # noqa: E272
        ("Description",           lambda r: r[0].Description,                         "str"),   # noqa: E272
        ("Model Permission",      lambda r: r[0].ModelPermission.ToString(),          "str"),   # noqa: E272
        ("Modified Time",         lambda r: dotnet_to_pandas_date(r[0].ModifiedTime), "datetime64[ns]"),  # noqa: E272
    ]

    if include_members:
        extraction_def.append(("Member",            lambda r: r[1].MemberName,       "str"))   # noqa: E272
        extraction_def.append(("Identity Provider", lambda r: r[1].IdentityProvider, "str"))   # noqa: E272

        collection = [(r, m) for r in model.Roles for m in r.Members]
    else:
        collection = [(r, None) for r in model.Roles]

    return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)


@log
@with_credential
def get_row_level_security_permissions(
    dataset: Union[str, UUID],
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    Retrieve row level security permissions for a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `tablepermission <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.tablepermission?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing tables and row filter expressions (DAX) for the dataset.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    model = workspace_client.get_dataset(dataset).Model

    # (role, table_permission)
    extraction_def = [
        ("Role",              lambda r: r[0].Name,             "str"),   # noqa: E272
        ("Table",             lambda r: r[1].Name,             "str"),   # noqa: E272
        ("Filter Expression", lambda r: r[1].FilterExpression, "str"),   # noqa: E272
    ]

    collection = [
        (role, table_permission)
        for role in model.Roles
        for table_permission in role.TablePermissions
    ]

    return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)


@log
@with_credential
def list_datasets(workspace: Optional[Union[str, UUID]] = None, mode: str = "xmla",

                  additional_xmla_properties: Optional[Union[str, List[str]]] = None,
                  endpoint: Literal["powerbi", "fabric"] = "powerbi",
                  credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    List datasets in a `Fabric workspace <https://learn.microsoft.com/en-us/fabric/get-started/workspaces>`_.

    ⚠️ By default (`mode="xmla"`), this function leverages the
    `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. To use this function in `xmla` mode, you must have at least **ReadWrite** permissions on the model.
    Alternatively, you can use `mode="rest"`.

    Parameters
    ----------
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    mode : str, default="xmla"
        Whether to use the XMLA "xmla" or REST API "rest".
        See `REST docs <https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasets>`_ for returned fields.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `model <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.model?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    endpoint : Literal["powerbi", "fabric"], default="powerbi"
        The endpoint to use when mode="rest". Supported values are "powerbi" and "fabric".
        When mode="xmla", this parameter is ignored.
        See `PowerBI List Datasets <https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-datasets>`__ for using "powerbi"
        and `Fabric List Datasets <https://learn.microsoft.com/en-us/rest/api/fabric/semanticmodel/items/list-semantic-models>`__ for using "fabric".
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing databases and their attributes.
    """
    return _get_or_create_workspace_client(workspace).get_datasets(mode, additional_xmla_properties, endpoint=endpoint)


@log
@with_credential
def list_measures(
    dataset: Union[str, UUID],
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    Retrieve all measures associated with the given dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `measure <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.measure?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing measures and their attributes.
    """
    return _get_or_create_workspace_client(workspace).list_measures(dataset, additional_xmla_properties)


@log
@with_credential
def refresh_dataset(
    dataset: Union[str, UUID],
    workspace: Optional[Union[str, UUID]] = None,
    refresh_type: str = "automatic",
    max_parallelism: int = 10,
    commit_mode: str = "transactional",
    retry_count: int = 0,
    objects: Optional[List] = None,
    apply_refresh_policy: bool = True,
    effective_date: datetime.date = datetime.date.today(),
    verbose: int = 0,
    credential: Optional["TokenCredential"] = None
) -> str:
    """
    Refresh data associated with the given dataset.

    For detailed documentation on the implementation see
    `Enhanced refresh with the Power BI REST API <https://learn.microsoft.com/en-us/power-bi/connect-data/asynchronous-refresh>`_.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    refresh_type : str, default="automatic"
        The type of processing to perform. Types align with the TMSL refresh command types: full,
        clearValues, calculate, dataOnly, automatic, and defragment. The add type isn't supported.
        Defaults to "automatic".
    max_parallelism : int, default=10
        Determines the maximum number of threads that can run the processing commands in parallel.
        This value aligns with the MaxParallelism property that can be set in the TMSL Sequence
        command or by using other methods. Defaults to 10.
    commit_mode : str, default="transactional"
        Determines whether to commit objects in batches or only when complete.
        Modes are "transactional" and "partialBatch". Defaults to "transactional".
    retry_count : int, default=0
        Number of times the operation retries before failing. Defaults to 0.
    objects : List, default=None
        A list of objects to process. Each object includes table when processing an entire table,
        or table and partition when processing a partition. If no objects are specified,
        the entire dataset refreshes. Pass output of json.dumps of a structure that specifies the
        objects that you want to refresh. For example, this is to refresh "DimCustomer1" partition
        of table "DimCustomer" and complete table "DimDate"::

            [
                {
                    "table": "DimCustomer",
                    "partition": "DimCustomer1"
                },
                {
                    "table": "DimDate"
                }
            ]

    apply_refresh_policy : bool, default=True
        If an incremental refresh policy is defined, determines whether to apply the policy.
        Modes are true or false. If the policy isn't applied, the full process leaves partition
        definitions unchanged, and fully refreshes all partitions in the table. If commitMode is
        transactional, applyRefreshPolicy can be true or false. If commitMode is partialBatch,
        applyRefreshPolicy of true isn't supported, and applyRefreshPolicy must be set to false.
    effective_date : datetime.date, default=datetime.date.today()
        If an incremental refresh policy is applied, the effectiveDate parameter overrides the current date.
    verbose : int, default=0
        If set to non-zero, extensive log output is printed.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The refresh request id.
    """
    client: DatasetRestClient = _get_or_create_workspace_client(workspace).get_dataset_client(dataset)  # type: ignore
    poll_url = client.refresh_async(refresh_type, max_parallelism, commit_mode, retry_count, objects,
                                    apply_refresh_policy, effective_date, verbose)

    # extract the refresh request id from the poll url
    return poll_url.split("/")[-1]


@log
@with_credential
def list_refresh_requests(
        dataset: Union[str, UUID],
        workspace: Optional[Union[str, UUID]] = None,
        top_n: Optional[int] = None,
        credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    Poll the status or refresh requests for a given dataset using Enhanced refresh with the Power BI REST API.

    See details in: `PBI Documentation <https://learn.microsoft.com/en-us/power-bi/connect-data/asynchronous-refresh>`_

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    top_n : int, default = None
        Limit the number of refresh operations returned.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame:
        Dataframe with statuses of refresh request retrieved based on the passed parameters.
    """
    client: DatasetRestClient = _get_or_create_workspace_client(workspace).get_dataset_client(dataset)  # type: ignore
    return client.list_refresh_history(top_n=top_n)


@log_error
@with_credential
def get_refresh_execution_details(
        dataset: Union[str, UUID],
        refresh_request_id: Union[str, UUID],
        workspace: Optional[Union[str, UUID]] = None,
        credential: Optional["TokenCredential"] = None
) -> RefreshExecutionDetails:
    """
    Poll the status for a specific refresh requests using Enhanced refresh with the Power BI REST API.

    More details on the underlying implementation in `PBI Documentation <https://learn.microsoft.com/en-us/power-bi/connect-data/asynchronous-refresh>`_

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    refresh_request_id : str or uuid.UUID
        Id of refresh request on which to check the status.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    RefreshExecutionDetails:
        RefreshExecutionDetails instance with statuses of refresh request retrieved based on the passed URL.
    """
    client: DatasetRestClient = _get_or_create_workspace_client(workspace).get_dataset_client(dataset)  # type: ignore
    return client.get_refresh_execution_details(refresh_request_id)


@log
@with_credential
def read_table(
    dataset: Union[str, UUID],
    table: str,
    fully_qualified_columns: bool = False,
    num_rows: Optional[int] = None,
    multiindex_hierarchies: bool = False,
    mode: Literal["xmla", "rest", "onelake"] = "xmla",
    onelake_import_method: Optional[Literal["spark", "pandas"]] = None,
    workspace: Optional[Union[str, UUID]] = None,
    verbose: int = 0,
    credential: Optional["TokenCredential"] = None
) -> FabricDataFrame:
    """
    Read a PowerBI table into a FabricDataFrame.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    table : str
        Name of the table to read.
    fully_qualified_columns : bool, default=False
        Whether or not to represent columns in their fully qualified form (TableName[ColumnName]).
    num_rows : int, default=None
        How many rows of the table to return. If None, all rows are returned.
    multiindex_hierarchies : bool, default=False
        Whether or not to convert existing `PowerBI Hierarchies <https://learn.microsoft.com/en-us/power-bi/create-reports/service-metrics-get-started-hierarchies>`_
        to pandas MultiIndex.
    mode : {"xmla", "rest", "onelake"}
        Whether to use the XMLA "xmla", REST API "rest", export of import datasets to Onelake "onelake" to retrieve the data.
    onelake_import_method : {"spark", "pandas"}, default=None
        The method to read from the onelake. Only be effective when the mode is "onelake". Use "spark" to read the table with spark API,
        "deltalake" with the deltalake API, or None with the proper method auto-selected based on the current runtime.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    verbose : int, default=0
        Verbosity. 0 means no verbosity.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    FabricDataFrame
        Dataframe for the given table name with metadata from the PowerBI model.
    """  # noqa E501

    conn_mode = parse_connection_mode(mode)

    dataset_client = _get_or_create_workspace_client(workspace) \
        .get_dataset_client(dataset, mode=conn_mode)

    if conn_mode == ConnectionMode.ONELAKE_IMPORT_DATASET:
        from sempy.fabric._client._dataset_onelake_import import DatasetOneLakeImportClient
        if onelake_import_method is None:
            onelake_import_method = "pandas" if _on_jupyter() else "spark"
        if isinstance(dataset_client, DatasetOneLakeImportClient):
            dataset_client._set_import_method(onelake_import_method)

    return dataset_client.read_table(table, fully_qualified_columns, num_rows,
                                     multiindex_hierarchies, verbose=verbose)


@log
@with_credential
def get_tmsl(dataset: Union[str, UUID], workspace: Optional[Union[str, UUID]] = None,
             credential: Optional["TokenCredential"] = None) -> str:
    """
    Retrieve the Tabular Model Scripting Language (`TMSL <https://learn.microsoft.com/en-us/analysis-services/tmsl/tabular-model-scripting-language-tmsl-reference?view=asallproducts-allversions>`_) for a given dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        `TMSL <https://learn.microsoft.com/en-us/analysis-services/tmsl/tabular-model-scripting-language-tmsl-reference?view=asallproducts-allversions>`_ for the given dataset.
    """ # noqa E501
    workspace_client = _get_or_create_workspace_client(workspace)
    return workspace_client.get_tmsl(dataset)


@log
@with_credential
def list_tables(
    dataset: Union[str, UUID],
    include_columns: bool = False,
    include_partitions: bool = False,
    extended: bool = False,
    advanced: bool = False,
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None,
    include_internal: bool = False,
    credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    List all tables in a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    include_columns : bool, default=False
        Whether or not to include column level information.
        Cannot be combined with include_partitions, extended, or advanced.
    include_partitions : bool, default=False
        Whether or not to include partition level information.
        Cannot be combined with include_columns, extended, or advanced.
    extended : bool, default False
        Fetches extended table information information.
        Cannot be combined with include_columns, include_partitions, or advanced.
    advanced : bool, default False
        Fetches advanced table information information including Vertipaq statistics.
        Cannot be combined with include_columns, include_partitions, or extended.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `table <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.table?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    include_internal : bool, default=False
        Whether or not to include internal tables.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing the tables and optional columns.
    """
    if sum([include_columns, include_partitions, extended, advanced]) > 1:
        raise ValueError("include_columns, include_partitions, extended, and advanced are mutually exclusive")

    workspace_client = _get_or_create_workspace_client(workspace)
    tabular_database = workspace_client.get_dataset(dataset)

    # must happen after workspace client is retrieved so .NET is loaded
    import Microsoft.AnalysisServices.Tabular as TOM  # type: ignore

    def table_type(t):
        if t.CalculationGroup is not None:
            return "Calculation Group"
        elif any(p.SourceType == TOM.PartitionSourceType.Calculated for p in t.Partitions):
            return "Calculated Table"
        else:
            return "Table"

    extraction_def = [
        ("Name",          lambda t: t.Name,         "str"),   # noqa: E272
        ("Description",   lambda t: t.Description,  "str"),   # noqa: E272
        ("Hidden",        lambda t: t.IsHidden,     "bool"),  # noqa: E272
        ("Data Category", lambda t: t.DataCategory, "str"),   # noqa: E272
        ("Type",          table_type,               "str"),   # noqa: E272
    ]

    if include_partitions:
        warnings.warn(DeprecationWarning("This option will be removed in a future release. Please use list_partitions instead."))
        extraction_def.extend([
            ("Partition Name",           lambda t: [p.Name for p in t.Partitions],    "object"),  # noqa: E272
            ("Partition Refreshed Time", lambda t: [
                    dotnet_to_pandas_date(p.RefreshedTime)
                    for p in t.Partitions
                ],                                                                    "datetime64[ns]"),
        ])

    if include_columns:
        warnings.warn(DeprecationWarning("This option will be removed in a future release. Please use list_columns instead."))
        extraction_def.extend([
            ("Column", lambda t: [c.Name for c in t.Columns if not c.Name.startswith("RowNumber")], "object")
        ])

    if advanced:
        def fetch_extended_stats():
            dict_df = evaluate_dax(
                dataset=dataset,
                workspace=workspace,
                dax_string="""
                EVALUATE SELECTCOLUMNS(
                    FILTER(INFO.STORAGETABLECOLUMNS(), [COLUMN_TYPE] = "BASIC_DATA"),
                    [DIMENSION_NAME],
                    [DICTIONARY_SIZE]
                )
                """
            )
            dict_sum = dict_df.groupby("[DIMENSION_NAME]")["[DICTIONARY_SIZE]"].sum()

            data = evaluate_dax(
                dataset=dataset,
                workspace=workspace,
                dax_string="""
                EVALUATE SELECTCOLUMNS(
                    INFO.STORAGETABLECOLUMNSEGMENTS(),
                    [TABLE_ID],
                    [DIMENSION_NAME],
                    [USED_SIZE]
                )
                """
            )
            data_sum = data[~data["[TABLE_ID]"].str.startswith(("R$", "U$", "H$"))].groupby("[DIMENSION_NAME]")["[USED_SIZE]"].sum()
            hier_sum = data[data["[TABLE_ID]"].str.startswith("H$")].groupby("[DIMENSION_NAME]")["[USED_SIZE]"].sum()
            rel_sum = data[data["[TABLE_ID]"].str.startswith("R$")].groupby("[DIMENSION_NAME]")["[USED_SIZE]"].sum()
            uh_sum = data[data["[TABLE_ID]"].str.startswith("U$")].groupby("[DIMENSION_NAME]")["[USED_SIZE]"].sum()

            rc = evaluate_dax(
                dataset=dataset,
                workspace=workspace,
                dax_string="""
                SELECT [DIMENSION_NAME], [ROWS_COUNT] FROM $SYSTEM.DISCOVER_STORAGE_TABLES
                WHERE RIGHT(LEFT(TABLE_ID, 2), 1) <> '$'
                """
            )

            model_size = (
                dict_sum.sum() + data_sum.sum() + hier_sum.sum() + rel_sum.sum() + uh_sum.sum()
            )

            return dict_sum, data_sum, hier_sum, rel_sum, uh_sum, rc, model_size

        dict_sum, data_sum, hier_sum, rel_sum, uh_sum, rc, model_size = fetch_extended_stats()
        extraction_def.extend([
            ("Refresh Policy",      lambda t: t.RefreshPolicy is not None,                                      "bool"),    # noqa: E272
            ("Source Expression",   lambda t: t.RefreshPolicy.SourceExpression if t.RefreshPolicy else None,    "str"),     # noqa: E272
            ("Row Count",           lambda t: (                                                                             # noqa: E272
                    rc.loc[rc["DIMENSION_NAME"] == t.Name, "ROWS_COUNT"].iloc[0] if not rc.empty else 0                     # noqa: E272
                ),                                                                                              "int"),     # noqa: E272
            ("Total Size",          lambda t: (                                                                             # noqa: E272
                    dict_sum.get(t.Name, 0) + data_sum.get(t.Name, 0) + hier_sum.get(t.Name, 0) +                           # noqa: E272
                    rel_sum.get(t.Name, 0) + uh_sum.get(t.Name, 0)                                                          # noqa: E272
                ),                                                                                              "int"),     # noqa: E272
            ("Dictionary Size",     lambda t: dict_sum.get(t.Name, 0),                                          "int"),     # noqa: E272
            ("Data Size",           lambda t: data_sum.get(t.Name, 0),                                          "int"),     # noqa: E272
            ("Hierarchy Size",      lambda t: hier_sum.get(t.Name, 0),                                          "int"),     # noqa: E272
            ("Relationship Size",   lambda t: rel_sum.get(t.Name, 0),                                           "int"),     # noqa: E272
            ("User Hierarchy Size", lambda t: uh_sum.get(t.Name, 0),                                            "int"),     # noqa: E272
            ("Partitions",          lambda t: len(t.Partitions),                                                "int"),     # noqa: E272
            ("Columns",             lambda t: (                                                                             # noqa: E272
                    sum(1 for c in t.Columns if str(c.Type) != "RowNumber")                                                 # noqa: E272
                ),                                                                                              "int"),     # noqa: E272
            ("% DB",                lambda t: (                                                                             # noqa: E272
                    round((dict_sum.get(t.Name, 0) + data_sum.get(t.Name, 0) + hier_sum.get(t.Name, 0) +                    # noqa: E272
                           rel_sum.get(t.Name, 0) + uh_sum.get(t.Name, 0)) / model_size * 100, 2)                           # noqa: E272
                ),                                                                                              "float"),   # noqa: E272
        ])

    collection = [
        t
        for t in tabular_database.Model.Tables
        if include_internal or not workspace_client._is_internal(t)
    ]

    df = collection_to_dataframe(collection, extraction_def, additional_xmla_properties)

    if include_columns:
        df = df.explode("Column")
    elif include_partitions:
        df = df.explode(["Partition Name", "Partition Refreshed Time"])
    elif extended:
        # Need to use something unique (e.g. SemPyInternalTableName) to avoid throwing a warning
        # as e.g. Name might overlap w/ other tables when resolving metadata
        df_ext = evaluate_dax(dataset,
                              """
                              SELECT DISTINCT
                                  [DIMENSION_NAME] AS [SemPyInternalTableName],
                                  [ROWS_COUNT]     AS [SemPyTableRowCount]
                              FROM
                                  $SYSTEM.DISCOVER_STORAGE_TABLES
                              WHERE
                                  RIGHT ( LEFT ( TABLE_ID, 2 ), 1 ) <> '$'
                              """,
                              workspace=workspace)

        df = (df.merge(df_ext, how="left", left_on="Name", right_on="SemPyInternalTableName")
                .drop("SemPyInternalTableName", axis="columns")
                .rename({"SemPyTableRowCount": "Row Count"}, axis="columns"))

        # rename columns (strip SemPy prefix)
        df = df.rename({"SemPyTableName": "Name", "SemPyTableRowCount": "Row Count"}, axis="columns")

    return df


@log
@with_credential
def list_translations(
    dataset: Union[str, UUID],
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    List all translations in a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `tramslation <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.translation?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing the translations.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset)

    # must happen after workspace client is retrieved so .NET is loaded
    import Microsoft.AnalysisServices.Tabular as TOM  # type: ignore

    # https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.culture?view=analysisservices-dotnet
    # (culture, object_translation)
    def table_name(r):
        if r[1].Object.ObjectType == TOM.ObjectType.Table:
            return r[1].Object.Name
        elif r[1].Object.ObjectType == TOM.ObjectType.Level:
            return r[1].Object.Parent.Parent.Name
        else:
            return r[1].Object.Table.Name

    def object_name(r):
        if r[1].Object.ObjectType == TOM.ObjectType.Level:
            hierarchy_name = r[1].Object.Parent.Name
            table_name = r[1].Object.Parent.Parent.Name
            return f"'{hierarchy_name}'[{table_name}]"
        else:
            return r[1].Object.Name

    extraction_def = [
        ("Culture Name",  lambda r: r[0].Name,                                "str"),             # noqa: E272
        ("Table Name",    table_name,                                         "str"),             # noqa: E272
        ("Object Name",   object_name,                                        "str"),             # noqa: E272
        ("Object Type",   lambda r: r[1].Object.ObjectType.ToString(),        "str"),             # noqa: E272
        ("Translation",   lambda r: r[1].Value,                               "str"),             # noqa: E272
        ("Property",      lambda r: r[1].Property.ToString(),                 "str"),             # noqa: E272
        ("Modified Time", lambda r: dotnet_to_pandas_date(r[1].ModifiedTime), "datetime64[ns]"),  # noqa: E272
    ]

    collection = [
        (culture, object_translation)
        for culture in database.Model.Cultures
        for object_translation in culture.ObjectTranslations
    ]

    return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)


@log
@with_credential
def list_expressions(
    dataset: Union[str, UUID],
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    List all expressions in a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `expression <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.namedexpression?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing the expressions.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset)

    # see https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.namedexpressioncollection?view=analysisservices-dotnet
    extraction_def = [
        ("Name",          lambda r: r.Name,                                "str"),   # noqa: E272
        ("Description",   lambda r: r.Description,                         "str"),   # noqa: E272
        ("Expression",    lambda r: r.Expression,                          "str"),   # noqa: E272
        ("Kind",          lambda r: r.Kind.ToString(),                     "str"),   # noqa: E272
        ("M Attributes",  lambda r: r.MAttributes,                         "str"),   # noqa: E272
        ("Modified Time", lambda r: dotnet_to_pandas_date(r.ModifiedTime), "datetime64[ns]"),  # noqa: E272
    ]

    return collection_to_dataframe(database.Model.Expressions, extraction_def, additional_xmla_properties)


@log
@with_credential
def evaluate_measure(
    dataset: Union[str, UUID],
    measure: Union[str, List[str]],
    groupby_columns: Optional[List[str]] = None,
    filters: Optional[Dict[str, List[str]]] = None,
    fully_qualified_columns: Optional[bool] = None,
    num_rows: Optional[int] = None,
    use_xmla: bool = False,
    workspace: Optional[Union[str, UUID]] = None,
    verbose: int = 0,
    use_readwrite_connection: bool = False,
    credential: Optional["TokenCredential"] = None
) -> FabricDataFrame:
    """
    Compute `PowerBI measure <https://learn.microsoft.com/en-us/power-bi/transform-model/desktop-measures>`_ for a given dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    measure : str or list of str
        Name of the measure, or list of measures to compute.
    groupby_columns : list, default=None
        List of columns in a fully qualified form e.g. "TableName[ColumnName]" or "'Table Name'[Column Name]".
    filters : dict, default=None
        Dictionary containing a list of column values to filter the output by, where
        the key is a column reference, which must be fully qualified with the table name.
        Currently only supports the "in" filter. For example, to specify that in the "State" table
        the "Region" column can only be "East" or "Central" and that the "State" column
        can only be "WA" or "CA"::

            {
                "State[Region]":    ["East", "Central"],
                "State[State]":     ["WA", "CA"]
            }

    fully_qualified_columns : bool, default=None
        Whether to output columns in their fully qualified form (TableName[ColumnName] for dimensions).
        Measures are always represented without the table name.
        If None, the fully qualified form will only be used if there is a name conflict between columns from different tables.
    num_rows : int, default=None
        How many rows of the table to return. If None, all rows are returned.
    use_xmla : bool, default=False
        Whether or not to use `XMLA <https://learn.microsoft.com/en-us/analysis-services/xmla/xml-for-analysis-xmla-reference?view=asallproducts-allversions>`_
        as the backend for evaluation. When False, REST backend will be used.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    verbose : int, default=0
        Verbosity. 0 means no verbosity.
    use_readwrite_connection : bool, default=False
        Whether to connect to the readwrite version of a semantic model with query scale out enabled.
        This parameter only applies when using XMLA backend and will force the use of XMLA if set to True.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    FabricDataFrame
        :class:`~sempy.fabric.FabricDataFrame` holding the computed measure stratified by groupby columns.
    """  # noqa E501
    # The REST API does not allow for pagination when using the "top" feature. Since the maximum page size is
    # 30,000 rows, we prevent the user from triggering pagination with num_rows set.
    # Also, if use_readwrite_connection is True, we must use XMLA mode.
    if use_xmla:
        mode = ConnectionMode.XMLA
    else:
        if use_readwrite_connection:
            if verbose > 0:
                print("Using readwrite connection, switching to XMLA backend.")
            mode = ConnectionMode.XMLA
        elif num_rows and num_rows > 30000:
            if verbose > 0:
                print(f"Provided num_rows ({num_rows}) is greater than 30,000. Switching to XMLA backend.")
            mode = ConnectionMode.XMLA
        else:
            mode = ConnectionMode.REST

    return _get_or_create_workspace_client(workspace) \
        .get_dataset_client(dataset, mode=mode, use_readwrite_connection=use_readwrite_connection) \
        .evaluate_measure(measure, groupby_columns, filters, fully_qualified_columns, num_rows, verbose)     # type: ignore


@log
@with_credential
def evaluate_dax(
    dataset: Union[str, UUID],
    dax_string: str,
    workspace: Optional[Union[str, UUID]] = None,
    verbose: int = 0,
    num_rows: Optional[int] = None,
    role: Optional[str] = None,
    effective_user_name: Optional[str] = None,
    use_readwrite_connection: bool = False,
    credential: Optional["TokenCredential"] = None
) -> FabricDataFrame:
    """
    Compute `DAX <https://learn.microsoft.com/en-us/dax/>`_ query for a given dataset.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    dax_string : str
        The DAX query.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    verbose : int, default=0
        Verbosity. 0 means no verbosity.
    num_rows : int, default=None
        Maximum number of rows to read from the result. None means read all rows.
    role : str, default=None
        The role to impersonate to run the DAX query. Cannot be used with effective_user_name.
    effective_user_name : str, default=None
        The effective user name to impersonate to run the DAX query. Cannot be used with role.
    use_readwrite_connection : bool, default=False
        Whether to connect to the readwrite version of a semantic model with query scale out enabled.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    FabricDataFrame
        :class:`~sempy.fabric.FabricDataFrame` holding the result of the DAX query.
    """
    # creating client directly to avoid any workspace access if not needed
    # a user can have access via XMLA to a dataset, but may not have access to the workspace
    return DatasetXmlaClient(workspace, dataset, role=role, effective_user_name=effective_user_name, use_readwrite_connection=use_readwrite_connection) \
        .evaluate_dax(dax_string, verbose, num_rows)


@log
@with_credential
def execute_xmla(
    dataset: Union[str, UUID],
    xmla_command: str,
    workspace: Optional[Union[str, UUID]] = None,
    use_readwrite_connection: bool = False,
    credential: Optional["TokenCredential"] = None
) -> int:
    """
    Execute XMLA command for a given dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    e.g. `clear cache <https://learn.microsoft.com/en-us/analysis-services/instances/clear-the-analysis-services-caches?view=asallproducts-allversions>`_
    when optimizing DAX queries.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    xmla_command : str
        The XMLA command.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    use_readwrite_connection : bool, default=False
        Whether to connect to the readwrite version of a semantic model with query scale out enabled.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    int
        Number of rows affected.
    """
    client: DatasetXmlaClient = _get_or_create_workspace_client(workspace) \
        .get_dataset_client(dataset, mode=ConnectionMode.XMLA, use_readwrite_connection=use_readwrite_connection)  # type: ignore
    return client._execute_xmla(xmla_command)


@log
@with_credential
def _trace_evaluate_dax(
    dataset: Union[str, UUID],
    dax_string: str,
    trace_event_schema: Optional[Dict[str, List[str]]] = None,
    clear_cache: bool = True,
    start_delay: int = 3,
    stop_timeout: int = 5,
    workspace: Optional[Union[str, UUID]] = None,
    verbose: int = 0,
    credential: Optional["TokenCredential"] = None
) -> Tuple[FabricDataFrame, pd.DataFrame]:
    """
    Compute `DAX <https://learn.microsoft.com/en-us/dax/>`_ query for a given dataset, with Tracing enabled.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset to list the measures for.
    dax_string : str
        The DAX query.
    trace_event_schema : dict, default=None
        Dictionary containing Trace event schema to use.
        If None, default events and columns will be used using :meth:`~sempy.fabric.Trace.get_default_query_trace_schema`.
        Note: Using event classes that do not specify SessionID as a column may result in recording events that are not related to this
        specific query execution.
    clear_cache : bool, default=True
        Whether or not to
        `clear the Analysis Services cache <https://learn.microsoft.com/en-us/analysis-services/instances/clear-the-analysis-services-caches?view=asallproducts-allversions>`_
        before runs to ensure consistent results.
    start_delay : int, delay=3
        Number of seconds to sleep for after starting the trace to allow engine to subscribe to added trace events.
    stop_timeout : int, default=5
        Number of seconds to wait for QueryEnd event to register.
        If QueryEnd is not reached in this time frame, the collected trace logs will still be returned but may be incomplete.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    verbose : int, default=0
        Verbosity. 0 means no verbosity.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    tuple of FabricDataFrame and pd.DataFrame
        Result of the DAX query as a :class:`~sempy.fabric.FabricDataFrame`, and the corresponding trace logs (without the SessionID column).
    """
    client = DatasetXmlaClient(workspace, dataset)

    if clear_cache:
        client._clear_analysis_services_cache()

    with TraceConnection(client) as trace_connection:
        event_schema = trace_event_schema if trace_event_schema else Trace.get_default_query_trace_schema()
        adomd_session_id = client.get_adomd_connection().get_or_create_connection().SessionID

        with trace_connection.create_trace(event_schema=event_schema, stop_event="QueryEnd") as trace:
            trace.set_filter(lambda e: e.SessionID == adomd_session_id if hasattr(e, "SessionID") else True)
            trace.start(delay=start_delay)
            result = client.evaluate_dax(dax_string, verbose)
            trace_logs = trace.stop(timeout=stop_timeout)

    trace_logs = trace_logs.drop("Session ID", axis=1)
    return result, trace_logs


@log_tables
def plot_relationships(
    tables: Union[Dict[str, FabricDataFrame], List[FabricDataFrame]],
    include_columns='keys',
    missing_key_errors='raise',
    *,
    graph_attributes: Optional[Dict] = None
) -> graphviz.Digraph:
    """
    Visualize relationship dataframe with a graph.

    Parameters
    ----------
    tables : dict[str, sempy.fabric.FabricDataFrame] or list[sempy.fabric.FabricDataFrame]
        A dictionary that maps table names to the dataframes with table content.
        If a list of dataframes is provided, the function will try to infer the names from the
        session variables and if it cannot, it will use the positional index to describe them in
        the results.
        It needs to provided only when `include_columns` = 'all' and it will be used
        for mapping table names from relationships to the dataframe columns.
    include_columns : str, default='keys'
        One of 'keys', 'all', 'none'. Indicates which columns should be included in the graph.
    missing_key_errors : str, default='raise'
        One of 'raise', 'warn', 'ignore'. Action to take when either table or column
        of the relationship is not found in the elements of the argument *tables*.
    graph_attributes : dict, default=None
        Attributes passed to graphviz. Note that all values need to be strings. Useful attributes are:

        - *rankdir*: "TB" (top-bottom) or "LR" (left-right)
        - *dpi*:  "100", "30", etc. (dots per inch)
        - *splines*: "ortho", "compound", "line", "curved", "spline" (line shape)

    Returns
    -------
    graphviz.Digraph
        Graph object containing all relationships.
        If include_attributes is true, attributes are represented as ports in the graph.
    """
    named_dataframes = _to_dataframe_dict(tables)  # type: ignore
    relationships = _get_relationships(named_dataframes)  # type: ignore
    return plot_relationship_metadata(
        relationships,
        tables,
        include_columns=include_columns,
        missing_key_errors=missing_key_errors,
        graph_attributes=graph_attributes)


@log_tables
def list_relationship_violations(
        tables: Union[Dict[str, FabricDataFrame], List[FabricDataFrame]],
        missing_key_errors='raise',
        coverage_threshold: float = 1.0,
        n_keys: int = 10
) -> pd.DataFrame:
    """
    Validate if the content of tables matches relationships.

    Relationships are extracted from the metadata in FabricDataFrames.
    The function examines results of joins for provided relationships and
    searches for inconsistencies with the specified relationship multiplicity.

    Relationships from empty tables (dataframes) are assumed as valid.

    Parameters
    ----------
    tables : dict[str, sempy.fabric.FabricDataFrame] or list[sempy.fabric.FabricDataFrame]
        A dictionary that maps table names to the dataframes with table content.
        If a list of dataframes is provided, the function will try to infer the names from the
        session variables and if it cannot, it will use the positional index to describe them in
        the results.
    missing_key_errors : str, default='raise'
        One of 'raise', 'warn', 'ignore'. Action to take when either table or column
        of the relationship is not found in the elements of the argument *tables*.
    coverage_threshold : float, default=1.0
        Fraction of rows in the "from" part that need to join in inner join.
    n_keys : int, default=10
        Number of missing keys to report. Random collection can be reported.

    Returns
    -------
    pandas.DataFrame
        Dataframe with relationships, error type and error message.
        If there are no violations, returns an empty DataFrame.
    """
    named_dataframes = _to_dataframe_dict(tables)  # type: ignore
    relationships = _get_relationships(named_dataframes)  # type: ignore
    return _list_relationship_violations(named_dataframes, relationships, missing_key_errors, coverage_threshold, n_keys)


@log
@with_credential
def resolve_workspace_id(workspace: Optional[Union[str, UUID]] = None,
                         credential: Optional["TokenCredential"] = None) -> str:
    """
    Resolve the workspace name or ID to the workspace UUID.

    Parameters
    ----------
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    uuid.UUID
        The workspace UUID.
    """
    return _get_or_create_workspace_client(workspace).get_workspace_id()


@log
@with_credential
def resolve_workspace_name(workspace: Optional[Union[str, UUID]] = None,
                           credential: Optional["TokenCredential"] = None) -> str:
    """
    Resolve the workspace name or ID to the workspace name.

    Parameters
    ----------
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The workspace name.
    """
    return _get_or_create_workspace_client(workspace).get_workspace_name()


@log
@with_credential
def resolve_workspace_name_and_id(
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> Tuple[str, str]:
    """
    Resolve the name and ID of the Fabric workspace.

    Parameters
    ----------
    workspace : str or UUID, default=None
        The Fabric workspace name or ID.
        If None, it resolves to the workspace of the attached lakehouse or
        the notebook's workspace if no lakehouse is attached.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    Tuple[str, str]
        A tuple containing the workspace name and workspace ID.
    """
    if workspace is None:
        workspace_id = get_workspace_id()
        workspace_name = resolve_workspace_name(workspace_id)

    elif isinstance(workspace, UUID) or is_valid_uuid(workspace):
        workspace_id = str(workspace)
        workspace_name = resolve_workspace_name(workspace_id)

    else:
        workspace_name = workspace
        workspace_id = resolve_workspace_id(workspace_name)

    return workspace_name, workspace_id


@log
@with_credential
def resolve_dataset_id(dataset_name: str, workspace: Optional[Union[str, UUID]] = None,
                       credential: Optional["TokenCredential"] = None) -> str:
    """
    Resolve the dataset ID by name in the specified workspace.

    Parameters
    ----------
    dataset_name : str
        Name of the dataset to be resolved.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The ID of the specified dataset.
    """
    return _get_or_create_workspace_client(workspace).resolve_dataset_id(dataset_name)


@log
@with_credential
def resolve_dataset_name(dataset_id: Union[str, UUID], workspace: Optional[Union[str, UUID]] = None,
                         credential: Optional["TokenCredential"] = None) -> str:
    """
    Resolve the dataset name by ID in the specified workspace.

    Parameters
    ----------
    dataset_id : str or uuid.UUID
        Dataset ID or UUID object containing the dataset ID to be resolved.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The name of the specified dataset.
    """
    return _get_or_create_workspace_client(workspace).resolve_dataset_name(dataset_id)


@log
@with_credential
def resolve_dataset_name_and_id(
    dataset: Union[str, UUID], workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> Tuple[str, str]:
    """
    Resolve the name and ID of a dataset in the specified or default workspace.

    Parameters
    ----------
    dataset : str or UUID
        The dataset name or ID.
    workspace : str or UUID, default=None
        The Fabric workspace name or ID. If None, the default workspace is used.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    Tuple[str, str]
        A tuple containing the dataset name and dataset ID.
    """

    workspace_name, workspace_id = resolve_workspace_name_and_id(workspace)

    if isinstance(dataset, UUID) or is_valid_uuid(dataset):
        dataset_id = str(dataset)
        dataset_name = resolve_dataset_name(dataset_id, workspace_id)

    else:
        dataset_name = dataset
        dataset_id = resolve_dataset_id(dataset_name, workspace_id)

    return dataset_name, dataset_id


@log
@with_credential
def resolve_item_id(item_name: str, type: Optional[str] = None,
                    workspace: Optional[Union[str, UUID]] = None,
                    credential: Optional["TokenCredential"] = None) -> str:
    """
    Resolve the item ID by name in the specified workspace.

    The item type can be given to limit the search. Otherwise the function will search for all items in the workspace.

    Please see `ItemTypes <https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item?tabs=HTTP#itemtype>_`
    for all supported item types.

    Parameters
    ----------
    item_name : str
        Name of the item to be resolved.
    type : str, default = None
        Type of the item to be resolved.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The item ID of the specified item.
    """
    return _get_or_create_workspace_client(workspace).resolve_item_id(item_name, type=type)


@log
@with_credential
def resolve_item_name(item_id: Union[str, UUID], type: Optional[str] = None,
                      workspace: Optional[Union[str, UUID]] = None,
                      credential: Optional["TokenCredential"] = None) -> str:
    """
    Resolve the item name by ID in the specified workspace.

    The item type can be given to limit the search. Otherwise the function will search for all items in the workspace.

    Please see `ItemTypes <https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item?tabs=HTTP#itemtype>_`
    for all supported item types.

    Parameters
    ----------
    item_id : str or uuid.UUID
        Item ID or UUID object containing the item ID to be resolved.
    type : str, default = None
        Type of the item to be resolved.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The item ID of the specified item.
    """
    return _get_or_create_workspace_client(workspace).resolve_item_name(item_id, type=type)


@log
@with_credential
def resolve_folder_id(folder: Union[str, os.PathLike, UUID],
                      workspace: Optional[Union[str, UUID]] = None,
                      credential: Optional["TokenCredential"] = None) -> str:
    """
    Resolve the folder ID in the specified workspace.

    If the input is already an ID, the function will check if it exists and return as is.

    ***Experimental***: This function is experimental and may change in future versions.

    Parameters
    ----------
    folder : str, os.PathLike, or uuid.UUID
        The Fabric folder path, folder ID, or UUID object containing the folder ID to be resolved.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The folder ID of the specified folder.
    """
    return _get_or_create_workspace_client(workspace).resolve_folder_id(folder)


@log
@with_credential
def resolve_folder_path(folder: Union[str, os.PathLike, UUID],
                        workspace: Optional[Union[str, UUID]] = None,
                        credential: Optional["TokenCredential"] = None) -> str:
    """
    Resolve the folder name in the specified workspace.

    If the input is already a path, the function will check if it exists and return the normalized folder path.

    ***Experimental***: This function is experimental and may change in future versions.

    Parameters
    ----------
    folder : str, os.PathLike, or uuid.UUID
        The Fabric folder path, folder ID, or UUID object containing the folder ID to be resolved.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The folder path of the specified folder.
    """
    return _get_or_create_workspace_client(workspace).resolve_folder_path(folder)


@log
@with_credential
def create_trace_connection(
    dataset: Union[str, UUID],
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> TraceConnection:
    """
    Create a TraceConnection to the server specified by the dataset.

    NOTE: This feature is only intended for exploratory use. Due to the asynchronous communication required between the
    Microsoft Analysis Services (AS) Server and other AS clients, trace events are registered on a best-effort basis where timings are
    dependent on server load.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset to list traces on.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    TraceConnection
        Server connected to specified dataset.
    """
    dataset_client: DatasetXmlaClient = _get_or_create_workspace_client(workspace).get_dataset_client(dataset, ConnectionMode.XMLA)   # type: ignore
    return TraceConnection(dataset_client)


@log
@with_credential
def list_workspaces(filter: Optional[str] = None, top: Optional[int] = None, skip: Optional[int] = None,
                    roles: Optional[str] = None, endpoint: Literal["powerbi", "fabric"] = "powerbi",
                    credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    Return a list of workspaces the user has access to.

    Parameters
    ----------
    filter : str, default=None
        OData filter expression. For example, to filter by name, use "name eq 'My workspace'".
        Only supported in "powerbi" endpoint.
    top : int, default=None
        Maximum number of workspaces to return.
        Only supported in "powerbi" endpoint.
    skip : int, default=None
        Number of workspaces to skip.
        Only supported in "powerbi" endpoint.
    roles : str, default=None
        A comma-separated list of roles (Admin,Member,Contributor,Viewer).
        Only supported in "fabric" endpoint.
    endpoint : Literal["powerbi", "fabric"], default="powerbi"
        The endpoint to use for listing workspaces. Supported values are "powerbi" and "fabric".
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per workspace.
    """
    rest_api: Union[_FabricRestAPI, _PBIRestAPI]

    if endpoint == "powerbi":
        if roles is not None:
            warnings.warn("The \"roles\" parameter is only supported in \"fabric\" endpoint and will be ignored.", UserWarning)

        rest_api = _PBIRestAPI()
        payload = rest_api.list_workspaces(filter, top, skip)

        df = rename_and_validate_from_records(payload, [
                                   ("id",                          "Id",                             "str"),
                                   ("isReadOnly",                  "Is Read Only",                   "bool"),
                                   ("isOnDedicatedCapacity",       "Is On Dedicated Capacity",       "bool"),
                                   ("capacityId",                  "Capacity Id",                    "str"),
                                   ("defaultDatasetStorageFormat", "Default Dataset Storage Format", "str"),
                                   ("type",                        "Type",                           "str"),
                                   ("name",                        "Name",                           "str")])

    elif endpoint == "fabric":
        if filter is not None or top is not None or skip is not None:
            warnings.warn("The \"filter\", \"top\", and \"skip\" parameters are only supported in \"powerbi\" endpoint and will be ignored.", UserWarning)

        rest_api = _FabricRestAPI()
        payload = rest_api.list_workspaces(roles)

        df = rename_and_validate_from_records(payload, [
                                   ("id",          "Id",           "str"),
                                   ("capacityId",  "Capacity Id",  "str?"),
                                   ("type",        "Type",         "str"),
                                   ("displayName", "Name",         "str"),
                                   ("description", "Description",  "str")],
                                   replace_na=True)

    else:
        raise ValueError(f"Unsupported endpoint: {endpoint}. Supported endpoints are \"powerbi\" and \"fabric\".")

    # make it consistent w/ other APIs and allow for easy join
    df["Capacity Id"] = df["Capacity Id"].str.lower()

    return df


@log
@with_credential
def list_capacities(credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    Return a list of capacities that the principal has access to (`details <https://learn.microsoft.com/en-us/rest/api/fabric/core/capacities/list-capacities>`_).

    Parameters
    ----------
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing the capacities.
    """
    payload = _get_fabric_rest_api().list_capacities()

    return rename_and_validate_from_records(payload, [
        ("id",          "Id",           "str"),
        ("displayName", "Display Name", "str"),
        ("sku",         "Sku",          "str"),
        ("region",      "Region",       "str"),
        ("state",       "State",        "str")])


@log
@with_credential
def list_reports(workspace: Optional[Union[str, UUID]] = None,
                 endpoint: Literal["powerbi", "fabric"] = "powerbi",
                 credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    Return a list of reports in the specified workspace.

    Parameters
    ----------
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    endpoint : Literal["powerbi", "fabric"], default="powerbi"
        The endpoint to use for listing reports. Supported values are "powerbi" and "fabric".
        See `PowerBI List Reports <https://learn.microsoft.com/en-us/rest/api/power-bi/reports/get-reports>`__ for using "powerbi"
        and `Fabric List Reports <https://learn.microsoft.com/en-us/rest/api/fabric/report/items/list-reports>`__ for using "fabric".
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per report.
    """

    return _get_or_create_workspace_client(workspace).list_reports(endpoint=endpoint)


@log
@with_credential
def list_items(type: Optional[str] = None, workspace: Optional[Union[str, UUID]] = None,
               root_folder: Optional[Union[str, os.PathLike, UUID]] = None,
               recursive: bool = True,
               credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    Return a list of items in the specified workspace.

    You need to have at least "viewer" access for the workspace to use this API.

    Parameters
    ----------
    type : str, default=None
        Filter the list of items by the type specified (see `valid types <https://learn.microsoft.com/en-us/rest/api/fabric/core/items/list-items?tabs=HTTP#itemtype>`_).
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    root_folder : str, os.PathLike, or uuid.UUID, default=None
        The Fabric folder path, folder ID, or UUID object containing the folder ID to start listing from.
        Defaults to None which starts from the root of the workspace.
        ***Experimental***: This parameter is experimental and may change in future versions.
    recursive : bool, default=True
        If True, list all items recursively. Otherwise, list only the top-level items.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per artifact.
    """
    root_folder_id = resolve_folder_id(root_folder, workspace=workspace) if root_folder else None

    return _get_or_create_workspace_client(workspace) \
        .list_items(type=type, root_folder_id=root_folder_id, recursive=recursive)


@log
@with_credential
def list_folders(workspace: Optional[Union[str, UUID]] = None,
                 root_folder: Optional[Union[str, os.PathLike, UUID]] = None,
                 recursive: bool = True,
                 extend_folder_path: bool = False,
                 credential: Optional["TokenCredential"] = None) -> pd.DataFrame:
    """
    Return a list of folders in the specified workspace.

    ***Experimental***: This function is experimental and may change in future versions.

    Parameters
    ----------
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    root_folder : str, os.PathLike, or uuid.UUID, default=None
        The Fabric folder path, folder ID, or UUID object containing the folder ID to start listing from.
        Defaults to None which starts from the root of the workspace.
    recursive : bool, default=True
        If True, list all folders recursively. Otherwise, list only the top-level folders.
    extend_folder_path : bool, default=False
        If True, the full folder path of each folder will be calculated and included in the result.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        DataFrame with one row per folder.
    """
    root_folder_id = resolve_folder_id(root_folder, workspace=workspace) if root_folder else None

    return _get_or_create_workspace_client(workspace) \
        .list_folders(root_folder_id=root_folder_id, recursive=recursive, extend_folder_path=extend_folder_path)


@log
@with_credential
def create_workspace(display_name: str, capacity_id: Optional[str] = None, description: Optional[str] = None,
                     credential: Optional["TokenCredential"] = None) -> str:
    """
    Create a workspace.

    Parameters
    ----------
    display_name : str
        The display name of the workspace.
    capacity_id : str, default=None
        The optional capacity id.
    description : str, default=None
        The optional description of the workspace.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The id of workspace.
    """
    return _get_fabric_rest_api().create_workspace(display_name, capacity_id, description)


@log
@with_credential
def create_lakehouse(display_name: str,
                     description: Optional[str] = None,
                     max_attempts: int = 10,
                     workspace: Optional[Union[str, UUID]] = None,
                     folder: Optional[Union[str, os.PathLike, UUID]] = None,
                     enable_schema: bool = False,
                     credential: Optional["TokenCredential"] = None) -> str:
    """
    Create a lakehouse in the specified workspace.

    Parameters
    ----------
    display_name : str
        The display name of the lakehouse.
    description : str, default=None
        The optional description of the lakehouse.
    max_attempts : int, default=10
        Maximum number of retries to wait for creation of the notebook.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    folder : str, os.PathLike, or uuid.UUID, default=None
        The Fabric folder path, folder ID, or UUID object containing the folder ID to create the lakehouse.
        Defaults to None which creates the lakehouse under the workspace root.
        ***Experimental***: This parameter is experimental and may change in future versions.
    enable_schema : bool, default=False
        If True, the notebook will be created with schema enabled.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The id of lakehouse.
    """
    folder_id = resolve_folder_id(folder, workspace=workspace) if folder else None

    return _get_or_create_workspace_client(workspace=workspace) \
        .create_lakehouse(display_name, description, max_attempts, folder_id=folder_id,
                          enable_schema=enable_schema)


@log
@with_credential
def create_folder(folder: Union[str, os.PathLike],
                  workspace: Optional[Union[str, UUID]] = None,
                  recursive: bool = False,
                  credential: Optional["TokenCredential"] = None) -> str:
    """
    Create a folder in the specified workspace.

    ***Experimental***: This function is experimental and may change in future versions.

    Parameters
    ----------
    folder : str or os.PathLike
        The Fabric folder path to be created.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    recursive : bool, default=False
        If True, create all intermediate folders in the path if they do not exist.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The ID of the created folder.
    """
    return _get_or_create_workspace_client(workspace=workspace) \
        .create_folder(folder, recursive=recursive)


@log
@with_credential
def delete_item(item_id: str, workspace: Optional[Union[str, UUID]] = None, credential: Optional["TokenCredential"] = None):
    """
    Delete the item in the specified workspace.

    Parameters
    ----------
    item_id : str
        The id of the item.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    _get_or_create_workspace_client(workspace).delete_item(item_id)


@log
@with_credential
def delete_workspace(workspace: Union[str, UUID], credential: Optional["TokenCredential"] = None):
    """
    Delete the specified workspace.

    Parameters
    ----------
    workspace : str or uuid.UUID
        The Fabric workspace name or UUID object containing the workspace ID.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    _get_or_create_workspace_client(workspace).delete_workspace()


@log
@with_credential
def delete_folder(folder: Union[str, os.PathLike, UUID],
                  workspace: Optional[Union[str, UUID]] = None,
                  credential: Optional["TokenCredential"] = None) -> None:
    """
    Delete a folder in the specified workspace.

    ***Experimental***: This function is experimental and may change in future versions.

    Parameters
    ----------
    folder : str, os.PathLike, or uuid.UUID
        The Fabric folder path, folder ID, or UUID object containing the folder ID to delete.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    folder_id = resolve_folder_id(folder, workspace=workspace)
    _get_or_create_workspace_client(workspace=workspace).delete_folder(folder_id)


@log
@with_credential
def create_notebook(display_name: str,
                    description: Optional[str] = None,
                    content: Optional[Union[str, dict]] = None,
                    default_lakehouse: Optional[Union[str, UUID]] = None,
                    default_lakehouse_workspace: Optional[Union[str, UUID]] = None,
                    max_attempts: int = 10,
                    workspace: Optional[Union[str, UUID]] = None,
                    folder: Optional[Union[str, os.PathLike, UUID]] = None,
                    credential: Optional["TokenCredential"] = None) -> str:
    """
    Create a notebook in the specified workspace.

    Parameters
    ----------
    display_name : str
        The display name of the lakehouse.
    description : str, default=None
        The optional description of the lakehouse.
    content : str or dict, default=None
        The optional notebook content (JSON).
    default_lakehouse : str or uuid.UUID, default=None
        The optional lakehouse name or UUID object to attach to the new notebook.
    default_lakehouse_workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID the lakehouse is in.
        If None, the workspace specified for the notebook is used.
    max_attempts : int, default=10
        Maximum number of retries to wait for creation of the notebook.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    folder : str, os.PathLike, or uuid.UUID, default=None
        The Fabric folder path, folder ID, or UUID object containing the folder ID to create the notebook.
        Defaults to None which creates the notebook under the workspace root.
        ***Experimental***: This parameter is experimental and may change in future versions.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The notebook id.
    """
    if isinstance(content, str):
        ntbk_content: Any = json.loads(content)
    else:
        ntbk_content = content

    workspace_client = _get_or_create_workspace_client(workspace)
    folder_id = resolve_folder_id(folder, workspace=workspace) if folder else None

    if default_lakehouse is not None:
        default_lakehouse_id = None
        default_lakehouse_name = None

        # resolve default_lakehouse to id
        if isinstance(default_lakehouse, UUID):
            default_lakehouse_id = str(default_lakehouse)
        elif is_valid_uuid(default_lakehouse):
            default_lakehouse_id = default_lakehouse
        else:
            default_lakehouse_name = default_lakehouse

        # resolve name or id
        if default_lakehouse_workspace is not None:
            df = list_items("Lakehouse", workspace=default_lakehouse_workspace)
        else:
            df = list_items("Lakehouse", workspace=workspace)

        if default_lakehouse_name is None:
            selected_df = df[df["Id"] == default_lakehouse_id]
            if selected_df.empty:
                raise ValueError(f"Cannot find lakehouse with id '{default_lakehouse_id}' in workspace '{workspace}'")
            default_lakehouse_name = selected_df["Display Name"].values[0]

        if default_lakehouse_id is None:
            selected_df = df[df["Display Name"] == default_lakehouse_name]
            if selected_df.empty:
                raise ValueError(f"Cannot find lakehouse with name '{default_lakehouse_name}' in workspace '{workspace}'")
            default_lakehouse_id = selected_df["Id"].values[0]

        # resolve default_lakehouse_workspace to id
        if default_lakehouse_workspace is None:
            default_lakehouse_workspace_id = workspace_client.get_workspace_id()
        else:
            default_lakehouse_workspace_id = _get_or_create_workspace_client(default_lakehouse_workspace).get_workspace_id()

        # public docs: https://learn.microsoft.com/en-us/fabric/data-engineering/notebook-public-api
        ntbk_content["metadata"]["dependencies"] = {
            "lakehouse": {
                "default_lakehouse": default_lakehouse,
                "known_lakehouses": [
                    {
                        "id": default_lakehouse
                    }
                ],
                "default_lakehouse_name": default_lakehouse_name,
                "default_lakehouse_workspace_id": default_lakehouse_workspace_id
            }
        }

    return workspace_client.create_notebook(display_name,
                                            description,
                                            json.dumps(ntbk_content),
                                            max_attempts,
                                            folder_id)


@log
@with_credential
def run_notebook_job(notebook_id: str, max_attempts: int = 10, workspace: Optional[Union[str, UUID]] = None, credential: Optional["TokenCredential"] = None) -> str:
    """
    Run a notebook job and wait for it to complete.

    Parameters
    ----------
    notebook_id : str
        The id of the notebook to run.
    max_attempts : int, default=10
        Maximum number of retries to wait for creation of the notebook.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    str
        The job id.
    """
    return _get_or_create_workspace_client(workspace).run_notebook_job(notebook_id, max_attempts)


@log
@with_credential
def create_tom_server(dataset: Optional[Union[str, UUID]] = None,
                      readonly: bool = True,
                      workspace: Optional[Union[str, UUID]] = None,
                      credential: Optional["TokenCredential"] = None) -> object:
    """
    Create a TOM server for the specified workspace.

    Note that not all properties and methods of the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    are supported due to limitation when bridging Python to .NET.

    If changes are made to models, make sure to call SaveChanges() on the model object and invoke refresh_tom_cache().

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID, default=None
        Name or UUID of the dataset to be included in the TOM server.
        Recommended to set if you plan to connect to a specific dataset.
    readonly : bool, default=True
        Whether to create a read-only server.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    object
        The TOM server. See `Microsoft.AnalysisServices.Tabular.Server <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server>`__.
    """
    workspace_client = _get_or_create_workspace_client(workspace)

    workspace_url = _get_workspace_url(workspace_client.get_workspace_name())

    if dataset is not None and is_valid_uuid(dataset):
        dataset = resolve_dataset_name(dataset, workspace=workspace)

    connection_str = _build_adomd_connection_string(
        workspace_url,
        initial_catalog=cast(Optional[str], dataset),
        readonly=readonly
    )

    return _create_tom_server(connection_str, credential)


@log
@with_credential
def move_folder(folder: Union[str, os.PathLike, UUID],
                target_folder: Optional[Union[str, os.PathLike, UUID]] = None,
                workspace: Optional[Union[str, UUID]] = None,
                credential: Optional["TokenCredential"] = None) -> None:
    """
    Move a folder to a new parent folder.

    ***Experimental***: This function is experimental and may change in future versions.

    Parameters
    ----------
    folder : str, os.PathLike, or uuid.UUID
        The Fabric folder path, folder ID, or UUID object containing the folder ID to be moved.
    target_folder : str, os.PathLike, or uuid.UUID, default=None
        The Fabric folder path, folder ID, or UUID object containing the folder ID to move the folder to.
        Defaults to None which will move the folder to the root of the workspace.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    folder_id = resolve_folder_id(folder, workspace=workspace)

    _get_or_create_workspace_client(workspace=workspace) \
        .move_folder(folder_id, target_folder=target_folder)


@log
@with_credential
def rename_folder(folder: Union[str, os.PathLike, UUID],
                  new_folder_name: str,
                  workspace: Optional[Union[str, UUID]] = None,
                  credential: Optional["TokenCredential"] = None) -> None:
    """
    Rename a folder in the specified workspace.

    ***Experimental***: This function is experimental and may change in future versions.

    Parameters
    ----------
    folder : str, os.PathLike, or uuid.UUID
        The Fabric folder path, folder ID, or UUID object containing the folder ID to be renamed.
    new_folder_name : str
        The new name of the folder.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID. Defaults to None
        which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    folder_id = resolve_folder_id(folder, workspace=workspace)

    _get_or_create_workspace_client(workspace=workspace) \
        .rename_folder(folder_id, new_folder_name)
