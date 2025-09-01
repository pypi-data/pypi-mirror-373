import pandas as pd
import graphviz
import warnings


def _list_dependency_violations(
        df: pd.DataFrame,
        determinant: str,
        dependent: str,
        *,
        dropna: bool = False,
        show_feeding_determinants: bool = False,
        max_violations: int = 10000,
        order_by: str = "count"
) -> pd.DataFrame:
    order_by_options = ["count", "determinant"]
    if order_by not in order_by_options:
        raise ValueError(f"Unexpected order_by argument given. Must be in {order_by_options}")

    pairs = df.groupby([determinant, dependent], dropna=dropna).size().reset_index(name='count')  # type: ignore
    # only keep the rows with duplicated values of A (violations)
    violations_df = pairs[pairs.duplicated(determinant, keep=False)]

    if show_feeding_determinants:
        violations_df = pairs.merge(violations_df[[dependent]].drop_duplicates(), how="inner")

    if order_by == "count":
        max_count = violations_df.groupby(determinant)['count'].transform('max')
        violations_df = violations_df.assign(max_pair_row_count=max_count)
        violations_df = violations_df.sort_values(
                                            ["max_pair_row_count", determinant, "count", dependent],
                                            ascending=[False, True, False, True]
                                        ).drop(
                                            'max_pair_row_count',
                                            axis=1
                                        ).reset_index(drop=True)
    elif order_by == "determinant":
        violations_df = violations_df.sort_values(
                                            [determinant, "count", dependent],
                                            ascending=[True, False, True]
                                        )

    num_violations = violations_df.shape[0]
    violations_df = violations_df.head(max_violations)

    if num_violations == 0:
        print("No violations")
    else:
        if num_violations > max_violations:
            warnings.warn(f"Results have been truncated: displaying {max_violations} out of {num_violations} rows", UserWarning)

    return violations_df.reset_index(drop=True)


def _plot_dependency_violations(
    df: pd.DataFrame,
    determinant: str,
    dependent: str,
    *,
    dropna: bool = False,
    show_feeding_determinants: bool = False,
    max_violations: int = 10000,
    order_by: str = "count"
) -> graphviz.Graph:

    violations_df = _list_dependency_violations(
        df,
        determinant,
        dependent,
        dropna=dropna,
        show_feeding_determinants=show_feeding_determinants,
        max_violations=max_violations,
        order_by=order_by)

    return _plot_dependency_violations_internal(violations_df, determinant, dependent)


def _plot_dependency_violations_internal(violations_df, determinant, dependent):

    import graphviz
    graph_name = f"{determinant}->{dependent}"
    g = graphviz.Graph(name=graph_name, strict=True, node_attr={'shape': 'box'},
                       graph_attr=[("rankdir", "LR"), ("ranksep", ".2"), ("nodesep", ".1")])
    g.node('title', fontsize="20", label=graph_name, shape='plain', style="")

    for _, row in violations_df.iterrows():
        g.edge(str(row[determinant]), str(row[dependent]), label=f"{row['count']}")

    return g


def _drop_dependency_violations(
    df: pd.DataFrame,
    determinant: str,
    dependent: str,
    verbose: int = 0
) -> pd.DataFrame:

    df_new = df.copy()

    group_sizes = df.groupby([determinant, dependent]).size()
    determinant_vals = group_sizes.index.get_level_values(0)
    dupl = determinant_vals[determinant_vals.duplicated()]
    for det_val in dupl:
        for dep_val, _ in list(group_sizes[det_val].sort_values().items())[:-1]:
            # highest one is biggest group, we keep it
            violators = (df_new[determinant] == det_val) & (df_new[dependent] == dep_val)
            if verbose:
                print(f"dropping {violators.sum()} violator(s)")
            if verbose > 1:
                print(df_new[violators])
            df_new = df_new[violators.__invert__()]

    return df_new
