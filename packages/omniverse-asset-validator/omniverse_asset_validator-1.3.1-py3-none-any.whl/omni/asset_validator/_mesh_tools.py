# SPDX-FileCopyrightText: Copyright (c) 2023-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
from __future__ import annotations

import operator
from collections import defaultdict
from collections.abc import Sequence
from functools import cache
from itertools import repeat
from typing import Any, TypeVar

from pxr import Gf, Sdf, Tf, Usd, UsdGeom, Vt

from ._import_utils import default_implementation, default_implementation_method

__all__ = [
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
]

VtArray = Sequence
"""Alias. For typing."""

ScalarType = TypeVar(
    "ScalarType",
    int,
    float,
    Gf.Vec2f,
    Gf.Vec3f,
)
"""Alias. For typing."""

_ARRAY_TYPE_NAMES: set[Sdf.ValueTypeNames] = {
    Sdf.ValueTypeNames.BoolArray,
    Sdf.ValueTypeNames.UCharArray,
    Sdf.ValueTypeNames.IntArray,
    Sdf.ValueTypeNames.UIntArray,
    Sdf.ValueTypeNames.Int64Array,
    Sdf.ValueTypeNames.UInt64Array,
    Sdf.ValueTypeNames.HalfArray,
    Sdf.ValueTypeNames.FloatArray,
    Sdf.ValueTypeNames.DoubleArray,
    Sdf.ValueTypeNames.TimeCodeArray,
    Sdf.ValueTypeNames.StringArray,
    Sdf.ValueTypeNames.TokenArray,
    Sdf.ValueTypeNames.AssetArray,
    Sdf.ValueTypeNames.Int2Array,
    Sdf.ValueTypeNames.Int3Array,
    Sdf.ValueTypeNames.Int4Array,
    Sdf.ValueTypeNames.Half2Array,
    Sdf.ValueTypeNames.Half3Array,
    Sdf.ValueTypeNames.Half4Array,
    Sdf.ValueTypeNames.Float2Array,
    Sdf.ValueTypeNames.Float3Array,
    Sdf.ValueTypeNames.Float4Array,
    Sdf.ValueTypeNames.Double2Array,
    Sdf.ValueTypeNames.Double3Array,
    Sdf.ValueTypeNames.Double4Array,
    Sdf.ValueTypeNames.Point3hArray,
    Sdf.ValueTypeNames.Point3fArray,
    Sdf.ValueTypeNames.Point3dArray,
    Sdf.ValueTypeNames.Vector3hArray,
    Sdf.ValueTypeNames.Vector3fArray,
    Sdf.ValueTypeNames.Vector3dArray,
    Sdf.ValueTypeNames.Normal3hArray,
    Sdf.ValueTypeNames.Normal3fArray,
    Sdf.ValueTypeNames.Normal3dArray,
    Sdf.ValueTypeNames.Color3hArray,
    Sdf.ValueTypeNames.Color3fArray,
    Sdf.ValueTypeNames.Color3dArray,
    Sdf.ValueTypeNames.Color4hArray,
    Sdf.ValueTypeNames.Color4fArray,
    Sdf.ValueTypeNames.Color4dArray,
    Sdf.ValueTypeNames.QuathArray,
    Sdf.ValueTypeNames.QuatfArray,
    Sdf.ValueTypeNames.QuatdArray,
    Sdf.ValueTypeNames.Matrix2dArray,
    Sdf.ValueTypeNames.Matrix3dArray,
    Sdf.ValueTypeNames.Matrix4dArray,
    Sdf.ValueTypeNames.Frame4dArray,
    Sdf.ValueTypeNames.TexCoord2hArray,
    Sdf.ValueTypeNames.TexCoord2fArray,
    Sdf.ValueTypeNames.TexCoord2dArray,
    Sdf.ValueTypeNames.TexCoord3hArray,
    Sdf.ValueTypeNames.TexCoord3fArray,
    Sdf.ValueTypeNames.TexCoord3dArray,
    # Sdf.ValueTypeNames.PathExpressionArray,
}


def is_typename_array(type_name: Sdf.ValueTypeName):
    return type_name in _ARRAY_TYPE_NAMES


