import pandas as pd
import graphviz

from sempy.relationships._multiplicity import Multiplicity
from sempy.relationships._utils import _to_dataframe_dict, _is_key_missing
from sempy._utils._log import log_tables

from collections import defaultdict
from typing import Dict, List, Optional, Union


@log_tables
def plot_relationship_metadata(
        metadata_df: pd.DataFrame,
        tables: Optional[Union[Dict[str, pd.DataFrame], List[pd.DataFrame]]] = None,
        include_columns: str = 'keys',
        missing_key_errors='raise',
        *,
        graph_attributes: Optional[Dict] = None) -> graphviz.Digraph:
    """
    Plot a graph of relationships based on metadata contained in the provided dataframe.

    The input "metadata" dataframe should contain one row per relationship.
    Each row names the "from" and "to" table/columns that participate in the relationship, and their
    multiplicity as defined by :func:`~sempy.relationships.Multiplicity`.

    Parameters
    ----------
    metadata_df : pandas.DataFrame, default=None
        A "metadata" dataframe with relationships to plot. It should  contain the columns  "multiplicity",
        "From Table", "From Column", "To Table", "To Column", which matches the
        output of :func:`~sempy.relationships.find_relationships`.
    tables : dict[str, pandas.DataFrame] or list[pandas.DataFrame], default=None
        It needs to provided only when `include_columns` = 'all' and it will be used
        for mapping table names from relationships to the dataframe columns.
    include_columns : str, default='keys'
        One of 'keys', 'all', 'none'. Indicates which columns should be included in the graph.
    missing_key_errors : str, default='raise'
        One of 'raise', 'warn', 'ignore'. Action to take when either table or column
        of the relationship is not found in the elements of the argument *tables*.
    graph_attributes : dict, default=None
        Attributes passed to graphviz. Note that all values need to be strings. Useful attributes are:

        - *rankdir*: "TB" (top-bottom) or "LR" (left-right)
        - *dpi*:  "100", "30", etc. (dots per inch)
        - *splines*: "ortho", "compound", "line", "curved", "spline" (line shape)

    Returns
    -------
    graphviz.Digraph
        Graph object containing all relationships.
        If include_attributes is true, attributes are represented as ports in the graph.
    """

    valid_include_columns = ['keys', 'all', 'none']

    if include_columns not in valid_include_columns:
        raise ValueError(f"Invalid \"include_columns\"='{include_columns}', must be one of {valid_include_columns}")

    if include_columns == 'all' and tables is None:
        raise ValueError("Argument \"tables\" must be provided when \"include_columns\"='all'")

    graph_attributes = graph_attributes or {}
    if "rankdir" not in graph_attributes:
        graph_attributes["rankdir"] = "LR"

    g = graphviz.Digraph(node_attr=[('shape', 'plaintext')], graph_attr=graph_attributes)

    head = '<<TABLE BORDER="0" CELLBORDER="1" CELLSPACING="0" ALIGN="LEFT">'
    tail = '</TABLE>>'

    # Dictionary of sets to dedupe columns per table
    relationship_columns: defaultdict = defaultdict(set)

    if tables is not None:
        named_dataframes = _to_dataframe_dict(tables)
        table_columns = {k: list(v.columns) for k, v in named_dataframes.items()}

    for r in metadata_df.to_dict(orient="records"):
        multiplicity, from_table, from_column, to_table, to_column = (
            r["Multiplicity"],
            r["From Table"],
            r["From Column"],
            r["To Table"],
            r["To Column"]
        )

        if multiplicity == Multiplicity.ONE_TO_ONE:
            attrs = {"dir": "both"}
        elif multiplicity == Multiplicity.MANY_TO_MANY:
            attrs = {"dir": "none"}
        else:
            attrs = {}

        if tables is not None:
            if _is_key_missing(r, table_columns, missing_key_errors):
                continue

        relationship_columns[from_table].add(from_column)
        relationship_columns[to_table].add(to_column)

        if include_columns == 'none':
            # Edge is between tables
            g.edge(f'{to_table}', f'{from_table}', color='black', colorscheme="accent8", **attrs)
        else:
            # Edge is between specific table columns, which is why we specify a combo of {from_table}:{from_column}'.
            # Each column will later be drawn as a rectangle where the edges will be anchored.
            g.edge(f'{to_table}:{to_column}', f'{from_table}:{from_column}', color='black', colorscheme="accent8", **attrs)

    if tables is None:
        table_columns = {k: sorted(v) for k, v in relationship_columns.items()}

    for table, columns in table_columns.items():
        body = f"<TR><TD><B>{table}</B></TD></TR>"
        if include_columns != 'none':

            if include_columns == 'keys':
                display_columns = sorted(relationship_columns[table])
            else:
                display_columns = columns

            for column in display_columns:
                body = body + f'<TR><TD ALIGN="LEFT" port="{column}">{column}</TD></TR>'

            if include_columns == 'keys' and len(columns) > len(display_columns):
                body = body + '<TR><TD ALIGN="LEFT">...</TD></TR>'

        g.node(table, head + body + tail)

    return g
