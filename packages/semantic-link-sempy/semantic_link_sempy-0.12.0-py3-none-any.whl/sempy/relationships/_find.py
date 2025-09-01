import pandas as pd
import itertools
import re
import difflib

from sempy.relationships._multiplicity import Multiplicity
from sempy.relationships._stats import DataFrameStats
from sempy.relationships._utils import _to_dataframe_dict, _to_exclude_tuples
from sempy._utils._log import log_tables

from typing import Any, Dict, List, Optional, Set, Tuple, Union


@log_tables
def find_relationships(
    tables: Union[Dict[str, pd.DataFrame], List[pd.DataFrame]],
    coverage_threshold: float = 1.0,
    name_similarity_threshold: float = 0.8,
    exclude: Optional[Union[List[Tuple[str]], pd.DataFrame]] = None,
    include_many_to_many: bool = False,
    verbose: int = 0
) -> pd.DataFrame:
    """
    Suggest possible relationships based on coverage threshold.

    By default `include_many_to_many` is `False`, which is the most common case.
    Generated relationship are m:1 (i.e. the "to" attribute is the primary key)
    and will also include 1:1 relationships.

    If `include_many_to_many` is set to `True` (less common case), we will search for additional many to many
    relationships. The results will be a superset of default m:1 case.

    Empty dataframes are not considered for relationships.

    Parameters
    ----------
    tables : dict[str, pandas.DataFrame] or list[pandas.DataFrame]
        A dictionary that maps table names to the dataframes with table content.
        If a list of dataframes is provided, the function will try to infer the names from the
        session variables and if it cannot, it will use the positional index to describe them in
        the results.
    coverage_threshold : float, default=1.0
        A minimum threshold to report a potential relationship. Coverage is a ratio of unique values in the
        "from" column that are found (covered by) the value in the "to" (key) column.
    name_similarity_threshold : float, default=0.8
        Minimum similarity of column names before analyzing for relationship.
        The value of 0 means that any 2 columns will be considered.
        The value of 1 means that only column that match exactly will be considered.
    exclude : pandas.DataFrame, default=None
        A dataframe with relationships to exclude. Its columns should  contain the columns
        "From Table", "From Column", "To Table", "To Column", which matches the output of
        :func:`~sempy.relationships.find_relationships`.
    include_many_to_many : bool, default=True
        Whether to also search for m:m relationships.
    verbose : int, default=0
        Verbosity. 0 means no verbosity.

    Returns
    -------
    pandas.DataFrame
        A dataframe with candidate relationships identified by: from_table, from_column,
        to_table, to_column. Also provides auxiliary statistics to help with evaluation.
        If no suitable candidates are found, returns an empty DataFrame.
    """
    named_dataframes = _to_dataframe_dict(tables)
    stats = {k: DataFrameStats(k, v) for k, v in named_dataframes.items()}
    exclude_tuples = _to_exclude_tuples(exclude)
    relationship_tuples = _find_relationships(stats, coverage_threshold, name_similarity_threshold, exclude_tuples, include_many_to_many, verbose)
    return _convert_rels_to_pandas(relationship_tuples, stats)


def determine_multiplicity(stats_from, stats_to):
    if stats_from.max_value_count == 1:
        if stats_to.max_value_count == 1:
            return Multiplicity.ONE_TO_ONE
        else:
            raise ValueError("Unexpected 1:m multiplicity")
    else:
        if stats_to.max_value_count == 1:
            return Multiplicity.MANY_TO_ONE
        else:
            return Multiplicity.MANY_TO_MANY


def _relationship_tuples_to_pandas(tuples: List[Any]):
    return pd.DataFrame(tuples, columns=[
        'Multiplicity',
        'To Table',
        'To Column',
        'From Table',
        'From Column',
        'Coverage To',
        'Coverage From',
        'Null Count To',
        'Null Count From',
        'Unique Count To',
        'Unique Count From',
        'Row Count To',
        'Row Count From'
    ])


def _convert_rels_to_pandas(relationships: List, stats: Dict):
    enriched_tuples = []
    for stype_from, column_from, stype_to, column_to, coverage_from, coverage_to in relationships:
        stats_from = stats[stype_from][column_from]
        stats_to = stats[stype_to][column_to]
        enriched_tuples.append((
            determine_multiplicity(stats_from, stats_to),
            stype_from,
            column_from,
            stype_to,
            column_to,
            coverage_from,
            coverage_to,
            stats_from.null_count,
            stats_to.null_count,
            stats_from.nunique,
            stats_to.nunique,
            stats_from.nrows,
            stats_to.nrows
        ))
    return _relationship_tuples_to_pandas(enriched_tuples)


