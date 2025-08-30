# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-04-22 22:32:34
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Random methods.
"""


from __future__ import annotations
from typing import Literal, Self, overload
from collections.abc import Sequence
from string import digits as string_digits, ascii_letters as string_ascii_letters, punctuation as string_punctuation
from math import ceil as math_ceil
from random import Random
from secrets import randbelow as secrets_randbelow
from threading import get_ident as threading_get_ident

from .rbase import T, Base, ConfigMeta, throw
from .rnum import digits


__all__ = (
    'ConfigRandom',
    'RandomSeed',
    'randn',
    'randb',
    'randi',
    'randchar',
    'randsort'
)


class ConfigRandom(Base, metaclass=ConfigMeta):
    """
    Config random type.
    """

    # RRandom.
    _rrandom_dict: dict[int, RandomSeed] = {}


class RandomSeed(Base):
    """
    Random seed type. set random seed.
    If set, based on `random` package.
    If not set, based on `secrets` package.

    Examples
    --------
    Use active switch.
    >>> RandomSeed(seed)
    >>> randn()
    >>> RandomSeed()

    Use `with` syntax.
    >>> with RandomSeed(seed):
    >>>     randn()
    """


    def __init__(self, seed: int | float | str | bytes | bytearray | None = None) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        seed : Random seed.
            - `None`: Clear seed.
            - `int | float | str | bytes | bytearray`: Set seed.
        """

        # Delete.
        if seed is None:
            self.__del__()

        # Build.
        else:
            self.seed = seed
            self.random = Random(seed)

            ## Record.
            thread_id = threading_get_ident()
            ConfigRandom._rrandom_dict[thread_id] = self


    def __del__(self) -> None:
        """
        Delete instance.
        """

        # Delete.
        thread_id = threading_get_ident()
        if thread_id in ConfigRandom._rrandom_dict:
            del ConfigRandom._rrandom_dict[thread_id]


    def __enter__(self) -> Self:
        """
        Enter syntax `with`.

        Returns
        -------
        Self.
        """

        return self


    def __exit__(
        self,
        *_
    ) -> None:
        """
        Exit syntax `with`.
        """

        # Delete.
        self.__del__()


@overload
def randn() -> int: ...

@overload
def randn(high: int = 10) -> int: ...

@overload
def randn(low: int = 0, high: int = 10) -> int: ...

@overload
def randn(*thresholds: float) -> float: ...

@overload
def randn(*thresholds: float, precision: Literal[0]) -> int: ...

@overload
def randn(*thresholds: float, precision: int) -> float: ...

def randn(*thresholds: float, precision: int | None = None) -> int | float:
    """
    Random number.

    Parameters
    ----------
    thresholds : Low and high thresholds of random range, range contains thresholds.
        - When `length is 0`, then low and high thresholds is `0` and `10`.
        - When `length is 1`, then low and high thresholds is `0` and `thresholds[0]`.
        - When `length is 2`, then low and high thresholds is `thresholds[0]` and `thresholds[1]`.
    precision : Precision of random range, that is maximum decimal digits of return value.
        - `None`: Set to Maximum decimal digits of element of parameter `thresholds`.
        - `int`: Set to this value.

    Returns
    -------
    Random number.
        - When parameters `precision` is 0, then return int.
        - When parameters `precision` is greater than 0, then return float.
    """

    # Handle parameter.
    thresholds_len = len(thresholds)
    match thresholds_len:
        case 0:
            threshold_low = 0
            threshold_high = 10
        case 1:
            threshold_low = 0
            threshold_high = thresholds[0]
        case 2:
            threshold_low = thresholds[0]
            threshold_high = thresholds[1]
        case _:
            raise ValueError('number of parameter "thresholds" must is 0 or 1 or 2')
    if precision is None:
        threshold_low_desimal_digits = digits(threshold_low)[1]
        threshold_high_desimal_digits = digits(threshold_high)[1]
        desimal_digits_max = max(threshold_low_desimal_digits, threshold_high_desimal_digits)
        precision = desimal_digits_max

    # Get random number.
    magnifier = 10 ** precision
    threshold_low = int(threshold_low * magnifier)
    threshold_high = int(threshold_high * magnifier)

    ## No seed.
    thread_id = threading_get_ident()
    seed = ConfigRandom._rrandom_dict.get(thread_id)
    if seed is None:
        range_ = threshold_high - threshold_low + 1
        number = secrets_randbelow(range_)
        number += threshold_low

    ## Seed.
    else:
        number = seed.random.randint(threshold_low, threshold_high)
    number = number / magnifier

    # Convert Integer.
    if precision == 0:
        number = int(number)

    return number


def randb(pr: float = 0.5) -> bool:
    """
    Random bool.

    Parameters
    ----------
    pr : Probability setting.
        - `∈(0, 1)`: Random probability, formula is `randn(1, int(1 / pr * 100)) <= 100`.
        - `∈(1, +∞)`: Random range, formula is `randn(1, ceil(pr)) == 1`.

    Returns
    -------
    Random bool.
    """

    # Random probability.
    if 0 < pr < 1:
        high = int(1 / pr * 100)
        result = randn(1, high) <= 100

    # Random range.
    elif 1 < pr:
        high = math_ceil(pr)
        result = randn(1, high) == 1

    # Throw exception.
    else:
        throw(ValueError, pr)

    return result


@overload
def randi(
    data: Sequence[T],
    multi: None = None,
    unique: bool = True
) -> T: ...

@overload
def randi(
    data: Sequence,
    multi: int,
    unique: bool = True
) -> list[T]: ...

def randi(
    data: Sequence,
    multi: int | None = None,
    unique: bool = True
) -> T | list[T]:
    """
    Random index data element.

    Parameters
    ----------
    data : Sequence data.
    multi : Whether index multiple data elements.
        - `None`: Return a value.
        - `int`: Return multiple values.
    unique : Whether index unique, non value constraint.

    Returns
    -------
    Element.
    """

    # Random.
    data_len = len(data)
    match multi:

        ## One.
        case None:
            index = randn(data_len - 1)
            result = data[index]

        ## Multiple.
        case _:
            match unique:

                ### Unique.
                case True:

                    #### Check.
                    if multi > data_len:
                        throw(IndexError, multi, data_len)

                    indexes = list(range(data_len))
                    indexes_randsort = [
                        indexes.pop(randn(indexes_len - 1))
                        for indexes_len in range(data_len, data_len - multi, -1)
                    ]
                    result = [
                        data[index]
                        for index in indexes_randsort
                    ]

                ### Not unique.
                case False:
                    rand_max = data_len - 1
                    result = [
                        data[randn(rand_max)]
                        for _ in range(multi)
                    ]

    return result


def randchar(
    length: int,
    punctuation: bool = True
) -> str:
    """
    Generate random characters.

    Parameters
    ----------
    length : Character length.
    punctuation : Whether contain punctuation.

    Returns
    -------
    Random characters.
    """

    # Handle parameter.
    char_range = string_digits + string_ascii_letters
    if punctuation:
        char_range += string_punctuation

    # Generate.
    char_list = randi(char_range, length, False)
    chars = ''.join(char_list)

    return chars


def randsort(data: Sequence[T]) -> list[T]:
    """
    Random sorting data.

    Parameters
    ----------
    data : Sequence data.

    Returns
    -------
    Sorted data.
    """

    # Random.
    data_len = len(data)
    data_randsort = randi(data, data_len)

    return data_randsort
