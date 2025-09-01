import datetime
import os
import pandas as pd
from warnings import warn
import time
from contextvars import ContextVar
from tqdm.auto import tqdm

from sempy.fabric._client._dataset_xmla_client import DatasetXmlaClient
from sempy.fabric._client._dataset_rest_client import DatasetRestClient
from sempy.fabric._client._dataset_onelake_import import DatasetOneLakeImportClient
from sempy.fabric._client._connection_mode import ConnectionMode
from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy.fabric._client._fabric_rest_api import _FabricRestAPI, OperationStart
from sempy.fabric._client._utils import _init_analysis_services, _create_tom_server, _build_adomd_connection_string
from sempy.fabric._environment import get_workspace_id, _get_workspace_url
from sempy.fabric._utils import (
    is_valid_uuid,
    dotnet_to_pandas_date,
    collection_to_dataframe,
    get_properties,
    normalize_fabric_path,
    split_fabric_path
)
from sempy._utils._pandas_utils import rename_and_validate_from_records
from sempy.fabric.exceptions import (
    DatasetNotFoundException,
    FabricHTTPException,
    FolderNotFoundException,
    WorkspaceNotFoundException,
)

from functools import lru_cache
from uuid import UUID
from typing import cast, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class WorkspaceClient:
    """
    Accessor class for a Power BI workspace.

    The workspace can contain multiple Datasets, which can be accessed via
    a PowerBIClient obtained via :meth:`get_dataset_client`.

    The class is a thin wrapper around
    `Microsoft.AnalysisServices.Tabular.Server <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    client that accesses cloud Power BI workspace and its Tabular Object Model (TOM)
    via the XMLA interface. The client caches the connection to the server for faster performance.

    Parameters
    ----------
    workspace : str or UUID
        PowerBI Workspace Name or UUID object containing the workspace ID.
    credential : TokenCredential, default=None
        The credential to acquire the token. If not provided, the default credential will be used.
    """
    def __init__(self, workspace: Optional[Union[str, UUID]] = None, credential: Optional["TokenCredential"] = None):

        _init_analysis_services()

        self.credential = credential
        self._pbi_rest_api = _PBIRestAPI(credential=self.credential)
        self._fabric_rest_api = _FabricRestAPI(credential=self.credential)
        self._cached_dataset_client = lru_cache()(
            lambda dataset_name, ClientClass: ClientClass(
                self,
                dataset_name,
                credential=self.credential
            )
        )

        self._workspace_id: str
        self._workspace_name: str

        if workspace is None:
            self._workspace_id = get_workspace_id()
            self._workspace_name = cast(str, self.get_workspace_name_from_id(self._workspace_id))
        elif isinstance(workspace, UUID):
            self._workspace_id = str(workspace)
            self._workspace_name = cast(str, self.get_workspace_name_from_id(self._workspace_id))
        elif isinstance(workspace, str):
            workspace_id = self.get_workspace_id_from_name(workspace, strict=False)
            # None if we couldn't find the workspace, so it might be a UUID as string
            if workspace_id is None:
                if is_valid_uuid(workspace):
                    self._workspace_id = workspace
                    self._workspace_name = cast(str, self.get_workspace_name_from_id(self._workspace_id))
                else:
                    raise WorkspaceNotFoundException(workspace)
            else:
                self._workspace_name = workspace
                self._workspace_id = workspace_id
        else:
            raise TypeError(f"Unexpected type {type(workspace)} for \"workspace\"")

        # Cached TOM server.
        #
        # This variable declares the TOM server object as a context variable
        # (see `contextvars <https://docs.python.org/3/library/contextvars.html>`_) to
        # support parallel TOM connections in multithreading scenarios.
        #
        # Examples
        # --------
        #
        # Create a WorkspaceClient instance and use it within multithreading context:
        #
        # >>> client = WorkspaceClient("My workspace")
        #
        # Define a worker function for executors:
        #
        # >>> def worker(*args, **kwargs):
        # >>>     # create a thread-local TOM server
        # >>>     tom_server = client._get_readonly_tom_server()
        # >>>     ...
        #
        # Copy the context for each executor and run in parallel:
        #
        # >>> with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        # >>>     # refresh the existing connection (needed if there's one created in the main thread)
        # >>>     client.refresh_tom_cache()
        # >>>     for i in range(5):
        # >>>         ctx = contextvars.copy_context()
        # >>>         ...
        # >>>         # Run executors in parallel
        # >>>         executor.submit(ctx.run, worker, ...)
        self._tom_server_readonly: ContextVar = \
            ContextVar(f"tom_server_readonly_{self._workspace_id}")

        self.dataset_client_types = {
            ConnectionMode.XMLA: DatasetXmlaClient,
            ConnectionMode.REST: DatasetRestClient,
            ConnectionMode.ONELAKE_IMPORT_DATASET: DatasetOneLakeImportClient,
        }

    @property
    def tom_server_readonly(self):
        return self._tom_server_readonly.get(None)

    @tom_server_readonly.setter
    def tom_server_readonly(self, value):
        self._tom_server_readonly.set(value)

    def get_workspace_id_from_name(self, workspace_name: str, strict: bool = True) -> Optional[str]:
        if workspace_name == "My workspace":
            return self._fabric_rest_api.get_my_workspace_id()

        try:
            return self._pbi_rest_api.get_workspace_id_from_name(workspace_name, strict=strict)
        except FabricHTTPException as e:
            # In some cases authentication may fail for PowerBI endpoints (e.g. when using OBO-SPN token)
            # We can try to get the workspace ID from the Fabric API as a fallback
            if e.status_code == 403:
                return self._fabric_rest_api.get_workspace_id_from_name(workspace_name, strict=strict)
            # For other errors, raise the exception
            raise

    def get_workspace_name_from_id(self, workspace_id: str, strict: bool = True) -> Optional[str]:
        try:
            return self._pbi_rest_api.get_workspace_name_from_id(workspace_id, strict=strict)
        except FabricHTTPException as e:
            # In some cases authentication may fail for PowerBI endpoints (e.g. when using OBO-SPN token)
            # We can try to get the workspace name from the Fabric API as a fallback
            if e.status_code == 403:
                return self._fabric_rest_api.get_workspace_name_from_id(workspace_id, strict=strict)
            # For other errors, raise the exception
            raise

    def get_workspace_id(self) -> str:
        """
        Get workspace ID of associated workspace.

        Returns
        -------
        String
            Workspace ID.
        """
        return self._workspace_id

    def get_workspace_name(self) -> str:
        """
        Get name ID of associated workspace.

        Returns
        -------
        String
            Workspace name.
        """
        return self._workspace_name

    def _get_readonly_tom_server(self, dataset: Optional[Union[str, UUID]] = None):
        """
        Connect to PowerBI TOM Server, or returns server if already connected.

        Parameters
        __________
        dataset : str or uuid.UUID, default=None
            Name or UUID of the dataset to be included in the TOM server.
            Recommended to set if you plan to connect to a specific dataset.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Server
            XMLA client with a cached connection to a PowerBI Tabular Object Model server.
        """
        if self.tom_server_readonly is None:
            self.tom_server_readonly = self._create_tom_server(dataset=dataset,
                                                               readonly=True)

        return self.tom_server_readonly

    def _create_tom_server(self, dataset: Optional[Union[str, UUID]] = None,
                           readonly: bool = True):
        """
        Creates a TOM server object.

        Parameters
        ----------
        dataset : str or uuid.UUID, default=None
            Name or UUID of the dataset to be included in the TOM server.
            Recommended to set if you plan to connect to a specific dataset.
        readonly: bool, default=True
            Whether the server should be readonly.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Server
            XMLA client with a cached connection to a PowerBI Tabular Object Model server.
        """

        # ?readonly enables connections to read-only replicas (see https://learn.microsoft.com/en-us/power-bi/enterprise/service-premium-scale-out-app)
        workspace_url = _get_workspace_url(self.get_workspace_name())

        if dataset is not None and is_valid_uuid(dataset):
            dataset = self.resolve_dataset_name(dataset)

        dataset = cast(Optional[str], dataset)

        connection_str = _build_adomd_connection_string(workspace_url,
                                                        initial_catalog=dataset,
                                                        readonly=readonly)

        return _create_tom_server(connection_str, self.credential)

    def get_datasets(self, mode: str, additional_xmla_properties: Optional[Union[str, List[str]]] = None, endpoint: str = "powerbi") -> pd.DataFrame:
        """
        Get a list of datasets in a PowerBI workspace.

        Each dataset is derived from
        `Microsoft.AnalysisServices.Tabular.Database <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.database?view=analysisservices-dotnet>`__

        The dataframe contains the following columns:

        - Dataset Name `see <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.namedcomponent.name?view=analysisservices-dotnet#microsoft-analysisservices-namedcomponent-name>`__
        - Created Date `see <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.majorobject.createdtimestamp?view=analysisservices-dotnet#microsoft-analysisservices-majorobject-createdtimestamp>`__
        - ID `see <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.namedcomponent.id?view=analysisservices-dotnet#microsoft-analysisservices-namedcomponent-id>`__
        - Last Update `see <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.core.database.lastupdate?view=analysisservices-dotnet#microsoft-analysisservices-core-database-lastupdate>`__

        Returns
        -------
        DataFrame
            Pandas DataFrame listing databases and their attributes.
        """  # noqa: E501
        databases = []

        # Alternative implementation using REST API
        # + returns the most updated dataset list (using XMLA caches the TOM model)
        # + returns default datasets too
        # - these might not work with XMLA client
        # - less metadata

        # REST displays most up-to-date list of datasets, but the discover/read operations in XMLA
        # are cached at the time of initialization and may not know about recently added/deleted datasets.
        # We are choosing XMLA to maintain consistency between what the user sees with list_datasets and
        # read_table operations.

        if mode == "rest":
            if endpoint == "powerbi":
                dataset_json = self._pbi_rest_api.get_workspace_datasets(self.get_workspace_name(), self.get_workspace_id())

                return rename_and_validate_from_records(dataset_json, [
                    ("id",                               "Dataset Id",                           "str"),
                    ("name",                             "Dataset Name",                         "str"),
                    ("webUrl",                           "Web Url",                              "str"),
                    ("addRowsAPIEnabled",                "Add Rows API Enabled",                 "bool"),
                    ("configuredBy",                     "Configured By",                        "str"),
                    ("isRefreshable",                    "Is Refreshable",                       "bool"),
                    ("isEffectiveIdentityRequired",      "Is Effective Identity Required",       "bool"),
                    ("isEffectiveIdentityRolesRequired", "Is Effective Identity Roles Required", "bool"),
                    ("isOnPremGatewayRequired",          "Is On Prem Gateway Required",          "bool"),
                    ("targetStorageMode",                "Target Storage Mode",                  "str"),
                    ("createdDate",                      "Created Timestamp",                    "datetime64[ns]"),
                    ("createReportEmbedURL",             "Create Report Embed URL",              "str"),
                    ("qnaEmbedURL",                      "Qna Embed URL",                        "str"),
                    ("upstreamDatasets",                 "Upstream Datasets",                    "object"),
                    ("users",                            "Users",                                "object"),
                    ("queryScaleOutSettings",            "Query Scale Out Settings",             "object"),
                ])
            elif endpoint == "fabric":
                payload = self._fabric_rest_api.list_datasets(self.get_workspace_id())

                return rename_and_validate_from_records(payload, [
                    ("id",          "Dataset Id",    "str"),
                    ("displayName", "Dataset Name",  "str"),
                    ("description", "Description",   "str"),
                    ("type",        "Type",          "str"),
                    ("workspaceId", "Workspace Id",  "str"),
                    ("folderId",    "Folder Id",     "str?")],
                    replace_na=True)
            else:
                raise ValueError(f"Unsupported endpoint: {endpoint}. Supported endpoints are \"powerbi\" and \"fabric\".")

        elif mode == "xmla":

            # TODO: figure out how to refresh list of TOM databases without re-establishing the connection (costly)
            for item in self._get_readonly_tom_server().Databases:
                # PowerBI is known to throw exceptions on individual attributes e.g. due to Vertipaq load failure
                # Careful with adding additional attributes here, can take a long time to load
                # e.g. EstimatedSize & CompatibilityLevel can be very slow
                try:
                    row = {'Dataset Name': item.Name,
                           'Dataset ID': item.ID,
                           'Created Timestamp': dotnet_to_pandas_date(item.CreatedTimestamp),
                           'Last Update': dotnet_to_pandas_date(item.LastUpdate)}

                    row.update(get_properties(item, additional_xmla_properties))

                    databases.append(row)
                except Exception as ex:
                    databases.append({'Dataset Name': item.Name, 'Error': str(ex)})
        else:
            raise ValueError(f"Unexpected mode {mode}")

        return pd.DataFrame(databases)

    def get_dataset(self, dataset: Union[str, UUID]):
        """
        Get PowerBI dataset for a given dataset_name.

        The dataset is derived from
        `Microsoft.AnalysisServices.Tabular.Database <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.database?view=analysisservices-dotnet>>`_

        Parameters
        ----------
        dataset : str or UUID
            Dataset name UUID object containing the dataset ID.

        Returns
        -------
        Dataset
            PowerBI Dataset represented as TOM Database object.
        """
        client = self.get_dataset_client(dataset)

        for db in self._get_readonly_tom_server(dataset=dataset).Databases:
            if db.Name == client.resolver.dataset_name:
                return db

        # Executing the following is very unlikely, because an exception should have
        # occured during dataset resolution. The only conceivable way is if the dataset
        # got deleted before we retrieved the list with self.get_connection().Databases.
        raise DatasetNotFoundException(str(dataset), self.get_workspace_name())

    def get_tmsl(self, dataset: Union[str, UUID]) -> str:
        """
        Retrieve the TMSL for a given dataset.

        Parameters
        ----------
        dataset : str or UUID
            Name or UUID of the dataset to list the measures for.

        Returns
        -------
        str
            TMSL for the given dataset.
        """
        tabular_database = self.get_dataset(dataset)

        import Microsoft.AnalysisServices.Tabular as TOM

        return TOM.JsonSerializer.SerializeDatabase(tabular_database)

    def execute_tmsl(self, script: str):
        """
        Executes TMSL script.

        Parameters
        ----------
        script : str
            The TMSL script json
        """
        # always create a new connection to avoid state issues
        server = self._create_tom_server(readonly=False)

        try:
            # deal with Power BI transient errors
            # max. weight <1min
            max_retries = 5
            for retry in range(1, max_retries+1):
                results = server.Execute(script)

                errors = []
                warnings = []
                for res in results:
                    for msg in res.Messages:
                        error_code = msg.GetType().GetProperty("ErrorCode")
                        if error_code is not None:
                            errors.append(f"Error {msg.ErrorCode}: {msg.Description}")
                        else:
                            warnings.append(msg.Description)

                if len(warnings) > 0:
                    warn("\n".join(warnings))

                if len(errors) > 0:
                    msg = "\n".join(errors)

                    if "was routed to wrong node by the Power BI request router. This is usually caused by intermittent issues. Please try again." not in msg \
                       or retry == max_retries:
                        raise RuntimeError(msg)

                    time.sleep(retry * retry)
                else:
                    # no errors, stop retry
                    return
        finally:
            # cleanup (True = drop session)
            server.Disconnect(True)
            server.Dispose()

        assert False, "Retry loop should have returned"

    def refresh_tom_cache(self):
        """
        Refresh the TOM Server (https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet)
        to it's latest state.
        """

        # Note: simply re-establishing the connection is the most stable solution
        # Refreshing can be very slow and also lead to errors
        # Element 'METADATA' with namespace name 'urn:schemas-microsoft-com:xml-analysis:rowset' was not found
        if self.tom_server_readonly is not None:
            # cleanup (True = drop session)
            self.tom_server_readonly.Disconnect(True)
            self.tom_server_readonly.Dispose()

        self.tom_server_readonly = None

    def list_measures(self, dataset: Union[str, UUID], additional_xmla_properties: Optional[Union[str, List[str]]] = None) -> pd.DataFrame:
        """
        Retrieve all measures associated with the given dataset.

        Each measure is derived from
        `Microsoft.AnalysisServices.Tabular.Measure <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.measure?view=analysisservices-dotnet>`__

        Parameters
        ----------
        dataset : str or UUID
            Name or UUID of the dataset to list the measures for.
        additional_xmla_properties : str or List[str], default=None
            Additional XMLA `measure <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.measure?view=analysisservices-dotnet>`_
            properties to include in the returned dataframe.

        Returns
        -------
        DataFrame
            Pandas DataFrame listing measures and their attributes.
        """
        client = self.get_dataset_client(dataset)
        database = self.get_dataset(client.resolver.dataset_name)

        # see https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.measure?view=analysisservices-dotnet
        # (table, measure)
        extraction_def = [
            ("Table Name",               lambda r: r[0].Name,                   "str"),   # noqa: E272
            ("Measure Name",             lambda r: r[1].Name,                   "str"),   # noqa: E272
            ("Measure Expression",       lambda r: r[1].Expression,             "str"),   # noqa: E272
            ("Measure Data Type",        lambda r: r[1].DataType.ToString(),    "str"),   # noqa: E272
            ("Measure Hidden",           lambda r: r[1].IsHidden,               "bool"),  # noqa: E272
            ("Measure Display Folder",   lambda r: r[1].DisplayFolder,          "str"),   # noqa: E272
            ("Measure Description",      lambda r: r[1].Description,            "str"),   # noqa: E272
            ("Format String",            lambda r: r[1].FormatString,           "str"),   # noqa: E272
            ("Data Category",            lambda r: r[1].DataCategory,           "str"),   # noqa: E272
            ("Detail Rows Definition",   lambda r: r[1].DetailRowsDefinition,   "str"),   # noqa: E272
            ("Format String Definition", lambda r: r[1].FormatStringDefinition, "str"),   # noqa: E272
        ]

        collection = [
            (table, measure)
            for table in database.Model.Tables
            for measure in table.Measures
        ]

        return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)

    def get_dataset_client(self, dataset: Union[str, UUID], mode: ConnectionMode = ConnectionMode.REST,
                           use_readwrite_connection: bool = False) -> Union[DatasetRestClient, DatasetXmlaClient, DatasetOneLakeImportClient]:
        """
        Get PowerBIClient for a given dataset name or GUID.

        The same cached reusable instance is returned for each dataset.

        Parameters
        ----------
        dataset : str or UUID
            Dataset name or UUID object containing the dataset ID.
        mode : ConnectionMode, default=REST
            Which client to use to connect to the dataset.
        use_readwrite_connection : bool, default=False
            If true, connects to the readwrite version of a semantic model with query scale out enabled.
            Only applicable for XMLA mode. When True, bypasses caching to create a new client instance.

        Returns
        -------
        DatasetRestClient, DatasetXmlaClient or DatasetOneLakeImportClient
            Client facilitating data retrieval from a specified dataset.
        """

        # If readwrite connection is requested and it's an XMLA client, bypass cache and create new instance
        if use_readwrite_connection and mode == ConnectionMode.XMLA:
            return DatasetXmlaClient(
                self,
                dataset,
                use_readwrite_connection=True,
                credential=self.credential
            )

        return self._cached_dataset_client(dataset, self.dataset_client_types[mode])

    def _is_internal(self, table) -> bool:
        if table.IsPrivate:
            return True
        # annotations = list(table.Annotations)
        for annotation in table.Annotations:
            if annotation.Name == "__PBI_LocalDateTable":
                return True
        return False

    def _get_xmla_datetime_utc(self, xmla_datetime) -> datetime.datetime:
        utc_dt_str = xmla_datetime.ToUniversalTime().ToString("s")
        return datetime.datetime.strptime(utc_dt_str, "%Y-%m-%dT%H:%M:%S")

    def __repr__(self):
        return f"PowerBIWorkspace('{self.get_workspace_name()}')"

    def list_reports(self, endpoint: str = "powerbi") -> pd.DataFrame:
        """
        Return a list of reports in the specified workspace.

        Parameters
        ----------
        endpoint : str, default="powerbi"
            The endpoint to use for listing reports. Supported values are "powerbi" and "fabric".

        Returns
        -------
        pandas.DataFrame
            DataFrame with one row per report.
        """

        if endpoint == "powerbi":
            payload = self._pbi_rest_api.list_reports(self.get_workspace_name(), self.get_workspace_id())

            return rename_and_validate_from_records(
                payload,
                [
                    ("id",                 "Id",                   "str"),
                    ("reportType",         "Report Type",          "str"),
                    ("name",               "Name",                 "str"),
                    ("webUrl",             "Web Url",              "str"),
                    ("embedUrl",           "Embed Url",            "str"),
                    ("isFromPbix",         "Is From Pbix",         "bool"),
                    ("isOwnedByMe",        "Is Owned By Me",       "bool"),
                    ("datasetId",          "Dataset Id",           "str"),
                    ("datasetWorkspaceId", "Dataset Workspace Id", "str"),
                    ("users",              "Users",                "object"),
                    ("subscriptions",      "Subscriptions",        "object")
                ])
        elif endpoint == "fabric":
            payload = self._fabric_rest_api.list_reports(self.get_workspace_id())

            return rename_and_validate_from_records(
                payload,
                [
                    ("id",          "Id",                   "str"),
                    ("type",        "Report Type",          "str"),
                    ("displayName", "Name",                 "str"),
                    ("workspaceId", "Dataset Workspace Id", "str"),
                    ("description", "Description",          "str"),
                    ("folderId",    "Folder Id",            "str?")
                ],
                replace_na=True)
        else:
            raise ValueError(f"Unsupported endpoint: {endpoint}. Supported endpoints are \"powerbi\" and \"fabric\".")

    def list_items(self, type: Optional[str] = None, root_folder_id: Optional[str] = None,
                   recursive: bool = True) -> pd.DataFrame:
        payload = self._fabric_rest_api.list_items(self.get_workspace_id(),
                                                   type=type,
                                                   root_folder_id=root_folder_id,
                                                   recursive=recursive)

        return rename_and_validate_from_records(payload, [
                                ("id",                 "Id",                   "str"),
                                ("displayName",        "Display Name",         "str"),
                                ("description",        "Description",          "str"),
                                ("type",               "Type",                 "str"),
                                ("workspaceId",        "Workspace Id",         "str"),
                                ("folderId",           "Folder Id",            "str?")],
                                replace_na=True)

    def create_lakehouse(self, display_name: str, description: Optional[str] = None, max_attempts: int = 10, folder_id: Optional[str] = None, enable_schema: bool = False) -> str:
        return self._fabric_rest_api.create_lakehouse(self.get_workspace_id(), display_name, description, lro_max_attempts=max_attempts, folder_id=folder_id, enable_schema=enable_schema)

    def create_workspace(self, display_name: str, description: Optional[str] = None) -> str:
        return self._fabric_rest_api.create_workspace(display_name, description)

    def delete_item(self, item_id: str):
        self._fabric_rest_api.delete_item(self.get_workspace_id(), item_id)

    def delete_workspace(self):
        self._fabric_rest_api.delete_workspace(self.get_workspace_id())

    def create_notebook(self, display_name: str, description: Optional[str] = None, content: Optional[str] = None, max_attempts: int = 10, folder_id: Optional[str] = None) -> str:
        return self._fabric_rest_api.create_notebook(self.get_workspace_id(), display_name, description, content, max_attempts, folder_id)

    def create_folder(self, folder: Union[str, os.PathLike], recursive: bool = False) -> str:
        folder = normalize_fabric_path(folder)
        folder_name = os.path.basename(folder)
        parent_folder_id = None
        created_path = ""

        # List folders will be throttled if called too often,
        # so we cache the result to avoid unnecessary calls
        # to the Fabric API to improve performance.
        @lru_cache(maxsize=None)
        def cached_folder_df():
            return self.list_folders()

        if recursive:

            for iter_folder_name in split_fabric_path(folder)[:-1]:
                try:
                    parent_folder_id = self._create_folder(iter_folder_name, parent_folder_id=parent_folder_id)
                except FabricHTTPException as e:
                    if e.status_code == 409:
                        # Folder already exists
                        parent_folder_id = self._get_folder_id(
                            os.path.join("/", created_path, iter_folder_name),
                            folder_df=cached_folder_df()
                        )
                    else:
                        raise e

                created_path = os.path.join("/", created_path, iter_folder_name)
        else:
            parent_folder_path = os.path.dirname(folder)
            if parent_folder_path != "/":
                parent_folder_id = self._get_folder_id(parent_folder_path, folder_df=cached_folder_df())

        return self._create_folder(folder_name, parent_folder_id=parent_folder_id)

    def list_folders(self, root_folder_id: Optional[str] = None,
                     recursive: bool = True, extend_folder_path: bool = False) -> pd.DataFrame:

        payload = self._fabric_rest_api.list_folders(self.get_workspace_id(),
                                                     root_folder_id=root_folder_id,
                                                     recursive=recursive)

        df = rename_and_validate_from_records(payload, [
                                ("id",                 "Id",                   "str"),
                                ("displayName",        "Display Name",         "str"),
                                ("workspaceId",        "Workspace Id",         "str"),
                                ("parentFolderId",     "Parent Folder Id",     "str?")],
                                replace_na=True)

        if extend_folder_path:

            # root path of the current start point of listing
            root_path = self._get_folder_path(root_folder_id) if root_folder_id else "/"

            # mapping from folder id to folder path
            id_to_path: Dict[str, str] = {}

            # mapping from folder id to folder name
            id_to_name: Dict[str, str] = df.set_index("Id")["Display Name"].to_dict()

            # mapping from child folder id to parent folder id
            # this excludes the top level folders whose parent folder id is None or the input root folder id
            child_to_parent: Dict[str, str] = {
                r["Id"]: r["Parent Folder Id"]
                for _, r in df.iterrows()
                if r["Parent Folder Id"] and r["Parent Folder Id"] != root_folder_id
            }

            # mapping from parent folder id to list of children folder id
            parent_to_child: Dict[str, List[str]] = {}
            for c, p in child_to_parent.items():
                if p not in parent_to_child:
                    parent_to_child[p] = []
                parent_to_child[p].append(c)

            def dfs(folder_id: str, path: List[str]):
                if folder_id in id_to_path:
                    return

                path.append(id_to_name[folder_id])
                id_to_path[folder_id] = os.path.join("/", *path)

                for child_folder_id in parent_to_child.get(folder_id, []):
                    dfs(child_folder_id, path)

                path.pop()

            for folder_id in id_to_name:
                # pruning to dfs only for top level folders
                if folder_id not in child_to_parent:
                    dfs(folder_id, [root_path])

            df["Folder Path"] = df.apply(lambda row: id_to_path.get(row["Id"], None), axis=1)

        return df

    def move_folder(self, folder_id: str, target_folder: Optional[Union[str, os.PathLike, UUID]] = None):

        target_folder_name: Optional[str] = None

        if target_folder is None:
            target_folder_id = None

        elif isinstance(target_folder, UUID):
            target_folder_id = self.resolve_folder_id(target_folder)

        else:
            try:
                if normalize_fabric_path(target_folder) == "/":
                    target_folder_id = None
                else:
                    target_folder_id = self.resolve_folder_id(target_folder)

            except FolderNotFoundException:

                target_folder = normalize_fabric_path(target_folder)
                target_folder_parent = os.path.dirname(target_folder)
                target_folder_name = os.path.basename(target_folder)

                if target_folder_parent == "/":
                    target_folder_id = None
                else:
                    target_folder_id = self.resolve_folder_id(target_folder_parent)

        if target_folder_id != self._get_parent_folder_id(folder_id):
            self._move_folder(folder_id, target_folder_id=target_folder_id)

        if target_folder_name is not None and target_folder_name != self._get_folder_name(folder_id):
            self.rename_folder(folder_id, target_folder_name)

    def delete_folder(self, folder_id: str):
        return self._fabric_rest_api.delete_folder(self.get_workspace_id(), folder_id)

    def rename_folder(self, folder_id: str, new_folder_name: str):
        payload = {
            "displayName": new_folder_name
        }
        return self._fabric_rest_api.update_folder(self.get_workspace_id(), folder_id, payload)

    def resolve_folder_id(self, folder: Union[str, os.PathLike, UUID]) -> str:
        # Resolve the folder directlry if input is already a UUID
        if isinstance(folder, (str, UUID)) and is_valid_uuid(folder):
            try:
                df = self._get_folder(str(folder))
                if not df.empty:
                    return df["Id"].values[0]
            except FabricHTTPException as e:
                if e.status_code != 404:
                    raise e

        folder = cast(Union[str, os.PathLike], folder)
        return self._get_folder_id(folder)

    def resolve_folder_path(self, folder: Union[str, os.PathLike, UUID]) -> str:
        # if the input is a UUID, resolve it and return the path
        if isinstance(folder, (str, UUID)) and is_valid_uuid(folder):
            folder = str(folder)
            return self._get_folder_path(folder)

        folder = cast(Union[str, os.PathLike], folder)

        # if the input is a path, check if path exists, and returned the normalized path
        folder = normalize_fabric_path(folder)
        self._get_folder_id(folder)
        return folder

    def resolve_item_id(self, item_name: str, type: Optional[str] = None) -> str:
        df = self.list_items(type=type)
        selected_df = df[df["Display Name"] == item_name]["Id"]
        if selected_df.empty:
            raise ValueError(f"There's no item with the name '{item_name}' in workspace '{self.get_workspace_name()}'")
        return selected_df.values[0]

    def resolve_item_name(self, item_id: Union[str, UUID], type: Optional[str] = None) -> str:
        df = self.list_items(type=type)
        selected_df = df[df["Id"] == str(item_id)]["Display Name"]
        if selected_df.empty:
            raise ValueError(f"There's no item with the ID '{item_id}' in workspace '{self.get_workspace_name()}'")
        return selected_df.values[0]

    def resolve_dataset_id(self, dataset_name: str) -> str:
        return self.get_dataset_client(dataset_name).resolver.dataset_id

    def resolve_dataset_name(self, dataset_id: Union[str, UUID]) -> str:
        return self.get_dataset_client(dataset_id).resolver.dataset_name

    def run_notebook_job(self, notebook_id: str, max_attempts: int = 10) -> str:
        workspace_id = self.get_workspace_id()
        op_start = self._fabric_rest_api.run_notebook_job(workspace_id, notebook_id)

        self._wait_for_job("notebook", workspace_id, notebook_id, op_start, max_attempts)

        return op_start.operation_id

    def _wait_for_job(self, name: str, workspace_id: str, item_id, operation_start: OperationStart, max_attempts: int):
        bar = tqdm(range(max_attempts), desc=f"Waiting {operation_start.retry_after} seconds for {name} job to check for status")

        time.sleep(operation_start.retry_after)

        for _ in bar:
            job_status = self._fabric_rest_api.get_job_status(workspace_id, item_id, operation_start.operation_id)

            if job_status.status in ['Cancelled', 'Deduped', 'Failed']:
                raise RuntimeError(f"{name.capitalize()} job failed: {job_status.status}")

            if job_status.status == 'Completed':
                bar.set_description(f"{name.capitalize()} job successfully completed")

                return

            bar.set_description(f"Waiting {job_status.retry_after} seconds to check for status of {name} job to complete: {job_status.status}")

            time.sleep(job_status.retry_after)

        raise TimeoutError(f"{name.capitalize()} job timed out.")

    def _folder_exists(self, folder: Union[str, os.PathLike]) -> bool:
        folder = normalize_fabric_path(folder)
        if folder == "/":
            return True
        try:
            self._get_folder_id(folder)
        except FolderNotFoundException:
            return False
        return True

    def _create_folder(self, folder_name: str, parent_folder_id: Optional[str] = None) -> str:
        payload = {
            "displayName": folder_name
        }
        if parent_folder_id is not None:
            payload["parentFolderId"] = parent_folder_id

        return self._fabric_rest_api.create_folder(self.get_workspace_id(), payload)

    def _get_folder_id(self, folder_path: Union[str, os.PathLike], folder_df: Optional[pd.DataFrame] = None) -> str:
        raw_folder_path = folder_path
        folder_path = normalize_fabric_path(folder_path)

        if folder_path == "/":
            raise ValueError("Root folder cannot be resolved to an ID.")

        current_folder_id = None
        if folder_df is None:
            folder_df = self.list_folders()

        for folder_name in split_fabric_path(folder_path):
            df_select = folder_df[folder_df["Display Name"] == folder_name]
            if current_folder_id is None:
                df_select = df_select[df_select["Parent Folder Id"].isnull()]
            else:
                df_select = df_select[df_select["Parent Folder Id"] == current_folder_id]

            if df_select.empty:
                raise FolderNotFoundException(str(raw_folder_path), self.get_workspace_name())

            current_folder_id = df_select["Id"].values[0]

        if not current_folder_id:
            raise RuntimeError(f"Cannot resolve path '{raw_folder_path}' in "
                               f"workspace '{self.get_workspace_name()}'")

        return current_folder_id

    def _get_folder_path(self, folder_id: Union[str, UUID]) -> str:
        folder_id = str(folder_id)

        df = self._get_folder(folder_id)
        if df.empty:
            raise FolderNotFoundException(folder_id, self.get_workspace_name())

        folder_path = [df["Display Name"].values[0]]
        parent_folder_id = df["Parent Folder Id"].values[0]

        while parent_folder_id:
            df = self._get_folder(parent_folder_id)
            if df.empty:
                break
            folder_path.append(df["Display Name"].values[0])
            parent_folder_id = df["Parent Folder Id"].values[0]

        return normalize_fabric_path(os.path.join("/", *reversed(folder_path)))

    def _get_folder_name(self, folder_id: Union[str, UUID]) -> str:
        folder_id = str(folder_id)

        df = self._get_folder(folder_id)

        if df.empty:
            raise FolderNotFoundException(folder_id, self.get_workspace_name())

        return df["Display Name"].values[0]

    def _get_parent_folder_id(self, folder_id: Union[str, UUID]) -> Optional[str]:
        folder_id = str(folder_id)

        df = self._get_folder(folder_id)

        if df.empty:
            raise FolderNotFoundException(folder_id, self.get_workspace_name())

        parent_folder_id = df["Parent Folder Id"].values[0]
        return None if not parent_folder_id else str(parent_folder_id)

    def _get_folder(self, folder_id: str) -> pd.DataFrame:
        try:
            payload = self._fabric_rest_api.get_folder(self.get_workspace_id(), folder_id)
            return rename_and_validate_from_records([payload], [
                ("id",                 "Id",                   "str"),
                ("displayName",        "Display Name",         "str"),
                ("workspaceId",        "Workspace Id",         "str"),
                ("parentFolderId",     "Parent Folder Id",     "str?")],
                replace_na=True
            )
        except FabricHTTPException as e:
            if e.status_code == 404:
                raise FolderNotFoundException(folder_id, self.get_workspace_name())
            else:
                raise e

    def _move_folder(self, folder_id: str, target_folder_id: Optional[str] = None):
        return self._fabric_rest_api.move_folder(self.get_workspace_id(), folder_id,
                                                 target_folder_id=target_folder_id)
