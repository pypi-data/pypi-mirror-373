import pandas as pd

from sempy.dependencies._stats import DataFrameDependencyStats

from typing import List, Set, Tuple


def _find_dependencies_with_stats(df, stats, dropna=False, threshold=0.01, verbose=0):

    groups, dependencies = _build_dependencies(df, stats, dropna, threshold, verbose)

    # If the group contains more than 1 member, then pack the field values into a list
    def _member_stats(group, field):
        items = [getattr(stats[m], field) for m in groups[group]]
        if len(items) == 1 or len(set(items)) == 1:
            return items[0]
        else:
            return items

    def _member_names(group):
        items = [m for m in groups[group]]
        if len(items) == 1:
            return items[0]
        else:
            return items

    enriched_tuples = []
    appended_groups = set()

    for i, j, conditional_entropy in dependencies:
        appended_groups.update((i, j))
        enriched_tuples.append((
            _member_names(i),
            _member_names(j),
            conditional_entropy,
            _member_stats(i, 'nunique_null_inclusive'),
            _member_stats(j, 'nunique_null_inclusive'),
            _member_stats(i, 'null_count'),
            _member_stats(j, 'null_count')
        ))

    # Add multi-member groups, if they have not shown up in any depedencies.
    # There is a problem with how to render such groups together with dependencies
    # in a two dimensional dataframe, and we choose to use None to signal "not applicable"
    for i in range(len(groups)):
        if len(groups[i]) > 1 and i not in appended_groups:
            enriched_tuples.append((
                _member_names(i),
                None,
                None,
                _member_stats(i, 'nunique_null_inclusive'),
                None,
                _member_stats(i, 'null_count'),
                None
            ))

    df = _dependency_tuples_to_pandas(enriched_tuples)

    # Order the dataframe by descending sequence of nuniques. We need to
    # account for a mix of tuples and integers
    def _max(x):
        return max(x) if type(x) is list else x

    df = df.assign(
        max_determinant=lambda x: _max(x['Determinant Unique Count']),
        max_dependent=lambda x: _max(x['Dependent Unique Count']))

    df.sort_values(by=['max_determinant', 'max_dependent'], ascending=False, inplace=True, ignore_index=True)

    if len(df) == 0:
        print("No dependencies found")

    return df.drop(['max_determinant', 'max_dependent'], axis=1)


def _dependency_tuples_to_pandas(tuples):
    df = pd.DataFrame(tuples, columns=[
        'Determinant',
        'Dependent',
        'Conditional Entropy',
        'Determinant Unique Count',
        'Dependent Unique Count',
        'Determinant Null Count',
        'Dependent Null Count'
    ])

    return df


def _build_dependencies(
    df: pd.DataFrame,
    stats: DataFrameDependencyStats,
    dropna: bool = False,
    threshold: float = 0.01,
    verbose: int = 0
) -> Tuple[List[List[str]], List[Tuple[int, int, float]]]:

    if len(df.columns) < 2:
        raise ValueError("At least two columns are needed to plot functional dependencies")

    sorted_groups = _group_equivalent_columns(stats, df, dropna, verbose)

    if verbose > 0:
        print()
        print(f"Dependencies for {len(df.columns)} columns {len(sorted_groups)} groups {stats.nrows} rows, dropna={dropna}, threshold={threshold}")

    if threshold == 0.0:
        return _exact_dependencies(sorted_groups, stats, dropna, verbose)
    else:
        return _threshold_dependencies(sorted_groups, stats, dropna, threshold, verbose)


