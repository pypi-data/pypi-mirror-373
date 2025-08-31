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

from .find_libs import _scotchpy_err_lib, _scotch_lib, _ptscotch_lib
from . import common as _common
from .exception import LibraryError


def context_alloc():
    return Context(init=False)


class Context:
    """docstring for Context"""

    class SCOTCH_Context(ctypes.Structure):
        _fields_ = [
            ("dummy", ctypes.c_double * _common.libscotch.SCOTCH_contextSizeof())
        ]  # sizeof(SCOTCH_Context) is 3 * sizeof(double)

    _exitval = True

    def __init__(self, init=True):
        _common.libscotch.SCOTCH_contextAlloc.restype = ctypes.POINTER(
            self.SCOTCH_Context
        )
        contextptr = _common.libscotch.SCOTCH_contextAlloc()
        self._contextptr = contextptr
        if init:
            self.init()

    def init(self):
        if not self._exitval:
            self.exit()
        self._exitval = False
        _common.libscotch.SCOTCH_contextInit(self._contextptr)

    def __del__(self):
        self.exit()
        _common.libscotch.SCOTCH_memFree(self._contextptr)

    def exit(self):
        if not self._exitval:
            _common.libscotch.SCOTCH_contextExit(self._contextptr)
            self._exitval = True

    def option_get_num(self, optinum, optival):
        if _common.libscotch.SCOTCH_contextOptionGetNum(
            self._contextptr, _common.proper_int(optinum), _common.proper_int(optival)
        ):
            raise LibraryError("contextOptionGetNum")

    def option_set_num(self, optinum, optival):
        if _common.libscotch.SCOTCH_contextOptionSetNum(
            self._contextptr, _common.proper_int(optinum), _common.proper_int(optival)
        ):
            raise LibraryError("contextOptionSetNum")

    def random_clone(self):
        if _common.libscotch.SCOTCH_contextRandomClone(self._contextptr):
            raise LibraryError("randomClone")

    def random_reset(self):
        if _common.libscotch.SCOTCH_contextRandomReset(self._contextptr):
            raise LibraryError("randomReset")

    def random_seed(self, seedval):
        if _common.libscotch.SCOTCH_contextRandomSeed(
            self._contextptr, _common.proper_int(seedval)
        ):
            raise LibraryError("randomSeed")

    def thread_import1(self, thrdnbr):
        if _common.libscotch.SCOTCH_contextThreadImport1(
            self._contextptr, _common.proper_int(thrdnbr)
        ):
            raise LibraryError("threadImport1")

    def thread_import2(self, thrdnum):
        if _common.libscotch.SCOTCH_contextThreadImport2(
            self._contextptr, _common.proper_int(thrdnum)
        ):
            raise LibraryError("threadImport2")

    def thread_spawn(self, thrdnbr, coretab):
        coretabnew = _common.properly_format(coretab)
        if _common.libscotch.SCOTCH_contextThreadSpawn(
            self._contextptr, _common.proper_int(thrdnbr), coretabnew
        ):
            raise LibraryError("threadSpawn")

    def bind_graph(self, orggraf, cntgraf):
        if _common.libscotch.SCOTCH_contextBindGraph(
            self._contextptr, orggraf._grafptr, cntgraf._grafptr
        ):
            raise LibraryError("bindGraph")

    def bind_mesh(self, orgmeshptr, cntmeshptr):
        if _common.libscotch.SCOTCH_meshBind(self._contextptr, orgmeshptr, cntmeshptr):
            raise LibraryError("meshBind")

    def bind_dgraph(self, orggrafptr, cntgrafptr):
        if _common.libscotch.SCOTCH_dgraphBind(
            self._contextptr, orggrafptr, cntgrafptr
        ):
            raise LibraryError("dgraphBind")
