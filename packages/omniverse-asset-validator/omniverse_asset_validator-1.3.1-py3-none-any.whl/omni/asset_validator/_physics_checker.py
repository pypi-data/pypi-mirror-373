# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
__all__ = [
    "RigidBodyChecker",
    "ColliderChecker",
    "PhysicsJointChecker",
    "ArticulationChecker",
]

from collections.abc import Callable

import omni.capabilities as cap
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics

from ._base_rule_checker import BaseRuleChecker
from ._requirements import Requirement, register_requirements


def _scale_is_uniform(scale: Gf.Vec3d) -> bool:
    eps = 1.0e-5
    # Find min and max scale values
    if scale[0] < scale[1]:
        lo, hi = scale[0], scale[1]
    else:
        lo, hi = scale[1], scale[0]

    if scale[2] < lo:
        lo = scale[2]
    elif scale[2] > hi:
        hi = scale[2]

    if lo * hi < 0.0:
        return False  # opposite signs

    return hi - lo <= eps * lo if hi > 0.0 else lo - hi >= eps * hi


def _is_dynamic_body(usd_prim: Usd.Prim) -> bool:
    rb_api = UsdPhysics.RigidBodyAPI(usd_prim)
    if rb_api:
        is_api_schema_enabled = rb_api.GetRigidBodyEnabledAttr().Get()
        return is_api_schema_enabled
    return False


def _get_rel(ref: Usd.Relationship) -> Sdf.Path:
    targets = ref.GetTargets()

    if not targets:
        return Sdf.Path()

    return targets[0]


def _check_joint_rel(rel_path: Sdf.Path, joint_prim: Usd.Prim) -> bool:
    if rel_path == Sdf.Path():
        return True

    rel_prim = joint_prim.GetStage().GetPrimAtPath(rel_path)
    return rel_prim.IsValid()


def register_requirements_and_add_doc(
    *requirements: Requirement,
) -> Callable[[type[BaseRuleChecker]], type[BaseRuleChecker]]:
    def _register_requirements_and_add_doc(rule_class: type[BaseRuleChecker]) -> type[BaseRuleChecker]:
        register_requirements(*requirements)(rule_class)
        rule_class.__doc__ = "Implements validation of the following requirements:\n\n"
        rule_class.__doc__ += "\n".join(f"\t* {req.code}: {req.message}" for req in requirements)
        return rule_class

    return _register_requirements_and_add_doc


