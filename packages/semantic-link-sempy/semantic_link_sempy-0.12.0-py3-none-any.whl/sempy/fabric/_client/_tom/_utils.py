from functools import partial
from typing import Any, Iterator, List, Optional, Callable

from sempy._utils._graph import dfs
from sempy.fabric._client._utils import shared_docstring_params
from sempy.fabric._client._tom import TOMWrapper


edge_props_doc = """
    edge_props : List[str], default=None
        A list specifying all the edge properties of a TOM object. If set to None, the default list will be used:
        - "Annotations"
        - "CalculationGroup"
        - "CalculationItems"
        - "Columns"
        - "Cultures"
        - "DataSources"
        - "ExtendedProperties"
        - "Hierarchies"
        - "Levels"
        - "Measures"
        - "Members"
        - "Partitions"
        - "Perspectives"
        - "PerspectiveColumns"
        - "PerspectiveHierarchies"
        - "PerspectiveMeasures"
        - "PerspectiveTables"
        - "Relationships"
        - "Roles"
        - "TablePermissions"
        - "Tables"
    extend_props : List[str], default=None
        A list specifying additional edge properties of TOM objects to extend the default list.
    exclude_props : List[str], default=None
        A list specifying edge properties of TOM objects to exclude from the default list.
    filter_predicate : Callable[[Any], bool], default=None
        A function that accepts a TOM object as input and returns a boolean value.
        If predicate returns true, the current TOM object will be included in the output.
        If set to None (default value), every TOM object will be included.
""".strip()


@shared_docstring_params(edge_props_doc=edge_props_doc)
def display_tom(tom: TOMWrapper,
                display_format: Optional[Callable[[Any], str]] = None,
                edge_props: Optional[List[str]] = None,
                filter_predicate: Optional[Callable[[Any], bool]] = None,
                extend_props: Optional[List[str]] = None,
                exclude_props: Optional[List[str]] = None):
    """
    Print a tree view of a given TOM wrapper.

    Parameters
    ----------
    tom : sempy.fabric._client._tom.TOMWrapper
        The TOM wrapper object to be displayed.
    display_format : Optional[Callable[[Any], str]], default=None
        A function to format the display string of each object. If None, the
        default format '<TOM Object Type>[<TOM Object Name>]' is used.
    {edge_props_doc}

    Examples
    --------
    >>> display_tom(tom, filter_predicate=lambda o: str(o.ObjectType) == 'Table')
    # Print all tables
    └──Model[Model]
       ├──Table[DimCurrency]
       ├──Table[DimCustomer]
       ├──Table[Calendar]
       ├──Table[Dim Product]
       ├──Table[Internet Sales]
       ├──Table[Colors]
       ├──Table[calcy]
       ├──Table[MyParam]
       ├──Table[KPI]
       └──Table[Measure]

    >>> display_tom(tom, display_format=lambda o: o.Name, filter_predicate=lambda o: str(o.ObjectType) == 'Table')
    # Print all tables with customized format
    └──Model
       ├──DimCurrency
       ├──DimCustomer
       ├──Calendar
       ├──Dim Product
       ├──Internet Sales
       ├──Colors
       ├──calcy
       ├──MyParam
       ├──KPI
       └──Measure

    >>> display_tom(tom, filter_predicate=lambda o: str(o.ObjectType) == 'Column' and o.Parent.Name == 'Calendar' and 'Day' in o.Name)
    # Print all columns containing 'Day' in the given table 'Calendar'
    └──Model[Model]
       └──Table[Calendar]
          ├──Column[DayNumberOfWeek]
          ├──Column[EnglishDayNameOfWeek]
          ├──Column[SpanishDayNameOfWeek]
          ├──Column[FrenchDayNameOfWeek]
          ├──Column[DayNumberOfMonth]
          └──Column[DayNumberOfYear]
    """
    elbow = "└──"
    pipe = "│  "
    tee = "├──"
    blank = "   "
    all_nodes: set = set()
    visited: set = set()

    if display_format is None:
        def _format(o):
            base_name = f'{o.ObjectType}[{getattr(o, "Name", "")}]'
            # Print extra info for relationship
            if str(o.ObjectType) == 'Relationship':
                from_table = getattr(o, "FromTable", None)
                from_column = getattr(o, "FromColumn", None)
                to_table = getattr(o, "ToTable", None)
                to_column = getattr(o, "ToColumn", None)
                base_name += (f'[{getattr(from_table, "Name", "")}'
                              f'[{getattr(from_column, "Name", "")}]'
                              f'-> {getattr(to_table, "Name", "")}'
                              f'[{getattr(to_column, "Name", "")}]]')
            return base_name
        display_format = _format

    if filter_predicate:
        for leaf in iter_tom_descendants(tom.model,
                                         edge_props=edge_props,
                                         extend_props=extend_props,
                                         exclude_props=exclude_props,
                                         filter_predicate=filter_predicate):
            n = leaf
            while n is not None:
                all_nodes.add(n)
                n = getattr(n, 'Parent', None)

    def print_tree(node, last=True, header=''):
        visited.add(node)
        print(header + (elbow if last else tee) + display_format(node))
        children = list(iter_tom_children(node,
                                          edge_props=edge_props,
                                          extend_props=extend_props,
                                          exclude_props=exclude_props,
                                          filter_predicate=(lambda n: n in all_nodes) if filter_predicate else None))
        for i, c in enumerate(children):
            if c in visited:
                continue
            print_tree(c, header=header + (blank if last else pipe), last=i == len(children) - 1)

    print_tree(tom.model)


