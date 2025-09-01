# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

import re
from functools import singledispatchmethod, total_ordering

_SEMVER_PATTERN = (
    r"^(\d+)\.(\d+)\.(\d+)(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
"""
Basic semantic versioning pattern: major.minor.patch[-prerelease][+build]
"""


@total_ordering
class SemVer:
    LATEST = "latest"

    @singledispatchmethod
    def __init__(self, arg):
        """Initialize SemVer from various argument types."""
        raise TypeError(f"Cannot create SemVer from {type(arg)}")

    @__init__.register
    def _(self, version: str):
        """Initialize SemVer from a version string."""
        match = re.match(_SEMVER_PATTERN, version)
        if not match:
            raise ValueError(f"Invalid version format: {version}. Expected semantic versioning format")

        major, minor, patch, prerelease, build = match.groups()
        self.major = int(major)
        self.minor = int(minor)
        self.patch = int(patch)
        self.prerelease = prerelease
        self.build = build

    @__init__.register
    def _(self, major: int, minor: int, patch: int, prerelease: str | None = None, build: str | None = None):
        """Initialize SemVer from individual components."""
        self.major = major
        self.minor = minor
        self.patch = patch
        self.prerelease = prerelease
        self.build = build

    def __lt__(self, other: SemVer) -> bool:
        # Compare major, minor, patch
        if (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch):
            return True
        elif (self.major, self.minor, self.patch) > (other.major, other.minor, other.patch):
            return False

        # If major.minor.patch are equal, compare prerelease
        if self.prerelease is None and other.prerelease is not None:
            return False  # self is greater
        elif self.prerelease is not None and other.prerelease is None:
            return True  # self is less
        elif self.prerelease is None and other.prerelease is None:
            return False  # equal
        else:
            return self.prerelease < other.prerelease

    def __eq__(self, other: SemVer) -> bool:
        return (
            self.major == other.major
            and self.minor == other.minor
            and self.patch == other.patch
            and self.prerelease == other.prerelease
            and self.build == other.build
        )

    def __hash__(self) -> int:
        return hash((self.major, self.minor, self.patch, self.prerelease, self.build))

    def __repr__(self) -> str:
        version_str = f"{self.major}.{self.minor}.{self.patch}"
        if self.prerelease:
            version_str += f"-{self.prerelease}"
        if self.build:
            version_str += f"+{self.build}"
        return version_str

    def __str__(self) -> str:
        return self.__repr__()

    def is_compatible(self, required_version: SemVer) -> bool:
        """
        Check if this version is compatible with the required version.
        Uses semantic versioning rules where major version changes indicate breaking changes.

        Args:
            required_version: Minimum required version

        Returns:
            True if this version is compatible, False otherwise
        """
        # Versions are only compatible if they have the same major version
        # and the current version is greater than or equal to the required version
        return self.major == required_version.major and self >= required_version