def _normalize_key(table: str, col: str):
    """
    Normalizes a key by removing noise words.
    """
    def _normalize_one(key):
        noise_words = ["name", "id", "key", "code", "pk", "fk"]
        words = re.findall("[a-zA-Z0-9]+", key)
        words_lower = [w.lower() for w in words]
        key = "".join([w for w in words_lower if w not in noise_words])
        return key
    return _normalize_one(col) or _normalize_one(table)


def _key_similarity(table_a: str, col_a: str, table_b: str, col_b: str):
    """
    Returns whether the two table/colum pairs are similar.
    """
    col_a_norm = _normalize_key(table_a, col_a)
    col_b_norm = _normalize_key(table_b, col_b)
    # This returns Ratcliff/Obershelp similarity, aka Gestalt Pattern Matching
    # https://en.wikipedia.org/wiki/Gestalt_Pattern_Matching
    ratio = difflib.SequenceMatcher(None, col_a_norm, col_b_norm).ratio()
    return ratio


def _threshold_pair_relationships(
        df_a_stats: DataFrameStats,
        df_b_stats: DataFrameStats,
        col_a: str,
        col_b: str,
        include_many_to_many: bool,
        coverage_threshold: float):

    results = []
    col_a_stats = df_a_stats[col_a]
    col_b_stats = df_b_stats[col_b]

    if col_a_stats.nunique > 0 and col_b_stats.nunique > 0:
        # This check seems redundant (its elements are repeated later again), but it prevents
        # unnecessary evaluation of intersect_count when the requested directionality and
        # column uniqueness would result in no addition to relationship suggestions
        if include_many_to_many or (include_many_to_many is False and (col_a_stats.max_value_count == 1 or col_b_stats.max_value_count == 1)):
            try:
                intersect_count = col_a_stats.intersect_count(col_b_stats)
            except Exception:
                # Certain combinations of types can throw exceptions (e.g. numpy ints and decimals)
                # It's not practical to test all problem combinations and keep it up to date with
                # future changes/fixes. Hence, indiscriminate exception catch
                intersect_count = 0

            # Jaccard similarity is the size intersection of the unique values divided by the
            # size of the union of the unique values in each column.

            coverage_b = intersect_count / col_b_stats.nunique
            coverage_a = intersect_count / col_a_stats.nunique

            if include_many_to_many is False:
                # a to b means b is primary key and contains all unique values
                if col_a_stats.max_value_count == 1:
                    # b->a is a possibility
                    if coverage_b >= coverage_threshold:
                        results.append((df_b_stats.name, col_b, df_a_stats.name,  col_a, coverage_b, coverage_a))
                if col_b_stats.max_value_count == 1:
                    # a->b is a possibility
                    if coverage_a >= coverage_threshold:
                        results.append((df_a_stats.name, col_a, df_b_stats.name, col_b, coverage_a, coverage_b))
            else:
                # For include_many_to_many coverage must exceed threshold in one of the directions.
                # This loose "or" condition is designed to generate a superset of results from "many to one only" case.
                # It may lead to many spurious matches. For example, in a system with intger keys any
                # large references table with a large number of sequential pkey IDs would map
                # to any column with a small number of sequential fkey IDs
                if coverage_a >= coverage_threshold or coverage_b >= coverage_threshold:
                    # An m:m relationship may result in 2 rows for each direction, analogous to 1:1 case.
                    # This enables the user to obtain a complete list of relationships when filtering by
                    # from/to columns.
                    # The following checks on max_value_count ensure that relationships are presented
                    # consistently as m:1 and not in reverse 1:m.
                    if col_a_stats.max_value_count == 1 or col_b_stats.max_value_count > 1:
                        results.append((df_b_stats.name, col_b, df_a_stats.name, col_a, coverage_b, coverage_a))
                    if col_b_stats.max_value_count == 1 or col_a_stats.max_value_count > 1:
                        results.append((df_a_stats.name, col_a, df_b_stats.name, col_b, coverage_a, coverage_b))

    return results


