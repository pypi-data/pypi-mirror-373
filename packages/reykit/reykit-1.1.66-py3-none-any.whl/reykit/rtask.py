# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-19 20:06:20
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Multi task methods.
"""


from typing import Any, Literal, overload
from collections.abc import Callable, Iterable, Generator, Coroutine
from threading import RLock as TRLock, get_ident as threading_get_ident
from concurrent.futures import ThreadPoolExecutor, Future as CFuture, as_completed as concurrent_as_completed
from queue import Queue as QQueue
from asyncio import (
    Future as AFuture,
    Lock as ALock,
    Task as ATask,
    Queue as AQueue,
    sleep as asyncio_sleep,
    run as asyncio_run,
    gather as asyncio_gather,
    iscoroutine as asyncio_iscoroutine,
    iscoroutinefunction as asyncio_iscoroutinefunction,
    run_coroutine_threadsafe as asyncio_run_coroutine_threadsafe,
    new_event_loop as asyncio_new_event_loop,
    set_event_loop as asyncio_set_event_loop
)
from aiohttp import ClientSession, ClientResponse

from .rbase import T, Base, throw, check_most_one, check_response_code
from .rtime import randn, TimeMark
from .rwrap import wrap_thread


__all__ = (
    'ThreadPool',
    'async_run',
    'async_sleep',
    'async_wait',
    'async_request',
    'AsyncPool'
)


class ThreadPool(Base):
    """
    Thread pool type.

    Attributes
    ----------
    Queue : Thread queue type.
    Lock : Thread lock type.
    """

    Queue = QQueue
    Lock = TRLock


    def __init__(
        self,
        task: Callable,
        *args: Any,
        _max_workers: int | None = None,
        **kwargs: Any
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        task : Thread task.
        args : ATask default position arguments.
        _max_workers : Maximum number of threads.
            - `None`: Number of CPU + 4, 32 maximum.
            - `int`: Use this value, no maximum limit.
        kwargs : ATask default keyword arguments.
        """

        # Set attribute.
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.pool = ThreadPoolExecutor(
            _max_workers,
            task.__name__
        )
        self.futures: list[CFuture] = []


    def one(
        self,
        *args: Any,
        **kwargs: Any
    ) -> CFuture:
        """
        Start a task.

        Parameters
        ----------
        args : ATask position arguments, after default position arguments.
        kwargs : ATask keyword arguments, after default keyword arguments.

        Returns
        -------
        ATask instance.
        """

        # Set parameter.
        func_args = (
            *self.args,
            *args
        )
        func_kwargs = {
            **self.kwargs,
            **kwargs
        }

        # Add.
        future = self.pool.submit(
            self.task,
            *func_args,
            **func_kwargs
        )

        # Save.
        self.futures.append(future)

        return future


    def batch(
        self,
        *args: tuple,
        **kwargs: tuple
    ) -> list[CFuture]:
        """
        Batch start tasks.
        parameters sequence will combine one by one, and discard excess parameters.

        Parameters
        ----------
        args : Sequence of task position arguments, after default position arguments.
        kwargs : Sequence of task keyword arguments, after default keyword arguments.

        Returns
        -------
        ATask instance list.

        Examples
        --------
        >>> func = lambda *args, **kwargs: print(args, kwargs)
        >>> a = (1, 2)
        >>> b = (3, 4, 5)
        >>> c = (11, 12)
        >>> d = (13, 14, 15)
        >>> thread_pool = ThreadPool(func, 0, z=0)
        >>> thread_pool.batch(a, b, c=c, d=d)
        (0, 1, 3) {'z': 0, 'c': 11, 'd': 13}
        (0, 2, 4) {'z': 0, 'c': 12, 'd': 14}
        """

        # Combine.
        args_zip = zip(*args)
        kwargs_zip = zip(
            *[
                [
                    (key, value)
                    for value in values
                ]
                for key, values in kwargs.items()
            ]
        )
        params_zip = zip(args_zip, kwargs_zip)

        # Batch add.
        futures = [
            self.one(*args_, **dict(kwargs_))
            for args_, kwargs_ in params_zip
        ]

        # Save.
        self.futures.extend(futures)

        return futures


    def repeat(
        self,
        number: int
    ) -> list[CFuture]:
        """
        Batch start tasks, and only with default parameters.

        Parameters
        ----------
        number : Number of add.

        Returns
        -------
        ATask instance list.
        """

        # Batch add.
        futures = [
            self.one()
            for _ in range(number)
        ]

        # Save.
        self.futures.extend(futures)

        return futures


    def generate(
        self,
        timeout: float | None = None
    ) -> Generator[CFuture]:
        """
        Return the generator of added task instance.

        Parameters
        ----------
        timeout : Call generator maximum waiting seconds, timeout throw exception.
            - `None`: Infinite.
            - `float`: Set this seconds.

        Returns
        -------
        Generator of added task instance.
        """

        # Build.
        generator = concurrent_as_completed(
            self.futures,
            timeout
        )

        return generator


    def join(
        self,
        timeout: float | None = None
    ) -> None:
        """
        Block until all tasks are done.

        Parameters
        ----------
        timeout : Call generator maximum waiting seconds, timeout throw exception.
            - `None`: Infinite.
            - `float`: Set this seconds.
        """

        # Generator.
        generator = self.generate(timeout)

        # Wait.
        for _ in generator:
            pass


    def __iter__(self) -> Generator:
        """
        Return the generator of task result.

        Returns
        -------
        Generator of task result.
        """

        # Generator.
        generator = self.generate()
        self.futures.clear()

        # Generate.
        for future in generator:
            yield future.result()


    @property
    def thread_id(self) -> int:
        """
        Get current thread ID.

        Returns
        -------
        Current thread ID.
        """

        # Get.
        thread_id = threading_get_ident()

        return thread_id


    __call__ = one

    __mul__ = repeat


