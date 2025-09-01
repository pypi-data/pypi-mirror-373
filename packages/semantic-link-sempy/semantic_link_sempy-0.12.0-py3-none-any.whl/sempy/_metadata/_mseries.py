import pandas as pd
from typing import Any, Dict, Optional, Callable


class MSeries(pd.Series):
    """
    An extension of a Pandas Series that allows storage and propogation of column metadata.

    Parameters
    ----------
    data : numpy.ndarray, iterable, dict or scalar value
        Contains data stored in Series. If data is a dict, argument order is
        maintained.
    *args : Any
        Remaining arguments to be passed to standard pandas constructor.
    column_metadata : dict, default=None
        Information about series column to be stored and propogated.
    **kwargs : Any
        Remaining kwargs to be passed to standard pandas constructor.
    """

    _metadata = ["name", "_column_metadata"]
    _column_metadata: Optional[dict] = None

    def __init__(
        self,
        data=None,
        *args,
        column_metadata: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        super().__init__(data, *args, **kwargs)  # type: ignore
        if column_metadata:
            self.column_metadata = column_metadata

    def __finalize__(self, other, method: Optional[str] = None, **kwargs) -> 'MSeries':
        """Override pandas __finalize__ to propagate metadata from other to self"""
        self = super().__finalize__(other, method=method, **kwargs)  # type: ignore

        if self.column_metadata and self.name in self.column_metadata:
            self.column_metadata = {self.name: self.column_metadata[self.name]}

        return self

    @property
    def _constructor(self) -> Callable:
        # Manipulation result has same dimension as original
        return type(self)

    @property
    def _constructor_expanddim(self) -> Callable:
        # Manipulation result should be a DataFrame
        from sempy._metadata._mdataframe import MDataFrame
        return MDataFrame

    def _column_metadata_setter(self, value: Optional[dict]) -> None:
        # NOTE: This is a workaround for the fact that super() doesn't work with property setters
        #       and with Pandas' use of __setattr__.
        # https://stackoverflow.com/questions/10810369/python-super-and-setting-parent-class-property
        if isinstance(value, dict):
            extra_keys = set(value.keys()) - {self.name}
            if extra_keys != set():
                raise ValueError(f"Labels not in the series: {extra_keys}")
        elif value is not None:
            raise TypeError(f" Unexpected type {type(value)} for \"column_metadata\": not a dict or None")
        self._column_metadata = value

    @property
    def column_metadata(self) -> Optional[dict]:
        """
        Information for Series values.
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
