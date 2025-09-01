# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

from ._assets import AssetLocatedCallback, AssetProgress, AssetProgressCallback, AssetType, AssetValidatedCallback
from ._atomic_asset_checker import AnchoredAssetPathsChecker, SupportedFileTypesChecker, UsdzUdimLimitationChecker
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
from ._capabilities import Capability, CapabilityRegistry
from ._categories import CategoryRuleRegistry, DefaultCategoryRules, get_category_rules_registry
from ._cli import ValidationArgsExec, ValidationNamespaceExec, cli_main, create_validation_parser
from ._compliance_checker import (
    ComplianceChecker,
    ComplianceCheckerEvent,
    ComplianceCheckerEventType,
    ComplianceCheckerRunner,
)
from ._context_managers import (
    MAXIMUM_BATCH_SIZE,
    MAXIMUM_COUNT_SIZE,
    AsyncBatchRunner,
    AsyncCounter,
    DelegateContextManager,
    PeriodicCallback,
)
from ._csv_reports import IssueCSVData
from ._engine import ValidationEngine
from ._expression import _common_pattern, _PatternTree
from ._features import Feature, FeatureRegistry
from ._fix import AuthoringLayers, FixResult, FixResultList, FixStatus, IssueFixer
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
from ._identifiers import (
    AttributeId,
    AtType,
    Identifier,
    LayerId,
    PrimId,
    PrimvarId,
    PropertyId,
    SchemaBaseId,
    SpecId,
    SpecIdList,
    StageId,
    VariantIdMixin,
    to_identifier,
    to_identifiers,
)
from ._import_utils import default_implementation, default_implementation_method
from ._issues import (
    Issue,
    IssueGroupBy,
    IssueGroupsBy,
    IssuePredicate,
    IssuePredicates,
    IssueSeverity,
    IssuesList,
    Suggestion,
)
from ._json_reports import IssueJSONEncoder, export_json_file
from ._layer_checker import LayerSpecChecker, UsdAsciiPerformanceChecker
from ._layout_checker import DanglingOverPrimChecker, DefaultPrimChecker
from ._material_checker import (
    MaterialOldMdlSchemaChecker,
    MaterialOutOfScopeChecker,
    MaterialPathChecker,
    MaterialUsdPreviewSurfaceChecker,
    ShaderImplementationSourceChecker,
    UsdDanglingMaterialBinding,
    UsdMaterialBindingApi,
)
from ._mesh_tools import (
    RepeatedValuesSet,
    check_manifold_elements,
    has_empty_faces,
    has_indexable_values,
    has_invalid_indices,
    has_invalid_primvar_indices,
    has_unreferenced_primvar,
    has_unreferenced_values,
    has_weldable_points,
    is_typename_array,
    remove_unused_values_and_remap_indices,
)
from ._misc_checker import SkelBindingAPIAppliedChecker, UsdGeomSubsetChecker, UsdLuxSchemaChecker
from ._omni_utils import is_omni_path
from ._performance_checker import (
    AlmostExtremeExtentChecker,
    BaseBoundsChecker,
    BoundsLimit,
    PointsPrecisionChecker,
    PointsPrecisionErrorChecker,
    PointsPrecisionWarningChecker,
    PrecisionLimit,
)
from ._physics_checker import ArticulationChecker, ColliderChecker, PhysicsJointChecker, RigidBodyChecker
from ._profiles import Profile, ProfileRegistry
from ._requirements import Requirement, RequirementsRegistry, register_requirements
from ._results import Results, ResultsList, to_issues_list
from ._semver import SemVer
from ._stats import ValidationStats
from ._url_utils import make_relative_url_if_possible, normalize_url
from ._usd_utils import get_sdf_type_for_shader_property
from ._utf8_checker import UnicodeNameChecker
from ._version import __version__, get_version

