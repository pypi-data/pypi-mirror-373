from sempy._metadata._mseries import MSeries
from typing import Callable


class _SSeries(MSeries):
    @property
    def _constructor_expanddim(self) -> Callable:
        # Manipulation result should be a DataFrame
        from sempy.functions._dataframe._sdataframe import _SDataFrame
        return _SDataFrame

    def __dir__(self):
        from sempy.functions._registry import _semantic_function_registry

        # get the list of the attributes of the parent class and this class
        result = list(super(MSeries, self).__dir__() + list(self.__dict__.keys()))

        # the try is for making debugging easier.
        try:
            result.extend(_semantic_function_registry().get_suggestions(self))
        except AttributeError as e:
            raise RuntimeError(e)
        return result

    def __getattr__(self, attr):
        try:
            return super(MSeries, self).__getattr__(attr)
        except AttributeError as e:
            from sempy.functions._registry import _semantic_function_registry

            func = _semantic_function_registry().get(attr, type(self))
            if func is None:
                raise e

            return func.apply(self)
