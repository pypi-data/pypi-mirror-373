from uuid import UUID
import pandas as pd
import re
from abc import abstractmethod
from collections import defaultdict

from sempy.fabric._dataframe._fabric_dataframe import FabricDataFrame
from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy.fabric._client._fabric_rest_api import _FabricRestAPI
from sempy.fabric.exceptions import DatasetNotFoundException, WorkspaceNotFoundException, FabricHTTPException
from sempy.fabric._metadatakeys import MetadataKeys
from sempy.fabric._utils import dax_escape_table_name, is_valid_uuid, dotnet_to_pandas_date, to_multiplicity

from typing import Any, Optional, Union, List, Dict, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from sempy.fabric._client import WorkspaceClient


class WorkspaceDatasetResolver:
    """
    Resolves workspace and dataset names to their respective IDs and makes sure to avoid unnecessary API calls.
    """
    def __init__(self,
                 workspace: Union[str, UUID, "WorkspaceClient"],
                 dataset: Union[str, UUID],
                 credential: Optional["TokenCredential"] = None):

        self._workspace_input = workspace
        self._dataset_input = dataset
        self._credential = credential

        self._workspace_client = None
        self._powerbi_rest_api = None
        self._fabric_rest_api = None

        self._dataset_name = None
        self._dataset_id = None

    @property
    def workspace_client(self):
        from sempy.fabric._client import WorkspaceClient

        if self._workspace_client is None:
            if isinstance(self._workspace_input, WorkspaceClient):
                self._workspace_client = self._workspace_input
            else:
                self._workspace_client = WorkspaceClient(self._workspace_input)

        return self._workspace_client

    @property
    def powerbi_rest_api(self):
        if self._powerbi_rest_api is None:
            self._powerbi_rest_api = _PBIRestAPI(credential=self._credential)

        return self._powerbi_rest_api

    @property
    def fabric_rest_api(self):
        if self._fabric_rest_api is None:
            self._fabric_rest_api = _FabricRestAPI(credential=self._credential)

        return self._fabric_rest_api

    @property
    def workspace_name_without_explicit_resolution(self) -> Optional[str]:
        if isinstance(self._workspace_input, str) and not is_valid_uuid(self._workspace_input):
            return self._workspace_input

        if self._workspace_client is not None:
            return self._workspace_client.get_workspace_name()

        return None

    @property
    def workspace_name(self) -> str:
        ws = self.workspace_name_without_explicit_resolution

        if ws is None:
            ws = self.workspace_client.get_workspace_name()

        return ws

    @property
    def workspace_id_without_explicit_resolution(self) -> Optional[str]:
        if isinstance(self._workspace_input, UUID):
            return str(self._workspace_input)

        if self._workspace_client is not None:
            return self._workspace_client.get_workspace_id()

        return None

    @property
    def workspace_id(self) -> str:
        id = self.workspace_id_without_explicit_resolution

        if id is None:
            id = self.workspace_client.get_workspace_id()

        return id

    @property
    def dataset_name_without_explicit_resolution(self) -> Optional[str]:
        if isinstance(self._dataset_input, str) and not is_valid_uuid(self._dataset_input):
            return self._dataset_input

        return None

    @property
    def dataset_name(self):
        if self._dataset_name is None:
            self._dataset_name = self.dataset_name_without_explicit_resolution

            if self._dataset_name is None:
                self._resolve_dataset_name_and_id()

        return self._dataset_name

    @property
    def dataset_id(self):
        self._resolve_dataset_name_and_id()

        return self._dataset_id

    def _resolve_dataset_name_and_id(self):
        if self._dataset_name and self._dataset_id:
            return

        if isinstance(self._dataset_input, UUID):
            self._dataset_id = str(self._dataset_input)
            self._dataset_name = self._get_dataset_name_from_id(str(self._dataset_input))
        elif isinstance(self._dataset_input, str):
            # It is possible to use UUID formatted strings as dataset name, so we need to
            # check first if a name exists before testing for UUID format:
            try:
                self._dataset_id = self._get_dataset_id_from_name(self._dataset_input)
                self._dataset_name = self._dataset_input
            except DatasetNotFoundException:
                if is_valid_uuid(self._dataset_input):
                    self._dataset_id = self._dataset_input
                    self._dataset_name = self._get_dataset_name_from_id(self._dataset_input)
                else:
                    raise
        else:
            raise TypeError(f"Unexpected type {type(self._dataset_input)} for \"dataset\"")

    def _get_dataset_name_from_id(self, dataset_id: str) -> str:
        """Get dataset name from ID with PowerBI -> Fabric fallback on 403 errors."""
        try:
            return self.powerbi_rest_api.get_dataset_name_from_id(dataset_id, self.workspace_id, self.workspace_name)
        except FabricHTTPException as e:
            if e.status_code == 403:
                # Fallback to Fabric API
                try:
                    workspace_id = self.workspace_id
                    dataset = self.fabric_rest_api.get_dataset_by_id(workspace_id, dataset_id)
                    return dataset["displayName"]
                except FabricHTTPException as fabric_e:
                    if fabric_e.status_code == 404:
                        raise DatasetNotFoundException(dataset_id, self.workspace_name)
                    raise
            raise

    def _get_dataset_id_from_name(self, dataset_name: str) -> str:
        """Get dataset ID from name with PowerBI -> Fabric fallback on 403 errors."""
        workspace_id = self.workspace_id
        if workspace_id is None:
            raise WorkspaceNotFoundException(self.workspace_name)

        try:
            datasets = self.powerbi_rest_api.get_workspace_datasets(self.workspace_name, str(workspace_id))
            for item in datasets:
                if item["name"] == dataset_name:
                    return item["id"]
            raise DatasetNotFoundException(dataset_name, str(self.workspace_name))
        except FabricHTTPException as e:
            if e.status_code == 403:
                # Fallback to Fabric API
                dataset = self.fabric_rest_api.get_dataset_by_name(workspace_id, dataset_name)
                return dataset["id"]
            raise e


