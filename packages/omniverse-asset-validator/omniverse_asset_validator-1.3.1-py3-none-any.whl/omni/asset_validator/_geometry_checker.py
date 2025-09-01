# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from collections.abc import Iterator

import omni.capabilities as cap
from pxr import Sdf, Tf, Usd, UsdGeom, Vt

from ._base_rule_checker import BaseRuleChecker
from ._fix import AuthoringLayers
from ._issues import Suggestion
from ._mesh_tools import (
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
from ._requirements import register_requirements

__all__ = [
    "IndexedPrimvarChecker",
    "ManifoldChecker",
    "SubdivisionSchemeChecker",
    "UnusedMeshTopologyChecker",
    "UnusedPrimvarChecker",
    "ValidateTopologyChecker",
    "WeldChecker",
    "ZeroAreaFaceChecker",
    "NormalsExistChecker",
]


@register_requirements(cap.GeometryRequirements.VG_010)
class SubdivisionSchemeChecker(BaseRuleChecker):
    """
    USD default value for subdivision scheme is Catmull-Clark. This is often overlooked and incorrect for tessellated
    CAD geometry. Additionally, it's often overlooked that normals should not be authored on a subdivision mesh.
    """

    @classmethod
    def set_to_none(cls, _: Usd.Stage, mesh: UsdGeom.Mesh) -> None:
        """Sets subdivision scheme to None"""
        mesh.GetSubdivisionSchemeAttr().Set(UsdGeom.Tokens.none)

    @classmethod
    def set_to_catmull_clark(cls, _: Usd.Stage, mesh: UsdGeom.Mesh) -> None:
        """Sets subdivision scheme to Catmull-Clark."""
        mesh.GetSubdivisionSchemeAttr().Set(UsdGeom.Tokens.catmullClark)

    def _validate_mesh(self, mesh: UsdGeom.Mesh) -> None:
        # Normals may be defined via attribute or via primvar.
        normals_attr: Usd.Attribute = mesh.GetNormalsAttr()
        primvar_api: UsdGeom.PrimvarsAPI = UsdGeom.PrimvarsAPI(mesh)
        primvar: UsdGeom.Primvar = primvar_api.GetPrimvar(UsdGeom.Tokens.normals)
        has_normals: bool = normals_attr.HasAuthoredValue() or primvar.HasAuthoredValue()

        # Get the subdivision attribute
        attr: Usd.Attribute = mesh.GetSubdivisionSchemeAttr()
        scheme: Tf.Token | None = attr.Get()
        if not attr.HasAuthoredValue() and not has_normals:
            self._AddFailedCheck(
                requirement=cap.GeometryRequirements.VG_010,
                message="Subdivision scheme is not set, set to the default, i.e. Catmull-Clark.",
                at=mesh,
                suggestion=Suggestion(
                    message="Set subdivision scheme to Catmull-Clark",
                    callable=self.set_to_catmull_clark,
                    at=AuthoringLayers(attr),
                ),
            )
        elif not attr.HasAuthoredValue() and has_normals:
            self._AddFailedCheck(
                requirement=cap.GeometryRequirements.VG_010,
                message="Subdivision scheme is not set, however normals are defined. The default setting i.e. "
                "Catmull-Clark will ignore the normals.",
                at=mesh,
                suggestion=Suggestion(
                    message="Set subdivision scheme to none for a simple polygonal mesh which uses normals",
                    callable=self.set_to_none,
                    at=AuthoringLayers(attr),
                ),
            )
        elif scheme != UsdGeom.Tokens.none and has_normals:
            self._AddWarning(
                requirement=cap.GeometryRequirements.VG_010,
                message="Normals should not be authored on a subdivision mesh, since subdivision algorithms "
                "define their own normals.",
                at=mesh,
            )

    def CheckPrim(self, prim: Usd.Prim) -> None:
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        if mesh:
            self._validate_mesh(mesh)


@register_requirements(cap.GeometryRequirements.VG_007)
class ManifoldChecker(BaseRuleChecker):
    """
    Counts the number of non-manifold edges and vertices. A non-manifold edge has more than two adjacent faces. A
    non-manifold vertex as more than two adjacent border edges, where a border edge is an edge with only one adjacent
    face.

    Works on non time varying geometry.
    """

    def _validate_mesh(self, mesh: UsdGeom.Mesh) -> None:
        points: Vt.Vec3fArray | None = mesh.GetPointsAttr().Get(Usd.TimeCode.EarliestTime())
        num_points: int = len(points) if points else 0
        indices: Vt.IntArray = mesh.GetFaceVertexIndicesAttr().Get(Usd.TimeCode.EarliestTime())
        face_sizes: Vt.IntArray = mesh.GetFaceVertexCountsAttr().Get(Usd.TimeCode.EarliestTime())

        if all((indices, face_sizes, num_points)):
            valid, _ = UsdGeom.Mesh.ValidateTopology(indices, face_sizes, num_points)
        else:
            valid = False
        if not valid:
            # Validated in ValidationTopologyChecker
            return

        num_non_manifold_vertices, num_non_manifold_edges, winding_consistent = check_manifold_elements(
            num_points, indices, face_sizes
        )

        if num_non_manifold_vertices > 0:
            self._AddWarning(
                requirement=cap.GeometryRequirements.VG_007,
                message=f"{num_non_manifold_vertices} vertices are non-manifold.",
                at=mesh,
            )
        if num_non_manifold_edges > 0:
            self._AddWarning(
                requirement=cap.GeometryRequirements.VG_007,
                message=f"{num_non_manifold_edges} edges are non-manifold.",
                at=mesh,
            )
        if not winding_consistent:
            self._AddWarning(
                requirement=cap.GeometryRequirements.VG_007,
                message="The face winding is not consistent.",
                at=mesh,
            )

    def CheckPrim(self, prim: Usd.Prim) -> None:
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        if mesh:
            points_attr: Usd.Attribute = mesh.GetPointsAttr()
            has_static_points: bool = points_attr.IsAuthored() and not points_attr.ValueMightBeTimeVarying()
            if not has_static_points:
                return
            indices_attr: Usd.Attribute = mesh.GetFaceVertexIndicesAttr()
            has_static_indices: bool = indices_attr.IsAuthored() and not indices_attr.ValueMightBeTimeVarying()
            if not has_static_indices:
                return
            face_sizes_attr: Usd.Attribute = mesh.GetFaceVertexCountsAttr()
            has_static_faces: bool = face_sizes_attr.IsAuthored() and not face_sizes_attr.ValueMightBeTimeVarying()
            if not has_static_faces:
                return
            self._validate_mesh(mesh)


@register_requirements(cap.GeometryRequirements.VG_009)
class IndexedPrimvarChecker(BaseRuleChecker):
    """
    For Primvars with non-constant values of interpolation, it is often the case that the same value is repeated many
    times in the array.

    An indexed primvar can be used in such cases to optimize for data storage if the primvar's interpolation is
    non-constant (i.e. uniform, varying, face varying or vertex).
    """

    def _validate_primvars(self, primvars_api: UsdGeom.PrimvarsAPI) -> None:
        for primvar in primvars_api.GetPrimvarsWithAuthoredValues():
            interpolation: Tf.Token = primvar.GetInterpolation()
            if interpolation == UsdGeom.Tokens.constant:
                continue
            try:
                if has_indexable_values(primvar):
                    self._AddWarning(
                        requirement=cap.GeometryRequirements.VG_009,
                        message=f"{primvar.GetName()} contains repeated values that can be indexed.",
                        at=primvar,
                    )
            except TypeError:
                self._AddError(
                    requirement=cap.GeometryRequirements.VG_009,
                    message="Primvar is not of array type.",
                    at=primvar,
                )
            except IndexError:
                self._AddError(
                    requirement=cap.GeometryRequirements.VG_009,
                    message="Primvar indices out of bounds",
                    at=primvar,
                )

    def CheckPrim(self, prim: Usd.Prim) -> None:
        primvars_api: UsdGeom.PrimvarsAPI = UsdGeom.PrimvarsAPI(prim)
        if not primvars_api:
            return
        interpolations: set[Tf.Token] = set(
            map(UsdGeom.Primvar.GetInterpolation, primvars_api.GetPrimvarsWithAuthoredValues())
        )
        if not interpolations or interpolations == {UsdGeom.Tokens.constant}:
            return
        self._validate_primvars(primvars_api)


@register_requirements(cap.GeometryRequirements.VG_018)
class UnusedMeshTopologyChecker(BaseRuleChecker):
    """
    Points which are not referenced by the indices can be removed.

    Works on non time varying geometry.
    """

    @staticmethod
    def __validate_mesh_points_indices(mesh: UsdGeom.Mesh):
        points: Vt.Vec3fArray = mesh.GetPointsAttr().Get(Usd.TimeCode.EarliestTime()) or Vt.Vec3fArray()
        num_points: int = len(points)
        indices: Vt.IntArray = mesh.GetFaceVertexIndicesAttr().Get(Usd.TimeCode.EarliestTime())
        face_sizes: Vt.IntArray = mesh.GetFaceVertexCountsAttr().Get(Usd.TimeCode.EarliestTime())
        if all((indices, face_sizes, num_points)):
            valid, _ = UsdGeom.Mesh.ValidateTopology(indices, face_sizes, num_points)
        else:
            valid = False

        return valid, points, indices

    def _validate_mesh(self, mesh: UsdGeom.Mesh) -> None:
        valid, points, indices = self.__validate_mesh_points_indices(mesh)
        if not valid:
            return

        num_points = len(points)
        if has_unreferenced_values(num_points, indices):
            if not self.__all_primvars_can_be_fixed(mesh.GetPrim(), points):
                self._AddFailedCheck(
                    requirement=cap.GeometryRequirements.VG_018,
                    message="Some points are not referenced by the faces (but it cannot be fixed"
                    " automatically as it has primvars that are vertex or varying interpolated"
                    " and time varying).",
                    at=mesh,
                )
            else:
                self._AddFailedCheck(
                    requirement=cap.GeometryRequirements.VG_018,
                    message="Some points are not referenced by the faces.",
                    at=mesh,
                    suggestion=Suggestion(
                        message="Removed unreferenced points", callable=self.remove_unreferenced_points
                    ),
                )
        elif has_invalid_indices(num_points, indices):
            self._AddFailedCheck(
                requirement=cap.GeometryRequirements.VG_018,
                message="Some face indices are invalid (above number of points).",
                at=mesh,
            )

    @classmethod
    def remove_unreferenced_points(cls, _: Usd.Stage, prim: Usd.Prim):
        if not (mesh := UsdGeom.Mesh(prim)):
            return

        valid, points, indices = UnusedMeshTopologyChecker.__validate_mesh_points_indices(mesh)
        if not valid:
            return

        # Don't remove invalid indices from faceIndices as it breaks geometry topology.
        remapped, remapped_points, indices, removed_value_indices = remove_unused_values_and_remap_indices(
            points, indices, False
        )
        if remapped:
            points_attr: Vt.Vec3fArray = mesh.GetPointsAttr()
            indices_attr: Vt.IntArray = mesh.GetFaceVertexIndicesAttr()
            with Sdf.ChangeBlock():
                points_attr.Set(remapped_points)
                indices_attr.Set(indices)

                # Remove corresponding primvar values if they are vertex or varying interpolated.
                primvars_api = UsdGeom.PrimvarsAPI(prim)
                for primvar in primvars_api.GetPrimvarsWithAuthoredValues():
                    if not cls.__is_interested_primvar(primvar):
                        continue

                    element_size = primvar.GetElementSize()
                    primvar_values = list(primvar.ComputeFlattened(Usd.TimeCode.EarliestTime())) or []
                    # Invalid primvar size.
                    if element_size < 1 or len(primvar_values) / element_size != len(points):
                        continue

                    # Remove value in reverse order to keep validity of indices.
                    if primvar.IsIndexed():
                        indices = list(primvar.GetIndices(Usd.TimeCode.EarliestTime())) or []
                        for index in sorted(removed_value_indices, reverse=True):
                            del indices[index]
                        primvar.SetIndices(indices)
                    else:
                        # Expand indices based on element size.
                        expanded_indices = []
                        for index in removed_value_indices:
                            expanded_indices.extend(range(index * element_size, (index + 1) * element_size))

                        for index in sorted(expanded_indices, reverse=True):
                            del primvar_values[index]
                        primvar.Set(primvar_values)

    def CheckPrim(self, prim: Usd.Prim) -> None:
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        if mesh:
            points_attr: Usd.Attribute = mesh.GetPointsAttr()
            has_static_points: bool = points_attr.IsAuthored() and not points_attr.ValueMightBeTimeVarying()
            if not has_static_points:
                return
            indices_attr: Usd.Attribute = mesh.GetFaceVertexIndicesAttr()
            has_static_indices: bool = indices_attr.IsAuthored() and not indices_attr.ValueMightBeTimeVarying()
            if not has_static_indices:
                return
            face_sizes_attr: Usd.Attribute = mesh.GetFaceVertexCountsAttr()
            has_static_faces: bool = face_sizes_attr.IsAuthored() and not face_sizes_attr.ValueMightBeTimeVarying()
            if not has_static_faces:
                return
            self._validate_mesh(mesh)

    @staticmethod
    def __is_interested_primvar(primvar: UsdGeom.Primvar):
        if not is_typename_array(primvar.GetTypeName()):
            return False

        interpolation: Tf.Token = primvar.GetInterpolation()
        is_vertex_or_varying = interpolation in [UsdGeom.Tokens.varying, UsdGeom.Tokens.vertex]
        if not is_vertex_or_varying:
            return False

        return True

    def __all_primvars_can_be_fixed(self, prim: Usd.Prim, points):
        primvars_api = UsdGeom.PrimvarsAPI(prim)
        for primvar in primvars_api.GetPrimvarsWithAuthoredValues():
            if not self.__is_interested_primvar(primvar):
                continue

            if primvar.ValueMightBeTimeVarying():
                return False

            element_size = primvar.GetElementSize()
            primvar_values = list(primvar.ComputeFlattened(Usd.TimeCode.EarliestTime())) or []
            # Invalid primvar size.
            if element_size < 1 or len(primvar_values) / element_size != len(points):
                return False

        return True


@register_requirements(cap.GeometryRequirements.VG_019)
class ZeroAreaFaceChecker(BaseRuleChecker):
    """
    Faces with zero area can be removed. May produce welding after removal.

    Works on non time varying geometry.
    """

    def validate_mesh(self, mesh: UsdGeom.Mesh) -> None:
        points: Vt.Vec3fArray | None = mesh.GetPointsAttr().Get(Usd.TimeCode.EarliestTime())
        point_size: int = len(points) if points else 0
        indices: Vt.IntArray = mesh.GetFaceVertexIndicesAttr().Get(Usd.TimeCode.EarliestTime())
        face_sizes: Vt.IntArray = mesh.GetFaceVertexCountsAttr().Get(Usd.TimeCode.EarliestTime())
        if all((indices, face_sizes, point_size)):
            valid_topology, _ = UsdGeom.Mesh.ValidateTopology(indices, face_sizes, point_size)
        else:
            valid_topology = False
        if not valid_topology:
            # Validated in ValidationTopologyChecker
            return

        if has_empty_faces(mesh):
            self._AddWarning(
                requirement=cap.GeometryRequirements.VG_019,
                message="The mesh contains zero area faces.",
                at=mesh,
            )

    def CheckPrim(self, prim: Usd.Prim) -> None:
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        if mesh:
            points_attr: Usd.Attribute = mesh.GetPointsAttr()
            has_static_points: bool = points_attr.IsAuthored() and not points_attr.ValueMightBeTimeVarying()
            if not has_static_points:
                return
            indices_attr: Usd.Attribute = mesh.GetFaceVertexIndicesAttr()
            has_static_indices: bool = indices_attr.IsAuthored() and not indices_attr.ValueMightBeTimeVarying()
            if not has_static_indices:
                return
            face_sizes_attr: Usd.Attribute = mesh.GetFaceVertexCountsAttr()
            has_static_faces: bool = face_sizes_attr.IsAuthored() and not face_sizes_attr.ValueMightBeTimeVarying()
            if not has_static_faces:
                return
            self.validate_mesh(mesh)


@register_requirements(cap.GeometryRequirements.VG_016)
class WeldChecker(BaseRuleChecker):
    """
    If attributes contain equal values they can be unified and the indices adjusted accordingly.

    Works on non time varying geometry.
    """

    def validate_mesh(self, mesh: UsdGeom.Mesh) -> None:
        try:
            if has_weldable_points(mesh):
                points_attr: Usd.Attribute = mesh.GetPointsAttr()
                self._AddWarning(
                    requirement=cap.GeometryRequirements.VG_016,
                    message="Some points are co-located and may be able to be merged.",
                    at=points_attr,
                )
        except ValueError as e:
            self._AddFailedCheck(
                requirement=cap.GeometryRequirements.VG_016,
                message=str(e),
                at=mesh,
            )

    def CheckPrim(self, prim: Usd.Prim) -> None:
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        if mesh:
            points_attr: Usd.Attribute = mesh.GetPointsAttr()
            has_static_points: bool = points_attr.IsAuthored() and not points_attr.ValueMightBeTimeVarying()
            if has_static_points:
                self.validate_mesh(mesh)


@register_requirements(cap.GeometryRequirements.VG_014)
class ValidateTopologyChecker(BaseRuleChecker):
    """
    Validate the topology of a mesh on all time samples.
    """

    @classmethod
    def _get_time_samples(cls, attribute: Usd.Attribute) -> Iterator[Usd.TimeCode]:
        if attribute.Get(Usd.TimeCode.Default()):
            yield Usd.TimeCode.Default()
        for time in attribute.GetTimeSamples():
            yield Usd.TimeCode(time)

    def _get_validate_topology_args(self, mesh: UsdGeom.Mesh) -> tuple[Vt.IntArray, Vt.IntArray, int]:
        # Get attributes
        points_attr: Usd.Attribute = mesh.GetPointsAttr()
        indices_attr: Usd.Attribute = mesh.GetFaceVertexIndicesAttr()
        counts_attr: Usd.Attribute = mesh.GetFaceVertexCountsAttr()
        # Determine time varying
        static_points: bool = not points_attr.ValueMightBeTimeVarying()
        static_indices: bool = not indices_attr.ValueMightBeTimeVarying()
        static_counts: bool = not counts_attr.ValueMightBeTimeVarying()
        static_topology: bool = static_indices and static_counts
        # Decide scenario
        if static_points and static_topology:
            indices: Vt.IntArray = indices_attr.Get(Usd.TimeCode.EarliestTime())
            counts: Vt.IntArray = counts_attr.Get(Usd.TimeCode.EarliestTime())
            points_attr_value: Vt.Vec3fArray | None = points_attr.Get(Usd.TimeCode.EarliestTime())
            point_size: int = len(points_attr_value) if points_attr_value else 0
            yield indices, counts, point_size
        elif static_topology:
            indices: Vt.IntArray = indices_attr.Get(Usd.TimeCode.EarliestTime())
            counts: Vt.IntArray = counts_attr.Get(Usd.TimeCode.EarliestTime())
            point_sizes: set[int] = set()
            for time in self._get_time_samples(points_attr):
                point_attr_value: Vt.Vec3fArray | None = points_attr.Get(time)
                point_size = len(point_attr_value) if point_attr_value else 0
                point_sizes.add(point_size)

            for point_size in point_sizes:
                yield indices, counts, point_size
        elif static_points:
            points_attr_value: Vt.Vec3fArray | None = points_attr.Get(Usd.TimeCode.EarliestTime())
            point_size: int = len(points_attr_value) if points_attr_value else 0
            if static_indices:
                indices: Vt.IntArray = indices_attr.Get(Usd.TimeCode.EarliestTime())
                for time in self._get_time_samples(counts_attr):
                    counts: Vt.IntArray = counts_attr.Get(time)
                    yield indices, counts, point_size
            elif static_counts:
                counts: Vt.IntArray = counts_attr.Get(Usd.TimeCode.EarliestTime())
                for time in self._get_time_samples(indices_attr):
                    indices: Vt.IntArray = indices_attr.Get(time)
                    yield indices, counts, point_size
            else:
                times: set[Usd.TimeCode] = set(self._get_time_samples(indices_attr)) & set(
                    self._get_time_samples(counts_attr)
                )
                for time in times:
                    indices: Vt.IntArray = indices_attr.Get(time)
                    counts: Vt.IntArray = counts_attr.Get(time)
                    yield indices, counts, point_size
        else:
            times: set[Usd.TimeCode] = (
                set(self._get_time_samples(points_attr))
                & set(self._get_time_samples(indices_attr))
                & set(self._get_time_samples(counts_attr))
            )
            for time in times:
                indices: Vt.IntArray = indices_attr.Get(time)
                counts: Vt.IntArray = counts_attr.Get(time)
                points: Vt.Vec3fArray | None = points_attr.Get(time)
                point_size: int = len(points) if points else 0
                yield indices, counts, point_size

    def validate(self, mesh: UsdGeom.Mesh) -> None:
        for indices, counts, point_size in self._get_validate_topology_args(mesh):
            if all((indices, counts, point_size)):
                valid_topology, _ = UsdGeom.Mesh.ValidateTopology(indices, counts, point_size)
            else:
                # No Points, no FaceVertexCounts, or no indices - not valid topology
                valid_topology = False

            if not valid_topology:
                self._AddFailedCheck(
                    requirement=cap.GeometryRequirements.VG_014,
                    message="Invalid topology found",
                    at=mesh,
                )
                break

    def CheckPrim(self, prim: Usd.Prim) -> None:
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        if mesh:
            self.validate(mesh)


@register_requirements(cap.GeometryRequirements.VG_011)
class UnusedPrimvarChecker(BaseRuleChecker):
    """
    Values which are not referenced by the indices in a primvar can be removed.

    Works on non time varying geometry.
    """

    def _validate_primvars(self, primvars_api: UsdGeom.PrimvarsAPI) -> None:
        for primvar in primvars_api.GetPrimvarsWithAuthoredValues():
            # Skips non-indexed primvars and ones without a list value type.
            if not primvar.IsIndexed():
                continue

            if not is_typename_array(primvar.GetTypeName()):
                continue

            interpolation: Tf.Token = primvar.GetInterpolation()
            is_vertex_or_varying = interpolation in [UsdGeom.Tokens.varying, UsdGeom.Tokens.vertex]
            invalid_indices = has_invalid_primvar_indices(primvar)
            unreferenced_values = has_unreferenced_primvar(primvar)
            if unreferenced_values or (is_vertex_or_varying and invalid_indices):
                if unreferenced_values:
                    warning_message = f"{primvar.GetName()} contains values not referenced by its indices."
                    suggestion_message = "Remove unreferenced values"
                else:
                    warning_message = (
                        f"{primvar.GetName()} contains invalid indices that are above the number of values."
                    )
                    suggestion_message = "Remove invalid indices"
                self._AddWarning(
                    requirement=cap.GeometryRequirements.VG_011,
                    message=warning_message,
                    at=primvar.GetAttr(),
                    suggestion=Suggestion(
                        message=suggestion_message,
                        callable=self.remove_unreferenced_values,
                    ),
                )
            elif invalid_indices:
                self._AddWarning(
                    requirement=cap.GeometryRequirements.VG_011,
                    message=f"{primvar.GetName()} contains invalid indices that are above the number of values "
                    f"(but it cannot be fixed automatically as the interpolation is neither UsdGeom.Tokens.Vertex "
                    f"nor UsdGeom.Tokens.Varying).",
                    at=primvar.GetAttr(),
                )

    def CheckPrim(self, prim: Usd.Prim) -> None:
        primvars_api: UsdGeom.PrimvarsAPI = UsdGeom.PrimvarsAPI(prim)
        if primvars_api:
            self._validate_primvars(primvars_api)

    @staticmethod
    def remove_unreferenced_values(_: Usd.Stage, attr: Usd.Attribute):
        if not (primvar := UsdGeom.Primvar(attr)) or not primvar.IsIndexed():
            return

        interpolation: Tf.Token = primvar.GetInterpolation()
        is_vertex_or_varying = interpolation and interpolation in [UsdGeom.Tokens.varying, UsdGeom.Tokens.vertex]
        primvar_values = primvar.Get(Usd.TimeCode.EarliestTime()) or []
        indices: Vt.IntArray = primvar.GetIndices(Usd.TimeCode.EarliestTime()) or []
        remapped, primvar_values, indices, _ = remove_unused_values_and_remap_indices(
            primvar_values, indices, is_vertex_or_varying
        )
        if remapped:
            with Sdf.ChangeBlock():
                primvar.Set(primvar_values)
                primvar.SetIndices(indices)


@register_requirements(cap.GeometryRequirements.VG_027)
class NormalsExistChecker(BaseRuleChecker):
    """
    Check that meshes have normals. All meshes should have normals
    unless they have the subdivision scheme set. Meshes cannot have
    both normals and subdivision set.
    """

    @classmethod
    def set_to_none(cls, _: Usd.Stage, mesh: UsdGeom.Mesh) -> None:
        """Sets subdivision scheme to None"""
        mesh.GetSubdivisionSchemeAttr().Set(UsdGeom.Tokens.none)

    def _validate_mesh(self, mesh: UsdGeom.Mesh) -> None:
        # Normals may be defined via attribute or via primvar.
        normals_attr: Usd.Attribute = mesh.GetNormalsAttr()
        primvar_api: UsdGeom.PrimvarsAPI = UsdGeom.PrimvarsAPI(mesh)
        primvar: UsdGeom.Primvar = primvar_api.GetPrimvar(UsdGeom.Tokens.normals)
        has_normals: bool = normals_attr.HasAuthoredValue() or primvar.HasAuthoredValue()

        # Get the subdivision attribute
        subdivision_attr: Usd.Attribute = mesh.GetSubdivisionSchemeAttr()
        subdivision_scheme: Tf.Token = mesh.GetSubdivisionSchemeAttr().Get()

        # Normals are set but subdivision scheme is not "none". Fail and suggest fix.
        if subdivision_scheme != UsdGeom.Tokens.none and has_normals:
            self._AddFailedCheck(
                requirement=cap.GeometryRequirements.VG_027,
                message="Normals are defined but subdivision mesh also has normals, either remove normals or set"
                "subdivision scheme to None.",
                at=mesh,
                suggestion=Suggestion(
                    message="Set subdivision scheme to none for a polygonal mesh which uses normals",
                    callable=self.set_to_none,
                    at=AuthoringLayers(subdivision_attr),
                ),
            )

        # No normals and subdivision is set to None. Invalid. Warn and ask user to set one
        elif subdivision_scheme == UsdGeom.Tokens.none and not has_normals:
            self._AddFailedCheck(
                requirement=cap.GeometryRequirements.VG_027,
                message="Either normals should be authored or subdivision should be set to Catmull-Clark or Loop ",
                at=mesh,
            )
            pass

    def CheckPrim(self, prim: Usd.Prim) -> None:
        mesh: UsdGeom.Mesh = UsdGeom.Mesh(prim)
        if mesh:
            self._validate_mesh(mesh)
