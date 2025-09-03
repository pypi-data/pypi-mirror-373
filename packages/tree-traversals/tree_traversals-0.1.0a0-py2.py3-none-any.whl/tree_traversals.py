# coding=utf-8
# Copyright (c) 2025 Jifeng Wu
# Licensed under the MIT License. See LICENSE file in the project root for full license information.
from collections import deque
from typing import Callable, Deque, Iterable, Iterator, Tuple, TypeVar

from cowlist import COWList

T = TypeVar('T')


def pre_order_dfs(start_node, get_descendants, ancestry=COWList()):
    # type: (T, Callable[[T], Iterable[T]], COWList[T]) -> Iterator[Tuple[COWList[T], T]]
    """
    Traverse a tree in pre-order (node, then children) depth-first order.

    This generator yields each node in the tree along with an immutable ancestry stack
    representing the path from the root node to the current node's parent.

    Args:
        start_node: The root node to begin traversal from.
        get_descendants: A function that takes a node and returns an iterable of its child nodes.
        ancestry: A COWList containing the ancestor path up to this node.
                  (Used internally during recursive calls; users should not pass this.)

    Yields:
        Tuple[COWList[T], T]: For each node in the pre-order traversal, yields a tuple of:
            - COWList[T]: An immutable list of ancestor nodes (empty for the root).
            - T: The current node.
    """
    # Visit start node
    yield ancestry, start_node

    # Get descendants and recurse
    descendant_ancestry = ancestry.append(start_node)
    for descendant in get_descendants(start_node):
        for _ in pre_order_dfs(descendant, get_descendants, descendant_ancestry):
            yield _


def post_order_dfs(start_node, get_descendants, ancestry=COWList()):
    # type: (T, Callable[[T], Iterable[T]], COWList[T]) -> Iterator[Tuple[COWList[T], T]]
    """
    Traverse a tree in post-order (children, then node) depth-first order.

    This generator yields each node after its descendants, along with an immutable ancestry stack
    representing the path from the root node to the current node's parent.

    Args:
        start_node: The root node to begin traversal from.
        get_descendants: A function that takes a node and returns an iterable of its child nodes.
        ancestry: A COWList containing the ancestor path up to this node.
                  (Used internally during recursive calls; users should not pass this.)

    Yields:
        Tuple[COWList[T], T]: For each node in the post-order traversal, yields a tuple of:
            - COWList[T]: An immutable list of ancestor nodes (empty for the root).
            - T: The current node.
    """
    # Get descendants and recurse
    descendant_ancestry = ancestry.append(start_node)
    for descendant in get_descendants(start_node):
        for _ in post_order_dfs(descendant, get_descendants, descendant_ancestry):
            yield _

    # Visit start node
    yield ancestry, start_node


def layer_order_bfs(start_node, get_descendants, ancestry=COWList()):
    # type: (T, Callable[[T], Iterable[T]], COWList[T]) -> Iterator[Tuple[COWList[T], T]]
    """
    Traverse a tree in layer-order (breadth-first level order).

    This generator yields each node in the tree along with an immutable ancestry stack
    representing the path from the root node to the current node's parent.

    Args:
        start_node: The root node to begin traversal from.
        get_descendants: A function that takes a node and returns an iterable of its child nodes.
        ancestry: A COWList containing the ancestor path up to this node.
                  (Used internally during recursion; users should not pass this.)

    Yields:
        Tuple[COWList[T], T]: For each node in the layer-order traversal, yields a tuple of:
            - COWList[T]: An immutable list of ancestor nodes (empty for the root).
            - T: The current node.
    """
    ancestry_and_node_queue = deque([(ancestry, start_node)])  # type: Deque[Tuple[COWList[T], T]]

    while ancestry_and_node_queue:
        ancestry, node = ancestry_and_node_queue.popleft()

        yield ancestry, node

        descendant_ancestry = ancestry.append(node)
        for descendant in get_descendants(node):
            ancestry_and_node_queue.append((descendant_ancestry, descendant))
