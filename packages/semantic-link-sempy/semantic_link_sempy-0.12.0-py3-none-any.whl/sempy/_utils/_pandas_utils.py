import datetime
import pandas as pd
import warnings
import re


from pandas.core.dtypes.common import is_dtype_equal
from typing import List, Optional, Tuple


def _pandas_merge_cast(left_df, left_on, right_df, right_on, relationship=None, warn=True):

    if not isinstance(left_on, str) or not isinstance(right_on, str):
        raise TypeError(f"Unexpected types {type(left_on)} and {type(right_on)}: not strings")

    string_types = ["string", "unicode", "mixed", "bytes", "empty"]

    # Try to cast some common type issues to make pandas behave more nicely
    if not is_dtype_equal(left_df[left_on], right_df[right_on]):
        left_dtype = pd.api.types.infer_dtype(left_df[left_on])
        right_dtype = pd.api.types.infer_dtype(right_df[right_on])
        msg = f"Mismatching dtypes in merging along relationship {relationship}."
        if (left_dtype in string_types):
            if (right_dtype in string_types):
                # both are string
                pass
            else:
                # left is string but right is not
                if warn:
                    warnings.warn(msg)
                right_df = right_df.astype({right_on: str})

        elif right_dtype in string_types:
            # right is string but left is not
            if warn:
                warnings.warn(msg)
            left_df = left_df.astype({left_on: str})

    return left_df, right_df


_safe_datetime_regex = re.compile(r"""^             # start of string
                                      (\d{4})-      # year
                                      (\d{2})-      # month
                                      (\d{2})T      # day
                                      (\d{2}):      # hour
                                      (\d{2}):      # minute
                                      (\d{2})       # second
                                      (?:\.(\d+))?  # optional milliseconds or nanoseconds
                                      Z?            # optional Z indicating UTC timezone (no support for offset)
                                      $             # end of string
                                  """,
                                  re.VERBOSE)


def safe_convert_rest_datetime(val: Optional[str]):
    if val is None:
        return None

    val = str(val)

    # refresh api sometimes returns these
    if val.lower() == 'nan':
        return None

    m = _safe_datetime_regex.match(val)
    if m is None:
        raise ValueError(f"Unable to parse datetime string: {val}")

    (year, month, day, hour, minute, second, ms_or_ns) = m.groups()

    # python doesn't support nanoseconds, just truncate to microseconds
    if ms_or_ns is None:
        ms_or_ns = "0"

    ms_or_ns = ms_or_ns[:6]
    ms_or_ns = "{v:0<6}".format(v=ms_or_ns)

    dt = datetime.datetime(
        year=int(year),
        month=int(month),
        day=int(day),
        hour=int(hour),
        minute=int(minute),
        second=int(second),
        microsecond=int(ms_or_ns),
        tzinfo=datetime.timezone.utc)

    return dt


def rename_and_validate(df: Optional[pd.DataFrame], schema: List[Tuple[str, str, str]]) -> pd.DataFrame:
    """
    Rename columns in a dataframe according to a schema and validate that the schema is satisfied.

    Parameters
    ----------
    df : pd.DataFrame
        The input data.
    schema : List[Tuple[str, str, str]]
        The expected schema. Each element is a tuple of (source column name, destination column name, column type).

    Returns
    -------
    pd.DataFrame
        The renamed dataframe.
    """
    # make sure we can deal w/ empty dataframes
    if df is None:
        df = pd.DataFrame()

    missing_columns = []

    # collect columns in the right order
    output_columns = {}

    for src, dest, column_type in schema:
        # Supported format: <type>[?], where ? indicates optional.
        if column_type.endswith("?"):
            column_type = column_type[:-1]
            optional = True
        else:
            optional = False

        assert column_type != "int", "int is not supported, use Int64 instead"
        assert column_type != "float", "int is not supported, use Float4 instead"

        if len(df.columns.values) > 0 and src in df.columns.values:
            # need to convert before inserting as we don't want to deal
            # w/ pd.NaT when trying to convert, rather just str
            output_columns[dest] = df[src]

            if column_type == "datetime64[ns]":
                output_columns[dest] = output_columns[dest].apply(safe_convert_rest_datetime)

        else:
            # it's (missing) and (mandatory)
            if not optional:
                missing_columns.append(src)

            # add missing column as the it's optional in the input data
            output_columns[dest] = pd.Series(dtype=column_type)

    # only warn for non-empty dataframes
    if len(df) > 0 and len(missing_columns) > 0:
        # don't fail, just warn. Assuming the backend returns less data than expected, we should still
        # pass the data
        warnings.warn(UserWarning(f"Missing columns from backend: {missing_columns}"))

    # create new dataframe with renamed columns in the right order (e.g. optional columns would be at the end)
    return pd.DataFrame(output_columns)


def rename_and_validate_from_records(records, schema: List[Tuple[str, str, str]], replace_na: bool = False) -> pd.DataFrame:
    """
    Rename columns in a list of records according to a schema and validate that the schema is satisfied.

    Parameters
    ----------
    records : List[dict]
        The input data.
    schema : List[Tuple[str, str, str]]
        The expected schema. Each element is a tuple of (source column name, destination column name, column type).
    replace_na : bool, default=False
        If True, replace NaN values with None in the output dataframe.

    Returns
    -------
    pd.DataFrame
        The renamed dataframe.
    """

    # prep schema
    if records is None or len(records) == 0:
        df = None
    else:
        df = pd.DataFrame.from_records(records)

    df = rename_and_validate(df, schema)

    if replace_na:
        import numpy as np
        return df.replace(np.NAN, None)

    return df
