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

import ctypes
import numpy as np
from .find_libs import _scotchpy_err_lib, _scotch_lib
from . import common as _common


def geom_alloc():
    return Geom(init=False)


class Geom:

    class _Geomtruct(ctypes.Structure):
        _fields_ = [("dummy", ctypes.c_char * _common.libscotch.SCOTCH_geomSizeof())]

    _readableattrs = ("dimnnbr", "geomtab")

    _exitval = True
    _geomptr = None
    _dimnnbr = None
    _geomtab = None

    def __init__(self, init=True):
        _common.libscotch.SCOTCH_geomAlloc.restype = ctypes.POINTER(self._GraphStruct)
        geomptr = _common.libscotch.SCOTCH_geomAlloc()
        self._geomptr = geomptr
        if init:
            self.init()

    def init(self):
        if not self._exitval:
            self.exit()
        self._exitval = False
        _common.libscotch.SCOTCH_geomInit(self._geomptr)

    def __del__(self):
        self.exit()
        _common.libscotch.SCOTCH_memFree(self._geomptr)

    def exit(self):
        if not self._exitval:
            _common.libscotch.SCOTCH_geomExit(self._geomptr)
            self._exitval = True

    def free(self):
        self.exit()
        self.init()

    def _data(self, geomptr=None, store=False):
        argue = [_common.proper_int(), ctypes.pointer(ctypes.c_double())]
        _common.libscotch.SCOTCH_geomData(
            self._geomptr or geomptr, *(ctypes.byref(arg) for arg in argue)
        )
        argue = dict(zip(self._readableattrs, argue))
        return_value = dict()
        for key, val in argue.items():
            if isinstance(val, _common.proper_int):
                if store:
                    setattr(self, "_" + key, val.value)
                return_value[key] = val.value
            elif isinstance(val, ctypes.POINTER(ctypes.c_double)):
                if store:
                    setattr(self, "_" + key, val.contents.value)
                return_value[key] = val.contents.value
        return return_value

    def data(self, as_dict=False):
        return_value = tuple(getattr(self, attr) for attr in self._readableattrs)
        if as_dict:
            return dict(zip(self._readableattrs, return_value))
        return return_value
