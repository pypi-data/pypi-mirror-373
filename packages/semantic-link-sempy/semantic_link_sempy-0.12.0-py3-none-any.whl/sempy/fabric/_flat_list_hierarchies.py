import pandas as pd
from uuid import UUID

from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._flat import evaluate_dax
from sempy.fabric._utils import collection_to_dataframe
from sempy._utils._log import log

from typing import List, Optional, Union


@log
def list_hierarchies(
    dataset: Union[str, UUID],
    extended: Optional[bool] = False,
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None
) -> pd.DataFrame:
    """
    List hierarchies in a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    extended : bool, default=False
        Fetches extended column information.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `level <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.level?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
        Use Parent to navigate to the parent level.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing the hierachies and their attributes.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset).Model

    # see https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.level?view=analysisservices-dotnet
    # (table, hierarchy, level)
    extraction_def = [
        ("Table Name",            lambda r: r[0].Name,        "str"),    # noqa: E272
        ("Column Name",           lambda r: r[2].Column.Name, "str"),    # noqa: E272
        ("Hierarchy Name",        lambda r: r[1].Name,        "str"),    # noqa: E272
        ("Hierarchy Description", lambda r: r[1].Description, "str"),    # noqa: E272
        ("Hierarchy Hidden",      lambda r: r[1].IsHidden,    "bool"),   # noqa: E272
        ("Hierarchy State",       lambda r: r[1].State,       "str"),    # noqa: E272
        ("Level Name",            lambda r: r[2].Name,        "str"),    # noqa: E272
        ("Level Description",     lambda r: r[2].Description, "str"),    # noqa: E272
        ("Level Ordinal",         lambda r: r[2].Ordinal,     "Int64"),  # noqa: E272
    ]

    collection = [
        (table, hierarchy, level)
        for table in database.Model.Tables
        for hierarchy in table.Hierarchies
        for level in hierarchy.Levels
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

        df_hierarchy = evaluate_dax(dataset,
                                    """
                                    SELECT
                                        [ID]      AS [SemPyHierarchyID],
                                        [TableID] AS [SemPyTableID],
                                        [Name]    AS [SemPyHierarchyName]
                                    FROM
                                        $SYSTEM.TMSCHEMA_HIERARCHIES
                                    """,
                                    workspace=workspace)

        df_table_hierarchy = pd.merge(df_table, df_hierarchy, on='SemPyTableID')

        df_stats = evaluate_dax(dataset,
                                """
                                SELECT
                                    [TABLE_ID]  AS [SemPyTableID],
                                    [USED_SIZE] AS [SemPyUsedSize]
                                FROM
                                    $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMN_SEGMENTS
                                """,
                                workspace=workspace)

        df_stats = df_stats[df_stats['SemPyTableID'].str.startswith("U$")]
        df_stats['SemPyHierarchyID'] = df_stats['SemPyTableID'].str.extract(r'\((\d+)\)$').astype('Int64')

        df_stats = pd.merge(df_stats, df_table_hierarchy, on='SemPyHierarchyID')

        df_stats = df_stats.groupby(['SemPyTableName', 'SemPyHierarchyName'], as_index=False)['SemPyUsedSize'].sum()

        df = pd.merge(df, df_stats, left_on=['Table Name', 'Hierarchy Name'], right_on=['SemPyTableName', 'SemPyHierarchyName'], how='left')

        df.drop(columns=['SemPyTableName', 'SemPyHierarchyName'], inplace=True)

        df.rename({"SemPyUsedSize": "Used Size"}, axis=1, inplace=True)

    return df
