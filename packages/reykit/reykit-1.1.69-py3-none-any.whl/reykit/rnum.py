# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-04-22 22:32:34
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Number methods.
"""


from typing import Any

from .rbase import throw


__all__ = (
    'is_int',
    'digits',
    'to_number',
    'number_ch'
)


def is_int(number: int | float) -> bool:
    """
    Judge is integer, excluding decimal part is 0.

    Parameters
    ----------
    number : Number to judge.

    Returns
    -------
    Judge result.
    """

    # judge.
    match number:
        case int():
            judge = True
        case _:
            judge = number % 1 == 0

    return judge


def digits(number: int | float) -> tuple[int, int]:
    """
    Judge the number of integer digits and decimal digits, excluding decimal part is 0.

    Parameters
    ----------
    number : Number to judge.

    Returns
    -------
    Integer digits and decimal digits.
    """

    # Get digits.
    if is_int(number):
        number_str = str(number)
        int_digits = len(number_str)
        dec_digits = 0
    else:
        number = int(number)
        number_str = str(number)
        int_str, dec_str = number_str.split('.')
        int_digits = len(int_str)
        dec_digits = len(dec_str)

    return int_digits, dec_digits


def to_number(
    data: Any,
    raising: bool = True
) -> Any:
    """
    Convert data to number.

    Parameters
    ----------
    data : Data.
    raising : When parameter `string` value error, whether throw exception, otherwise return original value.

    Returns
    -------
    Converted number.
    """

    # Convert.
    try:
        data = float(data)
    except (ValueError, TypeError):

        # Throw exception.
        if raising:
            throw(ValueError, data)

    else:
        if is_int(data):
            data = int(data)

    return data


def number_ch(number: int) -> str:
    """
    Convert number to chinese number.

    Parameters
    ----------
    number : Number to convert.

    Returns
    -------
    Chinese number.
    """

    # Import.
    from .rre import sub_batch

    # Set parameter.
    map_digit = {
        '0': '零',
        '1': '一',
        '2': '二',
        '3': '三',
        '4': '四',
        '5': '五',
        '6': '六',
        '7': '七',
        '8': '八',
        '9': '九',
    }
    map_digits = {
        0: '',
        1: '十',
        2: '百',
        3: '千',
        4: '万',
        5: '十',
        6: '百',
        7: '千',
        8: '亿',
        9: '十',
        10: '百',
        11: '千',
        12: '万',
        13: '十',
        14: '百',
        15: '千',
        16: '兆'
    }

    # Handle parameter.
    number_str = str(number)

    # Replace digit.
    for digit, digit_ch in map_digit.items():
        number_str = number_str.replace(digit, digit_ch)

    # Add digits.
    number_list = []
    for index, digit_ch in enumerate(number_str[::-1]):
        digits_ch = map_digits[index]
        number_list.insert(0, digits_ch)
        number_list.insert(0, digit_ch)
    number_str = ''.join(number_list)

    # Delete redundant content.
    number_str = sub_batch(
        number_str,
        ('(?<=零)[^万亿兆]', ''),
        ('零+', '零'),
        ('零(?=[万亿兆])', '')
    )
    if number_str.startswith('一十'):
        number_str = number_str[1:]
    if number_str.endswith('零'):
        number_str = number_str[:-1]

    return number_str
