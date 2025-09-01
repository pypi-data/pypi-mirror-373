from collections import OrderedDict
from typing import Callable, Dict, List, Optional, TypeVar, Type, Union, TYPE_CHECKING
from functools import wraps
import importlib.util
from sempy._utils._log import get_mds_fields, mds_log, SemPyExtractor
import pandas as pd

if TYPE_CHECKING:
    from sempy.fabric._dataframe._fabric_dataframe import FabricDataFrame
    from sempy.fabric._dataframe._fabric_series import FabricSeries

T = TypeVar("T")


def semantic_parameters(*args, **kwargs) -> Callable:
    """
    Attach the column type matcher to a function.

    Parameters
    ----------
    *args : list
        A list of column type matchers for which the resolve column name is ignored.
    **kwargs : dict
        A dictionary of column type matchers where key is the column name and value is the matcher.

    Returns
    -------
    typing.Callable
        The decorated function injection the column type matchers.
    """
    def decorator(func):
        if not hasattr(func, "__sempy_parameters__"):
            # make sure the arguments remain ordered
            func.__sempy_parameters__ = OrderedDict()

        func.__sempy_parameters__[None] = args
        func.__sempy_parameters__.update(kwargs)

        return func

    return decorator


def _semantic_decorator(
    name: Optional[str] = None,
    is_property: bool = False,
    requirement: Optional[Callable[[Union["FabricDataFrame", "FabricSeries"]], bool]] = None,
    suggestion: Optional[Callable[[str, Union["FabricDataFrame", "FabricSeries"]], List[str]]] = None,
    pip_packages: Optional[List[str]] = None,
    series_type: Optional[Type] = None,
):
    def semantic_function_wrapper(func):
        # allow for function name override
        func_name = func.__name__ if name is None else name

        # inject series type requirement
        if series_type is not None:
            func.__sempy_series_type__ = series_type

        @wraps(func)
        def pip_guard(*args, **kwargs):
            # any packages specified
            if pip_packages is not None:
                # any package missing?
                if any([importlib.util.find_spec(name) is None for name in pip_packages]):
                    pip_packages_str = ' '.join(pip_packages)
                    raise ValueError(f"Missing required packages. Please install using %pip install {pip_packages_str}")
                    # # install all packages
                    # import subprocess
                    # print(f"Auto-installing packages: {pip_packages_str}")
                    # result = subprocess.run(f"pip install {pip_packages_str}", shell=True, capture_output=True)

                    # print(result.stdout.decode("utf-8"))
                    # print(result.stderr.decode("utf-8"))

            return func(*args, **kwargs)

        # inject telemetry
        class FunctionExtractor(SemPyExtractor):

            def get_completion_message_dict(self, result, arg_dict) -> Dict:
                d = super().get_completion_message_dict(result, arg_dict)

                d["func_name_override"] = func_name

                df = arg_dict.get("df", None)
                if df is not None and isinstance(df, pd.DataFrame):
                    d['shape'] = df.shape

                series = arg_dict.get("series", None)
                if series is not None and isinstance(series, pd.Series):
                    d['shape'] = series.shape

                return d

        logged_pip_guard = mds_log(FunctionExtractor(), init_mds_fields=get_mds_fields)(pip_guard)

        # register function
        from sempy.functions._registry import _semantic_function_registry
        _semantic_function_registry().add(func_name, func, logged_pip_guard, is_property, requirement, suggestion)

        return logged_pip_guard

    return semantic_function_wrapper


def semantic_property(
    name: Optional[str] = None,
    requirement: Optional[Callable[[Union["FabricDataFrame", "FabricSeries"]], bool]] = None,
    suggestion: Optional[Callable[[str, Union["FabricDataFrame", "FabricSeries"]], List[str]]] = None,
    pip_packages: Optional[List[str]] = None,
    series_type: Optional[Type] = None,
) -> Callable:
    """
    Decorator for registering a property as a SemanticFunction.

    Parameters
    ----------
    name : str, default=None
        Override function name.
    requirement : typing.Callable
        Function that returns True if this SemanticFunction is applicable to a dataframe
        that is passed as an argument to the function.
    suggestion : list of str
        List of suggestions.
    pip_packages : list of str
        List of pip packages to include in installation message.
    series_type : type
        Expected type if the semantic function should be applied on a :class:`~sempy.fabric.FabricSeries`.

    Returns
    -------
    typing.Callable
        Decorated function.
    """

    return _semantic_decorator(name, True, requirement, suggestion, pip_packages, series_type)


def semantic_function(
    name: Optional[str] = None,
    requirement: Optional[Callable[[Union["FabricDataFrame", "FabricSeries"]], bool]] = None,
    suggestion: Optional[Callable[[str, Union["FabricDataFrame", "FabricSeries"]], List[str]]] = None,
    pip_packages: Optional[List[str]] = None,
    series_type: Optional[Type] = None,
) -> Callable:
    """
    Decorator for registering a function as a SemanticFunction.

    Parameters
    ----------
    name : str, default=None
        Override function name.
    requirement : typing.Callable
        Function that returns True if this SemanticFunction is applicable to a dataframe
        that is passed as an argument to the function.
    suggestion : list of str
        List of suggestions.
    pip_packages : list of str
        List of pip packages to include in installation message.
    series_type : type
        Expected type if the semantic function should be applied on a :class:`~sempy.fabric.FabricSeries`.

    Returns
    -------
    typing.Callable
        Decorated function.
    """

    return _semantic_decorator(name, False, requirement, suggestion, pip_packages, series_type)
