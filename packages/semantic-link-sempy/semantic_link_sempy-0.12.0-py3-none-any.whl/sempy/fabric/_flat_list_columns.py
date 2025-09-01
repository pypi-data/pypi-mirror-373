import pandas as pd
from uuid import UUID

from sempy.fabric._flat import evaluate_dax
from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._client._utils import _init_analysis_services
from sempy.fabric._utils import dotnet_to_pandas_date, collection_to_dataframe
from sempy._utils._log import log

from typing import List, Optional, Union


@log
def list_columns(
    dataset: Union[str, UUID],
    table: Optional[str] = None,
    extended: Optional[bool] = False,
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None
) -> pd.DataFrame:
    """
    List all columns for all tables in a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    table : str, default=None
        Name of the table.
    extended : bool, default=False
        Fetches extended column information.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `column <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.column?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing the columns.
    """
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM

    workspace_client = _get_or_create_workspace_client(workspace)
    tabular_database = workspace_client.get_dataset(dataset)

    def source(column) -> Optional[str]:
        if column.Type == TOM.ColumnType.Calculated:
            return column.Expression
        elif column.Type in [TOM.ColumnType.Data, TOM.ColumnType.CalculatedTableColumn]:
            return column.SourceColumn

        return None

    def sort_by_column(column) -> Optional[str]:
        if column.SortByColumn is None:
            return None
        else:
            return column.SortByColumn.Name

    def alternate_of_base_column(column) -> Optional[str]:
        if column.Name.startswith("RowNumber-") or column.AlternateOf is None or column.AlternateOf.BaseColumn is None:
            return None

        return f"'{column.AlternateOf.BaseColumn.Table.Name}'[{column.AlternateOf.BaseColumn.Name}]"

    def alternate_of_base_table(column) -> Optional[str]:
        if column.Name.startswith("RowNumber-") or column.AlternateOf is None or column.AlternateOf.BaseTable is None:
            return None

        return column.AlternateOf.BaseTable.Name

    # see https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.column?view=analysisservices-dotnet
    # see https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.calculatedcolumn?view=analysisservices-dotnet
    # see https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.datacolumn?view=analysisservices-dotnet
    # table, column
    extraction_def = [
        ("Table Name",               lambda r: r[0].Name,                      "str"),   # noqa: E272
        ("Column Name",              lambda r: r[1].Name,                      "str"),   # noqa: E272
        ("Description",              lambda r: r[1].Description,               "str"),   # noqa: E272
        ("Type",                     lambda r: r[1].Type.ToString(),           "str"),   # noqa: E272
        ("Data Type",                lambda r: r[1].DataType.ToString(),       "str"),   # noqa: E272
        ("Hidden",                   lambda r: r[1].IsHidden,                  "bool"),  # noqa: E272
        ("Format String",            lambda r: r[1].FormatString,              "str"),   # noqa: E272
        ("Source",                   lambda r: source(r[1]),                   "str"),   # noqa: E272
        ("Data Category",            lambda r: r[1].DataCategory,              "str"),   # noqa: E272
        ("Display Folder",           lambda r: r[1].DisplayFolder,             "str"),   # noqa: E272
        ("Key",                      lambda r: r[1].IsKey,                     "bool"),  # noqa: E272
        ("Unique",                   lambda r: r[1].IsUnique,                  "bool"),  # noqa: E272
        ("Sort By Column",           lambda r: sort_by_column(r[1]),           "str"),   # noqa: E272
        ("Summarize By",             lambda r: r[1].SummarizeBy.ToString(),    "str"),   # noqa: E272
        ("Is Available in MDX",      lambda r: r[1].IsAvailableInMDX,          "bool"),  # noqa: E272
        ("Encoding Hint",            lambda r: r[1].EncodingHint.ToString(),   "str"),   # noqa: E272
        ("State",                    lambda r: r[1].State.ToString(),          "str"),   # noqa: E272
        ("Error Message",            lambda r: r[1].ErrorMessage,              "str"),   # noqa: E272
        ("Alternate Of Base Column", lambda r: alternate_of_base_column(r[1]), "str"),   # noqa: E272
        ("Alternate Of Base Table",  lambda r: alternate_of_base_table(r[1]),  "str"),   # noqa: E272
        ("Modified Time",            lambda r: dotnet_to_pandas_date(r[1].ModifiedTime), "datetime64[ns]"),  # noqa: E272
    ]

    collection = [
        (table_obj, column)
        for table_obj in tabular_database.Model.Tables
        # filter internals
        if extended or not workspace_client._is_internal(table_obj)
        # filter by table name
        if table is None or table_obj.Name == table
        for column in table_obj.Columns
        # filter auto-generated RowNumber
        if extended or not column.Name.startswith("RowNumber")
    ]

    df = collection_to_dataframe(collection, extraction_def, additional_xmla_properties)

    if extended:
        # remember original column list
        df_columns = df.columns.values.tolist()

        # simplify join with additional information
        df.set_index(["Table Name", "Column Name"], inplace=True)

        # table id/column id -> table name/column name
        df_table_column = _fetch_table_column(dataset, workspace)

        # Column cardinality
        series_column_cardinality = _fetch_column_cardinality(df_table_column, dataset, workspace)
        df = df.join(series_column_cardinality, how="left")

        df_column_segments = _fetch_column_segments(df_table_column, dataset, workspace)

        # Column hierarchy size
        series_hierarchy_size = _fetch_column_hierarchy_size(df_column_segments)
        df = df.join(series_hierarchy_size, how="left")

        # Dictionary info
        df_dict = _fetch_dictionary_info(dataset, workspace)
        df = df.join(df_dict, how="left")

        # Data size
        series_data_size = _fetch_column_data_size(df_table_column, dataset, workspace)
        df = df.join(series_data_size, how="left")

        # compute total size
        # pandas bug: https://github.com/pandas-dev/pandas/issues/48480 inplace triggers future warning
        df = df.fillna({'Data Size': 0, 'Dictionary Size': 0, 'Hierarchy Size': 0})
        df['Total Size'] = df['Data Size'] + df['Dictionary Size'] + df['Hierarchy Size']

        # restore table name/column name
        df = df.reset_index()

        df = df[df_columns + [
            'Column Cardinality', 'Total Size', 'Data Size', 'Dictionary Size',
            'Hierarchy Size', 'Encoding', 'Is Resident', 'Temperature', 'Last Accessed'
        ]]

    return df