@overload
def async_run(
    coroutine: Coroutine[Any, Any, T] | ATask[Any, Any, T] | Callable[[], Coroutine[Any, Any, T]],
    *,
    return_exceptions: bool = False
) -> T: ...

@overload
def async_run(
    *coroutines: Coroutine[Any, Any, T] | ATask[Any, Any, T] |  Callable[[], Coroutine[Any, Any, T]],
    return_exceptions: bool = False
) -> list[T]: ...

def async_run(
    *coroutines: Coroutine[Any, Any, T] | ATask[Any, Any, T] |  Callable[[], Coroutine[Any, Any, T]],
    return_exceptions: bool = False
) -> T | list[T]:
    """
    Asynchronous run coroutines.

    Parameters
    ----------
    coroutines : `Coroutine` instances or `ATask` instances or `Coroutine` function.
    return_exceptions : Whether return exception instances, otherwise throw first exception.

    Returns
    -------
    run results.
    """

    # Handle parameter.
    coroutines = [
        coroutine()
        if asyncio_iscoroutinefunction(coroutine)
        else coroutine
        for coroutine in coroutines
    ]

    # Define.
    async def async_run_coroutine() -> list:
        """
        Asynchronous run coroutines.

        Returns
        -------
        Run result list.
        """

        # Gather.
        results = await asyncio_gather(*coroutines, return_exceptions=return_exceptions)

        return results


    # Run.
    coroutine = async_run_coroutine()
    results = asyncio_run(coroutine)

    # One.
    if len(results) == 1:
        results = results[0]

    return results


@overload
async def async_sleep() -> int: ...

@overload
async def async_sleep(second: int) -> int: ...

@overload
async def async_sleep(low: int = 0, high: int = 10) -> int: ...

@overload
async def async_sleep(*thresholds: float) -> float: ...

@overload
async def async_sleep(*thresholds: float, precision: Literal[0]) -> int: ...

@overload
async def async_sleep(*thresholds: float, precision: int) -> float: ...