@shared_docstring_params(edge_props_doc=edge_props_doc)
def iter_tom_children(tom_obj: Any,
                      edge_props: Optional[List[str]] = None,
                      extend_props: Optional[List[str]] = None,
                      exclude_props: Optional[List[str]] = None,
                      filter_predicate: Optional[Callable[[Any], bool]] = None) -> Iterator[Any]:
    """
    Generate an iterator of all selected children TOM objects (i.e. direct descendants) from the given TOM object.

    TOM objects are considered connected if one is within the specified properties (edge properties) of the other.

    Only TOM objects derived from the `Tabular MetadataObject <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.metadataobject?view=analysisservices-dotnet>`__
    will be visited and retrieved.

    Parameters
    ----------
    tom_obj : TOM Object
        An object (e.g., table, column, measure) within a semantic model.
    {edge_props_doc}

    Yields
    ------
    TOM Object
        All children TOM objects descending from the given TOM object.
    """
    import Microsoft.AnalysisServices.Tabular as TOM
    from sempy.fabric._client._utils import dotnet_isinstance

    edges = edge_props or set([
            "Annotations",
            "CalculationGroup",
            "CalculationItems",
            "Columns",
            "Cultures",
            "DataSources"
            "ExtendedProperties",
            "Hierarchies",
            "Levels",
            "Measures",
            "Members",
            "Partitions",
            "Perspectives",
            "PerspectiveColumns",
            "PerspectiveHierarchies",
            "PerspectiveMeasures",
            "PerspectiveTables",
            "Relationships",
            "Roles",
            "TablePermissions",
            "Tables"
        ]).union(extend_props or []).difference(exclude_props or [])

    edges = sorted(list(edges))

    for edge in edges:
        if not hasattr(tom_obj, edge):
            continue
        children = getattr(tom_obj, edge)
        if dotnet_isinstance(children, TOM.MetadataObjectCollection):
            if filter_predicate is not None:
                yield from filter(filter_predicate, children)
            else:
                yield from children

        elif dotnet_isinstance(children, TOM.MetadataObject):
            if filter_predicate is None or filter_predicate(children):
                yield children


@shared_docstring_params(edge_props_doc=edge_props_doc)
def iter_tom_descendants(tom_obj: Any,
                         edge_props: Optional[List[str]] = None,
                         extend_props: Optional[List[str]] = None,
                         exclude_props: Optional[List[str]] = None,
                         filter_predicate: Optional[Callable[[Any], bool]] = None) -> Iterator[Any]:
    """
    Generate an iterator of all selected TOM objects descending from the given TOM object.
    TOM objects are considered connected if one is within the specified properties (edge properties) of the other.

    Only TOM objects derived from the `Tabular MetadataObject <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.metadataobject?view=analysisservices-dotnet>`__
    will be visited and retrieved.

    Parameters
    ----------
    tom_obj : TOM Object
        An object (e.g., table, column, measure) within a semantic model.
    {edge_props_doc}

    Yields
    ------
    TOM Object
        All reachable TOM objects descending from the given TOM object.
    """
    yield from dfs(tom_obj,
                   partial(iter_tom_children, edge_props=edge_props,
                           extend_props=extend_props,
                           exclude_props=exclude_props),
                   filter_predicate=filter_predicate)
