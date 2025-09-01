import pandas as pd
from uuid import UUID

from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._flat import evaluate_dax
from sempy.fabric._flat_list_columns import list_columns
from sempy.fabric._utils import collection_to_dataframe, to_multiplicity, dotnet_to_pandas_date, dax_escape_table_name, dax_escape_column_name
from sempy._utils._log import log
from sempy.fabric._credentials import with_credential

from typing import List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


def _list_relationships_extended(
    df: pd.DataFrame,
    dataset: Union[str, UUID],
    workspace: Optional[Union[str, UUID]] = None
) -> pd.DataFrame:

    df_columns = list_columns(dataset, extended=True, workspace=workspace)[['Table Name', 'Column Name', 'Column Cardinality']]

    df_columns_from = df_columns.rename(columns={'Column Cardinality': 'Max From Cardinality'})
    df_columns_to = df_columns.rename(columns={'Column Cardinality': 'Max To Cardinality'})

    df = (pd.merge(df, df_columns_from, how='left', left_on=['From Table', 'From Column'], right_on=['Table Name', 'Column Name'])
            .drop(['Table Name', 'Column Name'], axis=1))
    df = (pd.merge(df, df_columns_to,   how='left', left_on=['To Table',   'To Column'],   right_on=['Table Name', 'Column Name'])  # noqa: E272
            .drop(['Table Name', 'Column Name'], axis=1))

    df_relationships = evaluate_dax(dataset,
                                    """
                                    SELECT
                                        [ID]   AS [SemPyRelationshipID],
                                        [Name] AS [SemPyRelationshipName]
                                    FROM
                                        $SYSTEM.TMSCHEMA_RELATIONSHIPS
                                    """,
                                    workspace=workspace)

    df_stats = evaluate_dax(dataset,
                            """
                            SELECT
                                [TABLE_ID]  AS [SemPyTableID],
                                [USED_SIZE] AS [SemPyUsedSize]
                            FROM
                                $SYSTEM.DISCOVER_STORAGE_TABLE_COLUMN_SEGMENTS
                            """,
                            workspace=workspace)

    df_stats = df_stats[df_stats['SemPyTableID'].str.startswith("R$")]
    df_stats['SemPyRelationshipID'] = df_stats['SemPyTableID'].str.extract(r'\((\d+)\)$').astype('Int64')

    df_stats = pd.merge(df_stats, df_relationships, on='SemPyRelationshipID')

    df_stats = df_stats.groupby('SemPyRelationshipName', as_index=False)['SemPyUsedSize'].sum()

    df = pd.merge(df, df_stats, left_on='Relationship Name', right_on='SemPyRelationshipName', how='left')

    df.drop('SemPyRelationshipName', axis=1, inplace=True)
    df.rename({"SemPyUsedSize": "Used Size"}, axis=1, inplace=True)

    return df


def _list_relationships_missing_rows(
    df: pd.DataFrame,
    dataset: Union[str, UUID],
    workspace: Optional[Union[str, UUID]] = None
) -> pd.DataFrame:
    missing_row_series = []

    for _, row in df.iterrows():
        from_table = f"'{dax_escape_table_name(row['From Table'])}'"
        from_object = f"'{dax_escape_table_name(row['From Table'])}'[{dax_escape_column_name(row['From Column'])}]"
        to_object = f"'{dax_escape_table_name(row['To Table'])}'[{dax_escape_column_name(row['To Column'])}]"
        active = row['Active']

        if active:
            dax = f"""
                EVALUATE
                    SUMMARIZECOLUMNS("NumMissingRows",
                        CALCULATE(COUNTROWS({from_table}), ISBLANK({to_object})))
                """
        else:
            dax = f"""
                EVALUATE
                    SUMMARIZECOLUMNS("NumMissingRows",
                        CALCULATE(COUNTROWS({from_table}), USERELATIONSHIP({from_object}, {to_object}), ISBLANK({to_object})))
                """
        df_missing_rows = evaluate_dax(dataset, dax, workspace=workspace)

        missing_rows = 0
        if len(df_missing_rows) > 0:
            missing_rows = df_missing_rows.iloc[0, 0]

        missing_row_series.append(missing_rows)

    df['Missing Rows'] = missing_row_series

    return df


@log
@with_credential
def list_relationships(
    dataset: Union[str, UUID],
    extended: Optional[bool] = False,
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    calculate_missing_rows: Optional[bool] = False,
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    List all relationship found within the Power BI model.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    extended : bool, default=False
        Fetches extended column information.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `relationship <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.relationship?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
        Use Parent to navigate to the parent level.
    calculate_missing_rows : bool, default=False
        Calculate the number of missing rows in the relationship.
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
    pandas.DataFrame
        DataFrame with one row per relationship.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset)

    extraction_def = [
        ("Multiplicity",                  lambda r: to_multiplicity(r),                    "str"),   # noqa: E272
        ("From Table",                    lambda r: r.FromTable.Name,                       "str"),   # noqa: E272
        ("From Column",                   lambda r: r.FromColumn.Name,                      "str"),   # noqa: E272
        ("To Table",                      lambda r: r.ToTable.Name,                         "str"),   # noqa: E272
        ("To Column",                     lambda r: r.ToColumn.Name,                        "str"),   # noqa: E272
        ("Active",                        lambda r: r.IsActive,                             "bool"),  # noqa: E272
        ("Cross Filtering Behavior",      lambda r: r.CrossFilteringBehavior.ToString(),    "str"),   # noqa: E272
        ("Security Filtering Behavior",   lambda r: r.SecurityFilteringBehavior.ToString(), "str"),   # noqa: E272
        ("Join On Date Behavior",         lambda r: r.JoinOnDateBehavior.ToString(),        "str"),   # noqa: E272
        ("Rely On Referential Integrity", lambda r: r.RelyOnReferentialIntegrity,           "bool"),  # noqa: E272
        ("State",                         lambda r: r.State.ToString(),                     "str"),   # noqa: E272
        ("Modified Time",                 lambda r: dotnet_to_pandas_date(r.ModifiedTime),  "datetime64[ns]"),  # noqa: E272
        ("Relationship Name",             lambda r: r.Name,                                 "str"),   # noqa: E272
    ]

    collection = [
        r for r in database.Model.Relationships
    ]

    df = collection_to_dataframe(collection, extraction_def, additional_xmla_properties)

    if extended:
        df = _list_relationships_extended(df, dataset, workspace)

    if calculate_missing_rows:
        df = _list_relationships_missing_rows(df, dataset, workspace)

    return df
