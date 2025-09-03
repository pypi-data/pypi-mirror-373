# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-10-08 21:26:43
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Log methods.
"""


from typing import Any, Literal, Final, overload
from collections.abc import Hashable, Callable
from queue import Queue
from os.path import abspath as os_abspath
from logging import (
    getLogger,
    Handler,
    StreamHandler,
    Formatter,
    Filter,
    LogRecord,
    DEBUG as LDEBUG,
    INFO as LINFO,
    WARNING as LWARNING,
    ERROR as LERROR,
    CRITICAL as LCRITICAL
)
from logging.handlers import QueueHandler
from concurrent_log_handler import ConcurrentRotatingFileHandler, ConcurrentTimedRotatingFileHandler

from .rbase import Base, ConfigMeta, null, throw, catch_exc, get_first_notnone, get_stack_param
from .rre import search, sub
from .rstdout import ConfigStdout, modify_print, reset_print
from .rtext import to_text
from .rtime import now, time_to
from .rwrap import wrap_thread


__all__ = (
    'ConfigLog',
    'Log',
    'Mark'
)


class ConfigLog(Base, metaclass=ConfigMeta):
    """
    Config log type.
    """

    # Module path.
    path_rlog: Final[str] = os_abspath(__file__)


class Log(Base):
    """
    Log type.
    """

    # Status.
    print_replaced: bool = False

    # Default value.
    default_format = (
        '%(format_time)s | '
        '%(format_levelname)s | '
        '%(format_path)s | '
        '%(format_message)s'
    )
    default_format_date = '%Y-%m-%d %H:%M:%S'
    default_format_width = 100

    # Whether print colour.
    print_colour: bool = True

    # Level.
    DEBUG = LDEBUG
    INFO = LINFO
    WARNING = LWARNING
    ERROR = LERROR
    CRITICAL = LCRITICAL


    def __init__(
        self,
        name: str = 'Log'
    ) -> None:
        """
        Build instance attributes.

        Parameters
        ----------
        name : Log name. When log name existed, then direct return, otherwise build.
        """

        # Set attribute.
        self.name: Final[str] = name
        self.stoped = False

        # Get logger.
        self.logger = getLogger(name)

        # Set level.
        self.logger.setLevel(self.DEBUG)


    def __get_message_stack(self) -> dict:
        """
        Get message stack parameters.

        Returns
        -------
        Stack parameters.
        """

        # Handle parameter.
        stack_params = get_stack_param('full', 12)
        stack_param = stack_params[-1]

        # Compatible.

        ## Compatible '__call__'.
        if (
            stack_param['filename'] == ConfigLog.path_rlog
            and stack_param['name'] in ('debug', 'info', 'warning', 'error', 'critical')
        ):
            stack_param = stack_params[-2]

        ## Compatible 'print'.
        if (
            stack_param['filename'] == ConfigLog.path_rlog
            and stack_param['name'] == 'preprocess'
        ):
            stack_param = stack_params[-3]

        ## Compatible 'echo'.
        if (
            stack_param['filename'] == ConfigStdout._path_rstdout
            and stack_param['name'] == 'echo'
        ):
            stack_param = stack_params[-4]

        return stack_param


    def __supply_format_standard(
        self,
        format_: str,
        record: LogRecord
    ) -> None:
        """
        Supply format standard parameters.

        Parameters
        ----------
        format\\_ : Record format.
        record : Log record instance.
        """

        # Format 'format_time'.
        if '%(format_time)s' in format_:
            datetime = now()
            datetime_str = time_to(datetime, True)
            record.format_time = datetime_str[:-3]

        # Format 'format_levelname'.
        if '%(format_levelname)s' in format_:
            record.format_levelname = record.levelname.ljust(8)

        # Format 'format_path'.
        if '%(format_path)s' in format_:
            message_stack = self.__get_message_stack()
            record.format_path = '%s:%s' % (
                message_stack['filename'],
                message_stack['lineno']
            )

        # Format 'format_message'.
        if '%(format_message)s' in format_:
            record.format_message = record.getMessage()


    def get_level_color_ansi(
        self,
        level: int
    ) -> str:
        """
        Get level color `ANSI` code.

        Parameters
        ----------
        level : Record level.

        Returns
        -------
        Level color ansi code.
        """

        # Set parameters.
        color_code_dict = {
            10: '\033[1;34m',
            20: '\033[1;37m',
            30: '\033[1;33m',
            40: '\033[1;31m',
            50: '\033[1;37;41m'
        }

        # Get.
        color_code = color_code_dict.get(level, '')

        return color_code


    def __supply_format_print(
        self,
        format_: str,
        record: LogRecord
    ) -> None:
        """
        Supply format print parameters.

        Parameters
        ----------
        format\\_ : Record format.
        record : Log record instance.
        """

        # Break.

        ## Switch.
        if not self.print_colour:
            return

        ## Added.
        pattern = '\033\\[[\\d;]+?m'
        result = search(pattern, format_)
        if result is not None:
            return

        # 'format_time'.
        if '%(format_time)s' in format_:
            record.format_time = '\033[32m%s\033[0m' % record.format_time

        # 'format_levelname'.
        if '%(format_levelname)s' in format_:
            level_color_code = self.get_level_color_ansi(record.levelno)
            record.format_levelname = '%s%s\033[0m' % (
                level_color_code,
                record.format_levelname
            )

        # 'format_path'.
        if '%(format_path)s' in format_:
            record.format_path = '\033[36m%s\033[0m' % record.format_path

        # 'format_message'.
        if (
            '%(format_message)s' in format_
            and search('\033\\[[\\d;]+?m', record.format_message) is None
        ):
            level_color_code = self.get_level_color_ansi(record.levelno)
            record.format_message = '%s%s\033[0m' % (
                level_color_code,
                record.format_message
            )


    def __supply_format_file(
        self,
        format_: str,
        record: LogRecord
    ) -> None:
        """
        Supply format file parameters.

        Parameters
        ----------
        format\\_ : Record format.
        record : Log record instance.
        """

        # Format 'format_message'.
        if '%(format_message)s' in format_:
            pattern = '\033\\[[\\d;]+?m'
            record.format_message = sub(pattern, record.format_message)


    def get_default_filter_method(
        self,
        format_: str,
        mode : Literal['print', 'file'] | None = None
    ) -> Callable[[LogRecord], Literal[True]]:
        """
        Get default filter method of handler.

        Parameters
        ----------
        format\\_ : Record format.
        mode : Handler mode.
            - `None`: Standard filter method.
            - `Literal['print']`: Print handler filter method.
            - `Literal['file']`: File handler filter method.

        Returns
        -------
        Filter method.
        """


        # Define.
        def default_filter_method(
            record: LogRecord
        ) -> Literal[True]:
            """
            Default filter method of handler.

            Parameters
            ----------
            record : Log record instance.

            Returns
            -------
            Whether pass.
            """

            # Format standard.
            self.__supply_format_standard(format_, record)

            match mode:

                # Format print.
                case 'print':
                    self.__supply_format_print(format_, record)

                # Format file.
                case 'file':
                    self.__supply_format_file(format_, record)

            return True


        return default_filter_method


    def get_filter(
        self,
        method: Callable[[LogRecord], bool]
    ):
        """
        Get filter.

        Parameters
        ----------
        method : Filter method.

        Returns
        -------
        Filter.
        """


        # Define.
        class _Filter(Base, Filter):
            """
            Filter type.
            """


            def filter(
                record: LogRecord
            ) -> Literal[True]:
                """
                Filter method.

                Parameters
                ----------
                record : Log record instance.

                Returns
                -------
                Whether pass.
                """

                # Filter.
                result = method(record)

                return result


        return _Filter


    def add_print(
        self,
        level: int = DEBUG,
        format_: str | None = None,
        filter_: Callable[[LogRecord], bool] | None = None
    ) -> StreamHandler:
        """
        Add print output record handler.

        Parameters
        ----------
        level : Handler level.
        format\\_ : Record format.
            - `None`: Use attribute `default_format`.
            - `str`: Use this value. 
                `Contain 'format_time'`: Date and time and millisecond, print output with color.
                `Contain 'format_levelname'`: Level name and fixed width, print output with color.
                `Contain 'format_path'`: Record code path, print output with color.
                `Contain 'format_message'`: message content, file output delete ANSI code, print outputwith color.
        filter\\_ : Filter method. The parameter is the `LogRecord` instance, return is `bool`.
            - `None`: Use default filter method.
            - `Callable`: Use this method.

        Returns
        -------
        Handler.
        """

        # Handle parameter.
        format_ = get_first_notnone(format_, self.default_format)
        filter_ = filter_ or self.get_default_filter_method(format_, 'print')

        # Create handler.
        handler = StreamHandler()
        handler.setLevel(level)
        formatter = Formatter(format_, self.default_format_date)
        handler.setFormatter(formatter)
        handler_filter = self.get_filter(filter_)
        handler.addFilter(handler_filter)

        # Add.
        self.logger.addHandler(handler)

        return handler


    @overload
    def add_file(
        self,
        path: str | None = None,
        mb: float | None = None,
        *,
        level: int = DEBUG,
        format_: str | None = None,
        filter_: Callable[[LogRecord], bool] | None = None
    ) -> ConcurrentRotatingFileHandler: ...

    @overload
    def add_file(
        self,
        path: str | None = None,
        *,
        time: float | Literal['m', 'w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6'] = None,
        level: int = DEBUG,
        format_: str | None = None,
        filter_: Callable[[LogRecord], bool] | None = None
    ) -> ConcurrentTimedRotatingFileHandler: ...

    def add_file(
        self,
        path: str | None = None,
        mb: float | None = None,
        time: float | Literal['m', 'w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6'] | None = None,
        level: int = DEBUG,
        format_: str | None = None,
        filter_: Callable[[LogRecord], bool] | None = None
    ) -> ConcurrentRotatingFileHandler | ConcurrentTimedRotatingFileHandler:
        """
        Add file output record handler, can split files based on size or time.

        Parameters
        ----------
        path : File path.
            - `None`: Use attribute `self.name`.
            - `str`: Use this value.
        mb : File split condition, max megabyte. Conflict with parameter `time`. Cannot be less than 1, prevent infinite split file.
        time : File split condition, interval time. Conflict with parameter `mb`.
            - `float`: Interval hours.
            - `Literal['m']`: Everyday midnight.
            - `Literal['w0', 'w1', 'w2', 'w3', 'w4', 'w5', 'w6']`: Weekly midnight, 'w0' is monday, 'w6' is sunday, and so on.
        level : Handler level.
        format\\_ : Record format.
            - `None`: Use attribute `default_format`.
            - `str`: Use this value.
                `Contain 'format_time'`: Date and time and millisecond, print output with color.
                `Contain 'format_levelname'`: Level name and fixed width, print output with color.
                `Contain 'format_path'`: Record code path, print output with color.
                `Contain 'format_message'`: message content, file output delete ANSI code, print outputwith color.
        filter\\_ : Filter method. The parameter is the `LogRecord` instance, return is `bool`.
            - `None`: Use default filter method.
            - `Callable`: Use this method.

        Returns
        -------
        Handler.
        """

        # Handle parameter.
        format_ = get_first_notnone(format_, self.default_format)
        path = path or self.name
        filter_ = filter_ or self.get_default_filter_method(format_, 'file')

        # Create handler.

        ## Throw exception.
        if (
            mb is not None
            and time is not None
        ):
            raise AssertionError('parameter "mb" and "time" cannot be used together')

        ## By size split.
        elif mb is not None:

            ### Check.
            if mb < 1:
                throw(ValueError, mb)

            byte = int(mb * 1024 * 1024)
            handler = ConcurrentRotatingFileHandler(
                path,
                'a',
                byte,
                1_0000_0000,
                delay=True
            )

        ## By time split.
        elif time is not None:
            match time:

                ### Interval hours.
                case int() | float():
                    second = int(time * 60 * 60)
                    handler = ConcurrentTimedRotatingFileHandler(
                        path,
                        'S',
                        second,
                        1_0000_0000,
                        delay=True
                    )

                ### Everyday midnight.
                case 'm':
                    handler = ConcurrentTimedRotatingFileHandler(
                        path,
                        'MIDNIGHT',
                        backupCount=1_0000_0000,
                        delay=True
                    )

                ### Weekly midnight
                case 'w0' | 'w1' | 'w2' | 'w3' | 'w4' | 'w5' | 'w6':
                    handler = ConcurrentTimedRotatingFileHandler(
                        path,
                        time,
                        backupCount=1_0000_0000,
                        delay=True
                    )

                ### Throw exception.
                case _:
                    throw(ValueError, time)

        ## Not split.
        else:
            handler = ConcurrentRotatingFileHandler(
                path,
                'a',
                delay=True
            )

        # Set handler.
        handler.setLevel(level)
        formatter = Formatter(format_, self.default_format_date)
        handler.setFormatter(formatter)
        handler_filter = self.get_filter(filter_)
        handler.addFilter(handler_filter)

        # Add.
        self.logger.addHandler(handler)

        return handler


    def add_queue(
        self,
        queue: Queue | None = None,
        level: int = DEBUG,
        filter_: Callable[[LogRecord], bool] | None = None
    ) -> tuple[QueueHandler, Queue[LogRecord]]:
        """
        Add queue output record handler.

        Parameters
        ----------
        queue : Queue instance.
            - `None`: Create queue and use.
            - `Queue`: Use this queue.
        level : Handler level.
        filter\\_ : Filter method. The parameter is the `LogRecord` instance, return is `bool`.

        Returns
        -------
        Handler and queue.
        """

        ## Create queue.
        queue = queue or Queue()

        # Create handler.
        handler = QueueHandler(queue)

        # Set handler.
        handler.setLevel(level)
        if filter_ is not None:
            handler_filter = self.get_filter(filter_)
            handler.addFilter(handler_filter)

        # Add.
        self.logger.addHandler(handler)

        return handler, queue


    def add_handler(
        self,
        method: Callable[[LogRecord], Any],
        level: int = DEBUG,
        filter_: Callable[[LogRecord], bool] | None = None
    ) -> None:
        """
        Add method record handler.

        Parameters
        ----------
        method : Handler method. The parameter is the `LogRecord` instance.
        level : Handler level.
        filter\\_ : Filter method. The parameter is the `LogRecord` instance, return is `bool`.
        """

        # Add queue out.
        _, queue = self.add_queue(level=level, filter_=filter_)


        # Define.
        @wrap_thread
        def execute() -> None:
            """
            Execute method.
            """

            while True:
                record = queue.get()
                method(record)


        # Execute.
        execute()


    def delete_handler(
        self,
        handler: Handler
    ) -> None:
        """
        Delete record handler.

        Parameters
        ----------
        handler : Handler.
        """

        # Delete.
        self.logger.removeHandler(handler)


    def clear_handler(self) -> None:
        """
        Delete all record handler.
        """

        # Delete.
        for handle in self.logger.handlers:
            self.logger.removeHandler(handle)


    def catch_print(self, printing: bool = True) -> None:
        """
        Catch print to log.

        Parameters
        ----------
        printing : Whether to still print.
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

            # Log.
            if __s not in ('\n', ' ', '[0m'):
                self(__s, level=self.INFO, catch=False)

            # Print.
            if printing:
                return __s


        # Modify.
        modify_print(preprocess)

        # Update status.
        self.print_replaced = True


    def reset_print(self) -> None:
        """
        Reset log replace print.
        """

        # Break.
        if not self.print_replaced:
            return

        # Reset.
        reset_print()

        # Update status.
        self.print_replaced = False


    def log(
        self,
        *messages: Any,
        level: int | None = None,
        catch: bool = True,
        **params: Any
    ) -> None:
        """
        Record log.

        Parameters
        ----------
        messages : Record content.
        level : Record level.
            - `None`: Automatic judge.
                `in 'except' syntax`: Use 'ERROR' level.
                `Other`: Use 'INFO' level.
            - `int`: Use this value.
        catch : Whether catch and append exception stack.
        params : Record Format parameters.
        """

        # Handle parameter.
        if (
            level is None
            or catch
        ):
            exc_text, exc, _ = catch_exc()

        ## Messages.
        messages_len = len(messages)
        if messages_len == 0:
            messages = [None]

        ## Level.
        if level is None:
            if exc is None:
                level = self.INFO
            else:
                level = self.ERROR

        ## Messages.
        messages = '\n'.join(
            [
                to_text(message, self.default_format_width)
                for message in messages
            ]
        )
        if '\n' in messages:
            messages = '\n' + messages

        ### Exception.
        if (
            catch
            and exc is not None
        ):
            messages = '%s\n%s' % (
                messages,
                exc_text
            )

        # Record.
        self.logger.log(level, messages, extra=params)


    def debug(
        self,
        *messages: Any,
        **params: Any
    ) -> None:
        """
        Record `debug` level log.

        Parameters
        ----------
        messages : Record content.
        params : Record Format parameters.
        """

        # Record.
        self.log(*messages, level=self.DEBUG, **params)


    def info(
        self,
        *messages: Any,
        **params: Any
    ) -> None:
        """
        Record `info` level log.

        Parameters
        ----------
        messages : Record content.
        params : Record Format parameters.
        """

        # Record.
        self.log(*messages, level=self.INFO, **params)


    def warning(
        self,
        *messages: Any,
        **params: Any
    ) -> None:
        """
        Record `warning` level log.

        Parameters
        ----------
        messages : Record content.
        params : Record Format parameters.
        """

        # Record.
        self.log(*messages, level=self.WARNING, **params)


    def error(
        self,
        *messages: Any,
        **params: Any
    ) -> None:
        """
        Record `error` level log.

        Parameters
        ----------
        messages : Record content.
        params : Record Format parameters.
        """

        # Record.
        self.log(*messages, level=self.ERROR, **params)


    def critical(
        self,
        *messages: Any,
        **params: Any
    ) -> None:
        """
        Record `critical` level log.

        Parameters
        ----------
        messages : Record content.
        params : Record Format parameters.
        """

        # Record.
        self.log(*messages, level=self.CRITICAL, **params)


    def pause(self) -> None:
        """
        Pause record.
        """

        # Set level.
        self.logger.setLevel(100)

        # Update status.
        self.stoped = True


    def resume(self) -> None:
        """
        Resume record.
        """

        # Set level.
        self.logger.setLevel(self.DEBUG)

        # Update status.
        self.stoped = False


    def __del__(self) -> None:
        """
        Delete handle.
        """

        # Reset.
        self.reset_print()

        # Delete handler.
        self.clear_handler()


    __call__ = log


