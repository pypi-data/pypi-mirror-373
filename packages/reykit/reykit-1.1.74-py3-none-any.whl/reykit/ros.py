# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-05-09 15:30:10
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Operation system methods.
"""


from __future__ import annotations
from typing import Any, Literal, TextIO, BinaryIO, overload, TYPE_CHECKING
if TYPE_CHECKING:
    from _typeshed import OpenTextMode, OpenBinaryMode
from io import TextIOBase, BufferedIOBase
from os import (
    walk as os_walk,
    listdir as os_listdir,
    makedirs as os_makedirs,
    renames as os_renames,
    remove as os_remove
)
from os.path import (
    join as os_join,
    isfile as os_isfile,
    isdir as os_isdir,
    basename as os_basename,
    dirname as os_dirname,
    exists as os_exists,
    getsize as os_getsize,
    getctime as os_getctime,
    getmtime as os_getmtime,
    getatime as os_getatime,
    split as os_split,
    splitext as os_splitext,
    splitdrive as os_splitdrive
)
from shutil import copy as shutil_copy
from pathlib import Path
from hashlib import md5 as hashlib_md5
from tomllib import loads as tomllib_loads
from json import JSONDecodeError
from filetype import guess as filetype_guess
from tempfile import TemporaryFile, TemporaryDirectory

from .rbase import Base, throw
from .rdata import to_json
from .rre import search, sub
from .rsys import run_cmd


__all__ = (
    'format_path',
    'join_path',
    'get_md5',
    'make_dir',
    'find_relpath',
    'read_file_str',
    'read_file_bytes',
    'read_toml',
    'File',
    'Folder',
    'TempFile',
    'TempFolder',
    'FileCache',
    'doc_to_docx',
    'extract_docx_content',
    'extract_pdf_content',
    'extract_file_content'
)


type FilePath = str
type FileText = str
type FileData = bytes
type FileSourceStr = FilePath | FileText | TextIOBase
type FileSourceBytes = FilePath | FileData | BufferedIOBase


def format_path(path: str | None = None) -> str:
    """
    Resolve relative path and replace to forward slash `/`.

    Parameters
    ----------
    path : Path.
        - `None`: Use working directory.

    Returns
    -------
    Formatted path.
    """

    # Handle parameter.
    path = path or ''

    # Format.
    path_obj = Path(path)
    path_obj = path_obj.resolve()
    path = path_obj.as_posix()

    return path


def join_path(*paths: str) -> str:
    """
    Join path and resolve relative path and replace to forward slash `/`.

    Parameters
    ----------
    paths : Paths.

    Returns
    -------
    Joined and formatted path.
    """

    # Join.
    path = os_join(*paths)

    # Format.
    path = format_path(path)

    return path


def get_md5(data: str | bytes) -> str:
    """
    Get MD5 value.

    Parameters
    ----------
    data : Data.

    Returns
    -------
    MD5 value.
    """

    # Handle parameter.
    if type(data) == str:
        data = data.encode()

    # Get.
    hash = hashlib_md5(data)
    md5 = hash.hexdigest()

    return md5


def make_dir(*paths: str, report: bool = False) -> None:
    """
    Make directorys.

    Parameters
    ----------
    paths : Folder paths.
    report : Whether report the creation process.
    """

    # Create.
    for path in paths:
        folder = Folder(path)
        folder.make(report)


def find_relpath(abspath: str, relpath: str) -> str:
    """
    Based absolute path and symbol `.` of relative path, find a new absolute path.

    Parameters
    ----------
    abspath : Original absolute path.
    relpath : relative path.

    Returns
    -------
    New absolute path.

    Examples
    --------
    >>> old_abspath = os.getcwd()
    >>> relpath = '../Folder4/File.txt'
    >>> new_abspath = convert_relpath(old_abspath, relpath)
    >>> old_abspath
    C:/Folder1/Folder2/Folder3
    >>> new_abspath
    C:/Folder1/Folder4/File.txt
    """

    # Handle parameter.
    level = 0
    for char in relpath:
        if char == '.':
            level += 1
        else:
            break
    strip_n = 0
    for char in relpath[level:]:
        if char in ('/', '\\'):
            strip_n += 1
        else:
            break

    # Convert.
    folder_path = abspath
    for _ in range(level):
        folder_path, _ = os_split(folder_path)
    relpath = relpath[level + strip_n:]
    path = join_path(folder_path, relpath)

    return path


def read_file_str(source: FileSourceStr) -> str:
    """
    Read file string data.

    Parameters
    ----------
    source : File source.
        - `'str' and path`: Return this string data.
        - `'str' and not path`: As a file path read string data.
        - `TextIOBase`: Read string data.

    Returns
    -------
    File string data.
    """

    # Get.
    match source:

        ## Path or string.
        case str():
            exist = os_exists(source)

            ## Path.
            if exist:
                file = File(source)
                file_str = file.str

            ## String.
            else:
                file_str = source

        ## IO.
        case TextIOBase():
            file_str = source.read()

        ## Throw exception.
        case _:
            throw(TypeError, source)

    return file_str


def read_file_bytes(source: FileSourceBytes) -> bytes:
    """
    Read file bytes data.

    Parameters
    ----------
    source : File source.
        - `bytes`: Return this bytes data.
        - `str`: As a file path read bytes data.
        - `BufferedIOBase`: Read bytes data.

    Returns
    -------
    File bytes data.
    """

    # Get.
    match source:

        ## Bytes.
        case bytes():
            file_bytes = source
        case bytearray():
            file_bytes = bytes(source)

        ## Path.
        case str():
            file = File(source)
            file_bytes = file.bytes

        ## IO.
        case BufferedIOBase():
            file_bytes = source.read()

        ## Throw exception.
        case _:
            throw(TypeError, source)

    return file_bytes


def read_toml(path: str | File) -> dict[str, Any]:
    """
    Read and parse TOML file.
    Treat nan as a None or null value.

    Parameters
    ----------
    path : File path or File object.

    Returns
    -------
    Parameter dictionary.
    """

    # Read.
    match path:

        ## File path.
        case str():
            file = File(path)
            text = file.str

        ## File object.
        case File():
            text = file.str

    # Parse.

    ## Handle nan.
    parse_float = lambda float_str: None if float_str == "nan" else float_str

    params = tomllib_loads(text, parse_float=parse_float)

    return params


class File(Base):
    """
    File type.
    """


    def __init__(self, path: str) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        path : File path.
        """

        # Set attribute.
        self.path = format_path(path)


    @overload
    def open(self, mode: OpenBinaryMode = 'wb+') -> BinaryIO: ...

    @overload
    def open(self, mode: OpenTextMode, encode: str = 'utf-8') -> TextIO: ...

    def open(self, mode: OpenTextMode | OpenBinaryMode = 'wb+', encode: str = 'utf-8') -> TextIO | BinaryIO:
        """
        Open file.

        Parameters
        ----------
        mode : Open mode.
        encode : Encoding method.

        Returns
        -------
        IO object.
        """

        # Handle parameter.
        if 'b' in mode:
            encode = None

        # Open.
        io = open(self.path, mode, encoding=encode)

        return io


    @overload
    def __getattr__(self, name: Literal['r', 'w', 'a']) -> TextIO: ...

    @overload
    def __getattr__(self, name: Literal['rb', 'wb', 'ab']) -> BinaryIO: ...

    def __getattr__(self, name: Literal['r', 'w', 'a', 'rb', 'wb', 'ab']) -> TextIO | BinaryIO:
        """
        Get attribute.

        Parameters
        ----------
        name : Open mode.

        Returns
        -------
        IO object.
        """

        # Open.
        if name in ('r', 'w', 'a', 'rb', 'wb', 'ab'):
            io = self.open(name)
            return io

        # Throw exception.
        throw(AttributeError, name)


    @overload
    def read(self, type_: Literal['bytes'] = 'bytes') -> bytes: ...

    @overload
    def read(self, type_: Literal['str']) -> str: ...

    def read(self, type_: Literal['str', 'bytes'] = 'bytes') -> bytes | str:
        """
        Read file data.

        Parameters
        ----------
        type\\_ : File data type.
            - `Literal['bytes']`: Return file bytes data.
            - `Literal['str']`: Return file string data.

        Returns
        -------
        File data.
        """

        # Handle parameter.
        match type_:
            case 'bytes':
                mode = 'rb'
            case 'str':
                mode = 'r'

        # Read.
        with self.open(mode) as file:
            content = file.read()

        return content


    def write(
        self,
        data: Any | None = '',
        append: bool = False
    ) -> None:
        """
        Write file data.

        Parameters
        ----------
        data : Write data.
            - `str`: File text.
            - `bytes`: File bytes data.
            - `Any`: To JSON format or string.
        append : Whether append data, otherwise overwrite data.
        """

        # Handle parameter.

        ## Write mode.
        if append:
            mode = 'a'
        else:
            mode = 'w'
        if type(data) in (bytes, bytearray):
            mode += 'b'

        ## Convert data to string.
        if type(data) not in (str, bytes, bytearray):
            try:
                data = to_json(data)
            except (JSONDecodeError, TypeError):
                data = str(data)

        # Write.
        with self.open(mode) as file:
            file.write(data)


    def copy(self, path: str) -> None:
        """
        Copy file to path.

        Parameters
        ----------
        path : Copy path.
        """

        # Copy.
        shutil_copy(
            self.path,
            path
        )


    def move(self, path: str) -> None:
        """
        Move file to path.

        Parameters
        ----------
        path : Move path.
        """

        # Move.
        os_renames(
            self.path,
            path
        )


    def rename(self, name: str) -> str:
        """
        Rename file name.

        Parameters
        ----------
        name : New file name.

        Returns
        -------
        New file path.
        """

        # Handle parameter.
        move_path = join_path(self.dir, name)

        # Move.
        self.move(move_path)

        return move_path


    def remove(self) -> None:
        """
        Remove file.
        """

        # Remove.
        try:
            os_remove(self.path)

        # Read only.
        except PermissionError:
            command = f'attrib -r "{self.path}"'
            run_cmd(command)
            os_remove(self.path)


    @property
    def str(self) -> str:
        """
        Read content as a string.

        Returns
        -------
        File string content.
        """

        # Read.
        file_str = self.read('str')

        return file_str


    @property
    def bytes(self) -> bytes:
        """
        Read content in byte form.

        Returns
        -------
        File bytes content.
        """

        # Read.
        file_bytes = self.read('bytes')

        return file_bytes


    @property
    def name_suffix(self) -> str:
        """
        Return file name with suffix.

        Returns
        -------
        File name with suffix.
        """

        # Get.
        file_name_suffix = os_basename(self.path)

        return file_name_suffix


    @property
    def name(self) -> str:
        """
        Return file name not with suffix.

        Returns
        -------
        File name not with suffix.
        """

        # Get.
        file_name, _ = os_splitext(self.name_suffix)

        return file_name


    @property
    def suffix(self) -> str:
        """
        Return file suffix.

        Returns
        -------
        File suffix.
        """

        # Get.
        _, file_suffix = os_splitext(self.path)

        return file_suffix


    @property
    def dir(self) -> str:
        """
        Return file directory.

        Returns
        -------
        File directory.
        """

        # Get.
        file_dir = os_dirname(self.path)

        return file_dir


    @property
    def drive(self) -> str:
        """
        Return file drive letter.

        Returns
        -------
        File drive letter.
        """

        # Get.
        file_drive, _ = os_splitdrive(self.path)

        return file_drive


    @property
    def size(self) -> int:
        """
        Return file byte size.

        Returns
        -------
        File byte size.
        """

        # Get.
        file_size = os_getsize(self.path)

        return file_size


    @property
    def ctime(self) -> float:
        """
        Return file create timestamp.

        Returns
        -------
        File create timestamp.
        """

        # Get.
        file_ctime = os_getctime(self.path)

        return file_ctime


    @property
    def mtime(self) -> float:
        """
        Return file modify timestamp.

        Returns
        -------
        File modify timestamp.
        """

        # Get.
        file_mtime = os_getmtime(self.path)

        return file_mtime


    @property
    def atime(self) -> float:
        """
        Return file access timestamp.

        Returns
        -------
        File access timestamp.
        """

        # Get.
        file_atime = os_getatime(self.path)

        return file_atime


    @property
    def md5(self) -> float:
        """
        Return file MD5 value.

        Returns
        -------
        File MD5 value
        """

        # Get.
        file_bytes = self.bytes
        file_md5 = get_md5(file_bytes)

        return file_md5


    @property
    def toml(self) -> dict[str, Any]:
        """
        Read and parse TOML file.
        Treat nan as a None or null value.

        Returns
        -------
        Parameter dictionary.
        """

        # Read and parse.
        params = read_toml(self.path)

        return params


    def __bool__(self) -> bool:
        """
        Judge if exist.

        Returns
        -------
        Judge result.
        """

        # Judge.
        file_exist = os_isfile(self.path)

        return file_exist


    def __len__(self) -> int:
        """
        Return file byte size.

        Returns
        -------
        File byte size.
        """

        # Get.
        file_size = self.size

        return file_size


    def __str__(self) -> str:
        """
        Read content as a string.

        Returns
        -------
        File string content.
        """

        # Read.
        file_text = self.str

        return file_text


    def __bytes__(self) -> bytes:
        """
        Read content in byte form.

        Returns
        -------
        File bytes content.
        """

        # Read.
        file_bytes = self.bytes

        return file_bytes


    def __contains__(self, value: str | bytes) -> bool:
        """
        Judge if file text contain value.

        Parameters
        ----------
        value : Judge value.

        Returns
        -------
        Judge result.
        """

        # Handle parameter.
        match value:
            case str():
                content = self.str
            case bytes() | bytearray():
                content = self.bytes
            case _:
                throw(TypeError, value)

        # Judge.
        judge = value in content

        return judge


    __call__ = write


