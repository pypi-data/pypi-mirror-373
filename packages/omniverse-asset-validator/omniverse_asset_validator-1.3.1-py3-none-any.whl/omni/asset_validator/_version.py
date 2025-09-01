# SPDX-FileCopyrightText: Copyright (c) 2024-2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#

__all__ = [
    "__version__",
    "get_version",
]

__version__ = "1.3.1"


def get_version():
    """
    Returns
        The version of this module.
    """
    return __version__
