from sempy._metadata._mseries import MSeries
from sempy.functions._util import _ParameterRequirement, _extract_requirement
from typing import Callable, Optional


def _extract_requirement_func_series(func: Callable) -> _ParameterRequirement:
    if not hasattr(func, "__sempy_series_type__"):
        raise ValueError(f"No series type requirements found for function {func.__name__}")

    requirement = _extract_requirement("<anonymous series>", func.__sempy_series_type__)

    if requirement is None:
        raise ValueError(f"No series type requirements found for function '{func.__name__}'")

    if not requirement.mandatory:
        raise ValueError("Series type requirements must be mandatory")

    if requirement.is_list:
        raise ValueError("Series type requirements cannot be list types")

    return requirement


def _get_or_create_parameter_requirements(func) -> _ParameterRequirement:
    if not hasattr(func, "__parameter_requirements_series__"):
        func.__parameter_requirements_series__ = _extract_requirement_func_series(func)

    return func.__parameter_requirements_series__


def _default_auto_args_series(func: Callable) -> Callable[[MSeries], Optional[str]]:
    requirement = _get_or_create_parameter_requirements(func)

    if requirement.name is None:
        return lambda _: None

    return lambda series: requirement.name if requirement.matcher.matches(series) else None


def _default_requirement_func_series(func: Callable) -> Callable[[MSeries], bool]:
    requirement = _get_or_create_parameter_requirements(func)

    return requirement.matcher.matches
