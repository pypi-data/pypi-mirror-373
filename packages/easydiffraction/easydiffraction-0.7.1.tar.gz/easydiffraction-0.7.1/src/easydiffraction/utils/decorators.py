# SPDX-FileCopyrightText: 2021-2025 EasyDiffraction Python Library contributors <https://github.com/easyscience/diffraction-lib>
# SPDX-License-Identifier: BSD-3-Clause

import inspect


def enforce_type(func):
    sig = inspect.signature(func)
    params = list(sig.parameters.items())

    # Find the first argument that isn't 'self'
    for name, param in params:
        if name != 'self':
            expected_type = param.annotation
            if expected_type is inspect._empty:
                raise TypeError(f"Missing type annotation for parameter '{name}' in {func.__qualname__}")
            break
    else:
        raise TypeError(f'No annotated parameter found in {func.__qualname__}')

    def wrapper(self, value):
        if not isinstance(value, expected_type):
            raise TypeError(f'Expected {expected_type.__name__}, got {type(value).__name__}.')
        return func(self, value)

    return wrapper
