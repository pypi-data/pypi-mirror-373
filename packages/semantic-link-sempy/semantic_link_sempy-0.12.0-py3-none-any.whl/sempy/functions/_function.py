import inspect
from functools import wraps
from typing import Callable, List, Type, Optional, Union, TYPE_CHECKING
import pandas as pd
from sempy.functions._matcher_dataframe import (
    _default_auto_args_dataframe,
    _default_requirement_func_dataframe,
    _default_suggestion_func_dataframe
)
from sempy.functions._matcher_series import (
    _default_auto_args_series,
    _default_requirement_func_series
)

if TYPE_CHECKING:
    from sempy.fabric._dataframe._fabric_dataframe import FabricDataFrame
    from sempy.fabric._dataframe._fabric_series import FabricSeries
    from sempy._metadata._mdataframe import MDataFrame
    from sempy._metadata._mseries import MSeries


class SemanticFunction:
    """
    A base class for functions that can be suggested to the user based on semantic context.

    Parameters
    ----------
    name : str
        Function name.
    function : callable
        Function definition.
    requirement : callable
        Function that returns True if this SemanticFunction is applicable to a FabricDataFrame
        that is passed as an argument to the function.
    suggestion : list of str
        List of suggestions.
    """

    function: Callable
    wrapped_function: Callable
    requirement: Callable
    suggestion: Callable
    is_property: bool
    auto_args: Optional[Callable]

    def __init__(self, name,
                 func: Callable,
                 wrapped_function: Callable,
                 self_type: Type,
                 is_property: bool = False,
                 requirement=None,
                 suggestion=None):
        self.name = name
        self.function = func
        self.wrapped_function = wrapped_function
        self.is_property = is_property

        # build requirement function based on parameter annotations
        if requirement is None:
            if issubclass(self_type, pd.DataFrame):
                requirement = _default_requirement_func_dataframe(func)
                self.auto_args = _default_auto_args_dataframe(func)
            elif issubclass(self_type, pd.Series):
                requirement = _default_requirement_func_series(func)
                self.auto_args = _default_auto_args_series(func)
            else:
                raise TypeError(f"Unexpected self type {self_type}")

        # build suggestion function based on parameter annotations
        if suggestion is None:
            if issubclass(self_type, pd.DataFrame):
                suggestion = _default_suggestion_func_dataframe(func)
            elif issubclass(self_type, pd.Series):
                if is_property:
                    suggestion = lambda *_: [self.name]  # noqa: E731
                else:
                    suggestion = lambda *_: [f"{self.name}()"]  # noqa: E731
            else:
                raise TypeError(f"Unexpected self type {self_type}")

        self.requirement = requirement
        self.suggestion = suggestion
        self.signature = inspect.signature(self.function)

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.name})"

    def __call__(self, df_or_series: Union["FabricDataFrame", "FabricSeries"], *args, **kwargs):
        """
        Allow invocation of the function on a FabricDataFrame.

        Parameters
        ----------
        df_or_series : FabricDataFrame or FabricSeries
            Dataframe to apply the function to.
        *args : any
            Passed to `SemanticFunction.function`.
        **kwargs : any
            Passed to `SemanticFunction.function`.

        Returns
        -------
        any
            Value returned from this SemanticFunction's _function_.
        """
        if not self.is_applicable(df_or_series):
            raise TypeError(f"Can't apply {self} to {df_or_series}")
        return self.wrapped_function(df_or_series, *args, **kwargs)

    def is_applicable(self, df_or_series: Union["MDataFrame", "MSeries"]) -> bool:
        """
        Return True if function can be applied to the provided FabricDataFrame.

        Parameters
        ----------
        df_or_series : MDataFrame or MSeries
             Target semantic data frame.

        Returns
        -------
        bool
            Return True if function can be applied to the provided FabricDataFrame.
        """
        return self.requirement(df_or_series)

    def suggest_signature(self, df_or_series: Union["MDataFrame", "MSeries"]) -> List[str]:
        """
        Suggest signature for the provided FabricDataFrame.

        Parameters
        ----------
        df_or_series : MDataFrame or MSeries
            Target semantic data frame.

        Returns
        -------
        list of str
            List of suggestions.
        """
        if self.suggestion is not None:
            return self.suggestion(self.name, df_or_series)
        else:
            return [self.name]

    def apply(self, df_or_series: Union["FabricDataFrame", "FabricSeries"]):
        """
        Return a callable that applies the SemanticFunction to the given FabricDataFrame.

        Parameters
        ----------
        df_or_series : FabricDataFrame or FabricSeries
            Target semantic data frame.

        Returns
        -------
        callable
            A callable that applies the SemanticFunction to the given dataframe.
        """

        if self.is_property:
            return self.wrapped_function(df_or_series)
        else:

            @wraps(self.function)
            def wrapper(*args, **kwargs):
                args = list(args)
                args.insert(0, df_or_series)

                try:
                    # try to bind args to function signature to determine if anything is missing
                    self.signature.bind(*args, **kwargs)

                    return self.wrapped_function(*args, **kwargs)
                except TypeError:
                    if self.auto_args is None:
                        raise

                    # use auto-args as default and kwargs to override
                    auto_args = self.auto_args(df_or_series)
                    auto_args.update(kwargs)

                    # print(f"Using auto-args {auto_args}")
                    return self.wrapped_function(*args, **auto_args)

            return wrapper
