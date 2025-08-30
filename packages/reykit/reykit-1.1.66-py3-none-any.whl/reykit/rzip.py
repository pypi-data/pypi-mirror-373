# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-01-19 19:23:57
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : File compress methods.
"""


from zipfile import ZipFile, is_zipfile, ZIP_DEFLATED
from os import getcwd as os_getcwd, walk as os_walk
from os.path import isfile as os_isfile

from .ros import File, Folder, join_path


__all__ = (
    'compress',
    'decompress',
    'zip'
)


def compress(
    path: str,
    build_dir: str | None = None,
    overwrite: bool = True
) -> None:
    """
    Compress file or folder.

    Parameters
    ----------
    path : File or folder path.
    build_dir : Build directory.
        - `None`: Work directory.
        - `str`: Use this value.
    overwrite : Whether to overwrite.
    """

    # Handle parameter.
    build_dir = Folder(build_dir).path
    if overwrite:
        mode = 'w'
    else:
        mode = 'x'
    is_file = os_isfile(path)
    if is_file:
        file = File(path)
        obj_name = file.name_suffix
    else:
        folder = Folder(path)
        obj_name = folder.name
    build_name = obj_name + '.zip'
    build_path = join_path(build_dir, build_name)

    # Compress.
    with ZipFile(build_path, mode, ZIP_DEFLATED) as zip_file:

        ## File.
        if is_file:
            zip_file.write(file.path, file.name_suffix)

        ## Folder.
        else:
            dir_path_len = len(folder.path)
            dirs = os_walk(folder.path)
            for folder_name, sub_folders_name, files_name in dirs:
                for sub_folder_name in sub_folders_name:
                    sub_folder_path = join_path(folder_name, sub_folder_name)
                    zip_path = sub_folder_path[dir_path_len:]
                    zip_file.write(sub_folder_path, zip_path)
                for file_name in files_name:
                    file_path = join_path(folder_name, file_name)
                    zip_path = file_path[dir_path_len:]
                    zip_file.write(file_path, zip_path)


def decompress(
    obj_path: str,
    build_dir: str | None = None,
    password: str | None = None
) -> None:
    """
    Decompress compressed object.

    Parameters
    ----------
    obj_path : Compressed object path.
    build_dir : Build directory.
        - `None`: Work directory.
        - `str`: Use this value.
    passwrod : Unzip Password.
        - `None`: No Unzip Password.
        - `str`: Use this value.
    """

    # Check object whether can be decompress.
    is_support = is_zipfile(obj_path)
    if not is_support:
        raise AssertionError('file format that cannot be decompressed')

    # Handle parameter.
    build_dir = build_dir or os_getcwd()

    # Decompress.
    with ZipFile(obj_path) as zip_file:
        zip_file.extractall(build_dir, pwd=password)


def zip(
    obj_path: str,
    build_dir: str | None = None
) -> None:
    """
    Automatic judge and compress or decompress object.

    Parameters
    ----------
    obj_path : File or folder or compressed object path.
    output_path : Build directory.
        - `None`: Work directory.
        - `str`: Use this value.
    """

    # Judge compress or decompress.
    is_support = is_zipfile(obj_path)

    # Execute.
    if is_support:
        decompress(obj_path, build_dir)
    else:
        compress(obj_path, build_dir)
