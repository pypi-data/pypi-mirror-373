# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

import itertools
import re
from collections import deque
from collections.abc import Iterator
from dataclasses import dataclass, field
from re import Pattern

__all__ = [
    "_PatternTree",
    "_common_pattern",
]

WILDCARD: str = r".*"
"""
A constant defining regex for match all.
"""


@dataclass
class EditNode:
    """
    Represents an edit node in a Myers Diff algorithm.
    """

    x: int = field()
    y: int = field()
    parent: EditNode | None = field()

    @property
    def k(self) -> int:
        """The diagonal number, as in Myers Diff Algorithm."""
        return self.x - self.y

    def edit_path(self) -> list[tuple[int, int, bool]]:
        """Returns the edit operations from root to self."""
        nodes: list[EditNode] = []
        node: EditNode = self
        while node.parent is not None:
            nodes.append(node)
            node = node.parent
        nodes.reverse()
        return [(prev.x, prev.y, prev.k == node.k) for prev, node in itertools.pairwise(nodes)]


@dataclass
class EditTree:
    """
    Represents a tree in a Myers Diff algorithm.
    """

    _leaves: dict[int, EditNode] = field(default_factory=lambda: {1: EditNode(0, -1, None)})

    def leaf(self, pos: int) -> EditNode:
        return self._leaves[pos]

    def move_down(self, pos: int) -> EditNode:
        node = self.leaf(pos)
        down = EditNode(node.x, node.y + 1, node)
        self._leaves[down.k] = down
        return down

    def move_right(self, pos: int) -> EditNode:
        node = self.leaf(pos)
        right = EditNode(node.x + 1, node.y, node)
        self._leaves[right.k] = right
        return right

    def move_diagonal(self, pos: int) -> EditNode:
        node = self.leaf(pos)
        diagonal = EditNode(node.x + 1, node.y + 1, node)
        self._leaves[diagonal.k] = diagonal
        return diagonal


def tokenize(value: str) -> list[str]:
    """
    If `value` does not contain any regex symbols, then "".join(tokenize(value)) == value. If `value` does contain
    Wildcards, the wildcards should be preserved. Notice wildcards could happen as substrings. Tokenize should also
    preserve any white space, tabs and line breaks.

    Args:
        value: The string to tokenize.

    Returns:
        The value broken into tokens.
    """
    tokens: list[str] = []
    for token in re.split(r"(\s+|\.\*)", value):
        if token.isspace():
            tokens.append(token)
        elif token == WILDCARD:
            tokens.append(WILDCARD)
        elif token:
            tokens.append(re.escape(token))
    return tokens


def normalize_regex(tokens: list[str]) -> str:
    """
    Attempts to normalize a regex. We generate only wildcards, as such, things like: `This is an .*.* example` should
    be written as `This is an .* example` instead.

    Args:
        tokens: The list of tokens.

    Returns:
        The normalized pattern as string.
    """
    flag: bool = True
    while flag:
        flag = False
        reduced_tokens: list[str] = []
        # Remove consecutive wildcards
        for key, group in itertools.groupby(tokens):
            if key == WILDCARD:
                reduced_tokens.append(key)
            else:
                reduced_tokens.extend(group)
        # Introduce more wildcards
        tokens = reduced_tokens
        for i in range(len(tokens) - 2):
            if tokens[i] == WILDCARD and tokens[i + 1].isspace() and tokens[i + 2] == WILDCARD:
                tokens[i + 1] = WILDCARD
                flag = True
    return "".join(tokens)


def _common_pattern(this: str, other: str, max_diff: int | None = None) -> Pattern | None:
    """
    Creates a common expression between `self` and `other`. A common expression should satisfy:
    - common.matches(self) -> True
    - common.matches(other) -> True

    Args:
        this: A string value.
        other: A string value.
        max_diff: Optional. The maximum number of editions (i.e. insertions and deletions).

    Returns:
        A common expression that matches both `self` and `other`. if `max_diff` was provided and a common pattern
        that has fewer edits than `max_diff` is not found, returns None.
    """
    if this == WILDCARD:
        return other
    elif other == WILDCARD:
        return this

    lh_tokens: list[str] = tokenize(this)
    rh_tokens: list[str] = tokenize(other)
    n, m = len(lh_tokens), len(rh_tokens)
    max_diff: int = max_diff or (n + m)

    tree: EditTree = EditTree()
    for d in range(max_diff + 1):
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and tree.leaf(k - 1).x < tree.leaf(k + 1).x):
                node = tree.move_down(k + 1)
            else:
                node = tree.move_right(k - 1)
            while node.x < n and node.y < m and lh_tokens[node.x] == rh_tokens[node.y]:
                node = tree.move_diagonal(k)

            if node.x >= n and node.y >= m:
                tokens: list[str] = []
                for x, y, match in node.edit_path():
                    if match:
                        tokens.append(lh_tokens[x])
                    else:
                        tokens.append(WILDCARD)
                return re.compile(normalize_regex(tokens), flags=re.DOTALL)
    return None


