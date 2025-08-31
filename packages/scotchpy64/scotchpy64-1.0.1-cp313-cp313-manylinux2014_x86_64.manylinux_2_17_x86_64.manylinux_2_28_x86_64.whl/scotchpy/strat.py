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

from . import common as _common
from .exception import LibraryError
from .find_libs import _ptscotch_lib

def strat_alloc():
    return Strat(init=False)


class Strat:
    """
    Strat is a class that wraps the SCOTCH_Strat struct
    and provides a pythonic interface to the SCOTCH_Strat struct
    """

    class _StratStruct(ctypes.Structure):
        _fields_ = [("dummy", ctypes.c_char * _common.libscotch.SCOTCH_stratSizeof())]

    _exitval = True

    def __init__(self, init=True):
        _common.libscotch.SCOTCH_stratAlloc.restype = ctypes.POINTER(self._StratStruct)
        straptr = _common.libscotch.SCOTCH_stratAlloc()
        self._straptr = straptr
        if init:
            self.init()

    def init(self):
        if not self._exitval:
            self.exit()
        self._exitval = False
        _common.libscotch.SCOTCH_stratInit(self._straptr)

    def __del__(self):
        self.exit()
        _common.libscotch.SCOTCH_memFree(self._straptr)

    def exit(self):
        if not self._exitval:
            _common.libscotch.SCOTCH_stratExit(self._straptr)
            self._exitval = True
            # clear each attribute

    def save(self, stream):
        if isinstance(stream, (str, bytes)):
            with open(stream, "w+") as st:
                return self.save(st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_stratSave(self._straptr, filep):
            raise LibraryError("stratSave")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def graph_cluster_build(self, flagval, pwgtmax, densmin, bbalval):
        if _common.libscotch.SCOTCH_stratGraphClusterBuild(
            self._straptr,
            _common.proper_int(flagval),
            _common.proper_int(pwgtmax),
            ctypes.c_double(densmin),
            ctypes.c_double(bbalval),
        ):
            raise LibraryError("stratGraphClusterBuild")

    def graph_map_build(self, flagval, partnbr, balrat):
        if _common.libscotch.SCOTCH_stratGraphMapBuild(
            self._straptr,
            _common.proper_int(flagval),
            _common.proper_int(partnbr),
            ctypes.c_double(balrat),
        ):
            raise LibraryError("stratGraphMapBuild")

    def graph_part_ovl_build(self, flagval, partnbr, balrat):
        if _common.libscotch.SCOTCH_stratGraphPartOvlBuild(
            self._straptr,
            _common.proper_int(flagval),
            _common.proper_int(partnbr),
            ctypes.c_double(balrat),
        ):
            raise LibraryError("stratGraphPartOvlBuild")

    def graph_order_build(self, flagval, levlnbr, balrat):
        if _common.libscotch.SCOTCH_stratGraphOrderBuild(
            self._straptr,
            _common.proper_int(flagval),
            _common.proper_int(levlnbr),
            ctypes.c_double(balrat),
        ):
            raise LibraryError("stratGraphOrderBuild")

    def mesh_order_build(self, flagval, balrat):
        if _common.libscotch.SCOTCH_stratMeshOrderBuild(
            self._straptr, _common.proper_int(flagval), ctypes.c_double(balrat)
        ):
            raise LibraryError("stratMeshOrderBuild")
    def dgraph_map(self, string):
        if _common.libscotch.SCOTCH_stratDgraphMap(
            self._straptr, ctypes.c_char_p(string)
        ):
            raise LibraryError("stratDgraphMap")

    if _ptscotch_lib: # Define these methods only when libptscotch is present

        def dgraph_cluster_build(self, flagval, pwgtmax, densmin, bbalval):
            if _common.libptscotch.SCOTCH_stratDgraphClusterBuild(
                self._straptr,
                _common.proper_int(flagval),
                _common.proper_int(pwgtmax),
                ctypes.c_double(densmin),
                ctypes.c_double(bbalval),
            ):
                raise LibraryError("stratDgraphClusterBuild")

        def dgraph_map_build(self, flagval, procnbr, partnbr, balrat):
            if _common.libptscotch.SCOTCH_stratDgraphMapBuild(
                self._straptr,
                _common.proper_int(flagval),
                _common.proper_int(procnbr),
                _common.proper_int(partnbr),
                ctypes.c_double(balrat),
            ):
                raise LibraryError("stratDgraphMapBuild")

        def dgraph_order(self, string):
            if _common.libptscotch.SCOTCH_stratDgraphOrder(
                self._straptr, ctypes.c_char_p(string)
            ):
                raise LibraryError("stratDgraphOrder")

        def dgraph_order_build(self, flagval, procnbr, levlnbr, balrat):
            if _common.libptscotch.SCOTCH_stratDgraphOrderBuild(
                self._straptr,
                _common.proper_int(flagval),
                _common.proper_int(procnbr),
                _common.proper_int(levlnbr),
                ctypes.c_double(balrat),
            ):
                raise LibraryError("stratDgraphOrderBuild")


for _method_name_elements in {
    ("graph", "bipart"),
    ("graph", "map"),
    ("graph", "part", "ovl"),
    ("graph", "order"),
    ("mesh", "order"),
}:

    def _strat_string_method(self, string, meth_name_els=None):
        octets = string if isinstance(string, bytes) else bytes(string, "utf8")
        libfuncname = "SCOTCH_strat" + "".join(
            [el[0].capitalize() + el[1:] for el in meth_name_els]
        )
        # SCOTCH_stratGraphPartOvl
        libfunc = getattr(_common.libscotch, libfuncname)
        if libfunc(self._straptr, ctypes.c_char_p(octets)):
            raise LibraryError(libfuncname[7:])

    setattr(
        Strat,
        "_".join(_method_name_elements),
        # Strat.graph_part_ovl
        _common.wrap(
            _common.curry(_strat_string_method, meth_name_els=_method_name_elements),
            __name__="_".join(_method_name_elements),
        ),
    )
# Similar wrapping can be done to stratXBuild methods
# by parsing a {funcname:argsnumber} dict
# and deducing the arg types from the number of args
