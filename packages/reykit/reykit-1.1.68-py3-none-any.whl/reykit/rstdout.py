# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-10-01 14:47:47
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Standard output and input methods.
"""


from typing import Any, Literal, Final
from collections.abc import Callable, Iterable
import sys
from io import TextIOWrapper
from os import devnull as os_devnull, isatty as os_isatty, get_terminal_size as os_get_terminal_size
from os.path import abspath as os_abspath

from .rbase import T, Base, ConfigMeta, get_stack_param, get_varname


__all__ = (
    'ConfigStdout',
    'get_terminal_size',
    'echo',
    'ask',
    'stop_print',
    'start_print',
    'modify_print',
    'reset_print',
    'add_print_position'
)


class ConfigStdout(Base, metaclass=ConfigMeta):
    """
    Config standard output type.

    Attributes
    ----------
    force_print_ascii : Whether force methods print frame use ascii border.
    """

    # Module path.
    _path_rstdout: Final[str] = os_abspath(__file__)

    # Status.
    _stoped: bool = False
    _modified: bool = False

    # IO.
    _io_null: TextIOWrapper = open(os_devnull, 'w')
    _io_stdout: TextIOWrapper = sys.stdout
    _io_stdout_write: Callable[[str], int] = sys.stdout.write

    # Force print ascii.
    force_print_ascii: bool = False

    # Added print position.
    _added_print_position: set = set()


def get_terminal_size(
    stream: Literal['stdin', 'stdout', 'stderr'] = 'stdout',
    default: T = (80, 24)
) -> tuple[int, int] | T:
    """
    Get terminal display character size.

    Parameters
    ----------
    stream : Standard stream type.

    Returns
    -------
    Column and line display character count.
    """

    # Handle parameter.
    match stream:
        case 'stdin':
            stream = 0
        case 'stdout':
            stream = 1
        case 'stderr':
            stream = 2

    # Get.
    exist = os_isatty(stream)
    if exist:
        terminal_size = os_get_terminal_size(stream)
        terminal_size = tuple(terminal_size)
    else:
        terminal_size = default

    return terminal_size


def echo(
    *data: Any,
    title: str | Iterable[str] | None = None,
    width: int | None = None,
    frame: Literal['left', 'top', 'box'] = 'box',
    border: Literal['ascii', 'thick', 'double'] = 'double',
    extra: str | None = None
) -> None:
    """
    Frame data and print.

    Parameters
    ----------
    data : Print data.
    title : Print title.
        - `None`: Use variable name of argument `data`.
        - `str` : Use this value.
        - `Iterable[str]` : Connect this values and use.
    width : Frame width.
        - `None` : Use terminal display character size.
    frame : Frame type.
        - `Literal[`left`]`: Line beginning add character column.
        - `Literal[`top`]`: Line head add character line, with title.
        - `Literal[`box`]`: Add four borders, with title, automatic newline.
    border : Border type.
        - `Literal['ascii']`: Use ASCII character.
        - `Literal['thick']`: Use thick line character.
        - `Literal['double']`: Use double line character.
    extra : Extra print text.
    """

    # Import.
    from .rtext import frame_data

    # Handle parameter.
    if title is None:
        title: list[str] = get_varname('data')
    if ConfigStdout.force_print_ascii:
        border = 'ascii'

    # Frame.
    text = frame_data(
        *data,
        title=title,
        width=width,
        frame=frame,
        border=border
    )

    # Extra.
    if extra is not None:
        text = f'{text}\n{extra}'

    # Print.
    print(text)


def ask(
    *data: Any,
    title: str | Iterable[str] | None = None,
    width: int | None = None,
    frame: Literal['left', 'top', 'box'] = 'box',
    border: Literal['ascii', 'thick', 'double'] = 'double',
    extra: str | None = None
) -> str:
    """
    Frame data and print and read string from standard input.

    Parameters
    ----------
    data : Print data.
    title : Print title.
        - `None`: Use variable name of argument `data`.
        - `str` : Use this value.
        - `Iterable[str]` : Connect this values and use.
    width : Frame width.
        - `None` : Use terminal display character size.
    frame : Frame type.
        - `Literal[`left`]`: Line beginning add character column.
        - `Literal[`top`]`: Line head add character line, with title.
        - `Literal[`box`]`: Add four borders, with title, automatic newline.
    border : Border type.
        - `Literal['ascii']`: Use ASCII character.
        - `Literal['thick']`: Use thick line character.
        - `Literal['double']`: Use double line character.
    extra : Extra print text.

    Returns
    -------
    Standard input string.
    """

    # Import.
    from .rtext import frame_data

    # Handle parameter.
    if ConfigStdout.force_print_ascii:
        border = 'ascii'

    # Frame.
    text = frame_data(
        *data,
        title=title,
        width=width,
        frame=frame,
        border=border
    )

    # Extra.
    if extra is not None:
        text = f'{text}\n{extra}'

    # Input.
    string = input(text)

    return string


def stop_print() -> None:
    """
    Stop standard output print.
    """

    # Stop.
    sys.stdout = ConfigStdout._io_null

    # Update status.
    ConfigStdout._stoped = True


def start_print() -> None:
    """
    Start standard output print.
    """

    # Check.
    if not ConfigStdout._stoped:
        return

    # Start.
    sys.stdout = ConfigStdout._io_stdout

    # Update status.
    ConfigStdout._stoped = False


def modify_print(preprocess: Callable[[str], str] | None) -> None:
    """
    Modify standard output print write method.

    Parameters
    ----------
    preprocess : Preprocess function.
        - `Callable[[str], str]`: Input old text, output new text, will trigger printing.
        - `Callable[[str], None]`: Input old text, no output, will not trigger printing.
    """


    # Define.
    def write(__s: str) -> int | None:
        """
        Modified standard output write method.

        Parameters
        ----------
        __s : Write text.

        Returns
        -------
        Number of text characters.
        """

        # Preprocess.
        __s = preprocess(__s)

        # Write.
        if type(__s) == str:
            write_len = ConfigStdout._io_stdout_write(__s)
            return write_len


    # Modify.
    ConfigStdout._io_stdout.write = write

    # Update status.
    ConfigStdout._modified = True


def reset_print() -> None:
    """
    Reset standard output print write method.
    """

    # Check.
    if not ConfigStdout._modified:
        return

    # Reset.
    ConfigStdout._io_stdout.write = ConfigStdout._io_stdout_write

    # Update status.
    ConfigStdout._modified = False


def add_print_position() -> None:
    """
    Add position text to standard output.
    """


    # Define.
    def preprocess(__s: str) -> str:
        """
        Preprocess function.

        Parameters
        ----------
        __s : Standard ouput text.

        Returns
        -------
        Preprocessed text.
        """

        # Handle parameter.
        stack_params = get_stack_param('full', 3)
        stack_floor = stack_params[-1]

        ## Compatible 'echo'.
        if (
            stack_floor['filename'] == ConfigStdout._path_rstdout
            and stack_floor['name'] == 'echo'
        ):
            stack_floor = stack_params[-2]

        # Add.
        position = 'File "%s", line %s' % (stack_floor['filename'], stack_floor['lineno'])

        # Added.
        if position in ConfigStdout._added_print_position:
            return __s

        ConfigStdout._added_print_position.add(position)
        __s = '%s\n%s' % (position, __s)

        return __s


    # Modify.
    modify_print(preprocess)
