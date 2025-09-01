import pandas as pd

from sempy._utils._pandas_utils import _pandas_merge_cast
from typing import Dict, Any

VALUE = "value"
SIZE = "size"


class DataFrameStats:
    """
    Cache of the dataframe value statistics for improved performance of
    relationship operations.

    Parameters
    ----------
    name : str
        The table name
    df : pandas.DataFrame
        The source dataframe to extract value statistics from
    """
    def __init__(self,
                 name: str,
                 df: pd.DataFrame):
        self.name = name
        self.column_stats: Dict[str, Any] = {}
        self.df = df

    def __getitem__(self, key: str):
        assert type(key) is str
        if key in self.column_stats:
            item = self.column_stats[key]
        else:
            item = PandasColumnStats(key, self.df)
            self.column_stats[key] = item
        return item

    def _get_columns(self):
        return self.df.columns


class PandasColumnStats:
    """
    Cache of the column value statistics for improved performance of
    relationship operations.

    Parameters
    ----------
    column : str
        The column name
    df : pandas.DataFrame
        The source dataframe to extract value statistics from
    """
    def __init__(self,
                 column: str,
                 df: pd.DataFrame):
        # We decided to exclude NaN, assuming nulls are "not applicable" when dealing
        # with them in keys. This is consistent with how they are treated in SQL/Spark joins,
        # but does not align with pandas merge implementations, where None/NaN are successfully
        # joined like any other value. We'll use as_index=False, since we want the columns to
        # reflect values and types of the original dataframe, so that they can be used in merge
        # operation rather than risk some type transformation when building multi-level index.
        # We want to use merge operation (rather than python set comparisons) for two reasons:
        # - we want to capture exceptions that stem from column type incompatibility
        # - merge results are reproducible from run to run, which was not true of sets
        self.value_counts = df[[column]]\
                                .rename(columns={column: VALUE})\
                                .groupby(VALUE, as_index=False, sort=False, dropna=True)\
                                .size()

        self.nrows = len(df)
        self.null_count = self.nrows - self.value_counts[SIZE].sum()  # type: ignore
        self.nunique = len(self.value_counts)
        if (self.nunique > 0):
            self.max_value_count = self.value_counts[SIZE].max()  # type: ignore
        else:
            self.max_value_count = 0

    def intersect_count(self, other):
        """
        Computes the size of an intersect of unique values

        This is size of the intersection divided by size of own unique values.

        Parameters
        ----------
        other : ColumnStats
            the statistics of the column beting compared to

        Returns
        -------
        intersect_count : int
            Size of the intersect
        """
        if self.nunique == 0 or other.nunique == 0:
            return 0
        else:
            left, right = _pandas_merge_cast(
                self.value_counts[[VALUE]],
                VALUE,
                other.value_counts[[VALUE]],
                VALUE,
                warn=False)

            join = pd.merge(left,
                            right,
                            how="inner",
                            left_on=VALUE,
                            right_on=VALUE)
            return len(join)

    def issubset(self, other):
        """
        Checks if this value set is the subset of the other for exact foreign key coverage

        Parameters
        ----------
        other : ColumnStats
            the statistics of the column beting compared to

        Returns
        -------
        issubset : bool
            True if this value set is subset of the other
        """
        if self.nunique > 0 and self.nunique <= other.nunique:
            try:
                return self.intersect_count(other) == self.nunique
            except Exception:
                # Certain combinations of types can throw exceptions (e.g. numpy ints and decimals)
                # It's not practical to test all problem combinations and keep it up to date with
                # future changes/fixes. Hence, indiscriminate exception catch
                return False
        else:
            return False

    def n_missing_keys(self, other, n_keys=10):
        """
        Picks randomly the first n missing keys

        Parameters
        ----------
        other : ColumnStats
            the statistics of the column beting compared to
        n_keys : int
            the number of keys to return

        Returns
        -------
        missing_keys : List[Tuple]
            List of missing keys expressed as tuple
        """
        left, right = _pandas_merge_cast(
            self.value_counts[[VALUE]],
            VALUE,
            other.value_counts[[VALUE]],
            VALUE,
            warn=False)

        join = pd.merge(left,
                        right,
                        how="left",
                        left_on=VALUE,
                        right_on=VALUE,
                        indicator=True)

        # indicator=True appends "_merge" columns that we can use to identify
        # missing keys. Then, choose first n records and project to just key column
        n_missing_rows = join[join._merge == "left_only"][:n_keys]
        return list(n_missing_rows[VALUE])
