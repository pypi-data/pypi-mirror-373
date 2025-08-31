# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-08 13:18:24
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Text methods.
"""


from typing import Any, Literal, overload
from collections.abc import Iterable
from pprint import pformat as pprint_pformat

from .rbase import throw, is_iterable, get_varname
from .rmonkey import monkey_pprint_modify_width_judgment
from .rstdout import get_terminal_size


__all__ = (
    'to_text',
    'split_text',
    'get_width',
    'fill_width',
    'frame_text',
    'frame_data',
    'join_data_text',
    'join_filter_text',
    'is_zh'
)


# Monkey path.
monkey_pprint_modify_width_judgment()


def to_text(data: Any, width: int | None = None) -> str:
    """
    Format data to text.

    Parameters
    ----------
    data : Data.
    width : Format width.
        - `None` : Use terminal display character size.

    Returns
    -------
    Formatted text.
    """

    # Handle parameter.
    if width is None:
        width, _ = get_terminal_size()

    # Format.
    match data:

        ## Replace tab.
        case str():
            text = data.replace('\t', '    ')

        ## Format contents.
        case list() | tuple() | dict() | set():
            text = pprint_pformat(data, width=width, sort_dicts=False)

        ## Other.
        case _:
            text = str(data)

    return text


def split_text(text: str, max_len: int, by_width: bool = False) -> list[str]:
    """
    Split text by max length or not greater than display width.

    Parameters
    ----------
    text : Text.
    max_len : max length.
    by_width : Whether by char displayed width count length.

    Returns
    -------
    Split text.
    """

    # Split.
    texts = []

    ## By char displayed width.
    if by_width:
        str_group = []
        str_width = 0
        for char in text:
            char_width = get_width(char)
            str_width += char_width
            if str_width > max_len:
                string = ''.join(str_group)
                texts.append(string)
                str_group = [char]
                str_width = char_width
            else:
                str_group.append(char)
        string = ''.join(str_group)
        texts.append(string)

    ## By char number.
    else:
        test_len = len(text)
        split_n = test_len // max_len
        if test_len % max_len:
            split_n += 1
        for n in range(split_n):
            start_indxe = max_len * n
            end_index = max_len * (n + 1)
            text_group = text[start_indxe:end_index]
            texts.append(text_group)

    return texts


def get_width(text: str) -> int:
    """
    Get text display width.

    Parameters
    ----------
    text : Text.

    Returns
    -------
    Text display width.
    """

    # Set parameter.
    widths = (
        (126, 1),
        (159, 0),
        (687, 1),
        (710, 0),
        (711, 1),
        (727, 0),
        (733, 1),
        (879, 0),
        (1154, 1),
        (1161, 0),
        (4347, 1),
        (4447, 2),
        (7467, 1),
        (7521, 0),
        (8369, 1),
        (8426, 0),
        (9000, 1),
        (9002, 2),
        (11021, 1),
        (12350, 2),
        (12351, 1),
        (12438, 2),
        (12442, 0),
        (19893, 2),
        (19967, 1),
        (55203, 2),
        (63743, 1),
        (64106, 2),
        (65039, 1),
        (65059, 0),
        (65131, 2),
        (65279, 1),
        (65376, 2),
        (65500, 1),
        (65510, 2),
        (120831, 1),
        (262141, 2),
        (1114109, 1)
    )

    # Get width.
    total_width = 0
    for char in text:
        char_unicode = ord(char)
        if (
            char_unicode == 0xe
            or char_unicode == 0xf
        ):
            char_width = 0
        else:
            char_width = 1
            for num, wid in widths:
                if char_unicode <= num:
                    char_width = wid
                    break
        total_width += char_width

    return total_width


def fill_width(text: str, char: str, width: int, align: Literal['left', 'right', 'center'] = 'right') -> str:
    """
    Text fill character by display width.

    Parameters
    ----------
    text : Fill text.
    char : Fill character.
    width : Fill width.
    align : Align orientation.
        - `Literal[`left`]`: Fill right, align left.
        - `Literal[`right`]`: Fill left, align right.
        - `Literal[`center`]`: Fill both sides, align center.

    Returns
    -------
    Text after fill.
    """

    # Check parameter.
    if get_width(char) != 1:
        throw(ValueError, char)

    # Fill width.
    text_width = get_width(text)
    fill_width = width - text_width
    if fill_width > 0:
        match align:
            case 'left':
                new_text = ''.join((char * fill_width, text))
            case 'right':
                new_text = ''.join((text, char * fill_width))
            case 'center':
                fill_width_left = int(fill_width / 2)
                fill_width_right = fill_width - fill_width_left
                new_text = ''.join((char * fill_width_left, text, char * fill_width_right))
            case _:
                throw(ValueError, align)
    else:
        new_text = text

    return new_text


@overload
def frame_text(
    *texts: Iterable[str],
    title: str | Iterable[str] | None = None,
    width: int | None = None,
    frame: Literal['top', 'box'] = 'box',
    border: Literal['ascii', 'thick', 'double'] = 'double'
) -> str: ...

@overload
def frame_text(
    *texts: Iterable[str],
    width: int | None = None,
    frame: Literal['left'],
    border: Literal['ascii', 'thick', 'double'] = 'double'
) -> str: ...

def frame_text(
    *texts: Iterable[str],
    title: str | Iterable[str] | None = None,
    width: int | None = None,
    frame: Literal['left', 'top', 'box'] = 'box',
    border: Literal['ascii', 'thick', 'double'] = 'double'
) -> str:
    """
    Frame text.

    Parameters
    ----------
    texts : Texts.
    title : Frame title.
        - `None`: No title.
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

    Returns
    -------
    Added frame text.
    """

    # Handle parameter.
    if width is None:
        width, _ = get_terminal_size()
    line_chars_dict = {
        'double': '║═╔╗╚╝╡│╞╟─╢╓╙╒╕╶╴',
        'thick': '┃━┏┓┗┛┥│┝┠─┨┎┖┍┑╶╴',
        'ascii': '|-++++|||+-+/\\/\\  '
    }
    (
        char_v,
        char_h,
        char_to_l,
        char_to_r,
        char_bo_l,
        char_bo_r,
        char_ti_l,
        char_ti_c,
        char_ti_r,
        char_sp_l,
        char_sp_c,
        char_sp_r,
        char_le_t_e,
        char_le_b_e,
        char_to_l_e,
        char_to_r_e,
        char_sp_l_e,
        char_sp_r_e
    ) = line_chars_dict[border]
    if frame == 'top':
        char_v = ' '
        char_to_l = char_to_l_e
        char_to_r = char_to_r_e
        char_sp_l = char_sp_l_e
        char_sp_r = char_sp_r_e

    # Lines.
    parts = []

    ## Top.
    match frame:
        case 'left':
            part_top = char_le_t_e
        case 'top' | 'box':
            if is_iterable(title, (str,)):
                title = f' {char_ti_c} '.join(title)
            if (
                title is not None
                and len(title) > width - 4
            ):
                title = None
            if title is None:
                part_top = char_h * (width - 2)
            else:
                part_top = f'{char_ti_l} {title} {char_ti_r}'
                part_top = fill_width(part_top, char_h, width - 2, 'center')
            part_top = f'{char_to_l}{part_top}{char_to_r}'
    parts.append(part_top)

    ## Content.
    match frame:
        case 'left':
            char_v_l = char_v
            char_v_r = ''
            width_content = width - 1
            line_split = char_sp_l
        case 'top' | 'box':
            char_v_l = char_v_r = char_v
            width_content = width - 2
            line_split = f'{char_sp_l}{char_sp_c * (width - 2)}{char_sp_r}'
    part_content = f'\n{line_split}\n'.join(
        [
            '\n'.join(
                [
                    f'{char_v_l}{fill_width(text_line_width, ' ', width_content)}{char_v_r}'
                    for text_line in text.split('\n')
                    for text_line_width in split_text(text_line, width_content, True)
                ]
            )
            for text in texts
        ]
    )
    parts.append(part_content)

    ## Bottom.
    match frame:
        case 'left':
            parts.append(char_le_b_e)
        case 'top':
            pass
        case 'box':
            part_bottom = f'{char_bo_l}{char_h * (width - 2)}{char_bo_r}'
            parts.append(part_bottom)

    # Join.
    result = '\n'.join(parts)
    return result


def frame_data(
    *data: Any,
    title: str | Iterable[str] | None = None,
    width: int | None = None,
    frame: Literal['left', 'top', 'box'] = 'box',
    border: Literal['ascii', 'thick', 'double'] = 'double'
) -> str:
    """
    Frame text.

    Parameters
    ----------
    data : Data.
    title : Frame title.
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

    Returns
    -------
    Added frame text.
    """

    # handle parameter.
    if title is None:
        title: list[str] = get_varname('data')
    if width is None:
        width, _ = get_terminal_size()
    if frame == 'left':
        width_text = width - 1
    else:
        width_text = width - 2
    texts = [
        to_text(elem, width_text)
        for elem in data
    ]

    # Frame.
    text = frame_text(
        *texts,
        title=title,
        width=width,
        frame=frame,
        border=border
    )

    return text


def join_data_text(data: Iterable) -> str:
    """
    Join data to text.

    Parameters
    ----------
    data : Data.

    Returns
    -------
    Joined text.
    """

    # Join.

    ## dict type.
    if type(data) == dict:
        texts = []
        for key, value in data.items():
            key_str = str(key)
            value_str = str(value)
            if '\n' in value_str:
                value_str = value_str.replace('\n', '\n    ')
                text_part = f'{key_str}:\n    {value_str}'
            else:
                text_part = f'{key_str}: {value_str}'
            texts.append(text_part)
        text = '\n'.join(texts)

    ## Other type.
    else:
        text = '\n'.join(
            [
                str(elem)
                for elem in data
            ]
        )

    return text


def join_filter_text(data: Iterable, char: str = ',', filter_: tuple = (None, '')) -> str:
    """
    Join and filter text.

    Parameters
    ----------
    data : Data.
        - `Element is 'str'`: Join.
        - `Element is 'Any'`: Convert to string and join.
    char : Join character.
    filter\\_ : Filter elements.

    Returns
    -------
    Joined text.
    """

    # Filter and convert.
    data = [
        str(elem)
        for elem in data
        if elem not in filter_
    ]

    # Join.
    text = char.join(data)

    return text


def is_zh(char: str) -> bool:
    """
    whther is Chinese character.
    Only includes basic Chinese character.

    Parameters
    ----------
    char : One character.

    Returns
    -------
    Judged result.
    """

    # Check.
    if len(char) != 1:
        throw(ValueError, char)

    # Judge.
    judge = '\u4e00' <= char <= '\u9fa5'

    return judge