class Folder(Base):
    """
    Folder type.
    """


    def __init__(self, path: str | None = None) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        path : Folder path.
            - `None`: Use working directory.
        """

        # Set attribute.
        self.path = format_path(path)


    def paths(
        self,
        target: Literal['all', 'file', 'folder'] = 'all',
        recursion: bool = False
    ) -> list[str]:
        """
        Get the path of files and folders in the folder path.

        Parameters
        ----------
        target : Target data.
            - `Literal['all']`: Return file and folder path.
            - `Literal['file']`: Return file path.
            - `Literal['folder']`: Return folder path.
        recursion : Is recursion directory.

        Returns
        -------
        String is path.
        """

        # Get paths.
        paths: list[str] = []

        ## Recursive.
        if recursion:
            obj_walk = os_walk(self.path)
            match target:
                case 'all':
                    targets_path = [
                        join_path(path, file_name)
                        for path, folders_name, files_name in obj_walk
                        for file_name in files_name + folders_name
                    ]
                    paths.extend(targets_path)
                case 'file':
                    targets_path = [
                        join_path(path, file_name)
                        for path, _, files_name in obj_walk
                        for file_name in files_name
                    ]
                    paths.extend(targets_path)
                case 'folder':
                    targets_path = [
                        join_path(path, folder_name)
                        for path, folders_name, _ in obj_walk
                        for folder_name in folders_name
                    ]
                    paths.extend(targets_path)

        ## Non recursive.
        else:
            names = os_listdir(self.path)
            match target:
                case 'all':
                    for name in names:
                        target_path = join_path(self.path, name)
                        paths.append(target_path)
                case 'file':
                    for name in names:
                        target_path = join_path(self.path, name)
                        is_file = os_isfile(target_path)
                        if is_file:
                            paths.append(target_path)
                case 'folder':
                    for name in names:
                        target_path = join_path(self.path, name)
                        is_dir = os_isdir(target_path)
                        if is_dir:
                            paths.append(target_path)

        return paths


    @overload
    def search(
        self,
        pattern: str = '',
        target: Literal['all', 'file', 'folder'] = 'all',
        recursion: bool = False
    ) -> str | None: ...

    @overload
    def search(
        self,
        pattern: str = '',
        target: Literal['all', 'file', 'folder'] = 'all',
        recursion: bool = False,
        *,
        first: Literal[False]
    ) -> list[str]: ...

    def search(
        self,
        pattern: str = '',
        target: Literal['all', 'file', 'folder'] = 'all',
        recursion: bool = False,
        first: bool = True
    ) -> str | list[str] | None:
        """
        Search file name by regular expression.

        Parameters
        ----------
        pattern : Regular expression pattern.
        target : Target data.
            - `Literal['all']`: Return file and folder path.
            - `Literal['file']`: Return file path.
            - `Literal['folder']`: Return folder path.
        recursion : Is recursion directory.
        first : Whether return first search path, otherwise return all search path.

        Returns
        -------
        Searched path or null.
        """

        # Get paths.
        file_paths = self.paths(target, recursion)

        # First.
        if first:
            for path in file_paths:
                name = os_basename(path)
                result = search(pattern, name)
                if result is not None:
                    return path

        # All.
        else:
            match_paths: list[str] = []
            for path in file_paths:
                name = os_basename(path)
                result = search(pattern, name)
                if result is not None:
                    match_paths.append(path)
            return match_paths


    def join(self, path: str) -> str:
        """
        Join folder path and relative path.

        Parameters
        ----------
        path : Relative path.

        Returns
        -------
        Joined path.
        """

        # Join.
        path = join_path(self.path, path)

        return path


    def make(self, report: bool = False) -> None:
        """
        Create folders.

        Parameters
        ----------
        report : Whether report the creation process.
        """

        # Exist.
        exist = os_exists(self.path)
        if exist:
            text = 'Directory already exists    | %s' % self.path

        # Not exist.
        else:
            os_makedirs(self.path)
            text = 'Directory creation complete | %s' % self.path

        # Report.
        if report:
            print(text)


    def move(self, path: str) -> None:
        """
        Move folder to path.

        Parameters
        ----------
        path : Move path.
        """

        # Move.
        os_renames(
            self.path,
            path
        )


    def rename(self, name: str) -> str:
        """
        Rename folder name.

        Parameters
        ----------
        name : New folder name.

        Returns
        -------
        New folder path.
        """

        # Handle parameter.
        move_path = join_path(self.dir, name)

        # Move.
        self.move(move_path)

        return move_path


    @property
    def name(self) -> str:
        """
        Return folder name.

        Returns
        -------
        Folder name.
        """

        # Get.
        folder_name = os_basename(self.path)

        return folder_name


    @property
    def dir(self) -> str:
        """
        Return folder directory.

        Returns
        -------
        Folder directory.
        """

        # Get.
        folder_dir = os_dirname(self.path)

        return folder_dir


    @property
    def drive(self) -> str:
        """
        Return folder drive letter.

        Returns
        -------
        Folder drive letter.
        """

        # Get.
        folder_drive, _ = os_splitdrive(self.path)

        return folder_drive


    @property
    def size(self) -> int:
        """
        Return folder byte size, include all files in it.

        Returns
        -------
        Folder byte size.
        """

        # Get.
        file_paths = self.paths('file', True)
        file_sizes = [
            os_getsize(path)
            for path in file_paths
        ]
        folder_size = sum(file_sizes)

        return folder_size


    @property
    def ctime(self) -> float:
        """
        Return file create timestamp.

        Returns
        -------
        File create timestamp.
        """

        # Get.
        folder_ctime = os_getctime(self.path)

        return folder_ctime


    @property
    def mtime(self) -> float:
        """
        Return file modify timestamp.

        Returns
        -------
        File modify timestamp.
        """

        # Get.
        folder_mtime = os_getmtime(self.path)

        return folder_mtime


    @property
    def atime(self) -> float:
        """
        Return file access timestamp.

        Returns
        -------
        File access timestamp.
        """

        # Get.
        folder_atime = os_getatime(self.path)

        return folder_atime


    def __bool__(self) -> bool:
        """
        Judge if exist.

        Returns
        -------
        Judge result.
        """

        # Judge.
        folder_exist = os_isdir(self.path)

        return folder_exist


    def __len__(self) -> int:
        """
        Return folder byte size, include all files in it.

        Returns
        -------
        Folder byte size.
        """

        # Get.
        folder_size = self.size

        return folder_size


    def __contains__(self, relpath: str) -> bool:
        """
        whether exist relative path object.

        Parameters
        ----------
        relpath : Relative path.

        Returns
        -------
        Judge result.
        """

        # Judge.
        path = self.join(relpath)
        judge = os_exists(path)

        return judge


    __call__ = paths

    __add__ = __radd__ = join


class TempFile(Base):
    """
    Temporary file type.
    """


    def __init__(self,
        dir_: str | None = None,
        suffix: str | None = None,
        type_: Literal['str', 'bytes'] = 'bytes'
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        dir\\_ : Directory path.
        suffix : File suffix.
        type\\_ : File data type.
        """

        # Handle parameter.
        match type_:
            case 'bytes':
                mode = 'w+b'
            case 'str':
                mode = 'w+'
            case _:
                throw(ValueError, type_)

        # Set attribute.
        self.file = TemporaryFile(
            mode,
            suffix=suffix,
            dir=dir_
        )
        self.path = format_path(self.file.name)


    def read(self) -> bytes | str:
        """
        Read file data.

        Returns
        -------
        File data.
        """

        # Read.
        self.file.seek(0)
        content = self.file.read()

        return content


    def write(self, data: str | bytes) -> None:
        """
        Write file data.

        Parameters
        ----------
        data : Write data.
        """

        # Write.
        self.file.write(data)
        self.file.seek(0)


    @property
    def name_suffix(self) -> str:
        """
        Return file name with suffix.

        Returns
        -------
        File name with suffix.
        """

        # Get.
        file_name_suffix = os_basename(self.path)

        return file_name_suffix


    @property
    def name(self) -> str:
        """
        Return file name not with suffix.

        Returns
        -------
        File name not with suffix.
        """

        # Get.
        file_name, _ = os_splitext(self.name_suffix)

        return file_name


    @property
    def suffix(self) -> str:
        """
        Return file suffix.

        Returns
        -------
        File suffix.
        """

        # Get.
        _, file_suffix = os_splitext(self.path)

        return file_suffix


    @property
    def dir(self) -> str:
        """
        Return file directory.

        Returns
        -------
        File directory.
        """

        # Get.
        file_dir = os_dirname(self.path)

        return file_dir


    @property
    def drive(self) -> str:
        """
        Return file drive letter.

        Returns
        -------
        File drive letter.
        """

        # Get.
        file_drive, _ = os_splitdrive(self.path)

        return file_drive


    @property
    def size(self) -> int:
        """
        Return file byte size.

        Returns
        -------
        File byte size.
        """

        # Get.
        file_size = os_getsize(self.path)

        return file_size


    @property
    def ctime(self) -> float:
        """
        Return file create timestamp.

        Returns
        -------
        File create timestamp.
        """

        # Get.
        file_ctime = os_getctime(self.path)

        return file_ctime


    @property
    def mtime(self) -> float:
        """
        Return file modify timestamp.

        Returns
        -------
        File modify timestamp.
        """

        # Get.
        file_mtime = os_getmtime(self.path)

        return file_mtime


    @property
    def atime(self) -> float:
        """
        Return file access timestamp.

        Returns
        -------
        File access timestamp.
        """

        # Get.
        file_atime = os_getatime(self.path)

        return file_atime


    @property
    def md5(self) -> float:
        """
        Return file MD5 value.

        Returns
        -------
        File MD5 value
        """

        # Get.
        file_bytes = self.read()
        file_md5 = get_md5(file_bytes)

        return file_md5


    @property
    def toml(self) -> dict[str, Any]:
        """
        Read and parse TOML file.
        Treat nan as a None or null value.

        Returns
        -------
        Parameter dictionary.
        """

        # Read and parse.
        params = read_toml(self.path)

        return params


    def __len__(self) -> int:
        """
        Return file byte size.

        Returns
        -------
        File byte size.
        """

        # Get.
        file_size = self.size

        return file_size


    def __contains__(self, value: str | bytes) -> bool:
        """
        Judge if file text contain value.

        Parameters
        ----------
        value : Judge value.

        Returns
        -------
        Judge result.
        """

        # Handle parameter.
        content = self.read()

        # Judge.
        judge = value in content

        return judge


    def __del__(self) -> None:
        """
        Close temporary file.
        """

        # Close.
        self.file.close()


    __call__ = write


