# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-11 23:25:36
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Regular expression methods.
"""


from typing import Literal, overload
from collections.abc import Callable
from re import (
    search as re_search,
    sub as re_sub,
    split as re_split,
    findall as re_findall,
    S as RS,
    Match as RMatch
)

from .rdata import unique


__all__ = (
    'search',
    'findall',
    'sub',
    'split',
    'search_batch',
    'findall_batch',
    'sub_batch',
    'split_batch'
)


def search(
    pattern: str,
    text: str
) -> str | tuple[str | None, ...] | None:
    """
    Regular search text.

    Parameters
    ----------
    pattern : Regular pattern, `period match any character`.
    text : Match text.

    Returns
    -------
    Matching result.
        - When match to and not use `group`, then return string.
        - When match to and use `group`, then return tuple with value string or None.
            If tuple length is `1`, extract and return string.
        - When no match, then return None.
    """

    # Search.
    obj_re = re_search(pattern, text, RS)

    # Return result.
    if obj_re is not None:
        result = obj_re.groups()
        if result == ():
            result = obj_re[0]
        elif len(result) == 1:
            result = obj_re[1]

        return result


def findall(
    pattern: str,
    text: str,
) -> list[str] | list[tuple[str, ...]]:
    """
    Regular find all text.

    Parameters
    ----------
    pattern : Regular pattern, `period match any character`.
    text : Match text.

    Returns
    -------
    Find result.
    """

    # Find all.
    result = re_findall(pattern, text, RS)

    return result


def sub(
    pattern: str,
    text: str,
    replace: str | Callable[[RMatch], str] | None = None,
    count: int | None = None
) -> str:
    """
    Regular replace text.

    Parameters
    ----------
    pattern : Regular pattern, `period match any character`.
    text : Match text.
    replace : Replace text or handle function.
        - `None`: Delete match part.
    count : Replace maximum count.

    Returns
    -------
    Replaced result.
    """

    # Handle parameter.
    replace = replace or ''
    count = count or 0

    # Replace.
    result = re_sub(pattern, replace, text, count, RS)

    return result


def split(
    pattern: str,
    text: str,
    count: int | None = None
) -> list[str]:
    """
    Regular split text.

    Parameters
    ----------
    pattern : Regular pattern, `period match any character`.
    text : Match text.
    count : Split maximum count.

    Returns
    -------
    Split result.
    """

    # Handle parameter.
    count = count or 0

    # Replace.
    result = re_split(pattern, text, count, RS)

    return result


@overload
def search_batch(
    text: str,
    *patterns: str,
    first: Literal[True] = True
) -> str | tuple[str | None, ...] | None: ...

@overload
def search_batch(
    text: str,
    *patterns: str,
    first: Literal[False]
) -> list[str | tuple[str | None, ...] | None]: ...

def search_batch(
    text: str,
    *patterns: str,
    first: bool = True
) -> str | tuple[str | None, ...] | list[str | tuple[str | None, ...] | None] | None:
    """
    Batch regular search text.

    Parameters
    ----------
    text : Match text.
    pattern : Regular pattern, `period match any character`.
    first : Whether return first successful match.

    Returns
    -------
    Matching result.
        - When match to and not use group, then return string.
        - When match to and use group, then return tuple with value string or None.
        - When no match, then return.
    """

    # Search.

    ## Return first result.
    if first:
        for pattern in patterns:
            result = search(pattern, text)
            if result is not None:
                return result

    ## Return all result.
    else:
        result = [search(pattern, text) for pattern in patterns]
        return result


def findall_batch(text: str, *patterns: str) -> str:
    """
    Batch regular find all text.

    Parameters
    ----------
    text : Match text.
    patterns : Regular pattern, `period match any character`.

    Returns
    -------
    List of Find result.
    """

    # Find all.
    texts = [
        string
        for pattern in patterns
        for string in findall(pattern, text)
    ]

    # De duplicate.
    texts = unique(texts)

    return texts


def sub_batch(text: str, *patterns: str | tuple[str, str | Callable[[RMatch], str]]) -> str:
    """
    Batch regular replace text.

    Parameters
    ----------
    text : Match text.
    patterns : Regular pattern and replace text, `period match any character`.
        - `str`: Regular pattern, delete match part.
        - `tuple[str, str]`: Regular pattern and replace text.
        - `tuple[str, Callable[[RMatch], str]]`: Regular pattern and replace handle function.

    Returns
    -------
    Replaced result.
    """

    # Replace.
    for pattern in patterns:
        if type(pattern) == str:
            replace = None
        else:
            pattern, replace = pattern
        text = sub(pattern, text, replace)

    return text


def split_batch(text: str, *patterns: str) -> str:
    """
    Batch regular split text.

    Parameters
    ----------
    text : Match text.
    patterns : Regular pattern, `period match any character`.

    Returns
    -------
    Split result.
    """

    # Split.
    texts = [
        string
        for pattern in patterns
        for string in split(pattern, text)
        if string != ''
    ]

    # De duplicate.
    texts = unique(texts)

    return texts