@default_implementation
def check_manifold_elements(num_vertices: int, indices: Vt.IntArray, face_sizes: Vt.IntArray) -> tuple[int, int, bool]:
    """
    Construct all the edges in geometry and finds if we have:
    - Non-manifold vertices: If vertices are repeated in the geometry.
    - Non-manifold edges: If edges are repeated multiple times.
    - Inconsistent winding: If polygon winding seems inconsistent.

    Args:
        num_vertices: The number of total vertices.
        indices: An array of all indices.
        face_sizes: An array of all face sizes.
    """
    # Create a mapping for the edges
    num_edges: int = len(indices)
    edges: Sequence[tuple[int, int, bool]] = [(0, 0, False)] * num_edges

    # Collect all edges, directions from all faces
    current_index: int = 0
    for face_size in face_sizes:
        for i in range(face_size):
            p: int = indices[current_index + i]
            q: int = indices[current_index + (i + 1) % face_size]
            edges[current_index + i] = (p, q, p < q)
        current_index += face_size

    # Create a dict of edge -> direction.
    indices_to_edges: dict[tuple[int, int], Sequence[bool]] = defaultdict(list)
    for p, q, direction in edges:
        # Create stable key, regardless of the order of p and q
        key: tuple[int, int] = (min(p, q), max(p, q))
        indices_to_edges[key].append(direction)

    num_nonmanifold_edges: int = 0
    num_adjacent_edges: Sequence[int] = [0] * num_vertices
    winding_consistent: bool = True
    for (p, q), directions in indices_to_edges.items():
        if len(directions) > 2:
            num_nonmanifold_edges += 1
        elif len(directions) == 2:
            if directions[0] == directions[1]:
                winding_consistent = False
        elif len(directions) == 1:
            num_adjacent_edges[p] += 1
            num_adjacent_edges[q] += 1

    # Count num nonmanifold vertices
    num_nonmanifold_vertices: int = 0
    for count in num_adjacent_edges:
        if count > 2:
            num_nonmanifold_vertices += 1

    return num_nonmanifold_vertices, num_nonmanifold_edges, winding_consistent


@check_manifold_elements.numpy
def _(num_vertices: int, indices: Vt.IntArray, face_sizes: Vt.IntArray) -> tuple[int, int, bool]:
    """NumPy implementation of check_manifold_elements"""
    import numpy as np

    # Convert to numpy arrays if not already
    indices = np.array(indices)
    face_sizes = np.array(face_sizes)

    # Create array of face start indices
    face_starts = np.concatenate(([0], np.cumsum(face_sizes)[:-1]))

    # Create all edges by pairing consecutive vertices in each face
    edge_starts = indices
    edge_ends = np.concatenate([indices[1:], indices[0:1]])

    # Fix the last vertex of each face to connect back to first vertex
    face_end_indices = face_starts + face_sizes - 1
    edge_ends[face_end_indices] = indices[face_starts]

    # Create stable edge keys (min vertex, max vertex)
    edge_mins = np.minimum(edge_starts, edge_ends)
    edge_maxs = np.maximum(edge_starts, edge_ends)
    edge_directions = edge_starts < edge_ends

    # Create stable edge keys using bit shifting for faster comparison
    # Assuming indices are less than 2^31
    edge_keys = (edge_mins.astype(np.int64) << 32) | edge_maxs.astype(np.int64)
    _, inverse_indices, edge_counts = np.unique(edge_keys, return_inverse=True, return_counts=True)
    # Count non-manifold edges
    num_nonmanifold_edges = np.sum(edge_counts > 2)

    # Check winding consistency only for double edges
    winding_consistent = True
    counts_of_edges = edge_counts[inverse_indices]
    double_edges_mask = counts_of_edges == 2
    if np.any(double_edges_mask):
        # Keep only the double edges
        edge_directions = edge_directions[double_edges_mask]
        edge_keys = edge_keys[double_edges_mask]
        # Argsort edge_keys to group the same edge together
        sorted_indices = np.argsort(edge_keys)
        # Get the directions and sort them by the sorted edge_keys
        directions = edge_directions[sorted_indices].reshape(-1, 2)
        # Check if the directions are consistent
        inconsistent_pairs = directions[:, 0] == directions[:, 1]
        winding_consistent = not np.any(inconsistent_pairs)

    single_edges_mask = counts_of_edges == 1
    if np.any(single_edges_mask):
        # Count num nonmanifold vertices
        vertex_edge_counts = np.bincount(edge_mins[single_edges_mask], minlength=num_vertices)
        vertex_edge_counts += np.bincount(edge_maxs[single_edges_mask], minlength=num_vertices)
        num_nonmanifold_vertices = np.sum(vertex_edge_counts > 2)
    else:
        num_nonmanifold_vertices = 0

    return num_nonmanifold_vertices, num_nonmanifold_edges, winding_consistent


