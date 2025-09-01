from typing import Callable, Dict, List, Optional, Tuple
from inspect import signature
import numpy as np

from sempy._metadata._mdataframe import MDataFrame
from sempy.functions.matcher import SeriesMatcher, AlwaysTrueMatcher
from sempy.functions._util import _ParameterRequirement, _extract_requirement


def _find_first_match(
    matcher: SeriesMatcher, columns: List[str], df: MDataFrame
) -> Optional[str]:
    for col in columns:
        if matcher.matches(df[col]):  # type: ignore
            return col

    return None


def _get_or_create_parameter_requirements(func) -> List[_ParameterRequirement]:
    if not hasattr(func, "__parameter_requirements_dataframe__"):
        func.__parameter_requirements_dataframe__ = _extract_requirement_func_dataframe(func)

    return func.__parameter_requirements_dataframe__


def _default_auto_args_dataframe(func: Callable) -> Callable[[MDataFrame], Dict[str, str]]:
    requirements = _get_or_create_parameter_requirements(func)

    def _default_auto_func_inner(df: MDataFrame) -> Dict[str, str]:
        param_assignments = {}

        columns = list(df.columns)

        for req in requirements:
            # skip anonymous parameters (e.g. NameMatcher() is passed as positional arg to semantic_parameters)
            if req.name is None:
                continue

            col_matches = [col for col in columns if req.matcher.matches(df[col])]  # type: ignore

            col_matches_len = len(col_matches)

            # mandatory columns must match
            # we must get a unique match
            if col_matches_len == 1:
                param_assignments[req.name] = col_matches[0]
                columns.remove(col_matches[0])
            elif col_matches_len > 1:
                return {}
            elif col_matches_len == 0 and req.mandatory:
                return {}

        return param_assignments

    return _default_auto_func_inner


def _default_requirement_func_dataframe(func: Callable) -> Callable[[MDataFrame], bool]:
    requirements = _get_or_create_parameter_requirements(func)

    mandatory = [req for req in requirements if req.mandatory]

    def _default_requirement_func_inner(df: MDataFrame) -> bool:
        columns = list(df.columns)

        # check if all mandatory columns are present
        for req in mandatory:
            # any matcher needs to match
            match = _find_first_match(req.matcher, columns, df)
            if not match:
                return False

            # remove matched column from candidate list
            columns.remove(match)

        return True

    return _default_requirement_func_inner


def _default_suggestion_func_dataframe(func: Callable) -> Callable[[str, MDataFrame], List[str]]:
    all_requirements = _get_or_create_parameter_requirements(func)

    # filter out anonymous parameters
    all_requirements = list(filter(lambda x: x.name is not None, all_requirements))

    # make tuple(index, value) for sorting (want to maintain order of original parameters)
    all_requirements_with_idx = [(i, req) for i, req in enumerate(all_requirements)]

    def _default_suggestion_func_inner(name: str, df: MDataFrame) -> List[str]:
        top_n = 10

        # recursively find the first 10 combinations
        def top_n_comb(columns: List[str],
                       requirements: List[Tuple[int, _ParameterRequirement]],
                       args: List[Tuple[int, str]] = []) -> List[str]:
            if len(requirements) == 0 or len(columns) == 0:
                return [", ".join(map(lambda x: x[1], args))]

            # use dict instead of set to maintain order
            all: Dict[str, None] = dict()
            for idx, req in requirements:
                result = []
                for col in columns:
                    if req.matcher.matches(df[col]):  # type: ignore
                        if req.is_list:
                            arg = f"{req.name}=['{col}']"
                        else:
                            arg = f"{req.name}='{col}'"

                        new_args = list(args)
                        new_args.append((idx, arg))

                        # sort by index
                        new_args.sort(key=lambda x: x[0])

                        # recurse and explore more options
                        result.extend(top_n_comb(
                            [x for x in columns if x != col],
                            [x for x in requirements if x[1] != req],
                            new_args))

                # if mandatory and no match, return empty list
                if req.mandatory and len(result) == 0:
                    return []

                all.update({r: None for r in result})

                if len(all) > top_n:
                    return list(all.keys())[:top_n]

            if np.all([not req[1].mandatory for req in requirements]):
                # all are options
                all[", ".join(map(lambda x: x[1], args))] = None

            return list(all.keys())

        arguments = top_n_comb(list(df.columns), all_requirements_with_idx)

        return [f"{name}({arg})" for arg in arguments]
    return _default_suggestion_func_inner


def _extract_requirement_func_dataframe(func) -> List[_ParameterRequirement]:
    # get function signature
    sig = signature(func)

    if not hasattr(func, "__sempy_parameters__"):
        return [_ParameterRequirement("<anonymous>", False, AlwaysTrueMatcher(), False)]

    # check that named parameters are in signature
    for param_name, param_type in func.__sempy_parameters__.items():
        if not (param_name is None or param_name in sig.parameters):
            raise ValueError(f"'{func.__name__}': parameter '{param_name}' not found in function signature")

    # collect all parameters
    parameters = []
    for param_name, param_type in func.__sempy_parameters__.items():
        if param_name is None:
            # anonymous parameters w/o name
            parameters.extend([(None, pt) for pt in param_type])
        else:
            # named parameters
            parameters.append((param_name, param_type))

    # extract requirements
    requirements = []
    for param_name, param_type in parameters:
        req = _extract_requirement(param_name, param_type)
        if req is not None:
            requirements.append(req)

    if len(requirements) == 0:
        raise ValueError(f"No column type requirements found for function '{func.__name__}'")

    return requirements