def edit_distance(this: str, other: str) -> int:
    """
    Computes the edit distance between `this` and `other`, i.e. the smallest number of additions and deletions to
    convert `this` into `other`.

    Args:
        this: A string value.
        other: A string value

    Returns:
        The edit distance between `this` and `other`.
    """
    if this == WILDCARD or other == WILDCARD:
        return len(this) + len(other)

    lh_tokens: list[str] = tokenize(this)
    rh_tokens: list[str] = tokenize(other)
    n, m = len(lh_tokens), len(rh_tokens)
    v: dict[int, int] = {1: 0}
    for d in range(n + m + 1):
        for k in range(-d, d + 1, 2):
            if k == -d or (k != d and v[k - 1] < v[k + 1]):
                x: int = v[k + 1]
            else:
                x: int = v[k - 1] + 1
            y: int = x - k
            while x < n and y < m and lh_tokens[x] == rh_tokens[y]:
                x += 1
                y += 1
            v[k] = x
            if x >= n and y >= m:
                return d
    return n + m


@dataclass
class PatternNode:
    value: Pattern | str = field()
    children: list[PatternNode] = field(default_factory=list)

    @property
    def literal(self) -> str:
        """Returns the string value of this node."""
        if isinstance(self.value, Pattern):
            return self.value.pattern
        else:
            return self.value

    @property
    def lower(self):
        """A lower node is one that is close to the leaves rather than the root."""
        wildcards, words = 0, 0
        for token in tokenize(self.literal):
            if token == WILDCARD:
                wildcards += 1
            elif not token.isspace():
                words += 1
        return wildcards + 1 < words

    def leaves(self) -> Iterator[PatternNode]:
        """Return the leave nodes under this node."""
        q: deque[PatternNode] = deque()
        q.append(self)
        while q:
            node: PatternNode = q.pop()
            if not node.children:
                yield node
            else:
                for child in node.children:
                    q.append(child)

    def match(self, literal: str) -> bool:
        if isinstance(self.value, Pattern):
            return self.value.fullmatch(literal)
        else:
            return self.value == literal

    def insert(self, literal: str) -> bool:
        """
        Args:
            literal: Another pattern.

        Returns:
            Returns true if it can insert the pattern as a child node. False otherwise.
        """
        if not self.match(literal):
            return False
        if self.literal == literal:
            return True
        # Find specific pattern first.
        for child in self.children:
            if child.insert(literal):
                return True

        # Append as a child or as a grandchild.
        min_dist: int = edit_distance(self.literal, literal)
        min_index: int | None = None
        min_common: Pattern | None = None
        for index, child in enumerate(self.children):
            common: Pattern | None = _common_pattern(child.literal, literal, min_dist)
            if common is None:
                # i.e. common pattern would require edits > min_dist
                continue
            if self.literal == common.pattern:
                # i.e. common pattern is self
                continue
            dist: int = max(
                edit_distance(common.pattern, child.literal),
                edit_distance(common.pattern, literal),
            )
            if dist < min_dist:
                min_dist, min_index, min_common = dist, index, common

        if min_index is None:
            self.children.append(
                PatternNode(value=literal),
            )
        else:
            self.children[min_index] = PatternNode(
                value=min_common,
                children=[
                    self.children[min_index],
                    PatternNode(value=literal),
                ],
            )
        return True


@dataclass
class _PatternTree:
    """
    A tree of patterns. The root of a pattern tree is a Wildcard (i.e. `.*`), the leaves are Literal expressions (
    i.e. do not contain Wildcards). The further down in the tree the more specific the patterns are.
    """

    root: PatternNode = field(default_factory=lambda: PatternNode(value=re.compile(WILDCARD, flags=re.DOTALL)))

    def insert(self, message: str) -> None:
        """
        Args:
            message: The message to insert into the pattern tree.
        """
        self.root.insert(message)

    def as_dict(self) -> dict[str, list[str]]:
        """
        Returns:
            Internal method to return this tree as a python dict.
        """
        patterns: list[PatternNode] = []

        q: deque[PatternNode] = deque()
        q.append(self.root)
        while q:
            node: PatternNode = q.pop()
            if node.lower:
                patterns.append(node)
            else:
                for child in reversed(node.children):
                    q.append(child)

        result = {}
        for node in patterns:
            expressions: list[str] = []
            for leaf in node.leaves():
                expressions.append(leaf.literal)
            result[node.literal] = expressions
        return result

    def __iter__(self) -> Iterator[tuple[int, Pattern]]:
        q: deque[PatternNode] = deque()
        q.append((self.root, 0))
        while q:
            node, height = q.pop()
            yield height, node.literal
            for child in reversed(node.children):
                q.append((child, height + 1))