def _fetch_table_column(dataset: Union[str, UUID], workspace: Optional[Union[str, UUID]] = None) -> pd.DataFrame:
    # Get Table ID + Name, Column ID + ID
    df_col = evaluate_dax(dataset,
                          """
                          SELECT
                            [ID]           AS [SemPyColumnID],
                            [TableID]      AS [SemPyTableID],
                            [ExplicitName] AS [SemPyColumnName]
                          FROM
                            $SYSTEM.TMSCHEMA_COLUMNS
                          """,
                          workspace=workspace)

    df_table = evaluate_dax(dataset,
                            """
                            SELECT
                                [ID]   AS [SemPyTableID],
                                [Name] AS [SemPyTableName]
                            FROM
                                $SYSTEM.TMSCHEMA_TABLES
                            """,
                            workspace=workspace)

    df_table = df_table.merge(df_col, on="SemPyTableID")

    # rename columns (strip SemPy prefix)
    df_table = df_table.rename({'SemPyTableName': 'Table Name', 'SemPyColumnName': 'Column Name'}, axis='columns')

    # change type of columns SemPyTableID and SemPyColumnID to Int64
    df_table = df_table.astype({'SemPyTableID': 'Int64', 'SemPyColumnID': 'Int64'})

    return df_table


def _fetch_column_cardinality(df_table_column: pd.DataFrame, dataset: Union[str, UUID], workspace: Optional[Union[str, UUID]] = None) -> pd.Series:
    df = evaluate_dax(dataset,
                      """
                      SELECT
                          [ColumnID]                  AS [SemPyColumnID],
                          [Statistics_DistinctStates] AS [SemPyStatistics_DistinctStates]
                      FROM
                        $SYSTEM.TMSCHEMA_COLUMN_STORAGES
                      """,
                      workspace=workspace)

    df = df.rename({"SemPyStatistics_DistinctStates": "Column Cardinality"}, axis="columns")

    df['Column Cardinality'] = df['Column Cardinality'].astype('Int64')

    df = (df_table_column.merge(df, on="SemPyColumnID"))

    return df.set_index(['Table Name', 'Column Name'])["Column Cardinality"]


