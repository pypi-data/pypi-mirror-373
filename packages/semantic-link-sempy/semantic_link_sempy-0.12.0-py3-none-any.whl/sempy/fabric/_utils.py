import datetime
import importlib
import pandas as pd
import os
import re
import string
from functools import wraps
from collections import defaultdict
import uuid
from operator import attrgetter
from urllib.parse import quote, quote_plus, urlparse, urlunparse

from sempy.relationships._multiplicity import Multiplicity

from typing import Any, Callable, Dict, Iterable, List, Tuple, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from sempy.fabric import FabricDataFrame
    from pandas._libs import NaTType


def _get_relationships(named_dataframes: Dict[str, "FabricDataFrame"]) -> pd.DataFrame:

    from sempy.fabric import FabricDataFrame

    relationship_tuples: List[Tuple] = []

    for name, df in named_dataframes.items():
        if not isinstance(df, FabricDataFrame):
            raise TypeError(f"Unexpected type {type(df)} for '{name}': not an FabricDataFrame")
        if df.column_metadata:
            for col, metadata in df.column_metadata.items():
                rel_metadata = metadata.get("relationship")
                if rel_metadata:
                    if rel_metadata['multiplicity'] not in Multiplicity._valid_multiplicities:
                        raise ValueError(f"Invalid multiplicity '{rel_metadata['multiplicity']}', which must be one of {Multiplicity._valid_multiplicities}")
                    relationship_tuples.append((
                        rel_metadata['multiplicity'],
                        name,
                        col,
                        rel_metadata['to_table'],
                        rel_metadata['to_column']
                    ))

    return pd.DataFrame(
        relationship_tuples,
        columns=[
            'Multiplicity',
            'From Table',
            'From Column',
            'To Table',
            'To Column'
        ]
    )


def validate_url(url):
    scheme, netloc, _, _, _, _ = urlparse(url)
    if not scheme or not netloc:
        raise ValueError(f"Invalid URL: {url}")
    return url


def normalize_url(url: str, default_scheme="https") -> str:
    scheme, netloc, path, params, query, fragment = urlparse(url)
    if not scheme:
        scheme = scheme or default_scheme
        url = urlunparse((scheme, path, "", params, query, fragment))
        scheme, netloc, path, params, query, fragment = urlparse(url)
    url_path = quote(path.rstrip("/"), "/%")
    params = quote_plus(params, ":&=")
    query = quote_plus(query, ":&=")
    fragment = fragment
    return urlunparse((scheme, netloc, url_path, params, query, fragment))


def normalize_fabric_path(path: Union[str, os.PathLike]) -> str:
    if not isinstance(path, (str, os.PathLike)):
        raise TypeError(f"folder_path must be a string or Path object, but got {type(path)}")

    # Ensure the path starts with a leading slash
    path = os.path.join("/", path)

    # trim leading slashes
    path = re.sub(r"^/+", "/", str(path))

    return os.path.normpath(path)


def split_fabric_path(path: Union[str, os.PathLike]) -> List[str]:
    if not isinstance(path, (str, os.PathLike)):
        raise TypeError(f"path must be a string or Path object, but got {type(path)}")

    normalized_path = normalize_fabric_path(path)
    return [name for name in normalized_path.split("/") if name]


def is_valid_uuid(val: Union[str, uuid.UUID]) -> bool:
    if isinstance(val, uuid.UUID):
        return True

    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False


def print_verbose(*args, verbose: int = 0, **kwargs):
    if verbose > 0:
        print(*args, **kwargs)


class LazyDotNetDate:
    def __init__(self, pandas_date):
        self._pandas_date = pandas_date
        self._dotnet_date = None

    def dotnet_date(self):
        if self._dotnet_date is None:
            # try hard to not parse the date every single invocation AND
            # not import System prior to having .NET initialized
            import System
            self._dotnet_date = System.DateTime.Parse(self._pandas_date.isoformat(), None, System.Globalization.DateTimeStyles.RoundtripKind)

        return self._dotnet_date


_dotnet_pandas_min_date = LazyDotNetDate(pd.Timestamp.min)
_dotnet_pandas_max_date = LazyDotNetDate(pd.Timestamp.max)


def dotnet_to_pandas_date(dt, milliseconds=False) -> Union[datetime.datetime, 'NaTType']:
    # convert NaN to NaT
    if pd.isna(dt):
        return pd.NaT

    # catch date issues early (e.g. dt.ToString() can be "1-01-01 00:00:00" which is not parsable by Pandas)
    if dt < _dotnet_pandas_min_date.dotnet_date() or dt > _dotnet_pandas_max_date.dotnet_date():
        return pd.NaT

    dotnet_format_string = "yyyy-MM-ddTHH:mm:ss"
    pandas_format_string = "%Y-%m-%dT%H:%M:%S"
    if milliseconds:
        dotnet_format_string += ".fff"
        pandas_format_string += ".%f"

    dt = pd.Timestamp(datetime.datetime.strptime(dt.ToString(dotnet_format_string), pandas_format_string))

    if dt < pd.Timestamp.min or dt > pd.Timestamp.max:
        return pd.NaT
    else:
        return dt


def clr_to_pandas_dtype(input_type: str) -> Optional[str]:
    if input_type == 'String':
        return 'string'
    elif input_type == 'Int64':
        return 'Int64'
    elif input_type == 'Int32':
        return 'Int64'
    elif input_type == 'Double':
        return 'Float64'
    elif input_type == 'Decimal':
        return 'Float64'
    elif input_type == 'Boolean':
        return 'boolean'   # different from 'bool', which converts nulls to 'False'
    else:
        return None


