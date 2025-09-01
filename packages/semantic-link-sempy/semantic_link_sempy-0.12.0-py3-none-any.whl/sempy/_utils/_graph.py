from collections import deque
from typing import Any, Callable, Iterable, Optional, Literal


def dfs(
    node: Any,
    generate_neighbors: Callable[[Any], Iterable[Any]],
    filter_predicate: Optional[Callable[[Any], bool]] = None,
    prune_predicate: Optional[Callable[[Any], bool]] = None,
    order: Literal['post', 'pre'] = 'post'
) -> Iterable[Any]:
    """
    Performs a depth-first search (DFS) on a graph.

    Parameters
    ----------
    node : Any
        The starting node for the DFS.
    generate_neighbors : Callable[[Any], Iterable[Any]]
        A function that returns the neighbors of a given node.
    filter_predicate : Callable[[Any], bool], default=None
        A function that accepts a node as input and returns a boolean value.
        If predicate returns true, the current node will be included in the output.
        If set to None (default value), every node will be included.
    prune_predicate : Callable[[Any], bool], default=None
        A function that accepts a TOM object as input and returns a boolean value to determine if a node and its descendants should be kept during pruning.
        If predicate returns true, the current node will be added to the travesal path.
        If set to None (default value), every node will be traversed.
    order : Literal['post', 'pre'], default=None
        The order of traversal, either 'pre' for pre-order or 'post' for post-order, by default 'post'.

    Yields
    ------
    Any
        Reachable nodes from the DFS.
    """
    if order not in ['post', 'pre']:
        raise ValueError(f'order should be in {{"post", "pre"}}, but found {order}')

    visited = set()

    def _dfs(node: Any) -> Iterable[Any]:
        if node in visited:
            return

        visited.add(node)

        if prune_predicate is not None and not prune_predicate(node):
            return

        if order == 'pre' and (filter_predicate is None or filter_predicate(node)):
            yield node

        for neighbor in generate_neighbors(node):
            if neighbor not in visited:
                yield from _dfs(neighbor)

        if order == 'post' and (filter_predicate is None or filter_predicate(node)):
            yield node

    yield from _dfs(node)


def bfs(
    node: Any,
    generate_neighbors: Callable[[Any], Iterable[Any]],
    filter_predicate: Optional[Callable[[Any], bool]] = None,
    prune_predicate: Optional[Callable[[Any], bool]] = None
) -> Iterable[Any]:
    """
    Performs a breadth-first search (BFS) on a graph.

    Parameters
    ----------
    node : Any
        The starting node for the BFS.
    generate_neighbors : Callable[[Any], Iterable[Any]]
        A function that returns the neighbors of a given node.
    filter_predicate : Callable[[Any], bool], default=None
        A function that accepts a node as input and returns a boolean value.
        If predicate returns true, the current node will be included in the output.
        If set to None (default value), every node will be included.
    prune_predicate : Callable[[Any], bool], default=None
        A function that accepts a TOM object as input and returns a boolean value to determine if a node and its descendants should be kept during pruning.
        If predicate returns true, the current node will be added to the travesal path.
        If set to None (default value), every node will be traversed.

    Yields
    ------
    Any
        Reachable nodes from the BFS.
    """
    visited = set()
    queue = deque([node])

    while queue:
        node = queue.popleft()

        if node in visited:
            continue

        visited.add(node)

        if prune_predicate is not None and not prune_predicate(node):
            continue

        if filter_predicate is None or filter_predicate(node):
            yield node

        for neighbor in generate_neighbors(node):
            if neighbor not in visited:
                queue.append(neighbor)