def _fetch_column_segments(df_table_column: pd.DataFrame, dataset: Union[str, UUID], workspace: Optional[Union[str, UUID]] = None) -> pd.DataFrame:
    df = evaluate_dax(dataset,
                      """
                      SELECT
                          [DIMENSION_NAME] as [SemPyDimensionName],
                          [TABLE_ID]       as [SemPyTableExpr],
                          [USED_SIZE]      as [SemPyUsedSize],
                          [SEGMENT_NUMBER] as [SemPySegmentNumber]
                      FROM
                        $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMN_SEGMENTS
                      """,
                      workspace=workspace)

    # extract table and column id
    # example format: H$DimDate (17)$DateKey (53)
    df["SemPyTableID"] = df["SemPyTableExpr"].str.extract(r"\((\d+)\)\$").astype('Int64')
    df["SemPyColumnID"] = df["SemPyTableExpr"].str.extract(r"\((\d+)\)$").astype('Int64')
    df["SemPyTableType"] = df["SemPyTableExpr"].str.extract(r"^([A-Z])\$")

    return df_table_column.merge(df, on=["SemPyTableID", "SemPyColumnID"])


def _fetch_column_hierarchy_size(df_column_segments: pd.DataFrame) -> pd.Series:
    df_column_segments = df_column_segments.copy()
    df_column_segments = df_column_segments.rename({"SemPyUsedSize": "Hierarchy Size"}, axis="columns")

    df_column_segments = df_column_segments[df_column_segments["SemPyTableType"] == "H"]

    return df_column_segments.groupby(["Table Name", "Column Name"])["Hierarchy Size"].sum().astype('Int64')


def _fetch_column_data_size(df_table_column: pd.DataFrame, dataset: Union[str, UUID], workspace: Optional[Union[str, UUID]] = None) -> pd.Series:
    df = evaluate_dax(dataset,
                      """
                      SELECT
                          [TABLE_ID]       as [SemPyTableExpr],
                          [COLUMN_ID]      as [SemPyColumnExpr],
                          [USED_SIZE]      as [SemPyUsedSize]
                      FROM
                        $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMN_SEGMENTS
                      """,
                      workspace=workspace)

    # extract table and column id
    # example format: H$DimDate (17)$DateKey (53)
    df["SemPyTableID"] = df["SemPyTableExpr"].str.extract(r"\((\d+)\)\$").astype('Int64')
    df["SemPyColumnID"] = df["SemPyColumnExpr"].str.extract(r"\((\d+)\)$").astype('Int64')
    df["SemPyTableType"] = df["SemPyTableExpr"].str.extract(r"^([A-Z])\$")

    df_column_segments = df_table_column.merge(df, on="SemPyColumnID")

    df_column_segments = df_column_segments.rename({"SemPyUsedSize": "Data Size"}, axis="columns")

    # filter by SemPyTableType to be neither H, R nor U
    df_column_segments = df_column_segments[~df_column_segments["SemPyTableType"].isin(["H", "R", "U"])]

    return df_column_segments.groupby(["Table Name", "Column Name"])["Data Size"].sum().astype('Int64')


def _fetch_dictionary_info(dataset: Union[str, UUID], workspace: Optional[Union[str, UUID]] = None) -> pd.DataFrame:
    # Used to calculate Dictionary Size, Temperature, Is Resident, Last Accessed
    df = evaluate_dax(dataset,
                      """
                      SELECT
                          [DIMENSION_NAME]            AS [SemPyTableName],
                          [ATTRIBUTE_NAME]            AS [SemPyColumnName],
                          [DICTIONARY_SIZE]           AS [SemPyDictionarySize],
                          [DICTIONARY_ISRESIDENT]     AS [SemPyDictionaryIsResident],
                          [DICTIONARY_TEMPERATURE]    AS [SemPyDictionaryTemperature],
                          [DICTIONARY_LAST_ACCESSED]  AS [SemPyDictionaryLastAccessed],
                          [ISROWNUMBER]               AS [SemPyRowNumber],
                          [COLUMN_ENCODING]           AS [SemPyColumnEncoding]
                      FROM
                        $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMNS
                      WHERE
                        [COLUMN_TYPE] = 'BASIC_DATA'
                      """,
                      workspace=workspace)

    df = df[df["SemPyRowNumber"] == 0].drop("SemPyRowNumber", axis="columns")

    df = df.rename({
            "SemPyTableName":              "Table Name",
            "SemPyColumnName":             "Column Name",
            "SemPyDictionarySize":         "Dictionary Size",
            "SemPyDictionaryIsResident":   "Is Resident",
            "SemPyDictionaryTemperature":  "Temperature",
            "SemPyDictionaryLastAccessed": "Last Accessed",
            "SemPyColumnEncoding":         "Encoding"
        },
        axis="columns")

    df["Dictionary Size"] = df["Dictionary Size"].astype('Int64')

    df["Encoding"] = df["Encoding"].map({1: "Hash", 2: "Value"})

    return df.set_index(["Table Name", "Column Name"])
