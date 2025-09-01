# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from functools import cache
from typing import Protocol, runtime_checkable

from omni.capabilities import Profiles

from ._capabilities import Capability
from ._registry import IdVersion, VersionedRegistry
from ._semver import SemVer

__all__ = [
    "Profile",
    "ProfileRegistry",
]


@runtime_checkable
class Profile(Protocol):
    """
    A protocol definition of profile.

    Attributes:
        id: A unique identifier of the profile
        version: The version of the profile
        path: The path to the profile
        capabilities: The capabilities of the profile
    """

    id: str
    version: str
    path: str
    capabilities: list[Capability]


@cache
class ProfileRegistry(VersionedRegistry[Profile]):
    """
    A singleton class that keeps profiles.
    """

    def __init__(self):
        super().__init__(Profiles)

    def create_key(self, value: Profile) -> IdVersion:
        return IdVersion(value.id, SemVer(value.version))

    @property
    def profiles(self) -> list[Profile]:
        """Get all profiles (all versions)."""
        return list(self)

    def add_profile(self, profile: Profile) -> None:
        """
        Add a profile to the registry.

        Args:
            profile: The profile to add

        Raises:
            ValueError: If a profile with the same ID and version already exists
        """
        self.add(profile)

    def find_profile(self, id: str, version: str | None = None) -> Profile | None:
        """
        Find a profile by ID and version.

        Args:
            id: The profile ID
            version: The version to find, defaults to latest

        Returns:
            The profile if found, None otherwise
        """
        return self.find(id, version)
