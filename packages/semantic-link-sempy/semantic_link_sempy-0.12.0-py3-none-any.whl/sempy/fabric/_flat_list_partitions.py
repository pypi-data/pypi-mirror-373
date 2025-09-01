import pandas as pd
from uuid import UUID

from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._flat import evaluate_dax
from sempy.fabric._utils import collection_to_dataframe, dotnet_to_pandas_date
from sempy._utils._log import log

from typing import List, Optional, Union


@log
def list_partitions(
    dataset: Union[str, UUID],
    table: Optional[str] = None,
    extended: Optional[bool] = False,
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None
) -> pd.DataFrame:
    """
    List all partitions in a dataset.

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
        Additional XMLA `partition <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.partition?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
        Use Parent to navigate to the parent level.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing the partitions.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset)

    # must happen after workspace client is retrieved so .NET is loaded
    import Microsoft.AnalysisServices.Tabular as TOM

    def query(table, partition):
        if partition.SourceType in [TOM.PartitionSourceType.M, TOM.PartitionSourceType.Calculated]:
            # https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.mpartitionsource?view=analysisservices-dotnet
            # https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.calculatedpartitionsource?view=analysisservices-dotnet
            return partition.Source.Expression
        elif partition.SourceType == TOM.PartitionSourceType.Query:
            # https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.querypartitionsource?view=analysisservices-dotnet
            return partition.Source.Query
        elif partition.SourceType == TOM.PartitionSourceType.Entity:
            # https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.entitypartitionsource?view=analysisservices-dotnet
            return partition.Source.EntityName
        elif partition.SourceType == TOM.PartitionSourceType.PolicyRange:
            return table.RefreshPolicy.SourceExpression
        else:
            # CalculationGroup, Inferred, ...
            return None

    def query_group(partition):
        if partition.QueryGroup is None:
            return None
        else:
            return partition.QueryGroup.Name

    # see https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.partition?view=analysisservices-dotnet
    # (table, partition)
    extraction_def = [
        ("Table Name",     lambda r: r[0].Name,                                 "str"),   # noqa: E272
        ("Partition Name", lambda r: r[1].Name,                                 "str"),   # noqa: E272
        ("Description",    lambda r: r[1].Description,                          "str"),   # noqa: E272
        ("Error Message",  lambda r: r[1].ErrorMessage,                         "str"),   # noqa: E272
        ("Mode",           lambda r: r[1].Mode.ToString(),                      "str"),   # noqa: E272
        ("Data View",      lambda r: r[1].DataView.ToString(),                  "str"),   # noqa: E272
        ("Source Type",    lambda r: r[1].SourceType.ToString(),                "str"),   # noqa: E272
        ("Query",          lambda r: query(r[0], r[1]),                         "str"),   # noqa: E272
        ("Query Group",    lambda r: query_group(r[1]),                         "str"),   # noqa: E272
        ("Refreshed Time", lambda r: dotnet_to_pandas_date(r[1].RefreshedTime), "datetime64[ns]"),  # noqa: E272
        ("Modified Time",  lambda r: dotnet_to_pandas_date(r[1].ModifiedTime),  "datetime64[ns]"),  # noqa: E272
    ]

    collection = [
        (table_obj, partition)
        for table_obj in database.Model.Tables
        # filter by table name
        if table is None or table_obj.Name == table
        for partition in table_obj.Partitions
    ]

    df = collection_to_dataframe(collection, extraction_def, additional_xmla_properties)

    if extended:

        df_table = evaluate_dax(dataset,
                                """
                                SELECT
                                    [ID]   AS [SemPyTableID],
                                    [Name] AS [SemPyTableName]
                                FROM
                                    $SYSTEM.TMSCHEMA_TABLES
                                """,
                                workspace=workspace)

        df_parts = evaluate_dax(dataset,
                                """
                                SELECT
                                    [ID]      AS [SemPyPartitionID],
                                    [TableID] AS [SemPyTableID],
                                    [Name] AS [SemPyPartitionName]
                                FROM
                                    $SYSTEM.TMSCHEMA_PARTITIONS
                                """,
                                workspace=workspace)

        df_table_parts = pd.merge(df_parts, df_table, on='SemPyTableID')

        # Shows Record Count, Segment Count, Records per Segment
        df_stats = evaluate_dax(dataset,
                                """
                                SELECT
                                    [PartitionStorageID]           AS [SemPyPartitionStorageID],
                                    [RecordCount]                  AS [SemPyRecordCount],
                                    [SegmentCount]                 AS [SemPySegmentCount],
                                    [RecordCount] / [SegmentCount] AS [SemPyRecordsPerSegment]
                                FROM
                                    $SYSTEM.TMSCHEMA_SEGMENT_MAP_STORAGES
                                """,
                                workspace=workspace)

        # Used to map Partition Storage IDs to Partition IDs
        df_id_map = evaluate_dax(dataset,
                                 """
                                 SELECT
                                     [ID]          AS [SemPyPartitionStorageID],
                                     [PartitionID] AS [SemPyPartitionID]
                                 FROM
                                     $SYSTEM.TMSCHEMA_PARTITION_STORAGES
                                 """,
                                 workspace=workspace)

        df_stats = pd.merge(df_stats, df_id_map, on='SemPyPartitionStorageID', how='left')
        df_stats = pd.merge(df_stats, df_table_parts, on='SemPyPartitionID', how='left')

        df = pd.merge(df, df_stats, how='left', left_on=["Table Name", "Partition Name"], right_on=["SemPyTableName", "SemPyPartitionName"])

        df.drop(['SemPyPartitionStorageID', 'SemPyPartitionID', 'SemPyTableID', 'SemPyPartitionName', 'SemPyTableName'], axis=1, inplace=True)
        df.rename({'SemPyRecordCount': 'Record Count', 'SemPySegmentCount': 'Segment Count', 'SemPyRecordsPerSegment': 'Records per Segment'}, axis=1, inplace=True)

    return df