class BaseRuleCheckerWCache(BaseRuleChecker):
    def __init__(self, verbose: bool, consumerLevelChecks: bool, assetLevelChecks: bool):
        super().__init__(verbose, consumerLevelChecks, assetLevelChecks)
        self.InitCaches()

    def InitCaches(self):
        self._xform_cache = UsdGeom.XformCache(Usd.TimeCode.Default())
        self._is_a_or_under_a_dynamic_body_cache = dict()
        self._is_under_articulation_root_cache = dict()

    def ResetCaches(self):
        self._xform_cache.Clear()
        self._is_a_or_under_a_dynamic_body_cache.clear()
        self._is_under_articulation_root_cache.clear()

    def _cache_value_to_list(self, cache: dict, value: tuple[bool, Usd.Prim], prim_paths: list[Sdf.Path]):
        for path in prim_paths:
            cache[path] = value

    def _is_under_articulation_root(self, usd_prim: Usd.Prim) -> bool:
        path = usd_prim.GetPath()
        prim_list = []
        current = usd_prim.GetParent()
        while current and current != usd_prim.GetStage().GetPseudoRoot():
            prim_list.append(path)
            path = current.GetPath()
            cached = self._is_under_articulation_root_cache.get(path)
            if cached is not None:
                self._cache_value_to_list(self._is_under_articulation_root_cache, cached, prim_list)
                return cached

            art_api = UsdPhysics.ArticulationRootAPI(current)
            if art_api:
                self._cache_value_to_list(self._is_under_articulation_root_cache, True, prim_list)
                return True

            current = current.GetParent()

        self._cache_value_to_list(self._is_under_articulation_root_cache, False, prim_list)
        return False

    def _check_non_uniform_scale(self, xformable: UsdGeom.Xformable) -> bool:
        tr = Gf.Transform(self._xform_cache.GetLocalToWorldTransform(xformable.GetPrim()))
        sc = tr.GetScale()
        return _scale_is_uniform(sc)

    def _has_dynamic_body_parent(self, usd_prim: Usd.Prim, rb_api: UsdPhysics.RigidBodyAPI) -> tuple[bool, Usd.Prim]:
        # early exit on disabled RB, no cache information
        if rb_api and not rb_api.GetRigidBodyEnabledAttr().Get():
            return False, None

        # early exit on immediate xformstack reset
        path = usd_prim.GetPath()
        xform = UsdGeom.Xformable(usd_prim)
        if xform and xform.GetResetXformStack():
            # save True to cache for children and point to me
            self._cache_value_to_list(self._is_a_or_under_a_dynamic_body_cache, (True, usd_prim), [path])
            return False, None

        # look for either a dynamic body or an xformstack reset towards the root
        # apply cache downwards to all children on exit
        prim_list = []
        current = usd_prim.GetParent()
        while current != usd_prim.GetStage().GetPseudoRoot():
            path = current.GetPath()
            cached = self._is_a_or_under_a_dynamic_body_cache.get(path)
            if cached is not None:
                self._cache_value_to_list(self._is_a_or_under_a_dynamic_body_cache, cached, prim_list)
                return cached[0], cached[1]

            prim_list.append(path)

            # first check dynamic body
            if _is_dynamic_body(current):
                self._cache_value_to_list(self._is_a_or_under_a_dynamic_body_cache, (True, current), prim_list)
                self._is_a_or_under_a_dynamic_body_cache[usd_prim.GetPath()] = (True, usd_prim)
                return True, current

            # then check xformstack reset
            xform = UsdGeom.Xformable(current)
            if xform and xform.GetResetXformStack():
                # save False, I am not a dynamic body (checked above) and reset was encountered
                self._cache_value_to_list(self._is_a_or_under_a_dynamic_body_cache, (False, None), prim_list)
                return False, None

            current = current.GetParent()

        # nothing found until root encountered
        self._cache_value_to_list(self._is_a_or_under_a_dynamic_body_cache, (False, None), prim_list)
        return False, None


@register_requirements_and_add_doc(
    cap.PhysicsRigidBodiesRequirements.RB_005,
    cap.PhysicsRigidBodiesRequirements.RB_006,
    cap.PhysicsRigidBodiesRequirements.RB_003,
    cap.PhysicsRigidBodiesRequirements.RB_009,
)
class RigidBodyChecker(BaseRuleCheckerWCache):
    _NESTED_RIGID_BODY_REQUIREMENT = cap.PhysicsRigidBodiesRequirements.RB_006
    _RIGID_BODY_ORIENTATION_SCALE_REQUIREMENT = cap.PhysicsRigidBodiesRequirements.RB_009
    _RIGID_BODY_NON_XFORMABLE_REQUIREMENT = cap.PhysicsRigidBodiesRequirements.RB_003
    _RIGID_BODY_NON_INSTANCEABLE_REQUIREMENT = cap.PhysicsRigidBodiesRequirements.RB_005

    _NESTED_RIGID_BODY_MESSAGE = (
        "Enabled rigid body is missing xformstack reset, when a child of a rigid body ({0}) in hierarchy. "
        "Simulation of multiple rigid bodies in a hierarchy will cause unpredicted results. Please fix the hierarchy "
        "or use XformStack reset."
    )
    _RIGID_BODY_NON_XFORMABLE_MESSAGE = "Rigid body API has to be applied to an xformable prim."
    _RIGID_BODY_NON_INSTANCEABLE_MESSAGE = "RigidBodyAPI on an instance proxy is not supported."
    _RIGID_BODY_ORIENTATION_SCALE_MESSAGE = "ScaleOrientation is not supported for rigid bodies."

    def CheckPrim(self, usd_prim: Usd.Prim):
        rb_api = UsdPhysics.RigidBodyAPI(usd_prim)
        if not rb_api:
            return

        # Check if rigid body is applied to xformable
        xformable = UsdGeom.Xformable(usd_prim)
        if not xformable:
            self._AddFailedCheck(
                message=self._RIGID_BODY_NON_XFORMABLE_MESSAGE,
                at=usd_prim,
                requirement=self._RIGID_BODY_NON_XFORMABLE_REQUIREMENT,
            )

        # Check instancing
        if usd_prim.IsInstanceProxy():
            report_instance_error = True

            # Check kinematic state
            kinematic = False
            rb_api.GetKinematicEnabledAttr().Get(kinematic)
            if kinematic:
                report_instance_error = False

            # Check if rigid body is enabled
            enabled = rb_api.GetRigidBodyEnabledAttr().Get()
            if not enabled:
                report_instance_error = False

            if report_instance_error:
                self._AddFailedCheck(
                    message=self._RIGID_BODY_NON_INSTANCEABLE_MESSAGE,
                    at=usd_prim,
                    requirement=self._RIGID_BODY_NON_INSTANCEABLE_REQUIREMENT,
                )

        # Check scale orientation
        if xformable:
            mat = self._xform_cache.GetLocalToWorldTransform(usd_prim)
            tr = Gf.Transform(mat)
            sc = tr.GetScale()

            if not _scale_is_uniform(sc) and tr.GetPivotOrientation().GetQuaternion() != Gf.Quaternion.GetIdentity():
                self._AddFailedCheck(
                    message=self._RIGID_BODY_ORIENTATION_SCALE_MESSAGE,
                    at=usd_prim,
                    requirement=self._RIGID_BODY_ORIENTATION_SCALE_REQUIREMENT,
                )

        # Check nested rigid body
        has_dynamic_parent, body_parent = self._has_dynamic_body_parent(usd_prim, rb_api)
        if has_dynamic_parent:
            self._AddFailedCheck(
                message=self._NESTED_RIGID_BODY_MESSAGE.format(body_parent.GetPath()),
                at=usd_prim,
                requirement=self._NESTED_RIGID_BODY_REQUIREMENT,
            )


