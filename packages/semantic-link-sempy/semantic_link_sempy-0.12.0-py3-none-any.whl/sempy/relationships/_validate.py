import pandas as pd
import functools

from sempy.relationships._multiplicity import Multiplicity
from sempy.relationships._stats import DataFrameStats
from sempy.relationships._utils import _to_dataframe_dict, _is_key_missing
from sempy._utils._log import log_tables

from typing import Dict, List, Union


@log_tables
def list_relationship_violations(
        tables: Union[Dict[str, pd.DataFrame], List[pd.DataFrame]],
        relationships: pd.DataFrame,
        missing_key_errors='raise',
        coverage_threshold: float = 1.0,
        n_keys: int = 10
) -> pd.DataFrame:

    """
    Validate to see if the content of tables matches relationships.

    The function examines results of joins for provided relationships and
    searches for inconsistencies with the specified relationship multiplicity.

    Relationships from empty tables (dataframes) are assumed as valid.

    Parameters
    ----------
    tables : dict[str, pandas.DataFrame] or list[pandas.DataFrame]
        A dictionary that maps table names to the dataframes with table content.
        If a list of dataframes is provided, the function will try to infer the names from the
        session variables and if it cannot, it will use the positional index to describe them in
        the results.
    relationships : pandas.DataFrame
        A dataframe with relationships to use for validation. Its columns should  contain the columns
        "Multiplicity", "From Table", "From Column", "To Table", "To Column", which matches the
        output of :func:`~sempy.relationships.find_relationships`.
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
    named_dataframes = _to_dataframe_dict(tables)
    return _list_relationship_violations(named_dataframes, relationships, missing_key_errors, coverage_threshold, n_keys)


def _list_relationship_violations(
        named_dataframes,
        relationships: pd.DataFrame,
        missing_key_errors: str,
        coverage_threshold: float,
        n_keys: int):

    stats_cache = functools.lru_cache()(lambda table_name: DataFrameStats(table_name, named_dataframes[table_name]))
    table_columns = {k: list(v.columns) for k, v in named_dataframes.items()}

    errors = []

    if len(relationships) == 0:
        raise ValueError("At least one relationships must be provided")

    for r in relationships.to_dict(orient="records"):
        multiplicity = r["Multiplicity"]
        from_table = r["From Table"]
        from_column = r["From Column"]
        to_table = r["To Table"]
        to_column = r["To Column"]

        if _is_key_missing(r, table_columns, missing_key_errors):
            continue

        from_df_stats = stats_cache(from_table)
        to_df_stats = stats_cache(to_table)

        from_col_stats = from_df_stats[from_column]
        to_col_stats = to_df_stats[to_column]

        violation_keys = (multiplicity, from_table, from_column, to_table, to_column)

        # Empty entities are a frequent result of failed ingestion, and they deserve separate
        # clear diagnostic messages
        if from_col_stats.nrows == 0:
            errors.append((*violation_keys, "source empty", f"{from_table}[{from_column}] empty"))
        if to_col_stats.nrows == 0:
            errors.append((*violation_keys, "target empty", f"{to_table}[{to_column}] empty"))

        if from_col_stats.nrows == 0 or to_col_stats.nrows == 0:
            # An empty entity on 'from' or 'to' side  would cause additional redundant "values not present" messages
            # that could divert user's attention from the fact that tables are empty. Therefore we want
            # to skip the remainder of validations.
            continue

        if multiplicity == Multiplicity.ONE_TO_ONE:
            if from_col_stats.max_value_count > 1:
                errors.append((*violation_keys, "source not PK", f"{from_table}[{from_column}] not unique"))
        if multiplicity in [Multiplicity.MANY_TO_ONE, Multiplicity.ONE_TO_ONE]:
            if to_col_stats.max_value_count > 1:
                errors.append((*violation_keys, "target not PK", f"{to_table}[{to_column}] not unique"))

        try:
            n_merged = from_col_stats.intersect_count(to_col_stats)
        except Exception as e:
            errors.append((*violation_keys, "exception", f"{type(e).__name__}: {e}"))
            continue

        null_count = from_col_stats.null_count
        if null_count > 0:
            errors.append((*violation_keys, "null FK", f"{from_table}[{from_column}] has {null_count} nulls"))

        if from_col_stats.nunique > 0 and n_merged / from_col_stats.nunique < coverage_threshold:
            n_missing = from_col_stats.nunique - n_merged
            missing_keys = from_col_stats.n_missing_keys(to_col_stats, n_keys=n_keys)
            missing_keys_list = ",".join(map(str, missing_keys))
            if n_missing > n_keys:
                missing_keys_list = missing_keys_list + ",..."
            message = f"{n_missing} out of {from_col_stats.nunique} values in {from_table}[{from_column}] not present in {to_table}[{to_column}]: {missing_keys_list}"
            errors.append((*violation_keys, "partial join", message))

    if len(errors) == 0:
        print("No violations")

    return pd.DataFrame(errors, columns=['Multiplicity', 'From Table', 'From Column', 'To Table', 'To Column', 'Type', 'Message'])
