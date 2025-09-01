# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from bisect import insort
from collections import defaultdict
from collections.abc import Iterator
from dataclasses import dataclass
from functools import total_ordering
from typing import Generic, TypeVar

from ._semver import SemVer

K = TypeVar("K")
V = TypeVar("V")


@total_ordering
@dataclass(frozen=True)
class IdVersion:
    """
    A class to represent an ID and version.
    """

    id: str
    version: SemVer

    def __lt__(self, other: IdVersion) -> bool:
        return (self.id, self.version) < (other.id, other.version)


class VersionedRegistry(Generic[V]):
    """
    A registry of values with versioned keys.
    """

    def __init__(self, values: list[V] | None = None):
        self._registry: dict[IdVersion, V] = {}
        self._registry_by_id: dict[str, list[IdVersion]] = defaultdict(list)
        if values:
            for value in values:
                self.add(value)

    def create_key(self, value: V) -> IdVersion:
        raise NotImplementedError("Subclass must implement this method")

    def add(self, value: V) -> None:
        key: IdVersion = self.create_key(value)
        if key in self._registry:
            raise ValueError(f"Value with key {key} already exists")
        self._registry[key] = value
        insort(self._registry_by_id[key.id], key)

    def get(self, key: IdVersion, default: V | None = None) -> V | None:
        """
        Get a value by key.
        """
        return self._registry.get(key, default)

    def find(self, id: str, version: str | SemVer | None = None) -> V | None:
        """
        Find a value by ID and version.
        """
        keys = self._registry_by_id[id]
        if not keys:
            return None
        if version is None or version == SemVer.LATEST:
            return self.get(keys[-1])
        version = SemVer(version) if isinstance(version, str) else version
        for key in reversed(keys):
            if key.version.is_compatible(version):
                return self._registry[key]
        return None

    def __getitem__(self, key: IdVersion) -> V:
        return self._registry[key]

    def __delitem__(self, key: IdVersion) -> None:
        del self._registry[key]

    def __iter__(self) -> Iterator[V]:
        return iter(self._registry.values())

    def __len__(self) -> int:
        return len(self._registry)

    def keys(self) -> list[IdVersion]:
        return list(self._registry.keys())

    def values(self) -> list[V]:
        return list(self._registry.values())

    def items(self) -> list[tuple[IdVersion, V]]:
        return list(self._registry.items())

    def latest_keys(self) -> list[IdVersion]:
        return [values[-1] for values in self._registry_by_id.values() if values]

    def latest_values(self) -> list[V]:
        return [self[key] for key in self.latest_keys()]