@default_implementation
def has_empty_faces(mesh: UsdGeom.Mesh) -> bool:
    vertices: Vt.Vec3fArray = mesh.GetPointsAttr().Get(Usd.TimeCode.EarliestTime())
    indices: Vt.IntArray = mesh.GetFaceVertexIndicesAttr().Get(Usd.TimeCode.EarliestTime())
    face_sizes: Vt.IntArray = mesh.GetFaceVertexCountsAttr().Get(Usd.TimeCode.EarliestTime())

    index: int = 0
    for face_size in face_sizes:
        # compute normal for orientation
        points: Sequence[Gf.Vec3f] = list(map(vertices.__getitem__, indices[index : index + face_size]))
        # points[i] - points[0]
        deltas: Sequence[Gf.Vec3f] = list(map(operator.sub, points[1:], repeat(points[0], face_size - 1)))
        # deltas[i] * deltas[i+1]
        products: Sequence[Gf.Vec3f] = list(map(Gf.Cross, deltas[:-1], deltas[1:]))
        # To support Python3.7 we can't use `start`
        # normal: Gf.Vec3f = sum(products, start=Gf.Vec3f(0, 0, 0))
        normal = Gf.Vec3f(0, 0, 0)
        for product in products:
            normal += product

        # compute area
        area: float = 0.0
        l: float = normal.GetLength()
        if l > 0.0:
            normal /= l
            area = 0.5 * sum(map(Gf.Dot, products, repeat(normal, len(products))))

        if abs(area) <= 0:
            return True

        index += face_size
    return False


@has_empty_faces.numpy
def _(mesh: UsdGeom.Mesh) -> bool:
    import numpy as np

    vertices: np.array = np.array(mesh.GetPointsAttr().Get(Usd.TimeCode.EarliestTime()))
    indices: np.array = np.array(mesh.GetFaceVertexIndicesAttr().Get(Usd.TimeCode.EarliestTime()))
    face_sizes: np.array = np.array(mesh.GetFaceVertexCountsAttr().Get(Usd.TimeCode.EarliestTime()))

    # compute flattened vertices
    flattened: np.array = vertices.take(indices, axis=0)
    flattened_start_indices = np.concatenate([[0], np.cumsum(face_sizes)[:-1]])

    # flattened[N][i] - flattened[N][0]
    deltas = flattened - flattened.take(flattened_start_indices, axis=0).repeat(face_sizes, axis=0)

    # deltas[N][i] x deltas[N][i+1]
    deltas = deltas.astype(np.float64)
    cross_product = np.concatenate([np.cross(deltas[:-1], deltas[1:]), deltas[0:1]])

    # sum(products[N][i])
    normals = np.add.reduceat(cross_product, flattened_start_indices, axis=0)
    lengths = np.linalg.norm(normals, axis=1)
    if not lengths.all():
        return True
    unit_normal = (normals / lengths[:, np.newaxis]).repeat(face_sizes, axis=0)

    dot_product = (cross_product * unit_normal).sum(axis=1)
    areas = np.add.reduceat(dot_product, flattened_start_indices, axis=0)
    areas = abs(areas) / 2
    return not areas.all()


