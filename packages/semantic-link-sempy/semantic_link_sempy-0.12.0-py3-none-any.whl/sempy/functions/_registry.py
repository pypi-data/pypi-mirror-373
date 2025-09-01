from collections import defaultdict
from sempy._metadata._mdataframe import MDataFrame
from sempy._metadata._mseries import MSeries
from sempy.functions._function import SemanticFunction
import pandas as pd
import importlib
import pkgutil
from inspect import getsourcefile
from typing import Callable, Dict, List, Optional, Type, Union
import warnings


# see https://packaging.python.org/en/latest/guides/creating-and-discovering-plugins/#using-naming-convention
class _SemanticFunctionRegistry:
    _registry: Dict[Type, Dict[str, "SemanticFunction"]]

    def __init__(self) -> None:
        self._registry = defaultdict(dict)

    def _discover(self) -> None:
        # iterate over modules to trigger registration
        for finder, name, ispkg in pkgutil.iter_modules():
            if name.startswith('sempy_functions_'):
                try:
                    importlib.import_module(name)
                except Exception as e:
                    warnings.warn(f"Error importing semantic function plugin module '{name}': {e}")

    def add(self,
            name: str,
            func: Callable,
            wrapped_func: Callable,
            is_property: bool,
            requirement=None,
            suggestion=None) -> None:
        # check the type annotation of the first parameter (dataframe vs series)
        annotations = func.__annotations__
        annotation_args = list(annotations.keys())

        if len(annotation_args) == 0:
            raise ValueError(f"Function '{name}' must have type annotation for at least first parameter")

        first_arg = annotations[annotation_args[0]]

        if not isinstance(first_arg, type):
            raise ValueError(f"First parameter of '{name}' must be type annotated: {first_arg}")

        if not issubclass(first_arg, (pd.DataFrame, pd.Series)):
            raise ValueError(f"First parameter of '{name}' must be annotated as DataFrame or Series: {first_arg}")

        _registry_per_type = self._registry[first_arg]

        if name in _registry_per_type:
            # we need to use the latest in case the user wants to redefine in the notebook as part of developing the function
            warnings.warn(f"Duplicate semantic function name: {name}. Replacing {getsourcefile(_registry_per_type[name].function)} with {getsourcefile(func)}")

        _registry_per_type[name] = SemanticFunction(name, func, wrapped_func, first_arg, is_property, requirement, suggestion)

    def _find_registries(self, first_arg_type: Type) -> List[Dict[str, "SemanticFunction"]]:
        # find all sub-type matches
        return [reg for reg_type, reg in self._registry.items() if issubclass(first_arg_type, reg_type)]

    def get_applicable(self, df_or_series: Union[MDataFrame, MSeries]) -> List["SemanticFunction"]:
        """
        Returns all functions that are applicable to the given DataFrame or Series.

        Returns
        -------
        List[SemanticFunction]
            List of applicable functions.
        """
        return [func
                for reg in self._find_registries(type(df_or_series))
                for func in reg.values()
                if func.is_applicable(df_or_series)]

    def get_suggestions(self, df_or_series: Union[MDataFrame, MSeries]) -> List[str]:
        """
        Return a list of IntelliSense suggestions for the given DataFrame or Series.
        If a function is applicable, it will return a suggestion with auto-completion for the function's parameters.
        Otherwise, the plain function name is returned.

        Parameters
        ----------
        df_or_series : MDataFrame or MSeries
            The DataFrame or Series to get suggestions for.

        Returns
        -------
        List[str]
            List of suggestions.
        """
        suggestions = []

        for reg in self._find_registries(type(df_or_series)):
            for func in reg.values():
                if func.is_applicable(df_or_series):
                    suggestions.extend(func.suggest_signature(df_or_series))
                else:
                    suggestions.append(func.name)

        return suggestions

    def get(self, name, type) -> Optional["SemanticFunction"]:
        # find the best match (=most specific first)
        for reg in self._find_registries(type):
            if name in reg:
                return reg[name]

        return None


_global_semantic_function_registry: Optional[_SemanticFunctionRegistry] = None


def _semantic_function_registry() -> _SemanticFunctionRegistry:
    global _global_semantic_function_registry

    if _global_semantic_function_registry is None:
        _global_semantic_function_registry = _SemanticFunctionRegistry()
        _global_semantic_function_registry._discover()

    return _global_semantic_function_registry