async def async_sleep(*thresholds: float, precision: int | None = None) -> float:
    """
    Sleep random seconds, in the coroutine.

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
    await asyncio_sleep(second)

    return second


async def async_wait(
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
            await async_sleep(_interval)

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
            await async_sleep(_interval)

    ## Return.
    tm()
    return tm.total_spend


async def async_request(
    url: str,
    params: dict | None = None,
    data: dict | str | bytes | None = None,
    json: dict | None = None,
    headers: dict[str, str] = {},
    timeout: float | None = None,
    proxy: str | None = None,
    method: Literal['get', 'post', 'put', 'patch', 'delete', 'options', 'head'] | None = None,
    check: bool | int | Iterable[int] = False,
    handler: str | tuple[str] | Callable[[ClientResponse], Coroutine | Any] | None = None
) -> Any:
    """
    Get asynchronous `Coroutine` instance of send request.

    Parameters
    ----------
    url : Request URL.
    params : Request URL add parameters.
    data : Request body data. Conflict with parameter `json`.
        - `dict`, Convert to `key=value&...`: format bytes.
            Automatic set `Content-Type` to `application/x-www-form-urlencoded`.
        - `dict and a certain value is 'bytes' type`: Key is parameter name and file name, value is file data.
            Automatic set `Content-Type` to `multipart/form-data`.
        - `str`: File path to read file bytes data.
            Automatic set `Content-Type` to file media type, and `filename` to file name.
        - `bytes`: File bytes data.
            Automatic set `Content-Type` to file media type.
    json : Request body data, convert to `JSON` format. Conflict with parameter `data`.
        Automatic set `Content-Type` to `application/json`.
    headers : Request header data.
    timeout : Request maximun waiting time.
    proxy : Proxy URL.
    method : Request method.
        - `None`: Automatic judge.
            When parameter `data` or `json` not has value, then request method is `get`.
            When parameter `data` or `json` has value, then request method is `post`.
        - `Literal['get', 'post', 'put', 'patch', 'delete', 'options', 'head']`: Use this request method.
    check : Check response code, and throw exception.
        - `Literal[False]`: Not check.
        - `Literal[True]`: Check if is between 200 and 299.
        - `int`: Check if is this value.
        - `Iterable`: Check if is in sequence.
    handler : Response handler.
        - `None`: Automatic handle.
            `Response 'Content-Type' is 'application/json'`: Use `ClientResponse.json` method.
            `Response 'Content-Type' is 'text/plain; charset=utf-8'`: Use `ClientResponse.text` method.
            `Other`: Use `ClientResponse.read` method.
        - `str`: Get this attribute.
            `Callable`: Execute this method. When return `Coroutine`, then use `await` syntax execute `Coroutine`.
            `Any`: Return this value.
        - `tuple[str]`: Get these attribute.
            `Callable`: Execute this method. When return `Coroutine`, then use `await` syntax execute `Coroutine`.
            `Any`: Return this value.
        - `Callable`, Execute this method. When return `Coroutine`, then use `await`: syntax execute `Coroutine`.

    Returns
    -------
    Response handler result.
    """

    # Check.
    check_most_one(data, json)

    # Handle parameter.
    if method is None:
        if data is None and json is None:
            method = 'get'
        else:
            method = 'post'

    # Session.
    async with ClientSession() as session:

        # Request.
        async with session.request(
            method,
            url,
            params=params,
            data=data,
            json=json,
            headers=headers,
            timeout=timeout,
            proxy=proxy
        ) as response:

            # Check code.
            if check is not False:
                if check is True:
                    range_ = None
                else:
                    range_ = check
                check_response_code(response.status, range_)

            # Receive.
            match handler:

                ## Auto.
                case None:
                    match response.content_type:
                        case 'application/json':
                            result = await response.json()
                        case 'text/plain; charset=utf-8':

                            # Set encode type.
                            if response.get_encoding() == 'ISO-8859-1':
                                encoding = 'utf-8'
                            else:
                                encoding = None

                            result = await response.text(encoding=encoding)
                        case _:
                            result = await response.read()

                ## Attribute.
                case str():
                    result = getattr(response, handler)

                    ### Method.
                    if callable(result):
                        result = result()

                        #### Coroutine.
                        if asyncio_iscoroutine(result):
                            result = await result

                ## Attributes.
                case tuple():
                    result = []
                    for key in handler:
                        result_element = getattr(response, key)

                        ### Method.
                        if callable(result_element):
                            result_element = result_element()

                            #### Coroutine.
                            if asyncio_iscoroutine(result_element):
                                result_element = await result_element

                        result.append(result_element)

                ## Method.
                case _ if callable(handler):
                    result = handler(response)

                    ### Coroutine.
                    if asyncio_iscoroutine(result):
                        result = await result

                ## Throw exception.
                case _:
                    throw(TypeError, handler)

            return result


class AsyncPool(Base):
    """
    Asynchronous pool type.

    Attributes
    ----------
    Queue : asynchronous queue type.
    Lock : asynchronous lock type.
    """

    Queue = AQueue
    Lock = ALock


    def __init__(
        self,
        task: Callable[..., Coroutine],
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        async_func : Function of create asynchronous `Coroutine`.
        args : Function default position arguments.
        kwargs : Function default keyword arguments.
        """

        # Set attribute.
        self.task = task
        self.args = args
        self.kwargs = kwargs
        self.loop = asyncio_new_event_loop()
        self.futures: list[AFuture] = []

        # Start.
        self.__start_loop()


    @wrap_thread
    def __start_loop(self) -> None:
        """
        Start event loop.
        """

        # Set.
        asyncio_set_event_loop(self.loop)

        ## Start and block.
        self.loop.run_forever()


    def one(
        self,
        *args: Any,
        **kwargs: Any
    ) -> None:
        """
        Start a task.

        Parameters
        ----------
        args : Function position arguments, after default position arguments.
        kwargs : Function keyword arguments, after default keyword arguments.
        """

        # Set parameter.
        func_args = (
            *self.args,
            *args
        )
        func_kwargs = {
            **self.kwargs,
            **kwargs
        }

        # Create.
        coroutine = self.task(*func_args, **func_kwargs)

        # Add.
        future = asyncio_run_coroutine_threadsafe(coroutine, self.loop)

        # Save.
        self.futures.append(future)


    def batch(
        self,
        *args: tuple,
        **kwargs: tuple
    ) -> None:
        """
        Batch start tasks.
        parameters sequence will combine one by one, and discard excess parameters.

        Parameters
        ----------
        args : Sequence of function position arguments, after default position arguments.
        kwargs : Sequence of function keyword arguments, after default keyword arguments.

        Examples
        --------
        >>> async def func(*args, **kwargs):
        ...     print(args, kwargs)
        >>> a = (1, 2)
        >>> b = (3, 4, 5)
        >>> c = (11, 12)
        >>> d = (13, 14, 15)
        >>> async_pool = AsyncPool(func, 0, z=0)
        >>> async_pool.batch(a, b, c=c, d=d)
        (0, 1, 3) {'z': 0, 'c': 11, 'd': 13}
        (0, 2, 4) {'z': 0, 'c': 12, 'd': 14}
        """

        # Combine.
        args_zip = zip(*args)
        kwargs_zip = zip(
            *[
                [
                    (key, value)
                    for value in values
                ]
                for key, values in kwargs.items()
            ]
        )
        params_zip = zip(args_zip, kwargs_zip)

        # Batch add.
        for args_, kwargs_ in params_zip:
            self.one(*args_, **dict(kwargs_))


    def repeat(
        self,
        number: int
    ) -> list[CFuture]:
        """
        Batch start tasks, and only with default parameters.

        Parameters
        ----------
        number : Number of add.
        """

        # Batch add.
        for _ in range(number):
            self.one()


    def generate(
        self,
        timeout: float | None = None
    ) -> Generator[CFuture]:
        """
        Return the generator of added task instance.

        Parameters
        ----------
        timeout : Call generator maximum waiting seconds, timeout throw exception.
            - `None`: Infinite.
            - `float`: Set this seconds.

        Returns
        -------
        Generator of added task instance.
        """

        # Build.
        generator = concurrent_as_completed(
            self.futures,
            timeout
        )

        return generator


    def join(
        self,
        timeout: float | None = None
    ) -> None:
        """
        Block until all tasks are done.

        Parameters
        ----------
        timeout : Call generator maximum waiting seconds, timeout throw exception.
            - `None`: Infinite.
            - `float`: Set this seconds.
        """

        # Generator.
        generator = self.generate(timeout)

        # Wait.
        for _ in generator:
            pass


    def __iter__(self) -> Generator:
        """
        Return the generator of task result.

        Returns
        -------
        Generator of task result.
        """

        # Generator.
        generator = self.generate()
        self.futures.clear()

        # Generate.
        for future in generator:
            yield future.result()


    def __del__(self) -> None:
        """
        End loop.
        """

        # Stop.
        self.loop.stop()


    __call__ = one

    __mul__ = repeat
