# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@Time    : 2023-12-06 16:17:04
@Author  : Rey
@Contact : reyxbo@163.com
@Explain : DLL file code methods.
"""


import ctypes
from ctypes.wintypes import (
    HANDLE,
    LPVOID,
    DWORD,
    BOOL,
    LPCVOID,
    HMODULE,
    LPCSTR,
    LPDWORD
)
import enum


def LPVOID_errcheck(result, func, args):
    if not result:
        raise ctypes.WinError()
    return result


def Win32API_errcheck(result, func, args):
    if not result:
        raise ctypes.WinError()


class SECURITY_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ('nLength', DWORD),
        ('lpSecurityDescriptor', LPVOID),
        ('bInheritHandle', BOOL)
    ]


INFINITE = ctypes.c_uint(-1)
SIZE_T = ctypes.c_size_t
FARPROC = ctypes.CFUNCTYPE(ctypes.c_int, LPVOID)
LPTHREAD_START_ROUTINE = ctypes.CFUNCTYPE(DWORD, LPVOID)

VirtualAllocEx = ctypes.windll.kernel32.VirtualAllocEx
VirtualAllocEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD, DWORD]
VirtualAllocEx.restype = LPVOID
VirtualAllocEx.errcheck = LPVOID_errcheck

VirtualFreeEx = ctypes.windll.kernel32.VirtualFreeEx
VirtualFreeEx.argtypes = [HANDLE, LPVOID, SIZE_T, DWORD]
VirtualFreeEx.restype = BOOL
VirtualFreeEx.errcheck = Win32API_errcheck

WriteProcessMemory = ctypes.windll.kernel32.WriteProcessMemory
WriteProcessMemory.argtypes = [HANDLE, LPVOID, LPCVOID, SIZE_T, ctypes.POINTER(SIZE_T)]
WriteProcessMemory.restype = BOOL
WriteProcessMemory.errcheck = Win32API_errcheck

GetProcAddress = ctypes.windll.kernel32.GetProcAddress
GetProcAddress.argtypes = [HMODULE, LPCSTR]
GetProcAddress.restype = FARPROC

OpenProcess = ctypes.windll.kernel32.OpenProcess
OpenProcess.argtypes = [DWORD, BOOL, DWORD]
OpenProcess.restype = HANDLE
OpenProcess.errcheck = LPVOID_errcheck

GetModuleHandleA = ctypes.windll.kernel32.GetModuleHandleA
GetModuleHandleA.argtypes = [LPCSTR]
GetModuleHandleA.restype = HMODULE
GetModuleHandleA.errcheck = LPVOID_errcheck

CloseHandle = ctypes.windll.kernel32.CloseHandle
CloseHandle.argtypes = [HANDLE]
CloseHandle.restype = BOOL
CloseHandle.errcheck = Win32API_errcheck

LPSECURITY_ATTRIBUTES = ctypes.POINTER(SECURITY_ATTRIBUTES)
CreateRemoteThread = ctypes.windll.kernel32.CreateRemoteThread
CreateRemoteThread.argtypes = [HANDLE, LPSECURITY_ATTRIBUTES, SIZE_T, LPTHREAD_START_ROUTINE, LPVOID, DWORD, LPDWORD]
CreateRemoteThread.restype = HANDLE
CreateRemoteThread.errcheck = LPVOID_errcheck

WaitForSingleObject = ctypes.windll.kernel32.WaitForSingleObject
WaitForSingleObject.argtypes = [HANDLE, DWORD]
WaitForSingleObject.restype = DWORD

GetExitCodeThread = ctypes.windll.kernel32.GetExitCodeThread
GetExitCodeThread.argtypes = [HANDLE, LPDWORD]
GetExitCodeThread.restype = BOOL
GetExitCodeThread.errcheck = Win32API_errcheck


class Process(enum.IntFlag):
    CREATE_PROCESS = 0x0080
    CREATE_THREAD = 0x0002
    DUP_HANDLE = 0x0002
    QUERY_INFORMATION = 0x0400
    QUERY_LIMITED_INFORMATION = 0x1000
    SET_INFORMATION = 0x0200
    SET_QUOTA = 0x0100
    SUSPEND_RESUME = 0x0800
    TERMINATE = 0x0001
    VM_OPERATION = 0x0008
    VM_READ = 0x0010
    VM_WRITE = 0x0020
    SYNCHRONIZE = 0x00100000


class AllocationType(enum.IntFlag):
    COMMIT = 0x00001000
    RESERVE = 0x00002000
    RESET = 0x00080000
    RESET_UNDO = 0x1000000
    LARGE_PAGES = 0x20000000
    PHYSICAL = 0x00400000
    TOP_DOWN = 0x00100000


class FreeType(enum.IntFlag):
    COALESCE_PLACEHOLDERS = 0x1
    PRESERVE_PLACEHOLDER = 0x2
    DECOMMIT = 0x4000
    RELEASE = 0x8000


class PageProtection(enum.IntFlag):
    EXECUTE = 0x10
    EXECUTE_READ = 0x20
    EXECUTE_READWRITE = 0x40
    EXECUTE_WRITECOPY = 0x80
    NOACCESS = 0x01
    READONLY = 0x02
    READWRITE = 0x04
    WRITECOPY = 0x08
    TARGETS_INVALID = 0x40000000
    TARGETS_NO_UPDATE = 0x40000000
    GUARD = 0x100
    NOCACHE = 0x200
    WRITECOMBINE = 0x400


def InjectDLL(
    target_pid,
    filename_dll
):

    target_handle = OpenProcess(
        Process.CREATE_THREAD | Process.VM_OPERATION | Process.VM_READ | Process.VM_WRITE,
        False,
        target_pid
    )

    dll_path_addr = VirtualAllocEx(
        target_handle,
        None,
        len(filename_dll),
        AllocationType.COMMIT | AllocationType.RESERVE,
        PageProtection.READWRITE
    )

    WriteProcessMemory(
        target_handle,
        dll_path_addr,
        filename_dll,
        len(filename_dll),
        None
    )

    module_handle = GetModuleHandleA(b'Kernel32')
    target_LoadLibraryA = GetProcAddress(module_handle, b'LoadLibraryA')

    thread_handle = CreateRemoteThread(
        target_handle,
        None,
        0,
        ctypes.cast(
            target_LoadLibraryA,
            LPTHREAD_START_ROUTINE
        ),
        dll_path_addr,
        0,
        None
    )

    WaitForSingleObject(thread_handle, INFINITE)

    exit_code = DWORD()
    GetExitCodeThread(thread_handle, ctypes.byref(exit_code))

    try:
        CloseHandle(thread_handle)
        VirtualFreeEx(thread_handle, dll_path_addr, 0, FreeType.RELEASE)
        CloseHandle(target_handle)
    except OSError:
        pass