class BaseDatasetClient():
    """
    Client for access to Power BI data in a specific dataset (database).

    Each client will usually map to a Dataset (Database) i.e. one or more clients can be instantiated
    within each accessed workspace.

    Parameters
    ----------
    workspace : str or WorkspaceClient
        PowerBI workspace name or workspace client that the dataset originates from.
    dataset : str or UUID
        Dataset name or UUID object containing the dataset ID.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    def __init__(
            self,
            workspace: Union[str, UUID, "WorkspaceClient"],
            dataset: Union[str, UUID],
            credential: Optional["TokenCredential"] = None
    ):
        self.credential = credential

        self.resolver = WorkspaceDatasetResolver(workspace, dataset, self.credential)

    def evaluate_dax(self, query: str, verbose: int = 0, num_rows: Optional[int] = None) -> FabricDataFrame:
        """
        Retrieve results of DAX query as a FabricDataFrame.

        Parameters
        ----------
        query : str
            DAX query.
        verbose : int, default=0
            Verbosity. 0 means no verbosity.
        num_rows : int, default=-1
            Maximum number of rows to read from the result. -1 means read all rows.

        Returns
        -------
        FabricDataFrame
            FabricDataFrame converted from the results of a DAX query.
        """
        df = self._evaluate_dax(query, verbose, num_rows)
        return FabricDataFrame(df, dataset=self.resolver.dataset_name, workspace=self.resolver.workspace_name)

    @abstractmethod
    def _evaluate_dax(self, query: str, verbose: int = 0, num_rows: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieve results of DAX query as a pandas DataFrame.

        Parameters
        ----------
        query : str
            DAX query.
        verbose : int
            Verbosity. 0 means no verbosity.
        num_rows : int, default=None
            Maximum number of rows to read from the result. -1 means read all rows.

        Returns
        -------
        DataFrame
            Pandas DataFrame converted from the results of a DAX query.
        """
        pass

    def evaluate_measure(
        self,
        measure: Union[str, List[str]],
        groupby_columns: Optional[List[str]] = None,
        filters: Optional[Dict[str, List[str]]] = None,
        fully_qualified_columns: Optional[bool] = None,
        num_rows: Optional[int] = None,
        verbose: int = 0
    ) -> FabricDataFrame:
        """
        Compute PowerBI metric for a given dataset.

        Parameters
        ----------
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
            Whether to output columns in their fully qualified form ("TableName[ColumnName]" for dimensions).
            If None, the fully qualified form will only be used if there is a name conflict between columns from different tables.
        num_rows : int, default=None
            How many rows of the table to return. If None, all rows are returned.
        verbose : int, default=0
            Verbosity. 0 means no verbosity.

        Returns
        -------
        FabricDataFrame
            :class:`~sempy.fabric.FabricDataFrame` holding the computed measure stratified by groupby columns.
        """
        if groupby_columns is None:
            groupby_columns = []
        if not isinstance(groupby_columns, list):
            raise TypeError(f"Unexpected type {type(groupby_columns)} for \"groupby_columns\": not a list")
        parsed_groupby = []
        for g in groupby_columns:
            if not isinstance(g, str):
                raise TypeError(f"Unexpected type {type(g)} for \"groupby_columns\" element: not a str")
            parsed_groupby.append(_parse_fully_qualified_column(g))

        if filters is None:
            filters = {}
        parsed_filters = {}
        for table_col, filter_lst in filters.items():
            if not isinstance(table_col, str):
                raise TypeError(f"Unexpected type {type(table_col)} for \"filters\" key: not a str")
            if not isinstance(filter_lst, list):
                raise TypeError(f"Unexpected type {type(filter_lst)} for \"filters\" value: not a list")
            parsed_filters[_parse_fully_qualified_column(table_col)] = filter_lst

        columns = [g[1] for g in parsed_groupby]
        naming_conflict = len(set(columns)) != len(columns)
        if naming_conflict and fully_qualified_columns is False:
            dupl_columns = [col for col in columns if columns.count(col) > 1]
            raise ValueError(f"Multiple columns with the name(s) '{set(dupl_columns)}' given. Use 'fully_qualified_columns=True' to avoid conflicts.")
        if fully_qualified_columns is None:
            fully_qualified_columns = True if naming_conflict else False
            if verbose > 1:
                print(f"Setting fully_qualified_columns to {fully_qualified_columns}")

        if isinstance(measure, list):
            measure_lst = measure
        elif isinstance(measure, str):
            measure_lst = [measure]
        else:
            raise TypeError(f"Unexpected type {type(measure)} for \"measure\": not a list or str")

        parsed_measures = []
        for m in measure_lst:
            if not isinstance(m, str):
                raise TypeError(f"Unexpected type {type(m)} for \"measure\" element: not a str")
            # strip [] from each measure
            parsed_measures.append(m[1:-1] if m.startswith("[") and m.endswith("]") else m)

        df = self._evaluate_measure(parsed_measures, parsed_groupby, parsed_filters, num_rows, verbose=verbose)
        if not fully_qualified_columns:
            df = self._simplify_col_names(df)
        # FIXME: We should be able to use the FabricDF constructor here and then rename the columns after,
        # but renaming is not currently propagated in metadata.
        # Rather than relying on auto-resolving column names, we rely on the column-table mappings already provided by groupby column tuples.
        return self._add_column_metadata_from_tuples(df, parsed_groupby)

    @abstractmethod
    def _evaluate_measure(
        self,
        measure: Union[str, List[str]],
        groupby_columns: List[Tuple[str, str]],
        filters: Dict[Tuple[str, str], List[str]],
        num_rows: Optional[int] = None,
        batch_size: int = 100000,
        verbose: int = 0
    ) -> pd.DataFrame:
        pass

    def read_table(
        self,
        table_name: str,
        fully_qualified_columns: bool = False,
        num_rows: Optional[int] = None,
        multiindex_hierarchies: bool = False,
        exclude_internal: bool = True,
        verbose: int = 0
    ) -> FabricDataFrame:
        """
        Read specified PBI Dataset tables into FabricDataFrames with populated metadata.

        Parameters
        ----------
        table_name : str
            Name of table from dataset.
        fully_qualified_columns : bool, default=False
            Whether or not to represent columns in their fully qualified form (TableName[ColumnName]).
        num_rows : int, default=None
            How many rows of the table to return. If None, all rows are returned.
        multiindex_hierarchies : bool, default=False
            Whether or not to convert existing `PowerBI Hierarchies <https://learn.microsoft.com/en-us/power-bi/create-reports/service-metrics-get-started-hierarchies>`_
            to pandas MultiIndex.
        exclude_internal : bool, default=True
            Whether internal PowerBI columns should be excluded during the load operation.
        verbose : int
            Verbosity. 0 means no verbosity.

        Returns
        -------
        FabricDataFrame
            DataFrame with metadata from the PBI model.
        """
        database = self.resolver.workspace_client.get_dataset(self.resolver.dataset_name)
        for table in database.Model.Tables:
            if table.Name == table_name:
                pandas_df = self._get_pandas_table(table.Name, num_rows, verbose)

                if not fully_qualified_columns:
                    pandas_df = self._simplify_col_names(pandas_df)

                meta_df = self._populate_table_meta(pandas_df, table, fully_qualified_columns, exclude_internal)
                if database.Model.Relationships is not None:
                    for relationship in database.Model.Relationships:
                        if relationship.FromTable.Name == table.Name:
                            self._populate_relationship_meta(relationship, meta_df, exclude_internal)
                if multiindex_hierarchies:
                    meta_df = self._convert_hierarchies(meta_df, table, fully_qualified_columns)
                return meta_df

        raise ValueError(f"'{table_name}' is not a valid table in Dataset '{self.resolver.dataset_name}'")

    def resolve_metadata(self, columns: pd.Index, verbose: int = 0) -> Dict[str, Any]:
        """
        Resolve column names to their Power BI metadata.

        Parameters
        ----------
        columns : list of str
            List of column names to resolve. Column names can be in any of the following formats:
            - Column name only: "Column Name"
            - Unquoted table name + column name (if no spaces in table name): "TableName[Column Name]"
            - Quoted table name + column name: "'Table Name'[Column Name]"
        verbose : int
            Verbosity. 0 means no verbosity.

        Returns
        -------
        Dict of str
            Dictionary containing mapping of column name to its metadata.
        """
        database = self.resolver.workspace_client.get_dataset(self.resolver.dataset_name)

        column_map = defaultdict(lambda: [])
        for table in database.Model.Tables:
            for column in table.Columns:
                column_data = self._get_column_data(table, column)

                # Any syntax for column names valid for DAX is valid here
                # https://learn.microsoft.com/en-us/dax/dax-syntax-reference

                # column name only
                column_map[column.Name].append(column_data)

                # quoted column name
                column_map[f"[{column.Name}]"].append(column_data)

                # unquoted table name (if no spaces in table name)
                if ' ' not in table.Name:
                    column_map[f"{table.Name}[{column.Name}]"].append(column_data)

                # quoted table name
                column_map[f"'{table.Name}'[{column.Name}]"].append(column_data)

        column_metadata = {}
        for column in columns:
            column_data_list = column_map[column]

            num_column_matches = len(column_data_list)

            if num_column_matches == 1:
                if verbose > 0:
                    print(f"Column '{column}' matched to '{column_data_list[0]}'")

                column_metadata[column] = column_data_list[0]
            elif num_column_matches == 0:
                if verbose > 0:
                    print(f"Column '{column}' not found in dataset '{self.resolver.dataset_name}'")
            else:
                if verbose > 0:
                    print(f"Ambiguous column name '{column}' found in dataset '{self.resolver.dataset_name}': '{column_data_list}'")

        return column_metadata

    def _get_pandas_table(self, table_name, num_rows, verbose):
        if num_rows is None:
            dax_query = f"EVALUATE '{dax_escape_table_name(table_name)}'"
        else:
            dax_query = f"EVALUATE TOPN({num_rows}, '{dax_escape_table_name(table_name)}')"

        df = self._evaluate_dax(dax_query, verbose)

        return df

    def _convert_hierarchies(self, df, table, fully_qualified_columns: bool) -> FabricDataFrame:
        num_hierarchies = len(table.Hierarchies)
        if num_hierarchies > 1:
            raise ValueError(f"Table '{table.Name}' contains {num_hierarchies} hierarchies. Cannot convert multiple hierarchies to MultiIndex.")

        for hierarchy in table.Hierarchies:
            levels = []
            for level in hierarchy.Levels:
                level_name = level.Column.Name if not fully_qualified_columns else f"{table.Name}[{level.Column.Name}]"
                levels.append(level_name)
            df = df.set_index(levels)

        return df

    def _populate_table_meta(self, df, table, fully_qualified_columns: bool, exclude_internal: bool) -> FabricDataFrame:
        # convert TOM table to FabricDataFrame
        table_name = table.Name
        meta_df = FabricDataFrame(df)
        meta_df.column_metadata = {}

        # populate standard column data
        for column in table.Columns:
            column_name = column.Name if not fully_qualified_columns else f"{table_name}[{column.Name}]"
            if exclude_internal and column.Name.startswith("RowNumber"):
                continue

            column_data_type = column.DataType.ToString()
            if column_data_type in ['DateTime', 'Time', 'Date']:
                meta_df[column_name] = pd.to_datetime(df[column_name])
            elif column_data_type == 'String':
                meta_df[column_name] = df[column_name].astype('string')
            elif column_data_type == 'Int64':
                meta_df[column_name] = df[column_name].astype('Int64')
            elif column_data_type in ['Decimal', 'Double']:
                meta_df[column_name] = df[column_name].astype('Float64')
            elif column_data_type == 'Boolean':
                meta_df[column_name] = df[column_name].astype('boolean')

            column_data = self._get_column_data(table, column)
            meta_df.column_metadata[column_name] = column_data

        return meta_df

    def _get_column_data(self, table, column):
        from Microsoft.AnalysisServices.Tabular import CompatibilityViolationException

        column_data = {
            # TODO: should we put these into an enum?
            MetadataKeys.TABLE: table.Name,
            MetadataKeys.COLUMN: column.Name
        }

        # table level
        # make sure we don't do service calls to resolve the metadata
        dataset_name = self.resolver.dataset_name_without_explicit_resolution
        workspace_id = self.resolver.workspace_id_without_explicit_resolution
        workspace_name = self.resolver.workspace_name_without_explicit_resolution

        if dataset_name:
            column_data[MetadataKeys.DATASET] = dataset_name
        if workspace_id:
            column_data[MetadataKeys.WORKSPACE_ID] = workspace_id
        if workspace_name:
            column_data[MetadataKeys.WORKSPACE_NAME] = workspace_name

        if table.Annotations:
            # Excluding keys that are present in all tables or are not valuable to the user to reduce clutter. Ex:
            # {'LinkedQueryName': 'Sales'}
            table_annotations = self._extract_annotations(table, exclude_keys=["LinkedQueryName"])
            if len(table_annotations) > 0:
                column_data[MetadataKeys.TABLE_ANNOTATIONS] = table_annotations

        # column level
        if column.Alignment:
            # The possible values are Default (1), Left (2), Right (3), Center (4).
            # needed for formatting
            column_data[MetadataKeys.ALIGNMENT] = str(column.Alignment)
        if column.Annotations:
            # Excluding keys that are present in all tables or not valuable to the user to reduce clutter. Ex:
            # {'SummarizationSetBy': 'Automatic'}
            # {'Format': '<Format Format="General" />'}
            # {'DataTypeAtRefresh': 'Int64#####not a type'}
            col_annotations = self._extract_annotations(column, exclude_keys=["SummarizationSetBy", "Format", "DataTypeAtRefresh"])
            if len(col_annotations) > 0:
                column_data[MetadataKeys.COLUMN_ANNOTATIONS] = col_annotations
        if column.DataCategory:
            column_data[MetadataKeys.DATA_CATEGORY] = column.DataCategory
        if column.DataType:
            column_data[MetadataKeys.DATA_TYPE] = column.DataType.ToString()
        if column.Description:
            column_data[MetadataKeys.DESCRIPTION] = column.Description
        if column.ErrorMessage:
            column_data[MetadataKeys.ERROR_MESSAGE] = column.ErrorMessage
        try:
            if column.FormatString:
                column_data[MetadataKeys.FORMAT_STRING] = column.FormatString
        except CompatibilityViolationException:
            # computation of compatibility level can take excessive time
            pass
        if column.IsHidden:
            column_data[MetadataKeys.IS_HIDDEN] = column.IsHidden
        if column.IsKey:
            column_data[MetadataKeys.IS_KEY] = column.IsKey
        if column.IsNullable:
            column_data[MetadataKeys.IS_NULLABLE] = column.IsNullable
        if column.IsRemoved:
            column_data[MetadataKeys.IS_REMOVED] = column.IsRemoved
        if column.IsUnique:
            column_data[MetadataKeys.IS_UNIQUE] = column.IsUnique
        if column.LineageTag:
            column_data[MetadataKeys.LINEAGE_TAG] = column.LineageTag
        if column.ModifiedTime:
            column_data[MetadataKeys.MODIFIED_TIME] = dotnet_to_pandas_date(column.ModifiedTime)
        if column.RefreshedTime:
            column_data[MetadataKeys.REFRESHED_TIME] = dotnet_to_pandas_date(column.RefreshedTime)
        if column.SortByColumn:
            column_data[MetadataKeys.SORT_BY_COLUMN] = column.SortByColumn.Name
        if column.SourceLineageTag:
            column_data[MetadataKeys.SOURCE_LINEAGE_TAG] = column.SourceLineageTag
        if column.SummarizeBy:
            column_data[MetadataKeys.SUMMARIZE_BY] = column.SummarizeBy.ToString()

        return column_data

    def _extract_annotations(self, tom_obj, exclude_keys: List[str]) -> Dict[str, str]:
        annotations = {}
        for annotation in tom_obj.Annotations:
            # keys starting with PBI_ appear to be internal use keys
            if annotation.Name not in exclude_keys and not annotation.Name.startswith("PBI_"):
                annotations[annotation.Name] = annotation.Value
        return annotations

    def _populate_relationship_meta(self, relationship, from_dataframe: FabricDataFrame, exclude_internal: bool) -> None:
        # Populate a single relationship in the given table's metadata
        to_table = relationship.ToTable.Name
        to_column = relationship.ToColumn.Name
        from_column = relationship.FromColumn.Name

        if self._show_relationship(relationship, exclude_internal):
            # ignore relationships for which we don't have columns
            col_meta = from_dataframe.column_metadata.get(from_column, None)        # type: ignore

            if col_meta is not None:
                col_meta[MetadataKeys.RELATIONSHIP] = {
                    "to_table": to_table,
                    "to_column": to_column,
                    "multiplicity": to_multiplicity(relationship)
                }

    def _add_column_metadata_from_tuples(self, df: Union[pd.DataFrame, FabricDataFrame], column_tuples: List[Tuple[str, str]]) -> FabricDataFrame:
        database = self.resolver.workspace_client.get_dataset(self.resolver.dataset_name)
        tables = {table.Name: table for table in database.Model.Tables}

        if isinstance(df, FabricDataFrame):
            meta_df = df
        else:
            meta_df = FabricDataFrame(df)

        if meta_df.column_metadata is None:
            meta_df.column_metadata = {}

        for table_name, col_name in column_tuples:
            table_tom = tables[table_name]
            for column in table_tom.Columns:
                if column.Name == col_name:
                    meta_df.column_metadata[col_name] = self._get_column_data(tables[table_name], column)

        return meta_df

    def _simplify_col_names(self, df):
        col_names = []
        for col in df.columns:
            match = re.match(r"^.*\[(.*)\]$", col)
            if match:
                col_names.append(match.group(1))
            else:
                col_names.append(col)
        df.columns = col_names
        return df

    def __repr__(self):
        return f"PowerBIClient('{self.resolver.workspace_name}[{self.resolver.dataset_name}]')"

    def _show_relationship(self, relationship, exclude_internal):
        if exclude_internal:
            if self.resolver.workspace_client._is_internal(relationship.FromTable) or self.resolver.workspace_client._is_internal(relationship.ToTable):
                return False
        return True


def _parse_column_reference(column_spec: str) -> Tuple[Optional[str], str]:
    # Simplistic parsing that does not yet take into account escaping of
    # square brackets and assumes that single quotes have to be present on both sides.
    # PBI client allows for these characters to be used in Table/Column names, but
    # we would need to investigate repercussions in downstream components, before
    # we decide on how to handle escaping.
    table_name = None
    column_name = column_spec
    if column_spec.endswith(']'):
        column_idx = column_spec.find('[')
        if column_idx >= 0:
            column_name = column_spec[column_idx + 1:-1]
            table_name = column_spec[:column_idx]
            if table_name.startswith("'") and table_name.endswith("'"):
                table_name = table_name[1:-1]

    return table_name, column_name


def _parse_fully_qualified_column(column_spec: str) -> Tuple[str, str]:
    # This method enforces that table name is specified, which is a requirement for
    # DAX/REST calls in groupby and filters.
    table_name, column_name = _parse_column_reference(column_spec)

    if table_name is None or table_name == "":
        raise ValueError(f"Cannot parse table name from '{column_spec}'")

    return table_name, column_name
