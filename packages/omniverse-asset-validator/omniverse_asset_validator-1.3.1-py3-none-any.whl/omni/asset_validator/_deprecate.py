# SPDX-FileCopyrightText: Copyright (c) 2025 NVIDIA CORPORATION & AFFILIATES. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
#
import logging
from collections.abc import Callable
from functools import cache, wraps


class deprecated:  # noqa: N801
    """
    Implementation of the deprecated decorator.
    """

    def __init__(self, message: str, *, category: type[Warning] = DeprecationWarning):
        self.message = message
        self.category: type[Warning] = category

    @cache
    def show_warning(self, obj: type | Callable) -> None:
        """
        Show deprecation warning only once.
        """
        logging.warning(f"{obj.__name__}: {self.message}")

    def __call__(self, arg: type | Callable) -> type | Callable:
        if isinstance(arg, type):
            old_new = arg.__new__

            @wraps(old_new)
            def new_new(cls, /, *args, **kwargs):
                if cls is arg:
                    self.show_warning(arg)
                if old_new is not object.__new__:
                    return old_new(cls, *args, **kwargs)
                elif cls.__init__ is object.__init__ and (args or kwargs):
                    raise TypeError(f"{cls.__name__}() takes no arguments")
                else:
                    return old_new(cls)

            arg.__new__ = staticmethod(new_new)
            return arg
        elif callable(arg):

            @wraps(arg)
            def wrapper(*args, **kwargs):
                self.show_warning(arg)
                return arg(*args, **kwargs)

            return wrapper
        else:
            raise TypeError(f"deprecated decorator can only be used on types or callables, got {type(arg)}")