class TempFolder(Base):
    """
    Temporary folder type.
    """


    def __init__(self, dir_: str | None = None) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        dir_ : Directory path.
        """

        # Set attribute.
        self.folder = TemporaryDirectory(dir=dir_)
        self.path = format_path(self.folder.name)


    def paths(
        self,
        target: Literal['all', 'file', 'folder'] = 'all',
        recursion: bool = False
    ) -> list:
        """
        Get the path of files and folders in the folder path.

        Parameters
        ----------
        target : Target data.
            - `Literal['all']`: Return file and folder path.
            - `Literal['file']`: Return file path.
            - `Literal['folder']`: Return folder path.
        recursion : Is recursion directory.

        Returns
        -------
        String is path.
        """

        # Get paths.
        paths = []

        ## Recursive.
        if recursion:
            obj_walk = os_walk(self.path)
            match target:
                case 'all':
                    targets_path = [
                        join_path(path, file_name)
                        for path, folders_name, files_name in obj_walk
                        for file_name in files_name + folders_name
                    ]
                    paths.extend(targets_path)
                case 'file':
                    targets_path = [
                        join_path(path, file_name)
                        for path, _, files_name in obj_walk
                        for file_name in files_name
                    ]
                    paths.extend(targets_path)
                case 'all' | 'folder':
                    targets_path = [
                        join_path(path, folder_name)
                        for path, folders_name, _ in obj_walk
                        for folder_name in folders_name
                    ]
                    paths.extend(targets_path)

        ## Non recursive.
        else:
            names = os_listdir(self.path)
            match target:
                case 'all':
                    for name in names:
                        target_path = join_path(self.path, name)
                        paths.append(target_path)
                case 'file':
                    for name in names:
                        target_path = join_path(self.path, name)
                        is_file = os_isfile(target_path)
                        if is_file:
                            paths.append(target_path)
                case 'folder':
                    for name in names:
                        target_path = join_path(self.path, name)
                        is_dir = os_isdir(target_path)
                        if is_dir:
                            paths.append(target_path)

        return paths


    @overload
    def search(
        self,
        pattern: str = '',
        target: Literal['all', 'file', 'folder'] = 'all',
        recursion: bool = False
    ) -> str | None: ...

    @overload
    def search(
        self,
        pattern: str = '',
        target: Literal['all', 'file', 'folder'] = 'all',
        recursion: bool = False,
        *,
        first: Literal[False]
    ) -> list[str]: ...

    def search(
        self,
        pattern: str = '',
        target: Literal['all', 'file', 'folder'] = 'all',
        recursion: bool = False,
        first: bool = True
    ) -> str | list[str] | None:
        """
        Search file name by regular expression.

        Parameters
        ----------
        pattern : Regular expression pattern.
        target : Target data.
            - `Literal['all']`: Return file and folder path.
            - `Literal['file']`: Return file path.
            - `Literal['folder']`: Return folder path.
        recursion : Is recursion directory.
        first : Whether return first search path, otherwise return all search path.

        Returns
        -------
        Searched path or null.
        """

        # Get paths.
        file_paths = self.paths(target, recursion)

        # First.
        if first:
            for path in file_paths:
                name = os_basename(path)
                result = search(pattern, name)
                if result is not None:
                    return path

        # All.
        else:
            match_paths: list[str] = []
            for path in file_paths:
                name = os_basename(path)
                result = search(pattern, name)
                if result is not None:
                    match_paths.append(path)
            return match_paths


    def join(self, path: str) -> str:
        """
        Join folder path and relative path.

        Parameters
        ----------
        path : Relative path.

        Returns
        -------
        Joined path.
        """

        # Join.
        join_path = join_path(self.path, path)

        return join_path


    @property
    def name(self) -> str:
        """
        Return folder name.

        Returns
        -------
        Folder name.
        """

        # Get.
        folder_name = os_basename(self.path)

        return folder_name


    @property
    def dir(self) -> str:
        """
        Return folder directory.

        Returns
        -------
        Folder directory.
        """

        # Get.
        folder_dir = os_dirname(self.path)

        return folder_dir


    @property
    def drive(self) -> str:
        """
        Return folder drive letter.

        Returns
        -------
        Folder drive letter.
        """

        # Get.
        folder_drive, _ = os_splitdrive(self.path)

        return folder_drive


    @property
    def size(self) -> int:
        """
        Return folder byte size, include all files in it.

        Returns
        -------
        Folder byte size.
        """

        # Get.
        file_paths = self.paths('file', True)
        file_sizes = [
            os_getsize(path)
            for path in file_paths
        ]
        folder_size = sum(file_sizes)

        return folder_size


    @property
    def ctime(self) -> float:
        """
        Return file create timestamp.

        Returns
        -------
        File create timestamp.
        """

        # Get.
        folder_ctime = os_getctime(self.path)

        return folder_ctime


    @property
    def mtime(self) -> float:
        """
        Return file modify timestamp.

        Returns
        -------
        File modify timestamp.
        """

        # Get.
        folder_mtime = os_getmtime(self.path)

        return folder_mtime


    @property
    def atime(self) -> float:
        """
        Return file access timestamp.

        Returns
        -------
        File access timestamp.
        """

        # Get.
        folder_atime = os_getatime(self.path)

        return folder_atime


    def __bool__(self) -> bool:
        """
        Judge if exist.

        Returns
        -------
        Judge result.
        """

        # Judge.
        folder_exist = os_isdir(self.path)

        return folder_exist


    def __len__(self) -> int:
        """
        Return folder byte size, include all files in it.

        Returns
        -------
        Folder byte size.
        """

        # Get.
        folder_size = self.size

        return folder_size


    def __contains__(self, relpath: str) -> bool:
        """
        whether exist relative path object.

        Parameters
        ----------
        relpath : Relative path.

        Returns
        -------
        Judge result.
        """

        # Judge.
        path = self.join(relpath)
        judge = os_exists(path)

        return judge


    def __del__(self) -> None:
        """
        Close temporary folder.
        """

        # Close.
        self.folder.cleanup()


    __call__ = paths

    __add__ = __radd__ = join


class FileCache(Base):
    """
    File cache type.
    """


    def __init__(self, path: str = 'cache') -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        path : Root directory path.
        """

        # Set attribute.
        self.folder = Folder(path)

        # Make directory.
        self.__make_dir()


    def __make_dir(self) -> None:
        """
        Make cache directory and subdirectories.
        """

        # Make.
        chars = '0123456789abcdef'

        ## Root.
        paths = [self.folder.path]

        ## Second layer.
        paths.extend(
            [
                self.folder + char
                for char in chars
            ]
        )

        ## Third layer.
        paths.extend(
            [
                self.folder + f'{char}/{char_sub}'
                for char in chars
                for char_sub in chars
            ]
        )

        make_dir(*paths)


    def index(self, md5: str, name: str | None = None, copy: bool = False) -> str | None:
        """
        Index file from cache directory.

        Parameters
        ----------
        md5 : File MD5 value.
        name : File name.
            - `None`: Use MD5 value.
        copy : Do you want to copy file when exist MD5 value file and not exist file name.

        Returns
        -------
        File path or not exist.
        """

        # Handle parameter.
        name = name or md5

        # Not exist md5.
        md5_relpath = f'{md5[0]}/{md5[1]}/{md5}'
        if md5_relpath not in self.folder:
            return

        # Exist md5.
        file_relpath = f'{md5_relpath}/{name}'
        file_path = self.folder + file_relpath

        ## Exist file.
        if file_path in self.folder:
            return file_path

        ## Copy file.
        elif copy:
            md5_path = self.folder + md5_relpath
            md5_folder = Folder(md5_path)
            md5_file_path = md5_folder.search(target='file')
            file = File(md5_file_path)
            file.copy(file_path)
            return file_path


    def store(self, source: FileSourceBytes, name: str | None = None, delete: bool = False) -> str:
        """
        Store file to cache directory.

        Parameters
        ----------
        source : Source file path or file data.
        name : File name.
            - `None`: Use MD5 value.
        delete : When source is file path, whether delete original file.

        Returns
        -------
        Store file path.
        """

        # Handle parameter.
        file_bytes = read_file_bytes(source)
        file_md5 = get_md5(file_bytes)
        name = name or file_md5
        delete = delete and type(source) == str

        # Exist.
        path = self.index(file_md5, name)
        if path is not None:

            ## Delete.
            if delete:
                file = File(source)
                file.remove()

            return path

        # Store.
        md5_relpath = f'{file_md5[0]}/{file_md5[1]}/{file_md5}'
        md5_path = self.folder + md5_relpath
        folder = Folder(md5_path)
        folder.make()
        path = folder + name

        ## Delete.
        if delete:
            file = File(source)
            file.move(path)

        ## Make.
        else:
            file = File(path)
            file(file_bytes)

        return path


    def download(self, url: str, name: str | None = None) -> str:
        """
        Download file from URL.

        Parameters
        ----------
        url : Download URL.
        name : File name.
            - `None`: Get from response, or is MD5 value join automatic judge file type.

        Returns
        -------
        File absolute path.
        """

        # Import.
        from .rnet import request

        # Download.
        response = request(url)
        content = response.content

        # File name.
        if name is None:
            Content_disposition = response.headers.get('Content-Disposition', '')
            if 'filename' in Content_disposition:
                name: str | None = search(
                    'filename=[\'"]?([^\\s\'"]+)',
                    Content_disposition
                )
            if name is None:
                file_md5 = get_md5(content)
                file_type_obj = filetype_guess(content)
                if file_type_obj is not None:
                    name = f'{file_md5}.{file_type_obj.EXTENSION}'
                else:
                    name = file_md5

        # Store.
        path = self.store(content, name)

        return path


