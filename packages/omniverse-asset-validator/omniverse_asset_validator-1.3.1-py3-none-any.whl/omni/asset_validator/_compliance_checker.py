#
# Copyright 2018 Pixar
# Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
#
# Licensed under the terms set forth in the LICENSE.txt file available at
# https://openusd.org/license.
#
from __future__ import annotations

import itertools
from collections.abc import Callable, Iterator, Sequence
from dataclasses import dataclass
from enum import Enum, auto
from functools import singledispatchmethod
from typing import Any

from pxr import Ar, Sdf, Usd, UsdUtils

from ._assets import AssetType
from ._base_rule_checker import BaseRuleChecker
from ._context_managers import AsyncBatchRunner, AsyncCounter, DelegateContextManager, PeriodicCallback
from ._identifiers import ANON_VALIDATOR_LAYER_NAME
from ._issues import Issue, IssueSeverity
from ._stats import ValidationStats

__all__ = [
    "ComplianceChecker",
    "ComplianceCheckerEvent",
    "ComplianceCheckerEventType",
    "ComplianceCheckerRunner",
]


def _is_package_or_packaged_layer(layer):
    return layer.GetFileFormat().IsPackage() or Ar.IsPackageRelativePath(layer.identifier)


class ComplianceCheckerEventType(Enum):
    """A type of event in compliance checker."""

    STAGE = auto()
    DIAGNOSTICS = auto()
    UNRESOLVED_PATHS = auto()
    DEPENDENCIES = auto()
    LAYER = auto()
    ZIP_FILE = auto()
    PRIM = auto()
    RESET_CACHE = auto()
    FLUSH = auto()


class ComplianceCheckerEvent:
    """A compliance checker event."""

    __slots__ = ("type", "value")

    def __init__(self, type: ComplianceCheckerEventType, value: Any):
        self.type = type
        self.value = value

    def apply(self, rules: Sequence[BaseRuleChecker], stats: ValidationStats) -> None:
        """Apply the event to a set of rules."""
        for rule in rules:
            with stats.time_rule(rule.__class__):
                try:
                    if self.type is ComplianceCheckerEventType.STAGE:
                        rule.CheckStage(self.value)
                    if self.type is ComplianceCheckerEventType.DIAGNOSTICS:
                        rule.CheckDiagnostics(self.value)
                    elif self.type is ComplianceCheckerEventType.UNRESOLVED_PATHS:
                        rule.CheckUnresolvedPaths(self.value)
                    if self.type is ComplianceCheckerEventType.DEPENDENCIES:
                        rule.CheckDependencies(*self.value)
                    elif self.type is ComplianceCheckerEventType.LAYER:
                        rule.CheckLayer(self.value)
                    elif self.type is ComplianceCheckerEventType.ZIP_FILE:
                        rule.CheckZipFile(*self.value)
                    elif self.type is ComplianceCheckerEventType.PRIM:
                        rule.CheckPrim(self.value)
                    elif self.type is ComplianceCheckerEventType.RESET_CACHE:
                        rule.ResetCaches()
                except Exception as error:
                    rule._AddError(message=f"Uncaught error: {error}")


@dataclass
class ComplianceCheckerRunner(AsyncBatchRunner):
    """
    Process events in batches thus reducing time to schedule while also giving time for other threads/process to run.
    """

    rules: Sequence[BaseRuleChecker]
    stats: ValidationStats

    async def append(self, event: ComplianceCheckerEvent) -> None:
        await super().append(event)
        if event.type is ComplianceCheckerEventType.FLUSH:
            await self.flush()

    def run(self, events: list[ComplianceCheckerEvent]) -> None:
        for event in events:
            event.apply(self.rules, self.stats)


