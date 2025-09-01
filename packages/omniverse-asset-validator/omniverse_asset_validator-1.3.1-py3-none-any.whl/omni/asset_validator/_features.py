# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

from functools import cache
from typing import Protocol, runtime_checkable

from omni.capabilities import Features

from ._registry import IdVersion, VersionedRegistry
from ._requirements import Requirement
from ._semver import SemVer


@runtime_checkable
class Feature(Protocol):
    """
    A protocol definition of feature.

    Attributes:
        id: A unique identifier of the feature
        version: The version of the feature
        path: The path to the feature
        requirements: The requirements of the feature
    """

    id: str
    version: str
    path: str
    requirements: list[Requirement]


@cache
class FeatureRegistry(VersionedRegistry[Feature]):
    """
    A registry of features.
    """

    def __init__(self):
        super().__init__(Features)

    def create_key(self, value: Feature) -> IdVersion:
        return IdVersion(value.id, SemVer(value.version))
