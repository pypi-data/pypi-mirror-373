# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

# TODO: This is temporary

from pxr import Sdf

__all__ = [
    "is_omni_path",
]

_OMNI_PRIM_PATHS: set[Sdf.Path] = {
    Sdf.Path("/OmniverseKit_Persp"),
    Sdf.Path("/OmniverseKit_Front"),
    Sdf.Path("/OmniverseKit_Top"),
    Sdf.Path("/OmniverseKit_Right"),
    Sdf.Path("/OmniKit_Viewport_LightRig"),
}
"""set: A set of paths created by Kit which should be ignored by Rules. """


def is_omni_path(path: Sdf.Path) -> bool:
    """
    Args:
        path: An Sdf Path object.

    Returns:
        True if this is used internally by Omniverse.
    """
    return path in _OMNI_PRIM_PATHS
