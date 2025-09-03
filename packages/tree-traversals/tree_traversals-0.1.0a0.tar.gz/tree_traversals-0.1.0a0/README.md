# tree-traversals

_Efficient and generic traversals for any Python tree structure with full ancestor paths._

## Installation

```bash
pip install tree-traversals
```

## Supported Traversal Functions

| Traversal Function | Order                             | Yields                              |
|--------------------|-----------------------------------|-------------------------------------|
| `pre_order_dfs`    | Node, then children (depth-first) | (`ancestry`, `node`) in preorder    |
| `post_order_dfs`   | Children, then node (depth-first) | (`ancestry`, `node`) in postorder   |
| `layer_order_bfs`  | By tree level (breadth-first)     | (`ancestry`, `node`) in layer order |

All traversals:

- Take a starting node and a function to get descendants,
- Return an immutable [`cowlist`](https://pypi.org/project/cowlist/) stack representing the full path from root to the
  current node, along with the current node itself.

## Usage

```python
# coding=utf-8
from __future__ import print_function
from typing import Dict, List
from tree_traversals import (
    pre_order_dfs,
    post_order_dfs,
    layer_order_bfs
)

# Consider a simple binary tree (as a dict)
# - A
#   - B
#     - D
#     - E
#   - C
#     - F
tree = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': [],
    'F': []
}  # type: Dict[str, List[str]]


def get_children(n):
    # type: (str) -> List[str]
    return tree[n]


# Then, you can perform any traversal easily:
print("Preorder DFS:")
for path, node in pre_order_dfs('A', get_children):
    print(repr(path), '->', repr(node))
# Preorder DFS:
# COWList([]) -> 'A'
# COWList(['A']) -> 'B'
# COWList(['A', 'B']) -> 'D'
# COWList(['A', 'B']) -> 'E'
# COWList(['A']) -> 'C'
# COWList(['A', 'C']) -> 'F'

print("\nPostorder DFS:")
for path, node in post_order_dfs('A', get_children):
    print(repr(path), '->', repr(node))
# Postorder DFS:
# COWList(['A', 'B']) -> 'D'
# COWList(['A', 'B']) -> 'E'
# COWList(['A']) -> 'B'
# COWList(['A', 'C']) -> 'F'
# COWList(['A']) -> 'C'
# COWList([]) -> 'A

print("\nLayer Order BFS:")
for path, node in layer_order_bfs('A', get_children):
    print(repr(path), '->', repr(node))
# Layer Order BFS
# COWList([]) -> 'A'
# COWList(['A']) -> 'B'
# COWList(['A']) -> 'C'
# COWList(['A', 'B']) -> 'D'
# COWList(['A', 'B']) -> 'E'
# COWList(['A', 'C']) -> 'F'
```

## Motivation

When working with trees, structure is easy - but traversal patterns are often rewritten, customized, and bug-prone.
`tree-traversals` lets you:

- Traverse any tree with a single function and a child-getter.
- Access the *full ancestor path* at every node.
- Clean up and de-duplicate your recursive tree code.
- Support any tree-shaped data—dicts, lists, ASTs, DOMs, file trees, you name it.

## Contributing

Contributions are welcome! Please submit pull requests or open issues on the GitHub repository.

## License

This project is licensed under the [MIT License](LICENSE).