class RepeatedValuesSet:
    """A class that finds and manages repetitions in a sequence of values.

    This class identifies repeated values in a sequence and maps each value to its first occurrence.
    It supports both standard Python and NumPy implementations for performance optimization.

    Attributes:
        _indices: List of indices where each index points to the first occurrence of its value.
    """

    @default_implementation_method
    def __init__(self, values: VtArray[ScalarType]) -> None:
        """Creates repetitions class from size and values.

        Args:
            values: The sequence of values to check for repetitions.
        """
        size = len(values)
        indices: list[int] = [0] * size
        value_to_first_index: dict[ScalarType, int] = {}
        for i, value in enumerate(values):
            if value in value_to_first_index:
                indices[i] = value_to_first_index[value]
            else:
                indices[i] = value_to_first_index[value] = i
        self._indices = indices

    @__init__.numpy
    def _(self, values: VtArray[ScalarType]) -> None:
        """NumPy implementation of repetition finding.

        Args:
            values: The sequence of values to check for repetitions.
        """
        import numpy as np

        values_array = np.array(values)
        if values_array.ndim > 1:
            sort_idx = np.lexsort(values_array.T)
            sorted_values = np.take_along_axis(values_array, sort_idx[:, None], axis=0)
            changes = np.any(sorted_values[1:] != sorted_values[:-1], axis=1)
        else:
            sort_idx = np.argsort(values_array, kind="stable")
            sorted_values = values_array[sort_idx]
            changes = sorted_values[1:] != sorted_values[:-1]

        changes = np.concatenate(([True], changes))
        first_occurrence = sort_idx[changes]
        group_ids = np.cumsum(changes) - 1

        size = len(values)
        indices = np.arange(size)
        indices[sort_idx] = first_occurrence[group_ids]
        self._indices = indices

    @default_implementation_method
    @cache
    def __len__(self) -> int:
        """Returns the number of repetitions using standard Python."""
        repetitions: set[int] = set()
        for i, index in enumerate(self._indices):
            if i != index:
                repetitions.add(i)
                repetitions.add(index)
        return len(repetitions)

    @__len__.numpy
    @cache
    def _(self) -> int:
        """Returns the number of repetitions using NumPy."""
        import numpy as np

        indices = np.array(self._indices)
        non_self = indices != np.arange(len(indices))
        repetitions = np.unique(np.concatenate([np.where(non_self)[0], indices[non_self]]))  # positions  # targets
        return len(repetitions)

    @default_implementation_method
    @cache
    def __bool__(self) -> bool:
        """Returns true if it has repetitions using standard Python."""
        for i, index in enumerate(self._indices):
            if i != index:
                return True
        return False

    @__bool__.numpy
    @cache
    def _(self) -> bool:
        """Returns true if it has repetitions using NumPy."""
        import numpy as np

        return bool(np.any(self._indices != np.arange(len(self._indices))))

    @default_implementation_method
    def __and__(self, other: RepeatedValuesSet) -> RepeatedValuesSet:
        """Returns a new repetition object where repetitions exist in both sets."""
        return RepeatedValuesSet(list(zip(self._indices, other._indices)))

    @__and__.numpy
    def _(self, other: RepeatedValuesSet) -> RepeatedValuesSet:
        """NumPy implementation of AND operation."""
        import numpy as np

        return RepeatedValuesSet(np.column_stack((self._indices, other._indices)))


@default_implementation
def has_indexable_values(primvar: UsdGeom.Primvar) -> bool:
    """
    Args:
        primvar: The primvar to verify.

    Returns:
        True if it has indexable values.

    Raises:
        TypeError: If primvar type is not array.
        ValueError: If indices are not numeric.
        IndexError: If indices go out of bounds.
    """
    if not is_typename_array(primvar.GetTypeName()):
        raise TypeError("Primvar type is not array")

    if primvar.GetTypeName() in (
        Sdf.ValueTypeNames.BoolArray,
        Sdf.ValueTypeNames.UCharArray,
        Sdf.ValueTypeNames.IntArray,
        Sdf.ValueTypeNames.UIntArray,
        Sdf.ValueTypeNames.Int64Array,
        Sdf.ValueTypeNames.UInt64Array,
    ):
        # We don't need to index simple type arrays. They do not use more memory than indexed.
        # TODO We need to determine the array size and memory usage for Int2Array, Int3Array, Int4Array types
        return False

    if primvar.GetNamespace() == "primvars:skel":
        # OM-123165: usdSkel related primvars cannot be indexed in the same way as a regular primvar.
        # Skip primvars with "primvars:skel" namespace.
        return False

    if primvar.GetElementSize() > 1:
        # ComputeFlattened in most USD version does not work correctly with elementSize > 1
        return False
    values: VtArray[ScalarType] = primvar.ComputeFlattened(Usd.TimeCode.EarliestTime())
    if not values:
        raise IndexError("Primvar indices are invalid")
    repetitions = RepeatedValuesSet(values)
    if repetitions and not primvar.IsIndexed():
        # Repetitions but no indices?
        return True
    indices: Vt.IntArray = primvar.GetIndices()
    counter: list[int] = [0] * len(values)
    for index in indices:
        counter[index] += 1
    if sum(count for count in counter if count > 1) < len(repetitions):
        # Indices does not cover repetitions set.
        return True
    return False


