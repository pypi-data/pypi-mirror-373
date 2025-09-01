import numpy as np


class DataFrameDependencyStats:
    """
    Cache of the dataframe value statistics for improved performance of
    dependency operations.

    Parameters
    ----------
    df : pandas or pyspark.pandas dataframe
        The source dataframe to extract value statistics from
    """
    def __init__(self, df):
        self.column_stats = {}
        self.df = df
        self.nrows = len(df)    # cache nrows, since it is expensive on Spark

    def __getitem__(self, key):
        if key in self.column_stats:
            item = self.column_stats[key]
        else:
            item = PandasColumnDependencyStats(key, self.df, self.nrows)
            self.column_stats[key] = item
        return item

    def confirm_dependency(self, determinant_col, dependent_col, verbose=0):
        determinant_nunique = self[determinant_col].nunique_null_inclusive
        dependent_nunique = self[dependent_col].nunique_null_inclusive
        if verbose > 0:
            print(f"{determinant_col}, {dependent_col}: nunique {determinant_nunique}, {dependent_nunique}")
        if determinant_nunique < dependent_nunique:
            # A determinant must have more or at least as many values as any dependent
            return False
        if determinant_nunique == len(self.df):
            # A unique column is a determinant of all others
            return True
        if dependent_nunique == 1:
            # A constant column is dependent on all others
            return True
        mapping_size = self._get_mapping_size(determinant_col, dependent_col)

        # Each determinant value must map to at most 1 value of the dependent.
        # If it does not, then the mapping size (number of distinct combinations) will be higher
        # than determinant nunique
        if verbose > 0:
            print(f"Mapping size {mapping_size}, dependency: {mapping_size == determinant_nunique}")
        return mapping_size == determinant_nunique

    def conditional_entropy(self, a, b, dropna, verbose=0):
        """
        Conditional entropy H(a|b) and H(b|a) for columns a and b

        Parameters
        ----------
        a : str
            First column name
        b : str
            Second column name

        Returns
        -------
        h_a_b : float
            Conditional entropy of a given b.
        h_b_a : float
            Conditional entropy of b given a.
        """
        # These checks for unique/constant columns are important for performance, because they
        # avoid costly value scans through all rows. Return 0.0 on the side of the unique column,
        # since it determines any other column (for which we use an inconsequential dummy
        # value of 1.0). Similarly, a constant column is determined by any other, so return 0.0
        # on the side of the other column if it's not constant.
        if (dropna is False) or (self[a].null_count == 0 and self[b].null_count == 0):
            a_nunique = self[a].nunique_null_inclusive
            b_nunique = self[b].nunique_null_inclusive
            a_cond = 1.0
            b_cond = 1.0
            if a_nunique == self.nrows or b_nunique == 1:
                a_cond = 0.0
            if b_nunique == self.nrows or a_nunique == 1:
                b_cond = 0.0
            if a_cond == 0.0 or b_cond == 0.0:
                if verbose > 0:
                    print(f"{a}, {b}: cardinality shortcut: {a_cond}, {b_cond}")
                return a_cond, b_cond

        # If dropna will reduce the row set, then the calculations get more time consuming,
        # because we have to recalculate entropies on columns (we cannot use cached overall entropy on
        # all rows). First, the faster calculation from cache, which we expect to kick in most of the time,
        # because for vast majority of dataframes NaN will be encountered infrequently and in few columns:
        if (dropna is False) or (self[a].null_count == 0 and self[b].null_count == 0):
            a_entropy = self[a].entropy()
            b_entropy = self[b].entropy()
            mi = self._get_mutual_info_score(a, b)
            if verbose > 0:
                print(f"{a}, {b}: cached calculation {a_entropy}, {b_entropy}, {mi}")
        else:
            a_entropy, b_entropy, mi = self._get_mutual_info_score_dropna(a, b)
            if verbose > 0:
                print(f"{a}, {b}: full calculation {a_entropy}, {b_entropy}, {mi}")

        return np.maximum([b_entropy - mi, a_entropy - mi], 0)

    def _get_mapping_size(self, determinant_col, dependent_col):
        return len(self.df[[determinant_col, dependent_col]].value_counts(dropna=False))

    def _get_mutual_info_score(self, a, b):
        # need to import late to avoid mlflow auto-tracking latency
        from sklearn.metrics.cluster import mutual_info_score

        return mutual_info_score(self[a].codes, self[b].codes)

    def _get_mutual_info_score_dropna(self, a, b):
        # need to import late to avoid mlflow auto-tracking latency
        from sklearn.metrics.cluster import mutual_info_score, entropy

        mask = self[a].null_mask & self[b].null_mask
        a_values = self.df.loc[mask, a]
        b_values = self.df.loc[mask, b]
        a_entropy = entropy(a_values)
        b_entropy = entropy(b_values)
        mi = mutual_info_score(a_values, b_values)
        return a_entropy, b_entropy, mi


class PandasColumnDependencyStats:
    """
    Cache of the column value statistics for improved performance of
    relationship operations.

    Parameters
    ----------
    column : str
        Column names
    df : dataframe
        The source dataframe to extract value statistics from
    nrows : int
        Number of rows in the dataframe
    """
    def __init__(self, column, df, nrows):
        self.codes = df[column].astype('category').cat.codes
        self.nunique_null_inclusive = self.codes.nunique()
        self.null_mask = self.codes >= 0     # astype('category') identifies Nan with -1
        self.null_count = nrows - sum(self.null_mask)
        self.cached_entropy = None

    def entropy(self):
        # need to import late to avoid mlflow auto-tracking latency
        from sklearn.metrics.cluster import entropy

        if self.cached_entropy is None:
            self.cached_entropy = entropy(self.codes)
        return self.cached_entropy
