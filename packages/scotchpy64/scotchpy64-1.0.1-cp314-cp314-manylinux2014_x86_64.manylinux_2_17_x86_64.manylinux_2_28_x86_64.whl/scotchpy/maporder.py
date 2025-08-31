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
from .find_libs import _scotchpy_err_lib, _scotch_lib, _ptscotch_lib
from . import common as _common

# from .exception import LibraryError


class _MapOrderBase:
    """Allows for extreme factorization in Mapping and Ordering classes"""

    _first = None  # replaces the _exitval attr and allows for disalloc security
    _fnampre = None

    def __init__(self):
        if self._fnampre is None:
            raise NotImplementedError

    def init(self, first, *args):

        funcname = "_".join((self._fnampre, "init"))
        func = getattr(first, funcname)
        return func(self, *args)

    def register(self, first):
        if self._first is not None:
            self.exit()
        self._first = first

    def exit(self):
        if self._first is not None:
            funcname = "_".join((self._fnampre, "exit"))
            func = getattr(self._first, funcname)
            return func(self)

    def unregister(self):
        if self._first is not None:
            self._first = None


def _meth(self, *args, fname=None):
    funcname = "_".join((self._fnampre, fname))
    func = getattr(self._first, funcname)
    return func(self, *args)


def map_alloc():
    """
    This function returns a Mapping object
    """
    return Mapping()


class Mapping(_MapOrderBase):
    """Mapping class constructor"""

    class _MappingStruct(ctypes.Structure):
        _fields_ = [("dummy", ctypes.c_char * _common.libscotch.SCOTCH_mapSizeof())]

    _re_map = None
    _fnampre = "map"

    def __init__(self, *args):
        super().__init__()
        _common.libscotch.SCOTCH_mapAlloc.restype = ctypes.POINTER(self._MappingStruct)
        mappptr = _common.libscotch.SCOTCH_mapAlloc()
        self._mappptr = mappptr
        if args:
            self.init(*args)

    def register(self, first, parttab=None):
        if parttab is not None and not isinstance(parttab, np.ndarray):
            if parttab.dtype != _common.proper_int():
                raise TypeError("The parttab argument must be properly formatted")
        self._parttab = parttab
        super().register(first)

    def unregister(self):
        self._re_map = None
        self._parttab = None
        super().unregister()

    def __del__(self):
        self.exit()
        _common.libscotch.SCOTCH_memFree(self._mappptr)

    compute = _common.curry(_meth, fname="compute")
    fixed_compute = _common.curry(_meth, fname="fixed_compute")
    load = _common.curry(_meth, fname="load")
    save = _common.curry(_meth, fname="save")
    view = _common.curry(_meth, fname="view")

    def re_compute(self, *args):
        self._first.remap_compute(self, *args)

    def re_fixed_compute(self, *args):
        self._first.remap_fixed_compute(self, *args)


class Ordering(_MapOrderBase):
    """Ordering class constructor"""

    class _OrderingStruct(ctypes.Structure):
        _fields_ = [("dummy", ctypes.c_char * _common.libscotch.SCOTCH_orderSizeof())]

    _fnampre = "order"

    def __init__(self, *args):
        super().__init__()
        _common.libscotch.SCOTCH_orderAlloc.restype = ctypes.POINTER(
            self._OrderingStruct
        )
        ordeptr = _common.libscotch.SCOTCH_orderAlloc()
        self._ordeptr = ordeptr
        if args:
            self.init(*args)

    def register(self, first, permtab, peritab, cblknbr, rangtab, treetab):
        self._permtab = permtab
        self._peritab = peritab
        self._cblkptr = [cblknbr]
        self._rangtab = rangtab
        self._treetab = treetab
        super().register(first)

    def unregister(self):
        self._permtab = None
        self._peritab = None
        self._cblkptr = None
        self._rangtab = None
        self._treetab = None
        super().unregister()

    def __del__(self):
        self.exit()
        _common.libscotch.SCOTCH_memFree(self._ordeptr)

    check = _common.curry(_meth, fname="check")
    compute = _common.curry(_meth, fname="compute")
    compute_list = _common.curry(_meth, fname="compute_list")
    load = _common.curry(_meth, fname="load")
    save = _common.curry(_meth, fname="save")
    save_map = _common.curry(_meth, fname="save_map")
    save_tree = _common.curry(_meth, fname="save_tree")


def order_alloc():
    """
    This function returns an Ordering object
    """
    return Ordering()

if _ptscotch_lib:
    class DOrdering:
        """DOrdering class constructor"""

        class _DOrderStruct(ctypes.Structure):
            _fields_ = [
                ("dummy", ctypes.c_char * _common.libptscotch.SCOTCH_dorderSizeof())
            ]

        def __init__(self, *args):
            _common.libptscotch.SCOTCH_dorderAlloc.restype = ctypes.POINTER(
                self._DOrderStruct
            )
            dordptr = _common.libptscotch.SCOTCH_dorderAlloc()
            self._dordptr = dordptr
            if args:
                self.init(*args)

        def __del__(self):
            _common.libptscotch.SCOTCH_memFree(self._dordptr)


    class DMapping:
        """DMapping class constructor"""

        class _DMappingStruct(ctypes.Structure):
            _fields_ = [("dummy", ctypes.c_char * _common.libptscotch.SCOTCH_dmapSizeof())]

        def __init__(self, *args):
            _common.libptscotch.SCOTCH_dmapAlloc.restype = ctypes.POINTER(
                self._DMappingStruct
            )
            dmappptr = _common.libptscotch.SCOTCH_dmapAlloc()
            self._dmappptr = dmappptr
            if args:
                self.init(*args)

        def __del__(self):
            _common.libptscotch.SCOTCH_memFree(self._dmappptr)


    def dorder_alloc():
        """
        This function returns a DOrdering object
        """
        return DOrdering()


    def dmap_alloc():
        """
        This function returns a DMapping object
        """
        return DMapping()