class Mark(Base):
    """
    Mark object type.
    Based on object hash value.
    """


    def __init__(self) -> None:
        """
        Build instance attributes.
        """

        # Build.
        self.data: dict[Hashable, set[int]] = {}


    def mark(self, obj: Any, group: Hashable = null) -> int:
        """
        Mark object.

        Parameters
        ----------
        obj : Object.
        group : Group index.

        Returns
        -------
        Object memory ID.
        """

        # Handle parameter.
        obj_id = hash(obj)
        group_set = self.data.setdefault(group, set())

        # Mark.
        group_set.add(obj_id)

        return obj_id


    def remove(self, obj: Any, group: Hashable = null) -> None:
        """
        Whether marked.

        Parameters
        ----------
        obj : Object.
        group : Group index.

        Returns
        -------
        Judgment result.
        """

        # Handle parameter.
        obj_id = hash(obj)
        group_set = self.data.setdefault(group, set())

        # Remove.
        group_set.remove(obj_id)


    def remove_group(self, group: Hashable) -> None:
        """
        Whether marked.

        Parameters
        ----------
        group : Group index.

        Returns
        -------
        Judgment result.
        """

        # Remove.
        del self.data[group]


    def is_marked(self, obj: Any, group: Hashable = null) -> bool:
        """
        Whether marked.

        Parameters
        ----------
        obj : Object.
        group : Group index.

        Returns
        -------
        Judgment result.
        """

        # Handle parameter.
        obj_id = hash(obj)
        group_set = self.data.setdefault(group, set())

        # Judge.
        result = obj_id in group_set

        return result


    __call__ = mark

    __contains__ = is_marked
