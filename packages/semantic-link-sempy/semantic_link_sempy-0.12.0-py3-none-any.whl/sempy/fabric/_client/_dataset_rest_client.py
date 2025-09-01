import pandas as pd
from uuid import UUID
import datetime

from sempy.fabric._client._base_dataset_client import BaseDatasetClient
from sempy._utils._pandas_utils import rename_and_validate_from_records, safe_convert_rest_datetime
from sempy.fabric._client._refresh_execution_details import RefreshExecutionDetails

from typing import Optional, Union, List, Tuple, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from sempy.fabric._client import WorkspaceClient


class DatasetRestClient(BaseDatasetClient):
    """
    Client for access to Power BI data in a specific dataset using REST API calls.

    Parameters
    ----------
    workspace : str or WorkspaceClient
        PowerBI workspace name or workspace client that the dataset originates from.
    dataset : str
        Dataset name or GUID.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    def __init__(
            self,
            workspace: Union[str, "WorkspaceClient"],
            dataset: Union[str, UUID],
            credential: Optional["TokenCredential"] = None
    ):
        BaseDatasetClient.__init__(self, workspace, dataset, credential)

    def _format_measure_df(self, columns: List[dict], rows: List[list], measure: Union[str, List[str]]) -> pd.DataFrame:
        if isinstance(measure, str):
            measure = [measure]

        col_names = []
        conversion_map = {}
        for col in columns:
            col_name = col['source'].get('measure', None)
            if col_name is None:
                col_name = f"{col['source']['table']}[{col['source']['column']}]"
            col_names.append(col_name)
            col_type = col["type"]
            if col_type == 1:
                conversion_map[col_name] = 'string'
            elif col_type == 2:
                conversion_map[col_name] = 'Float64'
            elif col_type == 3:
                conversion_map[col_name] = 'Float64'
            elif col_type == 4:
                conversion_map[col_name] = 'Int64'
            elif col_type == 5:
                conversion_map[col_name] = 'boolean'
            elif col_type == 7:
                conversion_map[col_name] = 'datetime64[ns]'

        df = pd.DataFrame(rows, columns=col_names)

        # I'm not sure how useful this old Decimal handling is. Would users even care if there were some precision loss?
        # It is an interesting piece of code though, so I think it's best to keep it around until the dust from
        # type conversions settles.
        #
        # from decimal import Decimal
        #
        # for decimal_col in decimals:    # type: ignore
        #     # Converting from float to Decimal results in exact conversion, which may add unintended places to
        #     # the Decimal value (ex: Decimal(13.34) = Decimal(13.339999999999999))
        #     # String to Decimal uses the exact string passed which is what we want (ex: Decimal('13.34') = Decimal(13.34))
        #     df[decimal_col] = df[decimal_col].astype(str).apply(Decimal)

        df = df.astype(conversion_map)

        # reorder columns so measure is last (match XMLA output)
        res_columns_reordered = col_names[len(measure):] + col_names[:len(measure)]
        return df[res_columns_reordered]

    def refresh_async(
            self,
            refresh_type: str = "automatic",
            max_parallelism: int = 10,
            commit_mode: str = "transactional",
            retry_count: int = 1,
            objects: Optional[List] = None,
            apply_refresh_policy: bool = True,
            effective_date: datetime.date = datetime.date.today(),
            verbose: int = 0
    ) -> str:
        workspace_id = self.resolver.workspace_id
        workspace_name = self.resolver.workspace_name
        dataset_id = self.resolver.dataset_id
        poll_url = self.resolver.powerbi_rest_api.refresh_post(dataset_id, workspace_id, workspace_name,
                                                               refresh_type, max_parallelism, commit_mode,
                                                               retry_count, objects, apply_refresh_policy, effective_date,
                                                               verbose)
        return poll_url

    def get_refresh_execution_details(
            self,
            refresh_request_id: Union[str, UUID]
    ) -> RefreshExecutionDetails:
        # see https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-execution-details
        payload = self.resolver.powerbi_rest_api.get_refresh_execution_details(
            self.resolver.dataset_id,
            str(refresh_request_id),
            self.resolver.workspace_id,
            self.resolver.workspace_name
        )

        objects = rename_and_validate_from_records(
            payload.get("objects"),
            [
                ("table",     "Table",     "str"),
                ("partition", "Partition", "str?"),
                ("status",    "Status",    "str"),
            ]
        )

        messages = rename_and_validate_from_records(
            payload.get("messages"),
            [
                ("message", "Message", "str"),
                ("type",    "Type",    "str"),
            ]
        )

        refresh_attempts = rename_and_validate_from_records(
            payload.get("refreshAttempts"),
            [
                ("attemptId", "Attempt Id", "Int64"),
                ("startTime", "Start Time", "datetime64[ns]"),
                ("endTime",   "End Time",   "datetime64[ns]?"),
                ("type",      "Type",       "Int64"),
            ]
        )

        return RefreshExecutionDetails(
            start_time          =safe_convert_rest_datetime(payload["startTime"]),    # noqa: E251, E221
            end_time            =safe_convert_rest_datetime(payload.get("endTime")),  # noqa: E251, E221
            type                =payload["type"],                                     # noqa: E251, E221
            commit_mode         =payload["commitMode"],                               # noqa: E251, E221
            status              =payload["status"],                                   # noqa: E251, E221
            extended_status     =payload["extendedStatus"],                           # noqa: E251, E221
            current_refresh_type=payload["currentRefreshType"],                       # noqa: E251, E221
            number_of_attempts  =payload["numberOfAttempts"],                         # noqa: E251, E221
            objects             =objects,                                             # noqa: E251, E221
            messages            =messages,                                            # noqa: E251, E221
            refresh_attempts    =refresh_attempts                                     # noqa: E251, E221
        )

    def list_refresh_history(
            self,
            top_n: Optional[int] = None
    ) -> pd.DataFrame:
        workspace_id = self.resolver.workspace_id
        workspace_name = self.resolver.workspace_name
        dataset_id = self.resolver.dataset_id
        payload = self.resolver.powerbi_rest_api.list_refresh_history(dataset_id, workspace_id, workspace_name, top_n)

        return rename_and_validate_from_records(payload, [
            ("id",                   "Id",                     "str"),
            ("requestId",            "Request Id",             "str"),
            ("startTime",            "Start Time",             "datetime64[ns]"),
            ("endTime",              "End Time",               "datetime64[ns]?"),
            ("refreshType",          "Refresh Type",           "str"),
            ("serviceExceptionJson", "Service Exception Json", "str?"),
            ("status",               "Status",                 "str"),
            # missing from public docs
            ("extendedStatus",       "Extended Status",        "str?"),
            ("refreshAttempts",      "Refresh Attempts",       "str?"),
            ])

    def _evaluate_dax(self, query: str, verbose: int = 0, num_rows: Optional[int] = None) -> pd.DataFrame:
        rows = self.resolver.powerbi_rest_api.execute_dax_query(self.resolver.dataset_id, query, num_rows)
        return pd.DataFrame(rows)

    def _evaluate_measure(
        self,
        measure: Union[str, List[str]],
        groupby_columns: List[Tuple[str, str]],
        filters: Dict[Tuple[str, str], List[str]],
        num_rows: Optional[int] = None,
        batch_size: int = 100000,
        verbose: int = 0
    ) -> pd.DataFrame:
        groupby_columns_obj = [{"table": g[0], "column": g[1]} for g in groupby_columns]

        if isinstance(measure, str):
            measure = [measure]
        measure_obj = [{"measure": m} for m in measure]

        filter_obj: List[Dict[str, list]] = []
        for table_col, filter_lst in filters.items():
            target = [{"table": table_col[0], "column": table_col[1]}]
            # REST API requires the "in" parameter to have every object as its own list
            filter_in = [[obj] for obj in filter_lst]
            filter_obj.append({"target": target, "in": filter_in})

        columns, rows = self.resolver.powerbi_rest_api.calculate_measure(self.resolver.dataset_id, measure_obj, groupby_columns_obj, filter_obj, num_rows, verbose)
        if not columns:
            col_names = [f"{g[0]}[{g[1]}]" for g in groupby_columns]
            col_names.extend(measure)
            return pd.DataFrame({}, columns=col_names)
        else:
            return self._format_measure_df(columns, rows, measure)

    def __repr__(self) -> str:
        return f"DatasetRestClient('{self.resolver.workspace_name}[{self.resolver.dataset_name}]')"
