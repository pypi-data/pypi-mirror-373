# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-12-06 16:14:11
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : DLL file methods.

Modules
-------
rdll_core : DLL file code methods.
"""


__all__ = (
    'inject_dll',
)


def inject_dll(
    id_: int,
    path: str
) -> None:
    """
    Inject DLL file.

    Parameters
    ----------
    id\\_ : Process ID.
    path : DLL file path.
    """

    # Import.
    from ctypes import create_string_buffer
    from .rdll_core import InjectDLL

    # Handle parameter.
    path_bytes = path.encode()
    buffer = create_string_buffer(path_bytes)

    # Inject.
    InjectDLL(id_, buffer)
