import pandas as pd
import inspect
import warnings

from numpy import ndarray
from typing import Any, Callable, Dict, Iterable, List, Optional, Union


class MDataFrame(pd.DataFrame):
    """
    An extension of a Pandas DataFrame that allows storage and propogation of column metadata.

    For operations between multiple objects, propogation is as follows:
        * ``merge`` - left object's metadata takes precedence.
        * ``concat`` - first object's metadata is used.

    Parameters
    ----------
    data : ndarray (structured or homogeneous), Iterable, dict or DataFrame
        Dict can contain Series, arrays, constants, dataclass or list-like objects. If
        data is a dict, column order follows insertion-order. If a dict contains Series
        which have an index defined, it is aligned by its index. This alignment also
        occurs if data is a Series or a DataFrame itself. Alignment is done on
        Series/DataFrame inputs.

        If data is a list of dicts, column order follows insertion-order.
    *args : Any
        Remaining arguments to be passed to standard pandas constructor.
    column_metadata : dict, default=None
        Information about dataframe columns to be stored and propogated.
    **kwargs : Any
        Remaining kwargs to be passed to standard pandas constructor.
    """

    _metadata = ["_column_metadata"]
    _column_metadata: Optional[dict] = None

    def __init__(
        self,
        data: Optional[Union[ndarray, Iterable, dict, pd.DataFrame]] = None,
        *args: Any,
        column_metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ):
        super().__init__(data, *args, **kwargs)  # type: ignore
        if column_metadata:
            self.column_metadata = column_metadata

    def __finalize__(self, other, method: Optional[str] = None, **kwargs) -> 'MDataFrame':
        """
        Override pandas __finalize__ to propagate metadata from other to self

        This is the only method of propagation for "General functions" such as
        pandas.concat([df1, df2]), pandas.merge(df1, df2) that are not executed on an object instance.
        Overriding the DataFrame method is therefore not an option.
        """
        self = super().__finalize__(other, method=method, **kwargs)  # type: ignore

        # dump_meta(self, other, method)

        column_metadata = self.column_metadata

        # pandas implements a large number of methods with "merge" and "concat" and slicing.
        # The physical implementation can be verified by placing a debugger breakpoint here.
        if method == "merge":
            column_metadata = _merge_metadata(other.left, other.right, other.suffixes)
        elif method == "concat":
            column_metadata = _concat_metadata(other.objs, self._headers)

        self._column_metadata = column_metadata
        self._trim_metadata_to_columns()

        return self

    def to_parquet(self, path: Any, *args, **kwargs) -> None:  # type: ignore
        """
        Write the DataFrame including metadata to a parquet file specified by path parameter using Arrow.

        Parameters
        ----------
        path : Any
            String containing the filepath to where the parquet should be saved.
        *args : Any
            Other args to be passed to PyArrow ``write_table``.
        **kwargs : Any
            Other kwargs to be passed to PyArrow ``write_table``.
        """
        import json
        import pyarrow as pa
        import pyarrow.parquet as pq

        table = pa.Table.from_pandas(self)

        if self.column_metadata:
            metadata = table.schema.metadata or {}
            metadata[b"column_metadata"] = json.dumps(self.column_metadata, default=lambda x: str(x))
            table = table.replace_schema_metadata(metadata)

        pq.write_table(table, path, *args, **kwargs)

    @property
    def _constructor(self) -> Callable:
        # Manipulation result has same dimension as original
        return type(self)

    @property
    def _constructor_sliced(self) -> Callable:
        # Manipulation result should be a Series
        from sempy._metadata._mseries import MSeries

        return MSeries

    def _column_metadata_setter(self, value: Optional[dict]) -> None:
        # NOTE: This is a workaround for the fact that super() doesn't work with property setters
        #       and with Pandas' use of __setattr__.
        # https://stackoverflow.com/questions/10810369/python-super-and-setting-parent-class-property
        if isinstance(value, dict):
            extra_keys = set(value.keys()) - set(self._headers)
            if extra_keys != set():
                raise ValueError(f"Columns not in the dataframe: {extra_keys}")
        elif value is not None:
            raise TypeError(f"Unexpected type {type(value)} for \"column_metadata\": not a dict or None")
        self._column_metadata = value

    @property
    def column_metadata(self) -> Optional[dict]:
        """
        Information for the columns in the table.
        """
        return self._column_metadata

    @column_metadata.setter
    def column_metadata(self, value: Optional[dict]) -> None:
        """
        Update column_metadata to new value.

        Parameters
        ----------
        value : dict
            New value for column_metadata.
        """
        self._column_metadata_setter(value)

    @property
    def _headers(self) -> List[str]:
        """
        Lists all column and index header names.
        """
        if isinstance(self.index, pd.MultiIndex):
            headers = self.index.names
        else:
            headers = [self.index.name] if self.index.name else []

        return headers + list(self.columns)

    def __getattribute__(self, name: str) -> Any:
        """
        Override/wrap pandas calls to tweak metadata.

        This could also be done by defining methods explicitly. Current arguments for doing it here:
        1. Likely less code, as multiple methods can be handled by a single code fragment.
        2. 'Catch all' approach will hopefully cover future needs.

        This design decision should be continuously evaluated as the code evolves.
        """
        attr = super().__getattribute__(name)
        # It is imperative that the check for attr.__module__ is after the inspect.ismethod()
        # to avoid infinite recursion. The check avoids unnecessary wraps, which simplifies stack traces.
        if inspect.ismethod(attr) and attr.__module__.startswith('pandas'):
            if name == "rename":
                # "rename" operation for inplace=True does not invoke __finalize__, so it must be done
                # via a method override/wrap. We choose to handle both variants here: inplace=False will
                # update self, while inplace=True will update result. We could examine the args to
                # perform the translation, but we choose to rely on the 1 to 1 correspondence of columns
                # in the original dataframe and the renamed one, which seems more future proof.
                original_headers = self._headers
                original_metadata = self._column_metadata

                def _column_metadata_renamer(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    self._rename_metadata(original_metadata, original_headers)
                    if result is not None:
                        result._rename_metadata(original_metadata, original_headers)
                    return result

                return _column_metadata_renamer
            else:
                # The trimming of column metadata after all pandas operations is motivated by the behavior of
                # inplace=True, which may result in dropped columns (e.g. drop(), dropna()). This is
                # a "catch all" approach for cases when __finalize__ may not kick in.
                def _column_metadata_trimmer(*args, **kwargs):
                    result = attr(*args, **kwargs)
                    self._trim_metadata_to_columns()
                    return result

                return _column_metadata_trimmer
        else:
            return attr

    def _trim_metadata_to_columns(self):
        if self._column_metadata:
            self._column_metadata = {
                k: v for k, v in self._column_metadata.items() if k in self._headers
            }

    def _rename_metadata(self, original_metadata: Optional[dict], original_headers: List[str]):
        if original_metadata:
            renamed_metadata: dict = {}
            # Renamed columns must map to each other at index.
            assert len(original_headers) == len(self._headers)
            for i in range(len(original_headers)):
                value = original_metadata.get(original_headers[i], None)
                # Not all columns may have metadata
                if value:
                    renamed_metadata[self._headers[i]] = value
            self._column_metadata = renamed_metadata
        else:
            self._column_metadata


def _merge_metadata(left: pd.DataFrame, right: pd.DataFrame, suffixes: tuple) -> dict:
    merged_metadata = {}

    # The choice of logic here is tricky, since it must account for columns that originally
    # ended with one of the suffixes, even before the merge. The suffix cannot be used
    # for determinging the origin of the column. Suffix is applied only in case of conflict.
    def _merge_for_suffix(df, other, suffix):
        column_metadata = getattr(df, "column_metadata", None)
        if column_metadata:
            for name, metadata in column_metadata.items():
                if name in other.columns:
                    if suffix is not None:
                        suffixed = name + suffix
                        merged_metadata[suffixed] = metadata
                    else:
                        merged_metadata[name] = metadata
                else:
                    merged_metadata[name] = metadata

    # The join key columns may be matching in both tables. We want "left" to take
    # precedence, so we process "left" after right, so that it overrides.
    _merge_for_suffix(right, left, suffixes[1])
    _merge_for_suffix(left, right, suffixes[0])

    return merged_metadata


def _concat_metadata(objs: list, columns: List[str]) -> dict:
    merged_metadata = {}
    for name in columns:
        metadata_candidates = [
            o.column_metadata[name]
            for o in objs
            if _column_metadata_has(name, o)
        ]
        if len(metadata_candidates) > 0:
            merged_metadata[name] = metadata_candidates[0]
        if len(metadata_candidates) > 1:
            if any(c != metadata_candidates[0] for c in metadata_candidates):
                warnings.warn(f"Conflicting metadata for column '{name}'. Choosing first encountered")

    return merged_metadata


def _column_metadata_has(name: str, frame: pd.DataFrame) -> bool:
    column_metadata = getattr(frame, "column_metadata", None)
    if column_metadata:
        return name in column_metadata
    else:
        return False