@register_requirements_and_add_doc(
    cap.PhysicsRigidBodiesRequirements.RB_COL_004,
)
class ColliderChecker(BaseRuleCheckerWCache):
    _COLLIDER_NON_UNIFORM_SCALE_REQUIREMENT = cap.PhysicsRigidBodiesRequirements.RB_COL_004
    _COLLIDER_NON_UNIFORM_SCALE_MESSAGE = "Non-uniform scale is not supported for {0} geometry."

    def CheckPrim(self, usd_prim: Usd.Prim):
        collision_api = UsdPhysics.CollisionAPI(usd_prim)
        if not collision_api:
            return

        if not usd_prim.IsA(UsdGeom.Gprim):
            return

        # Note: Removed Capsule_1 and Cylinder_1 from this check as they are not supported by older USD versions
        if (
            usd_prim.IsA(UsdGeom.Sphere)
            or usd_prim.IsA(UsdGeom.Capsule)
            or usd_prim.IsA(UsdGeom.Cylinder)
            or usd_prim.IsA(UsdGeom.Cone)
            or usd_prim.IsA(UsdGeom.Points)
        ):
            xform = UsdGeom.Xformable(usd_prim)
            if xform and not self._check_non_uniform_scale(xform):
                self._AddFailedCheck(
                    message=self._COLLIDER_NON_UNIFORM_SCALE_MESSAGE.format(usd_prim.GetTypeName()),
                    at=usd_prim,
                    requirement=self._COLLIDER_NON_UNIFORM_SCALE_REQUIREMENT,
                )


