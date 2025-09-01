from typing import Any, Type, Optional, Union
from sempy.functions.matcher import AlwaysTrueMatcher, OrMatcher, SeriesMatcher, TypeMatcher


class _ParameterRequirement:
    def __init__(
        self, name: str, mandatory: bool, matcher: SeriesMatcher, is_list: bool
    ):
        self.name = name
        self.mandatory = mandatory
        self.matcher = matcher
        self.is_list = is_list

    def __repr__(self) -> str:
        return f"ParameterRequirement({self.name}, mandatory={self.mandatory}, is_list={self.is_list}, {self.matcher})"


def _type_to_matcher(param_type_or_matcher: Type) -> SeriesMatcher:
    """
    Matchers can either be provided as type annotations or as matcher instances.
    The annotations can be both types (e.g. any, int, LatitudeMatcher, ...) or instances of SeriesMatcher.
    """
    if param_type_or_matcher == Any or param_type_or_matcher == any:
        return AlwaysTrueMatcher()

    if isinstance(param_type_or_matcher, SeriesMatcher):
        return param_type_or_matcher

    if issubclass(param_type_or_matcher, SeriesMatcher):
        # instantiate the matcher
        return param_type_or_matcher()

    return TypeMatcher(param_type_or_matcher)


def _extract_requirement(param_name: str, param_type: Type) -> Optional[_ParameterRequirement]:
    matcher: SeriesMatcher
    mandatory = True
    is_list = False

    # most complex: Optional[List[Union[str, int, mdatareq]]]
    # Optional is actuallly Union[T, None]
    if "__origin__" in dir(param_type) and \
       param_type.__origin__ == Union and \
       len(param_type.__args__) == 2 and \
       param_type.__args__[1] == type(None):  # noqa: E721
        mandatory = False
        param_type = param_type.__args__[0]

    if "__origin__" in dir(param_type) and param_type.__origin__ == list:
        is_list = True
        param_type = param_type.__args__[0]

    if "__origin__" in dir(param_type) and param_type.__origin__ == Union:
        matcher = OrMatcher(*map(_type_to_matcher, param_type.__args__))
    else:
        matcher = _type_to_matcher(param_type)

    return _ParameterRequirement(param_name, mandatory, matcher, is_list)