def _threshold_dependencies(
    sorted_groups: List[List[str]],
    stats: DataFrameDependencyStats,
    dropna: bool = False,
    threshold: float = 0.01,
    verbose: int = 0
) -> Tuple[List[List[str]], List[Tuple[int, int, float]]]:

    transitive_dependencies: List[Tuple[int, int, float]] = []
    non_transitive_dependencies: List[Tuple[int, int, float]] = []

    # 'i' index is from the smallest nunique group moving towards the largest nunique
    # We start 'i' from 1, because we are comparing pairs 'i' to 'j' where the inner
    # 'j' loop will move in reverse from 'i-1' towards 0. This is only important for
    # the detection of transitive dependencies when nulls do not spoil transitiveness.
    for i in range(1, len(sorted_groups)):
        indirect_dependents: Set = set()
        for j in reversed(range(i)):
            # Confirm dependency on the first i.e. [0]-indexed members of the group.
            # Group members are equivalent, so it does not matter which one we'll take.
            column_i = sorted_groups[i][0]
            column_j = sorted_groups[j][0]
            if j in indirect_dependents:
                if verbose > 0:
                    print(f"{column_i}, {column_j}: indirectly dependent")
            else:
                cond_i, cond_j = stats.conditional_entropy(column_i, column_j, dropna, verbose)
                cond_min = min(cond_i, cond_j)
                if verbose > 0:
                    print(f"{column_i}, {column_j}: conditional entropy {cond_i}, {cond_j}")
                # If we are dropping nulls in the evalution, then dependencies are no longer transitive.
                # This is determined by dropna flag or the presence of nulls in the columns.
                # When dropna=True, we expect nulls in small number of columns, because dropna=True
                # implies nulls as Unknown/Invalid rather than NotApplicable, and the data should never
                # have a lot of invalids which would render it useless.
                if cond_min < 1e-8 and ((dropna is False) or (stats[column_i].null_count == 0 and stats[column_j].null_count == 0)):
                    if column_j not in indirect_dependents:
                        _add_transitives_recursively(transitive_dependencies, indirect_dependents, j)
                        transitive_dependencies.append((i, j, 0.0))
                else:
                    if cond_min < threshold:
                        if cond_i < 1e-8 or cond_i <= cond_j:
                            non_transitive_dependencies.append((i, j, cond_i))
                        if cond_j < 1e-8 or cond_j <= cond_i:
                            non_transitive_dependencies.append((j, i, cond_j))

    return sorted_groups, transitive_dependencies + non_transitive_dependencies


def _exact_dependencies(
    sorted_groups: List[List[str]],
    stats: DataFrameDependencyStats,
    dropna: bool = False,
    verbose: int = 0
) -> Tuple[List[List[str]], List[Tuple[int, int, float]]]:

    dependencies: List[Tuple[int, int, float]] = []

    # 'i' index is from the smallest nunique group moving towards the largest nunique
    # We start 'i' from 1, because we are comparing pairs 'i' to 'j' where the inner
    # 'j' loop will move in reverse from 'i-1' towards 0
    for i in range(1, len(sorted_groups)):
        indirect_dependents: Set = set()
        for j in reversed(range(i)):
            # Confirm dependency on the first i.e. [0]-indexed members of the group.
            # Group members are equivalent, so it does not matter which one we'll take.
            column_i = sorted_groups[i][0]
            column_j = sorted_groups[j][0]
            if j in indirect_dependents:
                if verbose > 0:
                    print(f"{column_i}, {column_j}: indirectly dependent")
            else:
                # Confirm dependency on the first i.e. [0]-indexed members of the group.
                # Group members are equivalent, so it does not matter which one we'll take.
                if stats.confirm_dependency(column_i, column_j, verbose):
                    _add_transitives_recursively(dependencies, indirect_dependents, j)
                    dependencies.append((i, j, 0.0))

    return sorted_groups, dependencies


def _add_transitives_recursively(dependencies, transitive_dependents, index):
    if index not in transitive_dependents:
        transitive_dependents.add(index)
        for d in dependencies:
            # if the determinant d[0] is "index" then add its dependent d[1]
            if d[0] == index:
                _add_transitives_recursively(dependencies, transitive_dependents, d[1])


def _group_equivalent_columns(stats, df, dropna, verbose) -> List[List[str]]:

    sorted_columns = sorted(df.columns, key=lambda x: stats[x].nunique_null_inclusive)
    assigned_to_group = [False] * len(sorted_columns)
    sorted_groups = []

    for i in range(len(sorted_columns)):
        if not assigned_to_group[i]:
            assigned_to_group[i] = True
            current_group = [sorted_columns[i]]
            # We can only ascertain perfect 1:1 alignment if the columns have no nulls or nulls
            # should be treated like any other value (dropna=False). Otherwise the alignment cannot
            # be guaranteed and 1:1 relationships are not transitive e.g. A->B and B->C does not
            # guarantee A->C. So we may not be able to create group [A,B,C], and putting B in
            # two groups [[A,B], [B,C]] would make the code and results more difficult to interpret.
            if (dropna is False) or (stats[sorted_columns[i]].null_count == 0):
                # Scan forward, checking any columns with the same nunique_null_inclusive count to see if they map 1-to-1
                j = i + 1
                while j < len(sorted_columns) and stats[sorted_columns[i]].nunique_null_inclusive == stats[sorted_columns[j]].nunique_null_inclusive:
                    # The number of values can be the same, but the columns may not map 1 to 1. If they don't then we will
                    # have to evaluate them against other columns that have not yet been assigned to groups.
                    if (dropna is False) or (stats[sorted_columns[j]].null_count == 0):
                        if stats.confirm_dependency(sorted_columns[i], sorted_columns[j], verbose):
                            assigned_to_group[j] = True
                            current_group.append(sorted_columns[j])
                    j += 1
            sorted_groups.append(current_group)

    return sorted_groups
