## SPDX-License-Identifier: BSD-2-Clause
##
## Copyright 2020-2025 Inria & Université de Bordeaux
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions
## are met:
##
## 1. Redistributions of source code must retain the above copyright
## notice, this list of conditions and the following disclaimer.
##
## 2. Redistributions in binary form must reproduce the above
## copyright notice, this list of conditions and the following
## disclaimer in the documentation and/or other materials provided
## with the distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
## CONTRIBUTORS “AS IS” AND ANY EXPRESS OR IMPLIED WARRANTIES,
## INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
## MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS
## BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
## EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
## TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
## DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
## ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
## TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
## THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
## SUCH DAMAGE.
##

import os
from collections.abc import Iterable
import ctypes
from ctypes.util import find_library

import numpy as np

from .find_libs import _scotchpy_err_lib, _scotch_lib, _ptscotch_lib, _libptscotch_mpi4py_lib
from .exception import LibraryError
from .exception import last_error_msg as _last_error_msg

# Set up the call in case of error
def print_scotch(string):
    _last_error_msg.append("Inside Python %s " % string.decode("utf-8"))

lib_call_back = ctypes.PyDLL(_scotchpy_err_lib)

CallBackType = ctypes.CFUNCTYPE(None, ctypes.c_char_p)

setCallBack = lib_call_back.setCallBack
setCallBack.argtype = CallBackType
setCallBack.restype = None

callback = CallBackType(print_scotch)
setCallBack(callback)

ctypes.CDLL(_scotchpy_err_lib, mode=ctypes.RTLD_GLOBAL)

libscotch = ctypes.CDLL(_scotch_lib)

# When using PT-Scotch
if _ptscotch_lib:
    libptscotch = ctypes.CDLL(_ptscotch_lib)
    if _libptscotch_mpi4py_lib:
        libhelper = ctypes.CDLL(_libptscotch_mpi4py_lib)
    else:
        raise Exception("the extension liptscotch_mpi4py is not found")
        print(f"Warning: MPI helper not found. PT-ScotchPy routines will not work.")

# To call classic C functions such as fopen()
libc = ctypes.CDLL(find_library("c"))

class FILE(ctypes.Structure):
    pass

FILE_p = ctypes.POINTER(FILE)
libc.fdopen.argtypes = ctypes.c_int, ctypes.c_char_p
libc.fdopen.restype = FILE_p

libc.fclose.argtype = FILE_p
libc.fclose.restype = ctypes.c_int

libc.dup.argtype = ctypes.c_int
libc.dup.restype = ctypes.c_int


def num_sizeof():
    # num_sizeof() is libscotch.SCOTCH_numSizeof()
    return libscotch.SCOTCH_numSizeof()

proper_int_size = 8 * num_sizeof()  # 32 or 64
proper_int = getattr(ctypes, "c_int" + str(proper_int_size))


import warnings
if (np.arange(1).dtype.name[3:] != str(proper_int_size)):
    warnings.warn("Warning: (proper_int_size) {} != {} (dtype default value) ".format(np.zeros(1).dtype.name[5:], str(proper_int_size)))

# When properly implemented as library-wide constants in libscotch, define as:
# COARSENNONE = ctypes.c_long.in_dll(_libscotch, "COARSENNONE").value
# and decomment _libscotch import
COARSENNONE = 0x0000
COARSENFOLD = 0x0100
COARSENFOLDDUP = 0x0300
COARSENNOMERGE = 0x4000


def version(as_dict=False):
    """
    This routine returns the version number, release number and patch level of the SCOTCH library.
    """
    vers, rela, patc = proper_int(), proper_int(), proper_int()
    libscotch.SCOTCH_version(ctypes.byref(vers), ctypes.byref(rela), ctypes.byref(patc))
    rv = (vers.value, rela.value, patc.value)
    if as_dict:
        rv = dict(zip(("versnbr", "relanbr", "patcnbr"), rv))
    return rv


def mem_cur():
    """
    This routine returns the current memory usage.
    """
    return libscotch.SCOTCH_memCur()


def mem_max():
    """
    This routine returns the maximum memory usage.
    """
    return libscotch.SCOTCH_memMax()


def random_proc(procnum):
    """
    This routine sets to procnum the number of the process that will be used to generate random numbers.
    """
    libscotch.SCOTCH_randomProc(proper_int(procnum))


def random_reset():
    """
    This routine resets the seed of the global pseudo-random number generator used by default by the SCOTCH library.
    """
    libscotch.SCOTCH_randomReset()


def random_seed(seedval):
    """
    This routine sets the seed of the global pseudo-random number generator used by default by the SCOTCH library.
    """
    libscotch.SCOTCH_randomSeed(proper_int(seedval))


def random_val(randmax):
    """
    This routine returns a pseudo-random integer value between 0 and randmax-1.
    """
    return libscotch.SCOTCH_randomVal(proper_int(randmax))


def properly_format(ite):
    """
    Turns an Iterable in a numpy array whose dtype is proper_int.
    If something other than None or an Iterable is given, it is alleged to be a
    ctypes array and returned as is.
    """
    if ite is None:
        return None
    if not isinstance(ite, Iterable):
        return ite
    # np.array returns an instance of np.ndarray
    # copy=False creates a new object only if necessary
    return np.asarray(ite, dtype=proper_int)
    # turns floats in neat proper_ints, and raises an error if overflows occur


def array_to_pointer(arr):
    """
    Turns an np.ndarray or any iterable into a ctypes pointer.
    If something else is given (None or a ctypes array for example),
    it's returned as is.
    """
    if isinstance(arr, (np.ndarray, Iterable)):
        return properly_format(arr).ctypes.data_as(ctypes.POINTER(proper_int))
    return arr


def array_to_c_array(arr, length=None):
    """
    Turns any iterable into a ctypes array of given length.
    If None is given, the array will be empty.
    If something else is given (a ctypes array for example),
    it's returned as is.
    There will be no possible side-effect between the array and the initial arr.
    """
    if length is None:
        length = len(arr)
    if arr is None:
        arr = ()
    if isinstance(arr, (np.ndarray, Iterable)):
        return (proper_int * length)(*arr)
    return arr


# The following function wrappers remain untested
# for direct C function wrapping
# and they probably won't work in python2

def wrap(clbl, **kwargz):
    """
    Returns a callable with `clbl`'s behavior
    but for key : val in kwargs, the key attribute of the returned
    callable will be set to val.
    """

    def func(*args, **kwargs):
        return clbl(*args, **kwargs)

    for key, val in kwargz.items():
        setattr(func, key, val)
    # since python3's repr uses __qualname__ instead of __name__
    func.__qualname__ = func.__name__
    return func


def testwrap(clbl):
    """
    Returns a callable which calls clbl and raises a LibraryError if the
    returned value is other than 0.
    """

    def func(*args, **kwargs):
        if clbl(*args, **kwargs):
            raise LibraryError
        return 0

    func.__name__ = clbl.__name__[6:]
    # Since python3's repr uses __qualname__ instead of __name__
    func.__qualname__ = func.__name__
    return func


def curry(clbl, *argz, **kwargz):
    """
    Returns a callable which calls clbl. The arguments in that call are both
    the set argz and kwargz arguments and the call-given arguments.
    """

    def func(*args, **kwargs):
        return clbl(*argz, *args, **kwargz, **kwargs)

    return func