def convert_pascal_case_to_space_delimited(col_name: str) -> str:
    """
    Convert PascalCase to Space Delimited Case, handling all caps phrases like CPU and
    converting punctuation to spaces.
    """
    result = ""
    for i in range(len(col_name)):
        if col_name[i] in string.punctuation:
            result += " "
        else:
            # ignore the first character
            if i > 0 and col_name[i].isupper():
                # Ex: ...aB... -> ...a B... (ModelName --> Model Name)
                preceded_by_lower = col_name[i - 1].islower()
                # Ex: ...ABCc... -> ...AB Cc...  (CPUTime --> CPU Time)
                followed_by_lower = i < len(col_name) - 1 and col_name[i+1].islower()
                if preceded_by_lower or followed_by_lower:
                    result += " "

            result += col_name[i]

    # remove double whitespaces that may have been caused by punctuation
    result = " ".join(result.split())

    return result


def convert_space_delimited_case_to_pascal(col_name: str) -> str:
    """
    Convert Space Delimited Case to PascalCase.
    """
    return col_name.replace(" ", "")


def get_properties(obj, properties: Optional[Union[str, List[str]]] = None) -> Dict[str, Any]:
    if properties is None:
        return {}

    if isinstance(properties, str):
        properties = [properties]

    result = {}
    for prop in properties:
        # support both pascal and space delimited case
        prop_dotnet = convert_space_delimited_case_to_pascal(prop)
        prop_column = convert_pascal_case_to_space_delimited(prop)

        # get the value of the property
        value = None
        obj_local = obj
        for prop_path_element in prop_dotnet.split('.'):
            # a property can return different types (depending on the row e.g. CalculatedPartitionSource vs MPartition)
            prop_path_element = prop_path_element
            if not hasattr(obj_local, prop_path_element):
                value = None
                break
            value = obj_local = attrgetter(prop_path_element)(obj_local)

        # convert datetime to pandas datetime
        if isinstance(value, datetime.datetime):
            value = dotnet_to_pandas_date(value)
        elif value is None:
            pass
        elif not any([isinstance(value, t) for t in [str, int, bool, float]]):
            # convert enum and complex types to string to avoid C# leakage
            value = str(value)

        result[prop_column] = value

    return result


def collection_to_dataframe(collection: Iterable, definition: List[Tuple[str, Callable, str]], additional_properties: Optional[Union[str, List[str]]] = None) -> pd.DataFrame:
    """
    Convert a collection of objects to a Pandas DataFrame.

    Parameters
    ----------
    collection : Iterable
        The collection to convert.
    definition : List[Tuple[str, Callable, str]]
        The definition of the columns to create. Each tuple contains the column name, a function to extract the value and
        the pandas data type.

    Returns
    -------
    pd.DataFrame
        The DataFrame.
    """
    from sempy.fabric._client._utils import _init_analysis_services
    _init_analysis_services()

    from Microsoft.AnalysisServices.Tabular import CompatibilityViolationException

    rows = defaultdict(lambda: [])

    for element in collection:
        # regular definition
        for col_name, col_func, _ in definition:
            try:
                val = col_func(element)
            except CompatibilityViolationException:
                val = "Not supported (CompatibilityViolationException)"
            rows[col_name].append(val)

    # sort the columns according to definition
    df = pd.DataFrame({
        col_name: pd.Series(rows[col_name], dtype=col_type)
        for col_name, _, col_type in definition
    })

    if additional_properties is not None:
        rows_additional = []

        for element in collection:
            # dynamic props
            if isinstance(element, tuple):
                # get the last non-null element, it's the most specific one
                # customers can navigate via Parent.
                element = [x for x in element if x is not None][-1]

            # dynamically get the values for all properties
            rows_additional.append(get_properties(element, additional_properties))

        df = pd.concat([df, pd.DataFrame(rows_additional)], axis=1)

    return df


def try_import(module_name, error_message="", show_source_error=False, raise_exception=True, verbose=True):
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        if show_source_error:
            if error_message:
                error_message = f"{error_message} (source error: {e})"
            else:
                error_message = f"{e}"
        if raise_exception:
            raise RuntimeError(error_message)
        elif verbose and not error_message:
            print(error_message)
        return None


def capture_warnings(*warning_args, **warning_kwargs):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            import warnings
            with warnings.catch_warnings():
                warnings.filterwarnings(*warning_args, **warning_kwargs)
                ret = func(*args, **kwargs)
                return ret
        return wrapper
    return decorator


class SparkConfigTemporarily:
    """
    Temporarily set a Spark configuration value and restore it afterwards.

    Parameters
    ----------
    spark : pyspark.sql.SparkSession
        Spark session to set the configuration value on.
    config : Dict[str, str]
    """

    def __init__(self, spark, config):
        self.spark = spark
        self.config = config
        self.original_values = dict()
        for key in self.config:
            self.original_values[key] = spark.conf.get(key)

    def __enter__(self):
        for key, value in self.config.items():
            self.spark.conf.set(key, value)

    def __exit__(self, exc_type, exc_value, exc_tb):
        for key, value in self.original_values.items():
            self.spark.conf.set(key, value)


def to_multiplicity(relationship) -> str:
    from_cardinality = relationship.FromCardinality.ToString()
    to_cardinality = relationship.ToCardinality.ToString()
    map = {"One": "1", "Many": "m"}
    return f"{map[from_cardinality]}:{map[to_cardinality]}"


def dax_escape_table_name(table_name: str) -> str:
    """
    Escape single quotes in a table name.
    """
    return table_name.replace("'", "''")


def dax_escape_column_name(col_name: str) -> str:
    """
    Escape square brackets in a column/measures name.
    """
    return col_name.replace("]", "]]")
