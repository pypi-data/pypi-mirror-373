# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from collections import OrderedDict
from collections.abc import Sequence
from dataclasses import dataclass, field
from enum import Enum
from functools import cache

from ._atomic_asset_checker import AnchoredAssetPathsChecker, SupportedFileTypesChecker
from ._base_rule_checker import BaseRuleChecker
from ._base_rules import (
    ByteAlignmentChecker,
    CompressionChecker,
    ExtentsChecker,
    KindChecker,
    MissingReferenceChecker,
    NormalMapTextureChecker,
    PrimEncapsulationChecker,
    StageMetadataChecker,
    TextureChecker,
    TypeChecker,
)
from ._deprecate import deprecated
from ._geometry_checker import (
    IndexedPrimvarChecker,
    ManifoldChecker,
    NormalsExistChecker,
    SubdivisionSchemeChecker,
    UnusedMeshTopologyChecker,
    UnusedPrimvarChecker,
    ValidateTopologyChecker,
    WeldChecker,
    ZeroAreaFaceChecker,
)
from ._layer_checker import (
    LayerSpecChecker,
    UsdAsciiPerformanceChecker,
)
from ._layout_checker import (
    DanglingOverPrimChecker,
    DefaultPrimChecker,
)
from ._material_checker import (
    MaterialOutOfScopeChecker,
    MaterialPathChecker,
    MaterialUsdPreviewSurfaceChecker,
    ShaderImplementationSourceChecker,
    UsdDanglingMaterialBinding,
    UsdMaterialBindingApi,
)
from ._misc_checker import (
    SkelBindingAPIAppliedChecker,
    UsdGeomSubsetChecker,
    UsdLuxSchemaChecker,
)
from ._physics_checker import (
    ArticulationChecker,
    ColliderChecker,
    PhysicsJointChecker,
    RigidBodyChecker,
)

__all__ = [
    "CategoryRuleRegistry",
    "DefaultCategoryRules",
    "get_category_rules_registry",
]


@cache
@dataclass
class CategoryRuleRegistry:
    """
    A singleton mutable registry of all rules grouped by categories.
    """

    _rules: dict[str, list[type[BaseRuleChecker]]] = field(init=False, default_factory=OrderedDict)

    def __post_init__(self) -> None:
        for category_rules in DefaultCategoryRules:
            if category_rules is DefaultCategoryRules.ATOMIC_ASSET:
                continue
            for rule in category_rules.rules:
                self.add(category_rules.category, rule)

    @property
    def categories(self) -> Sequence[str]:
        """
        An immutable list of categories.
        """
        return tuple(category for category in self._rules.keys())

    @property
    def rules(self) -> Sequence[type[BaseRuleChecker]]:
        """
        An immutable list of rules.
        """
        return tuple(rule for rules in self._rules.values() for rule in rules)

    def add(self, category: str, rule: type[BaseRuleChecker]) -> None:
        """
        Associate a rule to a specific category. If the rule was associated to a previous category, it is removed and
        added into the new category.

        Args:
            category (str): The category to associate to the rule.
            rule (Type[BaseRuleChecker]): The rule class.
        """
        self.remove(rule)  # Remove from any existing category
        self._rules.setdefault(category, list()).append(rule)

    def clear(self) -> None:
        """
        Clears the registry.
        """
        self._rules.clear()

    def get_rules(self, category: str) -> set[type[BaseRuleChecker]]:
        """
        Get the rules associated to a specific category in the registry.

        Args:
            category: The category in the registry.

        Returns:
            The rules associated to the category.
        """
        return self._rules.get(category, set())

    def remove(self, rule: type[BaseRuleChecker]) -> None:
        """
        Removes a rule from the registry.

        Args:
            rule: The rule to remove from the registry.
        """
        for key, rules in list(self._rules.items()):
            if rule in rules:
                rules.remove(rule)
                if not rules:
                    del self._rules[key]

    def find_rule(self, rule_name: str) -> type[BaseRuleChecker] | None:
        """
        Returns:
            Find rule by name. Returns None otherwise.
        """
        for rule in self.rules:
            if rule.__name__ == rule_name:
                return rule
        return None

    def get_category(self, rule: type[BaseRuleChecker]) -> str | None:
        """
        Returns the category under the rule is associated.

        Args:
            rule: The rule in the registry.

        Returns:
            The category under the rule is associated. Returns None if the rule is not registered.
        """
        for key, rules in self._rules.items():
            if rule in rules:
                return key
        return None


