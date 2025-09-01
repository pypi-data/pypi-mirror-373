# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2022-12-05 14:09:42
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : Interpreter system methods.
"""


from typing import Any, TypedDict, Literal, overload
from collections.abc import Iterable, Sequence
from sys import path as sys_path, modules as sys_modules
from os import getpid as os_getpid
from os.path import abspath as os_abspath
from psutil import (
    boot_time as psutil_boot_time,
    cpu_count as psutil_cpu_count,
    cpu_freq as psutil_cpu_freq,
    cpu_percent as psutil_cpu_percent,
    virtual_memory as psutil_virtual_memory,
    disk_partitions as psutil_disk_partitions,
    disk_usage as psutil_disk_usage,
    pids as psutil_pids,
    net_connections as psutil_net_connections,
    users as psutil_users,
    net_connections as psutil_net_connections,
    process_iter as psutil_process_iter,
    pid_exists as psutil_pid_exists,
    Process
)
from subprocess import Popen, PIPE
from pymem import Pymem
from argparse import ArgumentParser
from datetime import datetime
from webbrowser import open as webbrowser_open
from tkinter.messagebox import (
    showinfo as tkinter_showinfo,
    showwarning as tkinter_showwarning,
    showerror as tkinter_showerror,
    askyesno as tkinter_askyesno,
    askyesnocancel as tkinter_askyesnocancel,
    askokcancel as tkinter_askokcancel,
    askretrycancel as tkinter_askretrycancel
)
from tkinter.filedialog import (
    askopenfilename as tkinter_askopenfilename,
    askopenfilenames as tkinter_askopenfilenames,
    asksaveasfilename as tkinter_asksaveasfilename,
    askdirectory as tkinter_askdirectory
)

from .rbase import Base, ConfigMeta, throw, get_varname


__all__ = (
    'ConfigSystem',
    'add_env_path',
    'reset_env_path',
    'del_modules',
    'run_cmd',
    'get_cmd_var',
    'get_computer_info',
    'get_network_table',
    'get_process_table',
    'search_process',
    'kill_process',
    'pause_process',
    'resume_process',
    'get_idle_port',
    'memory_read',
    'memory_write',
    'open_browser',
    'popup_message',
    'popup_ask',
    'popup_select'
)


LoginUsers = TypedDict('LoginUsers', {'time': datetime, 'name': str, 'host': str})
ComputerInfo = TypedDict(
    'ComputerInfo',
    {
        'boot_time': float,
        'cpu_count': int,
        'cpu_frequency': int,
        'cpu_percent': float,
        'memory_total': float,
        'memory_percent': float,
        'disk_total': float,
        'disk_percent': float,
        'process_count': int,
        'network_count': int,
        'login_users':LoginUsers
    }
)
NetWorkInfo = TypedDict(
    'NetWorkTable',
    {
        'family': str | None,
        'socket': str | None,
        'local_ip': str,
        'local_port': int,
        'remote_ip': str | None,
        'remote_port': int | None,
        'status': str | None,
        'pid': int | None
    }
)
ProcessInfo = TypedDict('ProcessInfo', {'create_time': datetime, 'id': int, 'name': str, 'ports': list[int] | None})


class ConfigSystem(Base, metaclass=ConfigMeta):
    """
    Config system type.
    """

    # Added environment path.
    _added_env_paths: list[str] = []


def add_env_path(path: str) -> list[str]:
    """
    Add environment variable path.

    Parameters
    ----------
    path : Path, can be a relative path.

    Returns
    -------
    Added environment variables list.
    """

    # Absolute path.
    abs_path = os_abspath(path)

    # Add.
    ConfigSystem._added_env_paths.append(abs_path)
    sys_path.append(abs_path)

    return sys_path


def reset_env_path() -> None:
    """
    Reset environment variable path.
    """

    # Delete.
    for path in ConfigSystem._added_env_paths:
        sys_path.remove(path)
    ConfigSystem._added_env_paths = []


def del_modules(path: str) -> list[str]:
    """
    Delete record of modules import dictionary.

    Parameters
    ----------
    path : Module path, use regular match.

    Returns
    -------
    Deleted modules dictionary.
    """

    # Import.
    from .rre import search

    # Set parameter.
    deleted_dict = {}
    module_keys = tuple(sys_modules)

    # Delete.
    for key in module_keys:
        module = sys_modules.get(key)

        ## Filter non file module.
        if (
            not hasattr(module, '__file__')
            or module.__file__ is None
        ):
            continue

        ## Match.
        result = search(path, module.__file__)
        if result is None:
            continue

        ## Take out.
        deleted_dict[key] = sys_modules.pop(key)

    return deleted_dict


@overload
def run_cmd(command: str | Iterable[str], read: Literal[False] = False) -> None: ...

@overload
def run_cmd(command: str | Iterable[str], read: Literal[True]) -> str: ...

def run_cmd(command: str | Iterable[str], read: bool = False) -> str | None:
    """
    Execute DOS command.

    Parameters
    ----------
    command : DOS command.
        - `str`: Use this command.
        - `Iterable[str]`: Join strings with space as command.
            When space in the string, automatic add quotation mark (e.g., ['echo', 'a b'] -> 'echo 'a b'').
    read : Whether read command output, will block.

    Returns
    -------
    Command standard output or None.
    """

    # Execute.
    popen = Popen(command, stdout=PIPE, stderr=PIPE, shell=True)

    # Output.
    if read:
        stderr_bytes: bytes = popen.stderr.read()
        stdout_bytes: bytes = popen.stdout.read()
        output_bytes = stdout_bytes + stderr_bytes
        output = output_bytes.decode('GBK')

        return output


def get_cmd_var(*vars: Any) -> list[Any]:
    """
    Get DOS command input arguments.
    Use DOS command `python file --help` to view help information.

    Parameters
    ----------
    vars : Variables.

    Returns
    -------
    Value of variables.

    Examples
    --------
    >>> var1 = 1
    >>> var2 = 2
    >>> var3 = 3
    >>> var1, var2, var3 = run_cmd(var1, var2, var3)
    >>> print(var1, var2, var3)
    >>> # Use DOS command 'python file.py 10 --var2 20 21'
    10 [20, 21] 3
    """

    # Handle parameter.
    vars_name: list[str] = get_varname('vars')
    vars_info = tuple(zip(vars_name, vars))

    # Set DOS command.
    usage = 'input arguments to variables'
    parser = ArgumentParser(usage=usage)
    for name, value in vars_info:
        if value is None:
            var_type = str
            var_help = None
        else:
            var_type = type(value)
            var_help = str(type(value))

        ## Position argument.
        parser.add_argument(
            name,
            nargs='?',
            type=var_type,
            help=var_help
        )

        ## Keyword argument.
        kw_name = '--' + name
        parser.add_argument(
            kw_name,
            nargs='*',
            type=var_type,
            help=var_help,
            metavar='value',
            dest=kw_name
        )

    # Get argument.
    namespace = parser.parse_args()
    values = []
    for name, value in vars_info:
        kw_name = '--' + name

        ## Position argument.
        dos_value = getattr(namespace, name)
        if dos_value is not None:
            values.append(dos_value)
            continue

        ## Keyword argument.
        dos_value = getattr(namespace, kw_name)
        if type(dos_value) == list:
            value_len = len(dos_value)
            match value_len:
                case 0:
                    dos_value = None
                case 1:
                    dos_value = dos_value[0]
            values.append(dos_value)
            continue

        values.append(value)

    return values


def get_computer_info() -> ComputerInfo:
    """
    Get computer information.

    Returns
    -------
    Computer information dictionary.
        - `Key 'boot_time'`: Computer boot time.
        - `Key 'cpu_count'`: Computer logical CPU count.
        - `Key 'cpu_frequency'`: Computer current CPU frequency.
        - `Key 'cpu_percent'`: Computer CPU usage percent.
        - `Key 'memory_total'`: Computer memory total gigabyte.
        - `Key 'memory_percent'`: Computer memory usage percent.
        - `Key 'disk_total'`: Computer disk total gigabyte.
        - `Key 'disk_percent'`: Computer disk usage percent.
        - `Key 'process_count'`: Computer process count.
        - `Key 'network_count'`: Computer network count.
        - `Key 'login_users'`: Computer login users information.
    """

    # Set parameter.
    info = {}

    # Get.

    ## Boot time.
    boot_time = psutil_boot_time()
    info['boot_time'] = datetime.fromtimestamp(
        boot_time
    ).strftime(
        '%Y-%m-%d %H:%M:%S'
    )

    ## CPU.
    info['cpu_count'] = psutil_cpu_count()
    info['cpu_frequency'] = int(psutil_cpu_freq().current)
    info['cpu_percent'] = round(psutil_cpu_percent(), 1)

    ## Memory.
    memory_info = psutil_virtual_memory()
    info['memory_total'] = round(memory_info.total / 1024 / 1024 / 1024, 1)
    info['memory_percent'] = round(memory_info.percent, 1)

    ## Disk.
    disk_total = []
    disk_used = []
    partitions_info = psutil_disk_partitions()
    for partition_info in partitions_info:
        try:
            partition_usage_info = psutil_disk_usage(partition_info.device)
        except PermissionError:
            continue
        disk_total.append(partition_usage_info.total)
        disk_used.append(partition_usage_info.used)
    disk_total = sum(disk_total)
    disk_used = sum(disk_used)
    info['disk_total'] = round(disk_total / 1024 / 1024 / 1024, 1)
    info['disk_percent'] = round(disk_used / disk_total * 100, 1)

    ## Process.
    pids = psutil_pids()
    info['process_count'] = len(pids)

    ## Network.
    net_info = psutil_net_connections()
    info['network_count'] = len(net_info)

    ## User.
    users_info = psutil_users()
    info['login_users'] = [
        {
            'time': datetime.fromtimestamp(
                user_info.started
            ).strftime(
                '%Y-%m-%d %H:%M:%S'
            ),
            'name': user_info.name,
            'host': user_info.host
        }
        for user_info in users_info
    ]
    sort_func = lambda row: row['time']
    info['login_users'].sort(key=sort_func, reverse=True)

    return info


def get_network_table() -> list[NetWorkInfo]:
    """
    Get network information table.

    Returns
    -------
    Network information table.
    """

    # Get.
    connections = psutil_net_connections('all')
    table = [
        {
            'family': (
                'IPv4'
                if connection.family.name == 'AF_INET'
                else 'IPv6'
                if connection.family.name == 'AF_INET6'
                else None
            ),
            'socket': (
                'TCP'
                if connection.type.name == 'SOCK_STREAM'
                else 'UDP'
                if connection.type.name == 'SOCK_DGRAM'
                else None
            ),
            'local_ip': connection.laddr.ip,
            'local_port': connection.laddr.port,
            'remote_ip': (
                None
                if connection.raddr == ()
                else connection.raddr.ip
            ),
            'remote_port': (
                None
                if connection.raddr == ()
                else connection.raddr.port
            ),
            'status': (
                None
                if connection.status == 'NONE'
                else connection.status.lower()
            ),
            'pid': connection.pid
        }
        for connection in connections
    ]

    # Sort.
    sort_func = lambda row: row['local_port']
    table.sort(key=sort_func)
    sort_func = lambda row: row['local_ip']
    table.sort(key=sort_func)

    return table


def get_process_table() -> list[ProcessInfo]:
    """
    Get process information table.

    Returns
    -------
    Process information table.
    """

    # Get.
    process_iter = psutil_process_iter()
    table = []
    for process in process_iter:
        info = {}
        with process.oneshot():
            info['create_time'] = datetime.fromtimestamp(
                process.create_time()
            ).strftime(
                '%Y-%m-%d %H:%M:%S'
            )
            info['id'] = process.pid
            info['name'] = process.name()
            connections = process.connections()
            if connections == []:
                info['ports'] = None
            else:
                info['ports'] = [
                    connection.laddr.port
                    for connection in connections
                ]
            table.append(info)

    # Sort.
    sort_func = lambda row: row['id']
    table.sort(key=sort_func)
    sort_func = lambda row: row['create_time']
    table.sort(key=sort_func)

    return table


def search_process(
    id_: int | Sequence[int] | None = None,
    name: str | Sequence[str] | None = None,
    port: str | int | Sequence[str | int] | None = None,
) -> list[Process]:
    """
    Search process by ID or name or port.

    Parameters
    ----------
    id\\_ : Search condition, a value or sequence of process ID.
    name : Search condition, a value or sequence of process name.
    port : Search condition, a value or sequence of process port.

    Returns
    -------
    List of process instances that match any condition.
    """

    # Handle parameter.
    match id_:
        case None:
            ids = []
        case int():
            ids = [id_]
        case _:
            ids = id_
    match name:
        case None:
            names = []
        case str():
            names = [name]
        case _:
            names = name
    match port:
        case None:
            ports = []
        case str() | int():
            ports = [port]
        case _:
            ports = port
    ports = [
        int(port)
        for port in ports
    ]

    # Search.
    processes = []
    if (
        names != []
        or ports != []
    ):
        table = get_process_table()
    else:
        table = []

    ## ID.
    for id__ in ids:
        if psutil_pid_exists(id__):
            process = Process(id__)
            processes.append(process)

    ## Name.
    for info in table:
        if (
            info['name'] in names
            and psutil_pid_exists(info['id'])
        ):
            process = Process(info['id'])
            processes.append(process)

    ## Port.
    for info in table:
        for port in ports:
            if (
                info['ports'] is not None
                and port in info['ports']
                and psutil_pid_exists(info['id'])
            ):
                process = Process(info['id'])
                processes.append(process)
                break

    return processes


def kill_process(
    id_: int | Sequence[int] | None = None,
    name: str | Sequence[str] | None = None,
    port: str | int | Sequence[str | int] | None = None,
) -> list[Process]:
    """
    Search and kill process by ID or name or port.

    Parameters
    ----------
    id\\_ : Search condition, a value or sequence of process ID.
    name : Search condition, a value or sequence of process name.
    port : Search condition, a value or sequence of process port.

    Returns
    -------
    List of process instances that match any condition.
    """

    # Handle parameter.
    self_pid = os_getpid()

    # Search.
    processes = search_process(id_, name, port)

    # Kill.
    for process in processes:
        with process.oneshot():

            ## Filter self process.
            if process.pid == self_pid:
                continue

            process.kill()

    return processes


def pause_process(
    id_: int | Sequence[int] | None = None,
    name: str | Sequence[str] | None = None,
    port: str | int | Sequence[str | int] | None = None,
) -> list[Process]:
    """
    Search and pause process by ID or name or port.

    Parameters
    ----------
    id\\_ : Search condition, a value or sequence of process ID.
    name : Search condition, a value or sequence of process name.
    port : Search condition, a value or sequence of process port.

    Returns
    -------
    List of process instances that match any condition.
    """

    # Handle parameter.
    self_pid = os_getpid()

    # Search.
    processes = search_process(id_, name, port)

    # Pause.
    for process in processes:
        with process.oneshot():

            ## Filter self process.
            if process.pid == self_pid:
                continue

            process.suspend()

    return processes


def resume_process(
    id_: int | Sequence[int] | None = None,
    name: str | Sequence[str] | None = None,
    port: str | int | Sequence[str | int] | None = None,
) -> list[Process]:
    """
    Search and resume process by ID or name or port.

    Parameters
    ----------
    id\\_ : Search condition, a value or sequence of process ID.
    name : Search condition, a value or sequence of process name.
    port : Search condition, a value or sequence of process port.

    Returns
    -------
    List of process instances that match any condition.
    """

    # Search.
    processes = search_process(id_, name, port)

    # Resume.
    for process in processes:
        with process.oneshot():
            process.resume()

    return processes


def get_idle_port(min: int = 49152) -> int:
    """
    Judge and get an idle port number.

    Parameters
    ----------
    min : Minimum port number.

    Returns
    -------
    Idle port number.
    """

    # Handle parameter.
    network_table = get_network_table()
    ports = [
        info['local_port']
        for info in network_table
    ]

    # Judge.
    while True:
        if min in ports:
            min += 1
        else:
            return min


def memory_read(
    process: int | str,
    dll: str,
    offset: int
) -> int:
    """
    Read memory value.

    Parameters
    ----------
    process : Process ID or name.
    dll : DLL file name.
    offset : Memory address offset.

    Returns
    -------
    Memory value.
    """

    # Get DLL address.
    pymem = Pymem(process)
    for module in pymem.list_modules():
        if module.name == dll:
            dll_address: int = module.lpBaseOfDll
            break

    ## Throw exception.
    else:
        throw(AssertionError, dll_address)

    # Get memory address.
    memory_address = dll_address + offset

    # Read.
    value = pymem.read_int(memory_address)

    return value


def memory_write(
    process: int | str,
    dll: str,
    offset: int,
    value: int
) -> None:
    """
    Write memory value.

    Parameters
    ----------
    process : Process ID or name.
    dll : DLL file name.
    offset : Memory address offset.
    value : Memory value.
    """

    # Get DLL address.
    pymem = Pymem(process)
    for module in pymem.list_modules():
        if module.name == dll:
            dll_address: int = module.lpBaseOfDll
            break

    # Get memory address.
    memory_address = dll_address + offset

    # Read.
    pymem.write_int(memory_address, value)


def open_browser(url: str) -> bool:
    """
    Open browser and URL.

    Parameters
    ----------
    url : URL.

    Returns
    -------
    Is it successful.
    """

    # Open.
    succeeded = webbrowser_open(url)

    return succeeded


def popup_message(
    style: Literal['info', 'warn', 'error'] = 'info',
    message: str | None = None,
    title: str | None = None
) -> None:
    """
    Pop up system message box.

    Parameters
    ----------
    style : Message box style.
        - `Literal['info']`: Information box.
        - `Literal['warn']`: Warning box.
        - `Literal['error']`: Error box.
    message : Message box content.
    title : Message box title.
    """

    # Pop up.
    match style:

        ## Information.
        case 'info':
            method = tkinter_showinfo

        ## Warning.
        case 'warn':
            method = tkinter_showwarning

        ## Error.
        case 'error':
            method = tkinter_showerror

    method(title, message)


@overload
def popup_ask(
    style: Literal['yes_no', 'ok_cancel', 'retry_cancel'] = 'yes_no',
    message: str | None = None,
    title: str | None = None
) -> bool: ...

@overload
def popup_ask(
    style: Literal['yes_no_cancel'],
    message: str | None = None,
    title: str | None = None
) -> bool | None: ...

def popup_ask(
    style: Literal['yes_no', 'ok_cancel', 'retry_cancel', 'yes_no_cancel'] = 'yes_no',
    message: str | None = None,
    title: str | None = None
) -> bool | None:
    """
    Pop up system ask box.

    Parameters
    ----------
    style : Ask box style.
        - `Literal['yes_no']`: Buttons are `yes` and `no`.
        - `Literal['ok_cancel']`: Buttons are `ok` and `cancel`.
        - `Literal['retry_cancel']`: Buttons are `retry` and `cancel`.
        - `Literal['yes_no_cancel']`: Buttons are `yes` and `no` and `cancel`.
    message : Ask box content.
    title : Ask box title.

    Returns
    -------
    Ask result.
    """

    # Pop up.
    match style:

        ## Yes and no.
        case 'yes_no':
            method = tkinter_askyesno

        ## Ok and cancel.
        case 'ok_cancel':
            method = tkinter_askokcancel

        ## Retry and cancel.
        case 'retry_cancel':
            method = tkinter_askretrycancel

        ## Yes and no and cancel.
        case 'yes_no_cancel':
            method = tkinter_askyesnocancel

    method(title, message)


@overload
def popup_select(
    style: Literal['file', 'save'] = 'file',
    title : str | None = None,
    init_folder : str | None = None,
    init_file : str | None = None,
    filter_file : list[tuple[str, str | list[str]]] | None = None
) -> str | None: ...

@overload
def popup_select(
    style: Literal['files'],
    title : str | None = None,
    init_folder : str | None = None,
    init_file : str | None = None,
    filter_file : list[tuple[str, str | list[str]]] | None = None
) -> tuple[str, ...] | None: ...

@overload
def popup_select(
    style: Literal['folder'],
    title : str | None = None,
    init_folder : str | None = None
) -> str | None: ...

def popup_select(
    style: Literal['file', 'files', 'folder', 'save'] = 'file',
    title : str | None = None,
    init_folder : str | None = None,
    init_file : str | None = None,
    filter_file : list[tuple[str, str | list[str]]] | None = None
) -> str | tuple[str, ...] | None:
    """
    Pop up system select box.

    Parameters
    ----------
    style : Select box style.
        - `Literal['file']`: Select file box.
        - `Literal['files']`: Select multiple files box.
        - `Literal['folder']`: Select folder box.
        - `Literal['save']`: Select save file box.
    title : Select box title.
    init_folder : Initial folder path.
    init_file : Initial file name.
    filter_file : Filter file.
        - `tuple[str, str]`: Filter name and filter pattern.
        - `tuple[str, list[str]]`: Filter name and multiple filter patterns (or).

    Returns
    -------
    File or folder path.
        - `None`: Close select box.
    """

    # Pop up.
    kwargs = {
        'filetypes': filter_file,
        'initialdir': init_folder,
        'initialfile': init_file,
        'title': title
    }
    kwargs = {
        key: value
        for key, value in kwargs.items()
        if value is not None
    }
    match style:

        ## File.
        case 'file':
            method = tkinter_askopenfilename

        ## Files.
        case 'files':
            method = tkinter_askopenfilenames

        ## Folder.
        case 'folder':
            method = tkinter_askdirectory

        ## Save.
        case 'save':
            method = tkinter_asksaveasfilename

    path = method(**kwargs)
    path = path or None

    return path
