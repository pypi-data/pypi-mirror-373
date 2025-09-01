# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from functools import cache
from typing import Protocol, runtime_checkable

from omni.capabilities import Capabilities

from ._deprecate import deprecated
from ._registry import IdVersion, VersionedRegistry
from ._requirements import Requirement
from ._semver import SemVer

__all__ = [
    "Capability",
    "CapabilityRegistry",
]


@runtime_checkable
class Capability(Protocol):
    """
    A protocol definition of capability.

    Attributes:
        id: A unique identifier of the capability
        version: The version of the capability
        path: The path to the capability
        requirements: The requirements of the capability
    """

    id: str
    version: str
    path: str
    requirements: list[Requirement]


@cache
class CapabilityRegistry(VersionedRegistry[Capability]):
    """
    A singleton class that keeps capabilities.
    """

    def __init__(self):
        super().__init__(Capabilities)

    def create_key(self, value: Capability) -> IdVersion:
        return IdVersion(value.id, SemVer(value.version))

    @property
    def capabilities(self) -> list[Capability]:
        """Get all capabilities (all versions)."""
        return list(self)

    @property
    def latest_capabilities(self) -> list[Capability]:
        """Get only the latest version of each capability."""
        return self.latest_values()

    @deprecated("Use keys() instead")
    def get_capability_ids(self) -> list[str]:
        return [key.id for key in self.keys()]

    @deprecated("Use add() instead")
    def add_capability(self, capability: Capability) -> None:
        """
        Add a capability to the registry.

        Args:
            capability: The capability to add

        Raises:
            ValueError: If a capability with the same ID and version already exists
        """
        self.add(capability)

    @deprecated("Use find() instead")
    def find_capability(self, id: str, version: str | None = None) -> Capability | None:
        """
        Find a capability by ID and version.

        Args:
            id: The capability ID
            version: The version to find, defaults to latest

        Returns:
            The capability if found, None otherwise
        """
        return self.find(id, version)
