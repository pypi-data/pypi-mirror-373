# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:11:50
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Time methods.
"""


from typing import Any, TypedDict, Literal, NoReturn, overload
from collections.abc import Callable
from time import (
    struct_time as StructTime,
    strftime as time_strftime,
    time as time_time,
    sleep as time_sleep
)
from datetime import (
    datetime as Datetime,
    date as Date,
    time as Time,
    timedelta as Timedelta
)

from .rbase import T, Base, throw
from .rnum import digits
from .rrand import randn
from .rre import search
from .rstdout import echo


__all__ = (
    'now',
    'time_to',
    'text_to_time',
    'to_time',
    'sleep',
    'wait',
    'TimeMark'
)


RecordData = TypedDict('RecordData', {'timestamp': int, 'datetime': Datetime, 'timedelta': Timedelta | None, 'note': str | None})


@overload
def now(format_: Literal['datetime'] = 'datetime') -> Datetime: ...

@overload
def now(format_: Literal['date']) -> Date: ...

@overload
def now(format_: Literal['time']) -> Time: ...

@overload
def now(format_: Literal['datetime_str', 'date_str', 'time_str']) -> str: ...

@overload
def now(format_: Literal['timestamp', 'timestamp_s']) -> int: ...

def now(
    format_: Literal[
        'datetime',
        'date',
        'time',
        'datetime_str',
        'date_str',
        'time_str',
        'timestamp',
        'timestamp_s'
    ] = 'datetime'
) -> Datetime | Date | Time | str | int:
    """
    Get the now time.

    Parameters
    ----------
    format\\_ : Format type.
        - `Literal['datetime']`: Return datetime object of datetime package.
        - `Literal['date']`: Return date object of datetime package.
        - `Literal['time']`: Return time object of datetime package.
        - `Literal['datetime_str']`: Return string in format `'%Y-%m-%d %H:%M:%S'`.
        - `Literal['date_str']`: Return string in format `'%Y-%m-%d'`.
        - `Literal['time_str']`: Return string in foramt `'%H:%M:%S'`.
        - `Literal['timestamp']`: Return time stamp in milliseconds.
        - `Literal['timestamp_s']`: Return time stamp in seconds.

    Returns
    -------
    The now time.
    """

    # Return.
    match format_:
        case 'datetime':
            return Datetime.now()
        case 'date':
            return Datetime.now().date()
        case 'time':
            return Datetime.now().time()
        case 'datetime_str':
            return Datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        case 'date_str':
            return Datetime.now().strftime('%Y-%m-%d')
        case 'time_str':
            return Datetime.now().strftime('%H:%M:%S')
        case 'timestamp':
            return int(time_time() * 1000)
        case 'timestamp_s':
            return int(time_time())
        case _:
            throw(ValueError, format_)


@overload
def time_to(
    obj: Datetime | Date | Time | Timedelta | StructTime,
    decimal: bool = False,
    raising: bool = True
) -> str: ...

@overload
def time_to(
    obj: Any,
    decimal: bool = False,
    raising: Literal[True] = True
) -> NoReturn: ...

@overload
def time_to(
    obj: T,
    *,
    raising: Literal[False]
) -> T: ...

def time_to(
    obj: Any,
    decimal: bool = False,
    raising: bool = True
) -> Any:
    """
    Convert time object to text.

    Parameters
    ----------
    obj : Time object.
        - `datetime`: Text format is `'%Y-%m-%d %H:%M:%S'`.
        - `date`: Text format is `'%Y-%m-%d'`.
        - `time`: Text format is `'%H:%M:%S'`.
        - `struct_time`: Text format is `'%Y-%m-%d %H:%M:%S'`.
    decimal : Whether with decimal, precision to microseconds.
    raising : When parameter `obj` value error, whether throw exception, otherwise return original value.

    Returns
    -------
    Converted text.
    """

    # Convert.
    match obj:

        ## Type 'datetime'.
        case Datetime():
            if decimal:
                format_ = '%Y-%m-%d %H:%M:%S.%f'
            else:
                format_ = '%Y-%m-%d %H:%M:%S'
            text = obj.strftime(format_)

        ## Type 'date'.
        case Date():
            text = obj.strftime('%Y-%m-%d')

        ## Type 'time'.
        case Time():
            if decimal:
                format_ = '%H:%M:%S.%f'
            else:
                format_ = '%H:%M:%S'
            text = obj.strftime(format_)

        ## Type 'timedelta'.
        case Timedelta():
            timestamp = obj.seconds + obj.microseconds / 1000_000
            if timestamp >= 0:
                timestamp += 57600
                time = Datetime.fromtimestamp(timestamp).time()
                if decimal:
                    format_ = '%H:%M:%S.%f'
                else:
                    format_ = '%H:%M:%S'
                text = time.strftime(format_)
                if obj.days != 0:
                    text = f'{obj.days}day ' + text

            ### Throw exception.
            elif raising:
                throw(ValueError, obj)

            ### Not raise.
            else:
                return obj

        ## Type 'struct_time'.
        case StructTime():
            if decimal:
                format_ = '%Y-%m-%d %H:%M:%S.%f'
            else:
                format_ = '%Y-%m-%d %H:%M:%S'
            text = time_strftime(format_, obj)

        ## Throw exception.
        case _ if raising:
            throw(TypeError, obj)

        ## Not raise.
        case _:
            return obj

    return text


def text_to_time(
    string: str
) -> Datetime | Date | Time | None:
    """
    Convert text to time object.

    Parameters
    ----------
    string : String.

    Returns
    -------
    Object or null.
    """

    # Handle parameter.
    time_obj = None
    str_len = len(string)

    # Extract.

    ## Standard.
    if 14 <= str_len <= 19:
        try:
            time_obj = Datetime.strptime(string, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            pass
        else:
            return time_obj
    if 8 <= str_len <= 10:
        try:
            time_obj = Datetime.strptime(string, '%Y-%m-%d').date()
        except ValueError:
            pass
        else:
            return time_obj
    if 5 <= str_len <= 8:
        try:
            time_obj = Datetime.strptime(string, '%H:%M:%S').time()
        except ValueError:
            pass
        else:
            return time_obj

    ## Regular.

    ### Type 'datetime'.
    if 14 <= str_len <= 21:
        pattern = r'^(\d{4})\S(\d{1,2})\S(\d{1,2})\S?.(\d{1,2})\S(\d{1,2})\S(\d{1,2})\S?$'
        result = search(pattern, string)
        if result is not None:
            year, month, day, hour, minute, second = [
                int(value)
                for value in result
            ]
            time_obj = Datetime(year, month, day, hour, minute, second)
            return time_obj

    ### Type 'date'.
    if 8 <= str_len <= 11:
        pattern = r'^(\d{4})\S(\d{1,2})\S(\d{1,2})\S?$'
        result = search(pattern, string)
        if result is not None:
            year, month, day = [
                int(value)
                for value in result
            ]
            time_obj = Date(year, month, day)
            return time_obj

    ### Type 'time'.
    if 5 <= str_len <= 9:
        pattern = r'^(\d{1,2})\S(\d{1,2})\S(\d{1,2})\S?$'
        result = search(pattern, string)
        if result is not None:
            hour, minute, second = [
                int(value)
                for value in result
            ]
            time_obj = Time(hour, minute, second)
            return time_obj


@overload
def to_time(obj: str, raising: bool = True) -> Datetime | Date | Time: ...

@overload
def to_time(obj: StructTime | float, raising: bool = True) -> Datetime: ...

@overload
def to_time(obj: Any, raising: Literal[True] = True) -> NoReturn: ...

@overload
def to_time(obj: T, raising: Literal[False]) -> T: ...

def to_time(
    obj: Any,
    raising: bool = True
) -> Any:
    """
    Convert object to time object.

    Parameters
    ----------
    obj : Object.
    raising : When parameter `obj` value error, whether throw exception, otherwise return original value.

    Returns
    -------
    Time object.
    """

    # Convert.
    match obj:

        ## Type 'str'.
        case str():
            time_obj = text_to_time(obj)

        ## Type 'struct_time'.
        case StructTime():
            time_obj = Datetime(
                obj.tm_year,
                obj.tm_mon,
                obj.tm_mday,
                obj.tm_hour,
                obj.tm_min,
                obj.tm_sec
            )

        ## Type 'float'.
        case int() | float():
            int_len, _ = digits(obj)
            match int_len:
                case 10:
                    time_obj = Datetime.fromtimestamp(obj)
                case 13:
                    time_obj = Datetime.fromtimestamp(obj / 1000)
                case _:
                    time_obj = None

    ## No time object.
    if time_obj is None:

        ### Throw exception.
        if raising:
            throw(ValueError, obj)

        ### Not raise.
        else:
            return obj

    return time_obj


@overload
def sleep() -> int: ...

@overload
def sleep(second: int) -> int: ...

@overload
def sleep(low: int = 0, high: int = 10) -> int: ...

@overload
def sleep(*thresholds: float) -> float: ...

@overload
def sleep(*thresholds: float, precision: Literal[0]) -> int: ...

@overload
def sleep(*thresholds: float, precision: int) -> float: ...

def sleep(
    *thresholds: float,
    precision: int | None = None
) -> float:
    """
    Sleep random seconds.

    Parameters
    ----------
    thresholds : Low and high thresholds of random range, range contains thresholds.
        - When `length is 0`, then low and high thresholds is `0` and `10`.
        - When `length is 1`, then sleep this value.
        - When `length is 2`, then low and high thresholds is `thresholds[0]` and `thresholds[1]`.
    
    precision : Precision of random range, that is maximum decimal digits of sleep seconds.
        - `None`: Set to Maximum decimal digits of element of parameter `thresholds`.
        - `int`: Set to this value.
    
    Returns
    -------
    Random seconds.
        - When parameters `precision` is `0`, then return int.
        - When parameters `precision` is `greater than 0`, then return float.
    """

    # Handle parameter.
    if len(thresholds) == 1:
        second = thresholds[0]
    else:
        second = randn(*thresholds, precision=precision)

    # Sleep.
    time_sleep(second)

    return second


def wait(
    func: Callable[..., bool],
    *args: Any,
    _interval: float = 1,
    _timeout: float | None = None,
    _raising: bool = True,
    **kwargs: Any
) -> float | None:
    """
    Wait success.

    Parameters
    ----------
    func : Function to be decorated, must return `bool` value.
    args : Position arguments of decorated function.
    _interval : Interval seconds.
    _timeout : Timeout seconds, timeout throw exception.
        - `None`: Infinite time.
        - `float`: Use this time.
    _raising : When timeout, whether throw exception, otherwise return None.
    kwargs : Keyword arguments of decorated function.

    Returns
    -------
    Total spend seconds or None.
    """

    # Set parameter.
    tm = TimeMark()
    tm()

    # Not set timeout.
    if _timeout is None:

        ## Wait.
        while True:
            success = func(*args, **kwargs)
            if success:
                break
            sleep(_interval)

    # Set timeout.
    else:

        ## Wait.
        while True:
            success = func(*args, **kwargs)
            if success:
                break

            ## Timeout.
            tm()
            if tm.total_spend > _timeout:

                ### Throw exception.
                if _raising:
                    throw(TimeoutError, _timeout)

                return

            ## Sleep.
            sleep(_interval)

    ## Return.
    tm()
    return tm.total_spend


class TimeMark(Base):
    """
    Time mark type.

    Examples
    --------
    >>> timemark = TimeMark()
    >>> timemark('one')
    >>> timemark['two']
    >>> timemark.three
    >>> print(timemark)
    """


    def __init__(self) -> None:
        """
        Build instance attributes.
        """

        # Record table.
        self.records: dict[int, RecordData] = {}


    def mark(self, note: str | None = None) -> int:
        """
        Marking now time.

        Parameters
        ----------
        note : Mark note.

        Returns
        -------
        Mark index.
        """

        # Get parametes.

        # Mark.
        index = len(self.records)
        now_timestamp = now('timestamp')
        now_datetime = now('datetime')
        record = {
            'timestamp': now_timestamp,
            'datetime': now_datetime,
            'timedelta': None,
            'note': note
        }

        ## Not first.
        if index != 0:
            last_index = index - 1
            last_datetime = self.records[last_index]['datetime']
            record['timedelta'] = now_datetime - last_datetime

        ## Record.
        self.records[index] = record

        return index


    def get_report(self, title: str | None = None):
        """
        Return time mark report table.

        Parameters
        ----------
        title : Print title.
            - `None`: Not print.
            - `str`: Print and use this title.

        Returns
        -------
        Time mark report table.
        """

        # Import.
        from pandas import DataFrame

        # Handle parameter.
        record_len = len(self.records)
        data = [
            info.copy()
            for info in self.records.values()
        ]
        indexes = [
            index
            for index in self.records
        ]

        # Generate report.

        ## No record.
        if record_len == 0:
            row: RecordData = dict.fromkeys(('timestamp', 'datetime', 'timedelta', 'note'))
            data = [row]
            indexes = [0]

        ## Add total row.
        if record_len > 2:
            row: RecordData = dict.fromkeys(('timestamp', 'datetime', 'timedelta', 'note'))
            max_index = record_len - 1
            total_timedelta = self.records[max_index]['datetime'] - self.records[0]['datetime']
            row['timedelta'] = total_timedelta
            data.append(row)
            indexes.append('total')

        ## Convert.
        for row in data:
            if row['timestamp'] is not None:
                row['timestamp'] = str(row['timestamp'])
            if row['datetime'] is not None:
                row['datetime'] = str(row['datetime'])[:-3]
            if row['timedelta'] is not None:
                if row['timedelta'].total_seconds() == 0:
                    timedelta_str = '00:00:00.000'
                else:
                    timedelta_str = str(row['timedelta'])[:-3]
                    timedelta_str = timedelta_str.rsplit(' ', 1)[-1]
                    if timedelta_str[1] == ':':
                        timedelta_str = '0' + timedelta_str
                    if row['timedelta'].days != 0:
                        timedelta_str = '%sday %s' % (
                            row['timedelta'].days,
                            timedelta_str
                        )
                row['timedelta'] = timedelta_str
        df_info = DataFrame(data, index=indexes)
        df_info.fillna('-', inplace=True)

        return df_info


    @property
    def total_spend(self) -> float:
        """
        Get total spend seconds.

        Returns
        -------
        Total spend seconds.
        """

        # Break.
        if len(self.records) <= 1:
            return 0.0

        # Handle parameter.
        first_timestamp = self.records[0]['timestamp']
        max_index = max(self.records)
        last_timestamp = self.records[max_index]['timestamp']

        # Calculate.
        seconds = round((last_timestamp - first_timestamp) / 1000, 3)

        return seconds


    def clear(self) -> None:
        """
        Clear records.
        """

        # Clear.
        self.records.clear()


    def __str__(self) -> str:
        """
        Convert to string.

        Returns
        -------
        Converted string.
        """

        # Get.
        report = self.get_report()

        # Convert.
        string = str(report)

        return string


    def __int__(self) -> int:
        """
        Get total spend seconds, truncate the decimal part.

        Returns
        -------
        Total spend seconds.
        """

        # Get
        total_speend = int(self.total_spend)

        return total_speend


    def __float__(self) -> float:
        """
        Get total spend seconds.

        Returns
        -------
        Total spend seconds.
        """

        # Get
        total_speend = self.total_spend

        return total_speend


    __call__ = __getitem__ = mark