def _exact_pair_relationships(
        df_a_stats: DataFrameStats,
        df_b_stats: DataFrameStats,
        col_a: str,
        col_b: str,
        include_many_to_many: bool):

    results = []
    col_a_stats = df_a_stats[col_a]
    col_b_stats = df_b_stats[col_b]

    if col_a_stats.nunique > 0 and col_b_stats.nunique > 0:
        if include_many_to_many is False:
            # check if a could be unique key and if it covers b completely
            if col_a_stats.max_value_count == 1 and col_b_stats.issubset(col_a_stats):
                results.append((df_b_stats.name, col_b, df_a_stats.name,  col_a, 1.0, col_b_stats.nunique / col_a_stats.nunique))
            # check if b could be unique key and if it covers a completely
            if col_b_stats.max_value_count == 1 and col_a_stats.issubset(col_b_stats):
                results.append((df_a_stats.name, col_a, df_b_stats.name, col_b, 1.0, col_a_stats.nunique / col_b_stats.nunique))
        else:
            # An m:m relationship may result in 2 rows for each direction, analogous to 1:1 case.
            # This enables the user to obtain a complete list of relationships when filtering by
            # from/to columns.
            # The following checks on max_value_count ensure that relationships are presented
            # consistently as m:1 and not in reverse 1:m. They are intentionally put before issubset,
            # which is expensive to evaluate.
            if col_a_stats.max_value_count == 1 or col_b_stats.max_value_count > 1:
                if col_b_stats.issubset(col_a_stats):
                    results.append((df_b_stats.name, col_b, df_a_stats.name, col_a, 1.0, col_b_stats.nunique / col_a_stats.nunique))
            if col_b_stats.max_value_count == 1 or col_a_stats.max_value_count > 1:
                if col_a_stats.issubset(col_b_stats):
                    results.append((df_a_stats.name, col_a, df_b_stats.name, col_b, 1.0, col_a_stats.nunique / col_b_stats.nunique))
    return results


def _relationships_from_column_combinations(
        df_a_stats: DataFrameStats,
        df_b_stats: DataFrameStats,
        name_similarity_threshold: float,
        coverage_threshold: float,
        include_many_to_many: bool,
        verbose: int) -> List[Tuple]:
    """
    For a pair of dataframes, find possible join columns coverage threshold.
    """
    results = []

    column_iter = list(itertools.product(df_a_stats._get_columns(), df_b_stats._get_columns()))

    for col_a, col_b in column_iter:
        if name_similarity_threshold > 0 and _key_similarity(df_a_stats.name, col_a, df_b_stats.name, col_b) < name_similarity_threshold:
            continue
        if verbose > 1:
            print(f"  Columns {col_a} and {col_b}")
        # Handling of exact match of join keys (coverage_threshold == 1.0) can be optimized to run
        # much faster than the inexact match (coverage_threshold < 1.0), because because we only need to get
        # a True/False answer where w can exit on the first failure and avoid scanning through
        # full set of values. In the most favorable case we may exit on first test comparison
        # (if there is no overlap between the sets or if we just get lucky)
        if coverage_threshold < 1.0:
            relationships = _threshold_pair_relationships(df_a_stats, df_b_stats, col_a, col_b, include_many_to_many, coverage_threshold)
        else:
            relationships = _exact_pair_relationships(df_a_stats, df_b_stats, col_a, col_b, include_many_to_many)
        results.extend(relationships)
    return results


def _find_relationships(
        stats: Dict[str, DataFrameStats],
        coverage_threshold: float,
        name_similarity_threshold: float,
        exclude_tuples: Optional[Set[Tuple[str]]],
        include_many_to_many: bool,
        verbose: int) -> List[Tuple]:

    results = []

    for table_a, table_b in itertools.combinations(stats.keys(), 2):
        if verbose > 0:
            print(f"Searching for relationships between tables {table_a} and {table_b}")
        relationships = _relationships_from_column_combinations(
                            stats[table_a],
                            stats[table_b],
                            name_similarity_threshold=name_similarity_threshold,
                            coverage_threshold=coverage_threshold,
                            include_many_to_many=include_many_to_many,
                            verbose=verbose)
        if verbose > 0:
            for relationship in relationships:
                print(f"    Detected {relationship[1]}->{relationship[3]} coverage: ({relationship[4]}, {relationship[5]})")
        results.extend(relationships)

    if exclude_tuples and len(exclude_tuples) > 0:
        filtered_results = []
        for rel in results:
            table_a, from_col, table_b, to_col, coverage_a, coverage_b = rel
            if (
                (table_a, from_col, table_b, to_col) in exclude_tuples or
                (table_b, to_col, table_a, from_col) in exclude_tuples
            ):
                pass
            else:
                filtered_results.append(rel)
        if len(filtered_results) == 0:
            print("No additional relationships found")
        return filtered_results

    if len(results) == 0:
        print("No relationships found")

    return results