def doc_to_docx(path: str, save_path: str | None = None) -> str:
    """
    Convert `DOC` file to `DOCX` file.

    Parameters
    ----------
    path : DOC file path.
    save_path : DOCX sve file path.
        - `None`: DOC file Directory.

    Returns
    -------
    DOCX file path.
    """

    # Import.
    from win32com.client import Dispatch, CDispatch

    # Handle parameter.
    if save_path is None:
        pattern = '.[dD][oO][cC]'
        save_path = sub(
            pattern,
            path.replace('\\', '/'),
            '.docx'
        )

    # Convert.
    cdispatch = Dispatch('Word.Application')
    document: CDispatch = cdispatch.Documents.Open(path)
    document.SaveAs(save_path, 16)
    document.Close()

    return save_path


def extract_docx_content(path: str) -> str:
    """
    Extract content from `DOCX` file.

    Parameters
    ----------
    path : File path.

    returns
    -------
    Content.
    """

    # Import.
    from docx import Document as docx_document
    from docx.document import Document
    from docx.text.paragraph import Paragraph
    from docx.table import Table
    from docx.oxml.text.paragraph import CT_P
    from docx.oxml.table import CT_Tbl
    from lxml.etree import ElementChildIterator

    # Extract.
    document: Document = docx_document(path)
    childs_iter: ElementChildIterator = document.element.body.iterchildren()
    contents = []
    for child in childs_iter:
        match child:

            ## Text.
            case CT_P():
                paragraph = Paragraph(child, document)
                contents.append(paragraph.text)

            ## Table.
            case CT_Tbl():
                table = Table(child, document)
                table_text = '\n'.join(
                    [
                        ' | '.join(
                            [
                                cell.text.strip().replace('\n', ' ')
                                for cell in row.cells
                                if (
                                    cell.text is not None
                                    and cell.text.strip() != ''
                                )
                            ]
                        )
                        for row in table.rows
                    ]
                )
                table_text = '\n%s\n' % table_text
                contents.append(table_text)

    ## Join.
    content = '\n'.join(contents)

    return content


def extract_pdf_content(path: str) -> str:
    """
    Extract content from `PDF` file.

    Parameters
    ----------
    path : File path.

    returns
    -------
    Content.
    """

    # Import.
    from pdfplumber import open as pdfplumber_open

    # Extract.
    document = pdfplumber_open(path)
    contents = [
        page.extract_text()
        for page in document.pages
    ]
    document.close()

    ## Join.
    content = '\n'.join(contents)

    return content


def extract_file_content(path: str) -> str:
    """
    Extract content from `DOC` or `DOCX` or `PDF` file.

    Parameters
    ----------
    path : File path.

    returns
    -------
    Content.
    """

    # Handle parameter.
    _, suffix = os_splitext(path)
    suffix = suffix.lower()
    if suffix == '.doc':
        path = doc_to_docx(path)
        suffix = '.docx'

    # Extract.
    match suffix:

        ## DOCX.
        case '.docx':
            content = extract_docx_content(path)

        ## PDF.
        case '.pdf':
            content = extract_pdf_content(path)

        ## Throw exception.
        case _:
            throw(AssertionError, suffix)

    return content