class ComplianceChecker:
    """A utility class for checking compliance of a given USD asset or a USDZ
    package.

    Since usdz files are zip files, someone could use generic zip tools to
    create an archive and just change the extension, producing a .usdz file that
    does not honor the additional constraints that usdz files require.  Even if
    someone does use our official archive creation tools, though, we
    intentionally allow creation of usdz files that can be very "permissive" in
    their contents for internal studio uses, where portability outside the
    studio is not a concern.  For content meant to be delivered over the web
    (eg. ARKit assets), however, we must be much more restrictive.

    This class provides a level of compliance checking:
    * "structural" validation that is represented by a set of base rules.

    Calling ComplianceChecker.DumpAllRules() will print an enumeration of the
    various rules in the two categories of compliance checking.
    """

    def __init__(
        self,
        *,
        skip_variants: bool = False,
        stats: ValidationStats | None = None,
    ):
        self._doVariants = not skip_variants
        self._issues = []
        self._stats = stats or ValidationStats()

        # Once a package has been checked, it goes into this set.
        self._checkedPackages = set()

        self._rule_types: set[type[BaseRuleChecker]] = set()
        self._rules: list[BaseRuleChecker] = []

    @property
    def rules(self) -> Sequence[BaseRuleChecker]:
        """
        Returns: The rules to use in this ComplianceChecker.
        """
        return tuple(self._rules)

    def AddRule(self, rule_type: type[BaseRuleChecker]) -> None:
        """
        Adds a rule to the ComplianceChecker.

        Args:
            rule_type (type[BaseRuleChecker]): The type of the rule to add.
        """
        if rule_type in self._rule_types:
            return
        self._rule_types.add(rule_type)
        try:
            rule: BaseRuleChecker = rule_type(verbose=False, consumerLevelChecks=False, assetLevelChecks=True)
            self._rules.append(rule)
        except Exception as error:
            self._issues.append(
                Issue(
                    severity=IssueSeverity.ERROR,
                    message=f"Failed to initialize rule {rule_type.__name__}: {error}",
                    rule=rule_type,
                )
            )

    def _AddError(self, errMsg):
        self._issues.append(Issue(severity=IssueSeverity.ERROR, message=errMsg))

    def _AddWarning(self, errMsg):
        self._issues.append(Issue(severity=IssueSeverity.WARNING, message=errMsg))

    def GetIssues(self) -> Sequence[Issue]:
        issues = self._issues
        for rule in self._rules:
            issues.extend(rule.GetIssues())
        return issues

    def check(self, asset: str | Usd.Stage) -> None:
        """Consolidates check_compliance (for files) and check_stage_compliance (for stages)."""
        for event in self._check_compliance(asset):
            event.apply(self._rules, self._stats)

    async def check_async(self, asset: str | Usd.Stage, callback: Callable[[float], None] | None = None) -> None:
        """Asynchronous version of check.
        Args:
            asset (str, Usd.Stage): Root asset to run the validation. Can be an uri or an USD stage.
        Kwargs:
            callback (Callable(float): A callable that will be called when a batch of checkers executed.
        """
        num_events: int = 1

        asset_dependencies = None
        if self._rules_check_assets():
            # OMPE-15461: We compute the asset dependencies and pass it to self._check_compliance to reduce the need of calling
            # UsdUtils.ComputeAllDependencies multiple times.
            identifier: str = asset if isinstance(asset, str) else asset.GetRootLayer().identifier
            # This recursively get all of inputFiles's external dependencies.
            # (all_layers, all_assets, unresolved_paths)
            asset_dependencies = UsdUtils.ComputeAllDependencies(Sdf.AssetPath(identifier))

        # Setup _callback
        # Collect the total number of checker events and create a progress callback function here.
        # Note that we are not actually running any checker rules here, but
        # iterating all prims of the given asset/stage. Potential a slow process if running on a large asset?
        if callback:
            async with AsyncCounter() as counter:
                for event in self._check_compliance(asset, asset_dependencies=asset_dependencies):
                    await counter.count(event)
                num_events = counter.counter

        # OMPE-11167: Clean up - make sure we don't have cached data.
        self._checkedPackages = set()
        self._stats.clear()
        # Run checkers
        runner = self._create_runner(self._rules, self._stats)
        progress = lambda: callback(min(runner.counter / num_events, 1.0)) if callback else None
        async with PeriodicCallback(progress):
            async with runner:
                for event in self._check_compliance(asset, asset_dependencies=asset_dependencies):
                    await runner.append(event)

    @classmethod
    def _create_runner(cls, rules: list[BaseRuleChecker], stats: ValidationStats) -> ComplianceCheckerRunner:
        return ComplianceCheckerRunner(rules, stats)

    def _rules_check_assets(self) -> bool:
        """Checks if any of the rules has implemented Asset checks."""
        return any(
            type(rule).CheckLayer is not BaseRuleChecker.CheckLayer
            or type(rule).CheckZipFile is not BaseRuleChecker.CheckZipFile
            or type(rule).CheckDependencies is not BaseRuleChecker.CheckDependencies
            or type(rule).CheckUnresolvedPaths is not BaseRuleChecker.CheckUnresolvedPaths
            for rule in self._rules
        )

    def _rules_check_prims(self) -> bool:
        """Checks if any of the rules has implemented CheckPrim."""
        return any(type(rule).CheckPrim is not BaseRuleChecker.CheckPrim for rule in self._rules)

    @singledispatchmethod
    @classmethod
    def _create_stage(cls, asset: AssetType) -> Usd.Stage:
        """
        Creates a stage from asset. If asset is string, it creates a new stage. If asset is an existing stage,
        it creates a copy to avoid possible data interfering.

        Args:
            asset (AssetType): Either str or existing stage.

        Returns:
            A new stage.
        """
        raise ValueError(f"Unknown asset of type {type(asset)}")

    @_create_stage.register
    @classmethod
    def _(cls, asset: str) -> Usd.Stage:
        compliance_layer: Sdf.Layer = Sdf.Layer.CreateAnonymous(ANON_VALIDATOR_LAYER_NAME)
        stage: Usd.Stage = Usd.Stage.Open(Sdf.Layer.FindOrOpen(asset), compliance_layer)
        stage.SetEditTarget(stage.GetEditTargetForLocalLayer(compliance_layer))
        return stage

    @_create_stage.register
    @classmethod
    def _(cls, asset: Usd.Stage) -> Usd.Stage:
        compliance_layer: Sdf.Layer = Sdf.Layer.CreateAnonymous(ANON_VALIDATOR_LAYER_NAME)
        compliance_layer.TransferContent(asset.GetSessionLayer())
        stage: Usd.Stage = Usd.Stage.Open(asset.GetRootLayer(), compliance_layer)
        mask: Usd.StagePopulationMask = asset.GetPopulationMask()
        if not mask.IsEmpty():
            stage.SetPopulationMask(mask)
        stage.SetEditTarget(stage.GetEditTargetForLocalLayer(compliance_layer))
        return stage

    @classmethod
    def _create_prims_it(cls, stage: Usd.Stage):
        return iter(Usd.PrimRange.Stage(stage, Usd.TraverseInstanceProxies()))

    def _check_compliance(
        self, asset: str | Usd.Stage, asset_dependencies: tuple[Sdf.Layer, str, str] | None = None
    ) -> Iterator[ComplianceCheckerEvent]:
        """Yield ComplianceCheckerEvents for the given asset.
        Args:
            asset (str, Usd.Stage): Stage identifier or stage to validate.

        Kwargs:
            asset_dependencies (tuple): Tuple of asset's dependencies = all_layers, all_assets, unresolved_paths.
                If this argument is given, this method uses the given asset dependencies instead of calling
                `UsdUtils.ComputeAllDependencies` on the given asset in order to speed up the process.
        """
        if isinstance(asset, str) and not Usd.Stage.IsSupportedFile(asset):
            self._AddError(f"Cannot open file '{asset}' on a USD stage.")
            return

        with DelegateContextManager() as ctx:
            usd_stage = self._create_stage(asset)
            stage_open_diagnostics = ctx.delegate.TakeUncoalescedDiagnostics()
        yield ComplianceCheckerEvent(ComplianceCheckerEventType.FLUSH, None)  # Pause

        yield ComplianceCheckerEvent(ComplianceCheckerEventType.STAGE, usd_stage)
        yield ComplianceCheckerEvent(ComplianceCheckerEventType.DIAGNOSTICS, stage_open_diagnostics)
        yield ComplianceCheckerEvent(ComplianceCheckerEventType.FLUSH, None)  # Pause

        with Ar.ResolverContextBinder(usd_stage.GetPathResolverContext()):
            if self._rules_check_assets():
                all_layers, all_assets, unresolved_paths = asset_dependencies or UsdUtils.ComputeAllDependencies(
                    Sdf.AssetPath(usd_stage.GetRootLayer().identifier)
                )

                # Compute dependencies can be expensive, pause quickly.
                yield ComplianceCheckerEvent(ComplianceCheckerEventType.FLUSH, None)
                yield ComplianceCheckerEvent(ComplianceCheckerEventType.UNRESOLVED_PATHS, unresolved_paths)
                yield ComplianceCheckerEvent(
                    ComplianceCheckerEventType.DEPENDENCIES, (usd_stage, all_layers, all_assets)
                )

            if self._rules_check_assets():
                # Process every package just once by storing them all in a set.
                packages = set()
                for layer in all_layers:
                    if _is_package_or_packaged_layer(layer):
                        package_path = Ar.SplitPackageRelativePathInner(layer.identifier)[0]
                        packages.add(package_path)
                    yield ComplianceCheckerEvent(ComplianceCheckerEventType.LAYER, layer)
                for package in packages:
                    yield from self._check_package(package)

            if self._rules_check_prims():
                all_prims_iterator = self._create_prims_it(usd_stage)
                yield from self._traverse_range(all_prims_iterator, isStageRoot=True)

    def _check_package(self, package_path) -> Iterator[ComplianceCheckerEvent]:

        # XXX: Should we open the package on a stage to ensure that it is valid
        # and entirely self-contained.
        pkg_ext = Ar.GetResolver().GetExtension(package_path)
        if pkg_ext != "usdz":
            self._AddError(f"Package at path {package_path} has an invalid extension.")
            return

        # Check the parent package first.
        if Ar.IsPackageRelativePath(package_path):
            parent_package_path = Ar.SplitPackageRelativePathInner(package_path)[0]
            yield from self._check_package(parent_package_path)

        # Avoid checking the same parent package multiple times.
        if package_path in self._checkedPackages:
            return
        self._checkedPackages.add(package_path)

        resolved_path = Ar.GetResolver().Resolve(package_path)
        if not resolved_path:
            self._AddError(f"Failed to resolve package path '{package_path}'.")
            return

        zip_file = Usd.ZipFile.Open(resolved_path)
        if not zip_file:
            self._AddError(f"Could not open package at path '{resolved_path}'.")
            return
        yield ComplianceCheckerEvent(ComplianceCheckerEventType.ZIP_FILE, (zip_file, package_path))

    def _traverse_range(self, primRangeIt, isStageRoot) -> Iterator[ComplianceCheckerEvent]:
        prims_with_variants = []
        root_prim = primRangeIt.GetCurrentPrim()
        for prim in primRangeIt:
            # Skip variant set check on the root prim if it is the stage'.
            if not self._doVariants or (not isStageRoot and prim == root_prim):
                yield ComplianceCheckerEvent(ComplianceCheckerEventType.PRIM, prim)
                continue

            variant_sets = prim.GetVariantSets()
            variant_sets_names = variant_sets.GetNames()
            if len(variant_sets_names) == 0:
                yield ComplianceCheckerEvent(ComplianceCheckerEventType.PRIM, prim)
            else:
                prims_with_variants.append(prim)
                primRangeIt.PruneChildren()

        # Process prims before prims_with_variants
        yield ComplianceCheckerEvent(ComplianceCheckerEventType.FLUSH, None)
        for prim in prims_with_variants:
            yield from self._traverse_variants(prim)

    def _traverse_variants(self, prim) -> Iterator[ComplianceCheckerEvent]:
        if prim.IsInstanceProxy():
            return
        variant_sets = prim.GetVariantSets()
        variant_sets_names = variant_sets.GetNames()
        all_variant_names = []
        for vset_name in variant_sets_names:
            variant_set = variant_sets.GetVariantSet(vset_name)
            variant_names = variant_set.GetVariantNames()
            all_variant_names.append(variant_names)

        all_variations = itertools.product(*all_variant_names)

        for variation in all_variations:
            for idx, sel in enumerate(variation):
                variant_sets.SetSelection(variant_sets_names[idx], sel)
            yield ComplianceCheckerEvent(ComplianceCheckerEventType.RESET_CACHE, None)
            prim_range_iterator = iter(Usd.PrimRange(prim, Usd.TraverseInstanceProxies()))
            yield from self._traverse_range(prim_range_iterator, isStageRoot=False)