__all__ = [
    "AnchoredAssetPathsChecker",
    "SupportedFileTypesChecker",
    "UsdzUdimLimitationChecker",
    "AssetLocatedCallback",
    "AssetProgress",
    "AssetProgressCallback",
    "AssetType",
    "AssetValidatedCallback",
    "BaseRuleChecker",
    "ByteAlignmentChecker",
    "CompressionChecker",
    "ExtentsChecker",
    "KindChecker",
    "MissingReferenceChecker",
    "NormalMapTextureChecker",
    "PrimEncapsulationChecker",
    "StageMetadataChecker",
    "TextureChecker",
    "TypeChecker",
    "CategoryRuleRegistry",
    "DefaultCategoryRules",
    "get_category_rules_registry",
    "ValidationArgsExec",
    "ValidationNamespaceExec",
    "cli_main",
    "create_validation_parser",
    "ComplianceChecker",
    "ComplianceCheckerEvent",
    "ComplianceCheckerEventType",
    "ComplianceCheckerRunner",
    "IssueCSVData",
    "ValidationEngine",
    "_PatternTree",
    "_common_pattern",
    "AuthoringLayers",
    "FixResult",
    "FixResultList",
    "FixStatus",
    "IssueFixer",
    "IndexedPrimvarChecker",
    "ManifoldChecker",
    "SubdivisionSchemeChecker",
    "UnusedMeshTopologyChecker",
    "UnusedPrimvarChecker",
    "ValidateTopologyChecker",
    "WeldChecker",
    "ZeroAreaFaceChecker",
    "NormalsExistChecker",
    "AtType",
    "AttributeId",
    "Identifier",
    "LayerId",
    "PrimId",
    "PropertyId",
    "SchemaBaseId",
    "PrimvarId",
    "SpecId",
    "SpecIdList",
    "StageId",
    "VariantIdMixin",
    "to_identifier",
    "to_identifiers",
    "default_implementation",
    "default_implementation_method",
    "Issue",
    "IssueGroupBy",
    "IssueGroupsBy",
    "IssuePredicate",
    "IssuePredicates",
    "IssueSeverity",
    "IssuesList",
    "Suggestion",
    "IssueJSONEncoder",
    "export_json_file",
    "LayerSpecChecker",
    "UsdAsciiPerformanceChecker",
    "DanglingOverPrimChecker",
    "DefaultPrimChecker",
    "MaterialOldMdlSchemaChecker",
    "MaterialOutOfScopeChecker",
    "MaterialPathChecker",
    "MaterialUsdPreviewSurfaceChecker",
    "ShaderImplementationSourceChecker",
    "UsdDanglingMaterialBinding",
    "UsdMaterialBindingApi",
    "RepeatedValuesSet",
    "check_manifold_elements",
    "has_empty_faces",
    "has_indexable_values",
    "has_invalid_indices",
    "has_invalid_primvar_indices",
    "has_unreferenced_primvar",
    "has_unreferenced_values",
    "has_weldable_points",
    "is_typename_array",
    "remove_unused_values_and_remap_indices",
    "SkelBindingAPIAppliedChecker",
    "UsdGeomSubsetChecker",
    "UsdLuxSchemaChecker",
    "is_omni_path",
    "AlmostExtremeExtentChecker",
    "BaseBoundsChecker",
    "BoundsLimit",
    "PointsPrecisionChecker",
    "PointsPrecisionErrorChecker",
    "PointsPrecisionWarningChecker",
    "PrecisionLimit",
    "ArticulationChecker",
    "ColliderChecker",
    "PhysicsJointChecker",
    "RigidBodyChecker",
    "RequirementsRegistry",
    "register_requirements",
    "Requirement",
    "CapabilityRegistry",
    "Capability",
    "ProfileRegistry",
    "Profile",
    "FeatureRegistry",
    "Feature",
    "Results",
    "ResultsList",
    "to_issues_list",
    "ValidationStats",
    "make_relative_url_if_possible",
    "normalize_url",
    "UnicodeNameChecker",
    "get_sdf_type_for_shader_property",
    "__version__",
    "get_version",
    "SemVer",
]
