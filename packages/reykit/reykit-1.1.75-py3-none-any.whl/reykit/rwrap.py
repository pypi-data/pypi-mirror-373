# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:12:25
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Decorator methods.
"""


from typing import Any, Literal, overload
from collections.abc import Callable
from io import IOBase, StringIO
from traceback import StackSummary
from inspect import getdoc as inspect_getdoc
from functools import wraps as functools_wraps, partial as functools_partial
from datetime import datetime as Datetime, timedelta as Timedelta
from threading import Thread
from argparse import ArgumentParser
from contextlib import redirect_stdout

from .rbase import T, catch_exc, get_arg_info
from .rstdout import echo
from .rtime import now, time_to, TimeMark


__all__ = (
    'wrap_wrap',
    'wrap_runtime',
    'wrap_thread',
    'wrap_exc',
    'wrap_retry',
    'wrap_dos_command',
    'wrap_cache_data',
    'wrap_cache',
    'wrap_redirect_stdout'
)


type Decorated = Callable
type Decorator = Callable[..., Decorated]


def wrap_wrap(decorator: Decorator | None = None) -> Decorator:
    """
    Decorate decorator.

    Parameters
    ----------
    decorator : Decorator.

    Retuens
    -------
    Decorated decorator.

    Examples
    --------
    >>> @wrap_wrap
    >>> def wrap_func(func, args, kwargs, **wrap_kwargs): ...

    Method one.
    >>> @wrap_func
    >>> def func(*args, **kwargs): ...

    Method two.
    >>> @wrap_func(**wrap_kwargs)
    >>> def func(*args, **kwargs): ...

    Method three.
    >>> def func(*args, **kwargs): ...
    >>> func = wrap_func(func, **wrap_kwargs)

    Method four.
    >>> def func(*args, **kwargs): ...
    >>> wrap_func = wrap_func(**wrap_kwargs)
    >>> func = wrap_func(func)

    >>> func(*args, **kwargs)
    """


    # Decorate Decorator.
    @overload
    def _wrap(func: Callable, **wrap_kwargs: Any) -> Decorated: ...

    @overload
    def _wrap(**wrap_kwargs: Any) -> Decorator: ...

    @functools_wraps(decorator)
    def _wrap(func: Callable | None = None, **wrap_kwargs: Any) -> Decorated | Decorator:
        """
        Decorated decorator.

        Parameters
        ----------
        func : Function.
        wrap_kwargs : Keyword arguments of decorator.

        Returns
        -------
        Decorated function or decorated self.
        """

        # Has decorator parameter.
        if func is None:
            __wrap = functools_partial(_wrap, **wrap_kwargs)
            return __wrap

        # No decorator parameter.
        else:


            @functools_wraps(func)
            def _func(*args: Any, **kwargs: Any) -> Any:
                """
                Decorated function.

                Parameters
                ----------
                args : Position arguments of function.
                kwargs : Keyword arguments of function.

                Returns
                -------
                Function return.
                """

                # Excute.
                result = decorator(func, args, kwargs, **wrap_kwargs)

                return result


            return _func


    return _wrap


@overload
def wrap_runtime(
    func: Callable[..., T],
    *,
    to_print: bool = True
) -> Callable[..., T]: ...

@overload
def wrap_runtime(
    func: Callable[..., T],
    to_return: Literal[True],
    to_print: bool = True
) -> Callable[..., tuple[T, str, Datetime, Timedelta, Datetime]]: ...

@overload
def wrap_runtime(
    *,
    to_print: bool = True
) -> Callable[[Callable[..., T]], T]: ...

@overload
def wrap_runtime(
    *,
    to_return: Literal[True],
    to_print: bool = True
) -> Callable[[Callable[..., T]], tuple[T, str, Datetime, Timedelta, Datetime]]: ...

@wrap_wrap
def wrap_runtime(
    func: Callable[..., T],
    args: Any,
    kwargs: Any,
    to_return: bool = False,
    to_print: bool = True
) -> T | tuple[T, str, Datetime, Timedelta, Datetime]:
    """
    Decorator, print or return runtime data of the function.

    Parameters
    ----------
    func : Function.
    args : Position arguments of function.
    kwargs : Keyword arguments of function.
    to_print : Whether to print runtime.
    to_return : Whether to return runtime.

    Returns
    -------
    Function return or runtime data.
    """

    # Execute function and marking time.
    tm = TimeMark()
    tm()
    result = func(*args, **kwargs)
    tm()

    # Generate report.
    start_time = tm.records[0]['datetime']
    spend_time: Timedelta = tm.records[1]['timedelta']
    end_time = tm.records[1]['datetime']
    start_str = time_to(start_time, True)[:-3]
    spend_str = time_to(spend_time, True)[:-3]
    end_str = time_to(end_time, True)[:-3]
    report = 'Start: %s -> Spend: %ss -> End: %s' % (
        start_str,
        spend_str,
        end_str
    )
    title = func.__name__

    # Print.
    if to_print:
        echo(report, title=title)

    # Return.
    if to_return:
        return result, report, start_time, spend_time, end_time

    return result


@overload
def wrap_thread(
    func: Callable,
    daemon: bool = True
) -> Callable[..., Thread]: ...

@overload
def wrap_thread(
    *,
    daemon: bool = True
) -> Callable[[Callable], Thread]: ...

@wrap_wrap
def wrap_thread(
    func: Callable,
    args: Any,
    kwargs: Any,
    daemon: bool = True
) -> Thread:
    """
    Decorator, function start in thread.

    Parameters
    ----------
    func : Function.
    args : Position arguments of function.
    kwargs : Keyword arguments of function.
    daemon : Whether it is a daemon thread.

    Returns
    -------
    Thread instance.
    """

    # Handle parameter.
    thread_name = '%s_%d' % (func.__name__, now('timestamp'))

    # Create thread.
    thread = Thread(target=func, name=thread_name, args=args, kwargs=kwargs)
    thread.daemon = daemon

    # Start thread.
    thread.start()

    return thread


@overload
def wrap_exc(
    func: Callable[..., T],
    handler: Callable[[str, BaseException, StackSummary], Any],
    exception: BaseException | tuple[BaseException, ...] | None = BaseException
) -> Callable[..., T | None]: ...

@overload
def wrap_exc(
    *,
    handler: Callable[[str, BaseException, StackSummary], Any],
    exception: BaseException | tuple[BaseException, ...] | None = BaseException
) -> Callable[[Callable[..., T]], T | None]: ...

@wrap_wrap
def wrap_exc(
    func: Callable[..., T],
    args: Any,
    kwargs: Any,
    handler: Callable[[str, BaseException, StackSummary], Any],
    exception: BaseException | tuple[BaseException, ...] | None = BaseException
) -> T | None:
    """
    Decorator, execute function with `try` syntax and handle exception.

    Parameters
    ----------
    func : Function.
    args : Position arguments of function.
    kwargs : Keyword arguments of function.
    handler : Exception handler.
    exception : Catch exception type.

    Returns
    -------
    Function return.
    """

    # Execute function.
    try:
        result = func(*args, **kwargs)

    # Handle exception.
    except exception:
        exc_text, exc, stack = catch_exc()
        handler(exc_text, exc, stack)

    else:
        return result


@overload
def wrap_retry(
    func: Callable[..., T],
    total: int = 1,
    handler: Callable[[tuple[str, BaseException, StackSummary]], Any] | None = None,
    exception: BaseException | tuple[BaseException, ...] = BaseException
) -> Callable[..., T]: ...

@overload
def wrap_retry(
    *,
    total: int = 1,
    handler: Callable[[tuple[str, BaseException, StackSummary]], Any] | None = None,
    exception: BaseException | tuple[BaseException, ...] = BaseException
) -> Callable[[Callable[..., T]], T]: ...

@wrap_wrap
def wrap_retry(
    func: Callable[..., T],
    args: Any,
    kwargs: Any,
    total: int = 2,
    handler: Callable[[tuple[str, BaseException, StackSummary]], Any] | None = None,
    exception: BaseException | tuple[BaseException, ...] = BaseException
) -> T:
    """
    Decorator, try again and handle exception.

    Parameters
    ----------
    func : Function.
    args : Position arguments of function.
    kwargs : Keyword arguments of function.
    total : Retry total.
    handler : Exception handler.
    exception : Catch exception type.

    Returns
    -------
    Function return.
    """

    # Loop.
    for _ in range(0, total - 1):

        # Try.
        try:
            result = func(*args, **kwargs)

        ## Handle.
        except exception:
            if handler is not None:
                exc_text, exc, stack = catch_exc()
                handler(exc_text, exc, stack)

        else:
            return result

    # Last.
    result = func(*args, **kwargs)

    return result


@overload
def wrap_dos_command(
    func: Callable[..., T]
) -> Callable[..., T]: ...

@overload
def wrap_dos_command() -> Callable[[Callable[..., T]], T]: ...

@wrap_wrap
def wrap_dos_command(
    func: Callable[..., T],
    args: Any,
    kwargs: Any,
) -> T:
    """
    Decorator, use DOS command to input arguments to function.
    Use DOS command `python file --help` to view help information.

    Parameters
    ----------
    func : Function.
    args : Position arguments of function.
    kwargs : Keyword arguments of function.

    Returns
    -------
    Function return.
    """

    # Handle parameter.
    arg_info = get_arg_info(func)

    # Set DOS command.
    usage = inspect_getdoc(func)
    if usage is not None:
        usage = 'input arguments to function "%s"\n\n%s' % (func.__name__, usage)
    parser = ArgumentParser(usage=usage)
    for info in arg_info:
        annotation_text = str(info['annotation'])
        if info['annotation'] is None:
            arg_type = str
            arg_help = None
        else:
            if 'str' in annotation_text:
                arg_type = str
            elif 'float' in annotation_text:
                arg_type = float
            elif 'int' in annotation_text:
                arg_type = int
            elif 'bool' in annotation_text:
                arg_type = bool
            else:
                arg_type = str
            arg_help = annotation_text
        if info['type'] in ('var_position', 'var_position'):
            parser.add_argument(
                info['name'],
                nargs='*',
                type=arg_type,
                help=arg_help
            )
        else:
            parser.add_argument(
                info['name'],
                nargs='?',
                type=arg_type,
                help=arg_help
            )
            kw_name = '--' + info['name']
            parser.add_argument(
                kw_name,
                nargs='*',
                type=arg_type,
                help=arg_help,
                metavar='value',
                dest=kw_name
            )

    # Get argument.
    namespace = parser.parse_args()
    command_args = []
    command_kwargs = {}
    for info in arg_info:

        ## Position argument.
        value = getattr(namespace, info['name'])
        if value is not None:
            if type(value) == list:
                command_args.extend(value)
            else:
                command_args.append(value)

        ## Keyword argument.
        if info['type'] not in ('var_position', 'var_position'):
            kw_name = '--' + info['name']
            kw_value = getattr(namespace, kw_name)
            if type(kw_value) == list:
                kw_value_len = len(kw_value)
                match kw_value_len:
                    case 0:
                        kw_value = None
                    case 1:
                        kw_value = kw_value[0]
                command_kwargs[info['name']] = kw_value

    # Execute function.
    if command_args == []:
        func_args = args
    else:
        func_args = command_args
    func_kwargs = {
        **kwargs,
        **command_kwargs
    }
    result = func(
        *func_args,
        **func_kwargs
    )

    return result


# Cache decorator data.
wrap_cache_data: dict[Callable, list[tuple[Any, Any, Any]]] = {}


@overload
def wrap_cache(
    func: Callable[..., T],
    overwrite: bool = False
) -> Callable[..., T]: ...

@overload
def wrap_cache(
    *,
    overwrite: bool = False
) -> Callable[[Callable[..., T]], T]: ...

@wrap_wrap
def wrap_cache(
    func: Callable[..., T],
    args: Any,
    kwargs: Any,
    overwrite: bool = False
) -> T:
    """
    Decorator, Cache the return result of function input.
    if no cache, cache it.
    if cached, skip execution and return result.

    Parameters
    ----------
    func : Function.
    args : Position arguments of function.
    kwargs : Keyword arguments of function.
    overwrite : Whether to overwrite cache.

    Returns
    -------
    Function return.
    """

    # Index.
    wrap_cache_data_func = wrap_cache_data.setdefault(func, [])
    cache_index = None
    for index, (cache_args, cache_kwargs, cache_result) in enumerate(wrap_cache_data_func):
        if (
            cache_args == args
            and cache_kwargs == kwargs
        ):
            if overwrite:
                cache_index = index
                break
            else:
                return cache_result

    # Execute.
    result = func(*args, **kwargs)

    # Cache.
    data = (args, kwargs, result)
    if cache_index is None:
        wrap_cache_data_func.append(data)
    else:
        wrap_cache_data_func[cache_index] = data

    return result


@overload
def wrap_redirect_stdout(
    func: Callable[..., T],
    *,
    redirect: list | IOBase | None = None
) -> Callable[..., T]: ...

@overload
def wrap_redirect_stdout(
    *,
    redirect: list | IOBase | None = None
) -> Callable[[Callable[..., T]], T]: ...

@wrap_wrap
def wrap_redirect_stdout(
    func: Callable[..., T],
    args: Any,
    kwargs: Any,
    redirect: list | IOBase | None = None
) -> T:
    """
    Redirect standard output.

    Parameters
    ----------
    func : Function.
    args : Position arguments of function.
    kwargs : Keyword arguments of function.
    redirect : Redirect output list or IO object.

    Returns
    -------
    Function return.
    """

    # Handle parameter.
    if isinstance(redirect, IOBase):
        str_io = redirect
    else:
        str_io = StringIO()

    # Execute.
    with redirect_stdout(str_io):
        result = func(*args, **kwargs)

    # Save.
    if type(redirect) == list:
        value = str_io.getvalue()
        redirect.append(value)

    return result