@register_requirements_and_add_doc(
    cap.PhysicsJointsRequirements.JT_002,
    cap.PhysicsJointsRequirements.JT_003,
)
class PhysicsJointChecker(BaseRuleChecker):
    _JOINT_INVALID_PRIM_REL_REQUIREMENT = cap.PhysicsJointsRequirements.JT_002
    _JOINT_MULTIPLE_PRIMS_REL_REQUIREMENT = cap.PhysicsJointsRequirements.JT_003

    _JOINT_INVALID_PRIM_REL_MESSAGE = (
        "Joint's Body{0} relationship points to a non-existent prim {1}, joint will not be parsed."
    )
    _JOINT_MULTIPLE_PRIMS_REL_MESSAGE = (
        "Joint prim does have a Body{0} relationship to multiple bodies and this is not supported."
    )

    def CheckPrim(self, usd_prim: Usd.Prim):
        physics_joint = UsdPhysics.Joint(usd_prim)

        if not physics_joint:
            return

        # Check valid relationship prims
        rel0path = _get_rel(physics_joint.GetBody0Rel())
        rel1path = _get_rel(physics_joint.GetBody1Rel())

        # Check relationship validity
        if not _check_joint_rel(rel0path, usd_prim):
            self._AddFailedCheck(
                message=self._JOINT_INVALID_PRIM_REL_MESSAGE.format(0, rel0path),
                at=usd_prim,
                requirement=self._JOINT_INVALID_PRIM_REL_REQUIREMENT,
            )

        if not _check_joint_rel(rel1path, usd_prim):
            self._AddFailedCheck(
                message=self._JOINT_INVALID_PRIM_REL_MESSAGE.format(1, rel1path),
                at=usd_prim,
                requirement=self._JOINT_INVALID_PRIM_REL_REQUIREMENT,
            )

        # Check multiple relationship prims
        targets0 = physics_joint.GetBody0Rel().GetTargets()
        targets1 = physics_joint.GetBody1Rel().GetTargets()

        # Check relationship validity
        if len(targets0) > 1:
            self._AddFailedCheck(
                message=self._JOINT_MULTIPLE_PRIMS_REL_MESSAGE.format(0),
                at=usd_prim,
                requirement=self._JOINT_MULTIPLE_PRIMS_REL_REQUIREMENT,
            )

        if len(targets1) > 1:
            self._AddFailedCheck(
                message=self._JOINT_MULTIPLE_PRIMS_REL_MESSAGE.format(1),
                at=usd_prim,
                requirement=self._JOINT_MULTIPLE_PRIMS_REL_REQUIREMENT,
            )


@register_requirements_and_add_doc(
    cap.PhysicsJointsRequirements.JT_ART_002,
    cap.PhysicsJointsRequirements.JT_ART_003,
    cap.PhysicsJointsRequirements.JT_ART_004,
)
class ArticulationChecker(BaseRuleCheckerWCache):
    _NESTED_ARTICULATION_REQUIREMENT = cap.PhysicsJointsRequirements.JT_ART_002
    _ARTICULATION_ON_STATIC_BODY_REQUIREMENT = cap.PhysicsJointsRequirements.JT_ART_003
    _ARTICULATION_ON_KINEMATIC_BODY_REQUIREMENT = cap.PhysicsJointsRequirements.JT_ART_004

    _NESTED_ARTICULATION_MESSAGE = "Nested ArticulationRootAPI not supported."
    _ARTICULATION_ON_STATIC_BODY_MESSAGE = "ArticulationRootAPI definition on a static rigid body is not allowed."
    _ARTICULATION_ON_KINEMATIC_BODY_MESSAGE = "ArticulationRootAPI definition on a kinematic rigid body is not allowed."

    def CheckPrim(self, usd_prim: Usd.Prim):
        art_api = UsdPhysics.ArticulationRootAPI(usd_prim)

        if not art_api:
            return

        # Check for nested articulation roots
        if self._is_under_articulation_root(usd_prim):
            self._AddFailedCheck(
                message=self._NESTED_ARTICULATION_MESSAGE,
                at=usd_prim,
                requirement=self._NESTED_ARTICULATION_REQUIREMENT,
            )

        # Check rigid body static or kinematic errors
        rbo_api = UsdPhysics.RigidBodyAPI(usd_prim)
        if rbo_api:
            # Check if rigid body is enabled
            body_enabled = rbo_api.GetRigidBodyEnabledAttr().Get()
            if not body_enabled:
                self._AddFailedCheck(
                    message=self._ARTICULATION_ON_STATIC_BODY_MESSAGE,
                    at=usd_prim,
                    requirement=self._ARTICULATION_ON_STATIC_BODY_REQUIREMENT,
                )

            # Check if kinematic is enabled
            kinematic_enabled = rbo_api.GetKinematicEnabledAttr().Get()
            if kinematic_enabled:
                self._AddFailedCheck(
                    message=self._ARTICULATION_ON_KINEMATIC_BODY_MESSAGE,
                    at=usd_prim,
                    requirement=self._ARTICULATION_ON_KINEMATIC_BODY_REQUIREMENT,
                )
