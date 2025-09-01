import pandas as pd
from numpy import ndarray
from typing import Any, Callable, Iterable, Dict, Union, Optional
from sempy.functions import _SSeries


class FabricSeries(_SSeries):
    """
    A series for storage and propogation of PowerBI metadata.

    Parameters
    ----------
    data : numpy.ndarray, typing.Iterable, dict, pandas.Series, default=None
        Contains data stored in Series. If data is a dict, argument order is
        maintained. Can also be a scalar value.
    *args : list
        Remaining arguments to be passed to standard pandas constructor.
    column_metadata : dict, default=None
        Information about series column to be stored and propogated.
    **kwargs : dict
        Remaining kwargs to be passed to standard pandas constructor.
    """
    def __init__(
        self,
        data: Optional[Union[ndarray, Iterable, dict, pd.DataFrame]] = None,
        *args: Any,
        column_metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any
    ):
        super().__init__(data, *args, column_metadata=column_metadata, **kwargs)

    @property
    def _constructor_expanddim(self) -> Callable:
        # Manipulation result should be a DataFrame
        from sempy.fabric import FabricDataFrame
        return FabricDataFrame

    @property
    def column_metadata(self) -> Optional[dict]:
        """
        Information for Series values.
        """
        return super(_SSeries, self).column_metadata

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