def has_weldable_points(mesh: UsdGeom.Mesh) -> bool:
    points: Vt.Vec3fArray = mesh.GetPointsAttr().Get(Usd.TimeCode.EarliestTime())
    # Points
    repetitions: RepeatedValuesSet = RepeatedValuesSet(points)
    if not repetitions:
        return False

    # Collect and pre validate
    attributes: list[Usd.Attribute] = []
    attr: Usd.Attribute = mesh.GetAccelerationsAttr()
    if attr.IsAuthored():
        if not attr.ValueMightBeTimeVarying():
            attributes.append(attr)
        else:
            return False
    attr: Usd.Attribute = mesh.GetVelocitiesAttr()
    if attr.IsAuthored():
        if not attr.ValueMightBeTimeVarying():
            attributes.append(attr)
        else:
            return False
    interpolation: Tf.Token = mesh.GetNormalsInterpolation()
    if interpolation == UsdGeom.Tokens.vertex or interpolation == UsdGeom.Tokens.varying:
        attr: Usd.Attribute = mesh.GetNormalsAttr()
        if attr.IsAuthored():
            if not attr.ValueMightBeTimeVarying():
                attributes.append(attr)
            else:
                return False
    primvars: list[UsdGeom.Primvar] = []
    for primvar in UsdGeom.PrimvarsAPI(mesh).GetPrimvarsWithAuthoredValues():
        interpolation: Tf.Token = primvar.GetInterpolation()
        if interpolation != UsdGeom.Tokens.vertex and interpolation != UsdGeom.Tokens.varying:
            continue
        element_size: int = primvar.GetElementSize()
        if element_size > 1:
            continue
        if not primvar.ValueMightBeTimeVarying():
            primvars.append(primvar)
        else:
            return False

    # Validate
    for attr in attributes:
        values = attr.Get(Usd.TimeCode.EarliestTime())
        if len(values) != len(points):
            raise ValueError(
                f"Attribute ({attr.GetPath()}) values length "
                "does not match points length although its "
                "interpolation is vertex or varying."
            )
        repetitions &= RepeatedValuesSet(values)
        if not repetitions:
            return False

    for primvar in primvars:
        values: VtArray[ScalarType] = primvar.ComputeFlattened(Usd.TimeCode.EarliestTime())
        if len(values) != len(points):
            raise ValueError(
                f"Primvar ({primvar.GetAttr().GetPath()}) values length "
                "does not match points length although its "
                "interpolation is vertex or varying."
            )
        repetitions &= RepeatedValuesSet(values)
        if not repetitions:
            return False

    return True


@default_implementation
def has_unreferenced_values(num_values: int, indices: Vt.IntArray) -> bool:
    used_index: Sequence[bool] = [False] * num_values
    for index in indices:
        if index >= num_values:
            continue

        used_index[index] = True

    return not all(used_index)


@has_unreferenced_values.numpy
def _(num_values: int, indices: VtArray[int]) -> bool:
    """NumPy implementation of has_unreferenced_values"""
    import numpy as np

    # Create boolean array to track used indices
    used_index = np.zeros(num_values, dtype=bool)

    # Filter out invalid indices and mark used ones
    indices_array = np.array(indices)
    valid_indices = indices_array[indices_array < num_values]
    used_index[valid_indices] = True

    # Return True if any values are unreferenced (False in used_index)
    return not np.all(used_index)


