import os
import tempfile
import pandas as pd
from uuid import UUID, uuid4
import warnings

from sempy.fabric._client._base_dataset_client import BaseDatasetClient
from sempy.fabric._client._utils import _init_analysis_services, _create_tom_server, _build_adomd_connection_string
from sempy.fabric._client._adomd_connection import AdomdConnection
from sempy.fabric._environment import _get_workspace_url, get_workspace_id
from sempy.fabric._utils import clr_to_pandas_dtype

from sempy._utils._log import log_xmla, log

from typing import Optional, Union, TYPE_CHECKING, List, Tuple, Dict

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from sempy.fabric._client import WorkspaceClient


class DatasetXmlaClient(BaseDatasetClient):
    """
    Client for access to Power BI data in a specific dataset (database) using an XMLA client.

    Generally, a single instance of the class is needed per dataset (database),
    where it can execute multiple DAX queries.

    In contrast to :class:`PowerBIWorkspace` it wraps a different XMLA client:
    `AdomdDataAdapter <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.adomdclient.adomddataadapter?view=analysisservices-dotnet>`__
    which deals with data access rather than the PowerBI Model (metadata).
    Each client will usually map to a Dataset (Database) i.e. one or more clients can be instantiated
    within each accessed workspace.

    Parameters
    ----------
    workspace : str or WorkspaceClient
        PowerBI workspace name or workspace client that the dataset originates from.
    dataset : str or UUID
        Dataset name or UUID object containing the dataset ID.
    role: str, default=None
        The role name to impersonate to run the DAX query. Cannot be used with `effective_user_name`.
    effective_user_name: str, default=None
        The effective user name to impersonate to run the DAX query. Cannot be used with `role`.
    use_readwrite_connection : bool, default=False
        Whether to connect to the readwrite version of a semantic model with query scale out enabled.
    credential : TokenCredential, default=None
        The credential to acquire the token. If not provided, the default credential will be used.
    """
    def __init__(
            self,
            workspace: Union[str, UUID, "WorkspaceClient", None],
            dataset: Union[str, UUID],
            role: Optional[str] = None,
            effective_user_name: Optional[str] = None,
            use_readwrite_connection: bool = False,
            credential: Optional["TokenCredential"] = None
    ):
        _init_analysis_services()

        if workspace is None:
            workspace = get_workspace_id()

        if role is not None and effective_user_name is not None:
            raise ValueError("Cannot set both role and effective_user_name.")

        BaseDatasetClient.__init__(self, workspace, dataset, credential)

        self.role = role
        self.effective_user_name = effective_user_name
        self.use_readwrite_connection = use_readwrite_connection

        self.adomd_connection: Optional[AdomdConnection] = None

    def _get_connected_dataset_server(self, readonly: bool = True):
        connection_string = self._get_dax_connection_string(readonly)
        tom_server = _create_tom_server(connection_string, self.credential)

        return tom_server

    def _get_dax_connection_string(self, readonly: bool = True) -> str:
        workspace_url = _get_workspace_url(self.resolver.workspace_name)

        if self.use_readwrite_connection:
            # reset readonly to False, as readwrite connection is used
            readonly = False

        return _build_adomd_connection_string(workspace_url, initial_catalog=self.resolver.dataset_name, readonly=readonly,
                                              use_readwrite_connection=self.use_readwrite_connection,
                                              role=self.role, effective_user_name=self.effective_user_name)

    def _evaluate_dax(self, query: str, verbose: int = 0, num_rows: Optional[int] = None, batch_size: int = 100000) -> pd.DataFrame:
        return self._get_DAX(dax_string=query, batch_size=batch_size, verbose=verbose, num_rows=num_rows)

    def _evaluate_measure(
        self,
        measure: Union[str, List[str]],
        groupby_columns: List[Tuple[str, str]],
        filters: Dict[Tuple[str, str], List[str]],
        num_rows: Optional[int] = None,
        batch_size: int = 100000,
        verbose: int = 0,
    ) -> pd.DataFrame:

        # we should always quote table names (e.g. Date/Calendar as table name will fail without quotes)
        groupby_string = ", ".join(f"'{col[0]}'[{col[1]}]" for col in groupby_columns)

        measure_lst = measure if isinstance(measure, list) else [measure]
        measure_string = ", ".join(f'"{m}", CALCULATE([{m}])' for m in measure_lst)

        filter_clauses = []
        for table_col, filter_list in filters.items():
            table_name = table_col[0]
            col_name = table_col[1]
            # DAX requires the "IN" items to use double quotes within braces:
            filter_vals = "{" + ", ".join([f'"{val}"' for val in filter_list]) + "}"
            # Create individual FILTER functions for every filter specified by user (table names always quoted with single quotes)
            # See https://learn.microsoft.com/en-us/dax/filter-function-dax)
            filter_clauses.append(f"FILTER('{table_name}', '{table_name}'[{col_name}] IN {filter_vals})")
        # Final String: FILTER('Table1', 'Table1'[Col1] IN {"X", "Y"}), FILTER('Table2', 'Table2'[Col2] IN {"A"})
        filter_string = ", ".join(filter_clauses)

        summarize_columns = 'SUMMARIZECOLUMNS('
        if len(groupby_string) > 0:
            summarize_columns += f'{groupby_string}, '
        if len(filter_string) > 0:
            summarize_columns += f"{filter_string}, "
        summarize_columns += f"{measure_string})"

        if num_rows:
            dax_string = f"EVALUATE TOPN({num_rows}, {summarize_columns})"
        else:
            dax_string = f"EVALUATE {summarize_columns}"

        if verbose > 0:
            print(f"Executing DAX query: {dax_string}")

        df = self._get_DAX(dax_string=dax_string, verbose=verbose)

        # DAX returns all measures in the form [MeasureName]. To maintain consistency with REST we remove this formatting.
        renamed_measure_cols = {f"[{m}]": m for m in measure_lst}
        df.rename(columns=renamed_measure_cols, inplace=True)

        return df

    def get_adomd_activity_id(self) -> str:
        """
        Get the activity ID of the current AdomdCommand.

        Please only use this inside the AdomdConnection context manager.

        Returns
        -------
        str
            The string value of the AdomdCommand activity ID.
        """
        if self.adomd_connection is None:
            raise ValueError("No active adomd_connection.")
        return self.adomd_connection.adomd_activity_id

    def get_adomd_connection(self) -> AdomdConnection:
        """
        Get python AdomdConnection object

        Returns
        -------
        AdomdConnection
            Python AdomdConnection object.
        """
        if self.adomd_connection is None:
            self.adomd_connection = AdomdConnection(self._get_dax_connection_string(), self.credential)
        return self.adomd_connection

    @log_xmla
    def _get_DAX(self, dax_string: str, batch_size: int = 100000, verbose: int = 0, num_rows: Optional[int] = None) -> pd.DataFrame:
        # = Chapter 1 =
        # At the beginning there was a simple implementation that used the AdomdDataAdapter filling DataTable and
        # directly accessing the DataTable via PythonNet. This was very slow and the team was sad.
        # = Chapter 2 =
        # Then a new age came and a might warrior created a .NET implementation which access the DataTable
        # without PythonNet and wrote a parquet file. The team was happy and the performance was good.
        # Tales are told about 15x to 110x performance improvements.
        # = Chapter 3 =
        # Then the code was rolled out and customers discovered more issues. The team was sad again.
        # On large datasets (>45mio rows) the code failed with a parquet exception.
        # We gather reports about "ArgumentOutOfRangeException: Specified argument was out of the range of valid values. (Parameter 'minimumLength')"
        # To fix the issue, the parquet row groups were split up into smaller chunks.
        # Along the way we also ditched the AdomdDataAdapter & DataTable and directly interfaced with DataReader.
        # This allows us to reduce the memory footprint (previously the whole dataset was loaded into memory - namely the DataTable), then copied again
        # into various Arrays to satisfy the parquet writer and lastly the pandas dataframe.
        # Using the data reader we can bound the memory consumption using the batch size.
        # Additionally reading the data from Adomd and post-processing & writing the parquet file is now interleaved.
        # The test set was ~650MB of snappy compressed parquet, which is 45mio rows and 14 columns.
        # Running on the dev box, the entire code took 70mins to execute. On Fabric it takes 16mins.

        from Microsoft.Fabric.SemanticLink import DAXToParquetWriter
        from Microsoft.AnalysisServices.AdomdClient import AdomdConnectionException
        from System import AggregateException, Guid, InvalidOperationException

        @log
        def dax_to_parquet():
            # Manually build file temp_file_name. Using a simpler tempfile.NamedTemporaryFile breaks on Windows,
            # where file held by python cannot be overriden by C#
            temp_file_name = os.path.join(tempfile.gettempdir(), f"sempy-{uuid4()}.parquet")

            try:
                with self.get_adomd_connection() as adomd_connection:
                    fields = DAXToParquetWriter.Write(
                        dax_string,
                        temp_file_name,
                        batch_size,
                        adomd_connection,
                        verbose,
                        num_rows,
                        Guid(self.get_adomd_activity_id())
                    )
                    df = pd.read_parquet(temp_file_name)
                    return df, fields
            finally:
                try:
                    os.remove(temp_file_name)
                except FileNotFoundError:
                    # File will not be written if exception thrown in DAXToParquet (e.g. error in DAX)
                    pass

        try:
            df, fields = dax_to_parquet()
        except AdomdConnectionException:
            # retry on connection error - examples include "The connection either timed out or was lost." or "The request was routed to the wrong node"
            df, fields = dax_to_parquet()
        except InvalidOperationException as e:
            if e.Message == "The connection is closed.":
                df, fields = dax_to_parquet()
            else:
                raise e
        except AggregateException as e:
            # connection error may be hidden in AggregateException
            adomd_exception_present = any(isinstance(inner_exception, AdomdConnectionException) for inner_exception in e.InnerExceptions)
            if adomd_exception_present:
                df, fields = dax_to_parquet()
            else:
                raise e

        return self._convert_dtypes(df, fields)

    def _execute_xmla(self, xmla_command: str) -> int:
        from Microsoft.AnalysisServices.AdomdClient import AdomdCommand
        from System import Guid

        with self.get_adomd_connection() as adomd_connection:
            command = None
            try:
                command = AdomdCommand(xmla_command, adomd_connection)
                command.ActivityID = Guid(self.get_adomd_activity_id())

                return command.ExecuteNonQuery()
            finally:
                if command is not None:
                    command.Dispose()

    def _clear_analysis_services_cache(self) -> None:
        xmla_command = f"""
            <ClearCache xmlns="http://schemas.microsoft.com/analysisservices/2003/engine">
                <Object>
                    <DatabaseID>{self.resolver.dataset_id}</DatabaseID>
                </Object>
            </ClearCache>
        """
        rows = self._execute_xmla(xmla_command)
        if rows != 1:
            warnings.warn("Failed to clear cache.")

    def _convert_dtypes(self, df: pd.DataFrame, fields) -> pd.DataFrame:
        # Deal with the legacies of pandas null handling. We cannot affect the output type via
        # parquet type/value manipulation, because:
        #
        #  - Parquet.NET uses Nullable C# types for all columns, since all columns are nullable in parquet.
        #  - pd.read_parquet() will output run length encoded nulls as well as explicit Double.NaN into the
        #    same np.NaN.
        #
        # Originally pandas used np.NaN as null, which is a 'float64' that does not fit in 'int' columns:
        #
        #   - pd.read_parquet() "solved" the dilemma by reading all ints into a 'float64' column, as a shortcut
        #     that gets around the fact that in parquet all supported types are nullable.
        #   - pd.read_csv() doesn't have metadata, so it looks at the values to infer the dtypes. If if finds
        #     all non-null ints then it will output an 'int' column. As soon as a single null is encountered
        #     the column will become 'float64'.
        #
        # To try to address these "minor" imperfections, pandas 2.0.0 introduced pd.NA, but it came
        # hand-in-hand with new dtypes: 'Int64', 'Float64' and 'boolean' (pay attention to capitalization).
        # Why they didn't just use python's None (which they handle fine in 'object') is a mystery
        # someone will take to the grave. The new and legacy dtypes work in joins, i.e.  'int' <-> 'Int64',
        # 'float64' <-> 'Float64', but things get dicey across:
        #
        #    - 'int' <->'Float64' works just dandy
        #    - 'float' <->'Int64' will bomb as of pandas 2.0.3
        #
        # Standardizing on the new pd.NA achieves the greatest consistency and avoids join problems, but
        # it comes with the problem in Spark 3.4, which is compatible only with the old np.NaN.
        # We are adding conversion that would satisfy its needs in to_lakehouse_table.
        #
        # We tried to use pd.convert_types() but its conversions are not predictable for the same table:
        # imagine that one query/filter happens to return a float value and another query happens to return
        # just int(s). So you change the query predicate, and your join now starts failing...

        conversion_map = {}
        for f in fields:
            pandas_dtype = clr_to_pandas_dtype(f.ClrType.Name)
            if pandas_dtype:
                conversion_map[f.Name] = pandas_dtype

        if len(conversion_map) > 0:
            return df.astype(conversion_map)
        else:
            return df

    def __repr__(self):
        return f"DatasetXmlaClient('{self.resolver.workspace_name}[{self.resolver.dataset_name}]')"