class DefaultCategoryRules(Enum):
    """
    The declared Categories and Rules defined in `omni.asset_validator` module. For additional classes use
    `CategoryRuleRegistry`.

    Args:
        category: The name of the category.
        rules: The sequence of rules associated to the category.
    """

    ATOMIC_ASSET = (
        "AtomicAsset",
        (
            AnchoredAssetPathsChecker,
            SupportedFileTypesChecker,
        ),
    )
    """
    AtomicAsset category is for all rules associated to Atomic Asset.

    :meta hide-value:
    """

    BASIC = (
        "Basic",
        (
            ByteAlignmentChecker,
            CompressionChecker,
            ExtentsChecker,
            KindChecker,
            MissingReferenceChecker,
            NormalMapTextureChecker,
            PrimEncapsulationChecker,
            StageMetadataChecker,
            TextureChecker,
            TypeChecker,
        ),
    )
    """
    Basic category is for all rules delivered with ComplianceChecker.

    :meta hide-value:
    """

    GEOMETRY = (
        "Geometry",
        (
            SubdivisionSchemeChecker,
            ManifoldChecker,
            IndexedPrimvarChecker,
            UnusedMeshTopologyChecker,
            ZeroAreaFaceChecker,
            WeldChecker,
            ValidateTopologyChecker,
            UnusedPrimvarChecker,
            NormalsExistChecker,
        ),
    )
    """
    Geometry category is for all rules for geometry and topology checks.

    :meta hide-value:
    """

    LAYER = (
        "Layer",
        (
            LayerSpecChecker,
            UsdAsciiPerformanceChecker,
        ),
    )
    """
    Layer category is for all rules running at layer level.

    :meta hide-value:
    """

    LAYOUT = (
        "Layout",
        (
            DanglingOverPrimChecker,
            DefaultPrimChecker,
        ),
    )
    """
    Layout category is for all rules concerned about best practices of prim hierarchy.

    :meta hide-value:
    """

    MATERIAL = (
        "Material",
        (
            MaterialOutOfScopeChecker,
            MaterialPathChecker,
            MaterialUsdPreviewSurfaceChecker,
            ShaderImplementationSourceChecker,
            UsdDanglingMaterialBinding,
            UsdMaterialBindingApi,
        ),
    )
    """
    Material category is for all rules about Materials.

    :meta hide-value:
    """

    PHYSICS = (
        "Physics",
        (
            ArticulationChecker,
            ColliderChecker,
            PhysicsJointChecker,
            RigidBodyChecker,
        ),
    )
    """
    Physics category is for all rules about Physics.

    :meta hide-value:
    """

    OTHER = (
        "Other",
        (
            SkelBindingAPIAppliedChecker,
            UsdGeomSubsetChecker,
            UsdLuxSchemaChecker,
        ),
    )
    """
    Category for other rules.

    :meta hide-value:
    """

    def __init__(self, category: str, rules: Sequence[type[BaseRuleChecker]]):
        self.category = category
        self.rules = rules


@cache
@deprecated("Use CategoryRuleRegistry instead")
def get_category_rules_registry() -> CategoryRuleRegistry:
    """
    Returns:
        A singleton mutable category rule registry. By default, this includes all rules found in this module
        except for AtomicAsset rules.
    """
    return CategoryRuleRegistry()