def has_unreferenced_primvar(primvar: UsdGeom.Primvar) -> bool:
    """

    Args:
        primvar: The primvar to verify.

    Returns:
        True if there are values in the primvar that are unreferenced by its indices.
    """
    if not primvar.IsIndexed():
        return False
    primvar_values = primvar.Get(Usd.TimeCode.EarliestTime()) or []
    num_values: int = len(primvar_values)
    if not num_values:
        return False
    indices: Vt.IntArray = primvar.GetIndices(Usd.TimeCode.EarliestTime()) or []
    return has_unreferenced_values(num_values, indices)


@default_implementation
def has_invalid_indices(num_values: int, indices: Vt.IntArray) -> bool:
    for index in indices:
        if index >= num_values:
            return True

    return False


@has_invalid_indices.numpy
def _(num_values: int, indices: VtArray[int]) -> bool:
    """NumPy implementation of has_invalid_indices"""
    import numpy as np

    # Convert to numpy array and check for invalid indices
    indices_array = np.array(indices)
    return np.any(indices_array >= num_values)


def has_invalid_primvar_indices(primvar: UsdGeom.Primvar) -> bool:
    """

    Args:
        primvar: The primvar to verify.

    Returns:
        True if there are values in the primvar that are unreferenced by its indices.
    """
    if not primvar.IsIndexed():
        return False
    primvar_values = primvar.Get(Usd.TimeCode.EarliestTime()) or []
    num_values: int = len(primvar_values)
    indices: Vt.IntArray = primvar.GetIndices(Usd.TimeCode.EarliestTime()) or []
    return has_invalid_indices(num_values, indices)


def remove_unused_values_and_remap_indices(
    values, indices, remove_invalid_indices=False
) -> tuple[bool, list[Any], list[int], list[int]]:
    """Remove used values that are not referenced by indices array.

    Args:
        values (_type_): Value array.
        indices (_type_): Index array that references the value array.
        remove_invalid_indices (bool, optional): When it's True, it also removes those indices
                                                 that are beyond the length of value array. Defaults to False.

    Returns:
        Tuple[bool, List[Any], List[int], List[int]]: A tuple that the first item returns if the operation is successful
        or not, the second item returns the updated values after this operation, the third item returns the updated indices
        after this operation, and the last item returns all removed indices of the values in the original value array
        after this operation, which doesn't include those indices that are invalid and beyond the length of the original
        value array.
    """

    num_values: int = len(values)
    num_indices: int = len(indices)
    valid_index_count: int = 0
    valid_value_count: int = 0
    removed_value_indices = []

    if num_values == 0:
        if num_indices == 0:
            return False, values, indices, []
        else:
            return True, [], [], []

    # Count all used/unused values and valid indices.
    used_index: list[bool] = [False] * num_values
    for index in indices:
        # Index is out of the bound.
        if index >= num_values:
            continue

        valid_index_count += 1
        if not used_index[index]:
            valid_value_count += 1
        used_index[index] = True

    # No unused values or invalid indices.
    if valid_value_count == num_values and (not remove_invalid_indices or valid_index_count == num_indices):
        return False, values, indices, []

    # Remove unused values, and remap indices.
    updated_values: list[Any] = [None] * valid_value_count
    indices_remapped: list[int] = [None] * num_values
    current_index = 0
    for index, value in enumerate(values):
        if used_index[index]:
            updated_values[current_index] = value
            indices_remapped[index] = current_index
            current_index += 1
        else:
            removed_value_indices.append(index)

    updated_indices: list[int] = [0] * valid_index_count if remove_invalid_indices else [0] * num_indices
    current_index = 0
    for index in indices:
        if index >= num_values and remove_invalid_indices:
            continue

        # If it's not remapped, it means the index is over the bound and it's kept untouched
        # if remove_invalid_indices is False.
        new_index = indices_remapped[index] if index < num_values and used_index[index] else index
        updated_indices[current_index] = new_index
        current_index += 1

    return True, updated_values, updated_indices, removed_value_indices
