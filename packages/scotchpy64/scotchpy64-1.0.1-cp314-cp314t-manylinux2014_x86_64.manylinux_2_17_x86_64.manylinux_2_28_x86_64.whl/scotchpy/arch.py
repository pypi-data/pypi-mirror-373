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


def arch_alloc():
    return Arch(init=False)


class Arch:
    """docstring for Arch"""

    class _ArchStruct(ctypes.Structure):
        _fields_ = [("dummy", ctypes.c_char * _common.libscotch.SCOTCH_archSizeof())]

    _exitval = True
    _sub_arch = None

    def __init__(self, init=True):
        _common.libscotch.SCOTCH_archAlloc.restype = ctypes.POINTER(self._ArchStruct)
        archptr = _common.libscotch.SCOTCH_archAlloc()
        self._archptr = archptr
        if init:
            self.init()

    def init(self):
        if not self._exitval:
            self.exit()
        self._exitval = False
        _common.libscotch.SCOTCH_archInit(self._archptr)

    def __del__(self):
        self.exit()
        _common.libscotch.SCOTCH_memFree(self._archptr)

    def exit(self):
        if not self._exitval:
            self._sub_arch = None
            _common.libscotch.SCOTCH_archExit(self._archptr)
            self._exitval = True

    def load(self, stream):
        """
        `stream` being either a file object (result of an `open()`, don't forget to close it)
        or a filename, as a string or as a bytes object (such as b"file/name").
        """
        if isinstance(stream, (str, bytes)):
            with open(stream) as st:
                return self.load(st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_archLoad(self._archptr, filep):
            raise LibraryError("archLoad")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def save(self, stream):
        """
        `stream` being either a file object (result of an `open()`, don't forget to close it)
        or a filename, as a string or as a bytes object (such as b"file/name").
        """
        if isinstance(stream, (str, bytes)):
            with open(stream, "w+") as st:
                return self.save(st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_archSave(self._archptr, filep):
            raise LibraryError("archSave")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def name(self):
        """
        Returns a string giving the name of the arch.
        """
        _common.libscotch.SCOTCH_archName.restype = ctypes.c_char_p
        return _common.libscotch.SCOTCH_archName(self._archptr).value.decode()

    def size(self):
        """
        Returns the number of nodes of the given architecture as a SCOTCH_Num.
        """
        return _common.libscotch.SCOTCH_archSize(self._archptr)

    def build(self, graf, listtab, strat):
        """
        The listnbr arg is omitted and taken from listtab's length.
        """
        if _common.libscotch.SCOTCH_archBuild(
            self._archptr,
            graf._grafptr,
            _common.proper_int(len(listtab)),
            _common.array_to_pointer(listtab),
            strat._straptr,
        ):
            raise LibraryError("archBuild")

    def build0(self, graf, listtab, strat):
        """
        The listnbr arg is omitted and taken from listtab's length.
        """
        if _common.libscotch.SCOTCH_archBuild0(
            self._archptr,
            graf._grafptr,
            _common.proper_int(len(listtab)),
            _common.array_to_pointer(listtab),
            strat._straptr,
        ):
            raise LibraryError("archBuild0")

    def build2(self, graf, listtab):
        """
        The listnbr arg is omitted and taken from listtab's length.
        """
        if _common.libscotch.SCOTCH_archBuild2(
            self._archptr,
            graf._grafptr,
            _common.proper_int(len(listtab)),
            _common.array_to_pointer(listtab),
        ):
            raise LibraryError("archBuild2")

    def cmplt(self, vertnbr):
        if _common.libscotch.SCOTCH_archCmplt(
            self._archptr, _common.proper_int(vertnbr)
        ):
            raise LibraryError("archCmplt")

    def cmpltw(self, velotab):
        """
        The vertnbr arg is omitted and taken from velotab's length.
        """
        if _common.libscotch.SCOTCH_archCmpltw(
            self._archptr,
            _common.proper_int(len(velotab)),
            _common.array_to_pointer(velotab),
        ):
            raise LibraryError("archCmpltw")

    def hcub(self, hdimval):
        if _common.libscotch.SCOTCH_archHcub(
            self._archptr, _common.proper_int(hdimval)
        ):
            raise LibraryError("archHcub")

    def ltleaf(self, sizetab, linktab, permtab):
        """
        The levlnbr and permnbr args are omitted and taken from sizetab's and permtab's lengths,
        respectively.
        """
        if _common.libscotch.SCOTCH_archLtleaf(
            self._archptr,
            _common.proper_int(len(sizetab)),
            _common.array_to_pointer(sizetab),
            _common.array_to_pointer(linktab),
            _common.proper_int(len(permtab)),
            _common.array_to_pointer(permtab),
        ):
            raise LibraryError("archLtLeaf")

    def mesh(self, *args):
        """
        A generalized version of mesh2, mesh3 and meshX - it's almost meshX, but the integers don't
        have to be wrapped in an iterable and must be given ore after the other.
        """
        if len(args) == 2:
            return self.mesh2(*args)
        elif len(args) == 3:
            return self.mesh3(*args)
        else:
            return self.meshX(args)

    def mesh2(self, xdimval, ydimval):
        if _common.libscotch.SCOTCH_archMesh2(
            self._archptr, _common.proper_int(xdimval), _common.proper_int(ydimval)
        ):
            raise LibraryError("archMesh2")

    def mesh3(self, xdimval, ydimval, zdimval):
        if _common.libscotch.SCOTCH_archMesh3(
            self._archptr,
            _common.proper_int(xdimval),
            _common.proper_int(ydimval),
            _common.proper_int(zdimval),
        ):
            raise LibraryError("archMesh3")

    def meshX(self, dimntab):
        """
        The dimnbr arg is omitted and taken from dimntab's length.
        """
        if _common.libscotch.SCOTCH_archMeshX(
            self._archptr,
            _common.proper_int(len(dimntab)),
            _common.array_to_pointer(dimntab),
        ):
            raise LibraryError("archMeshX")

    def sub(self, orgarch, vnumtab):
        """
        The vnumnbr arg is omitted and taken from vnumtab's length.
        """
        self._sub_arch = orgarch
        if _common.libscotch.SCOTCH_archSub(
            self._archptr,
            orgarch._archptr,
            _common.proper_int(len(vnumtab)),
            _common.array_to_pointer(vnumtab),
        ):
            raise LibraryError("archSub")

    def tleaf(self, sizetab, linktab):
        """
        The levlnbr arg is omitted and taken from sizetab's length.
        """
        if _common.libscotch.SCOTCH_archTleaf(
            self._archptr,
            _common.proper_int(len(sizetab)),
            _common.array_to_pointer(sizetab),
            _common.array_to_pointer(linktab),
        ):
            raise LibraryError("archTleaf")

    def torus(self, *args):
        if len(args) == 2:
            return self.torus2(*args)
        elif len(args) == 3:
            return self.torus3(*args)
        else:
            return self.torusX(args)

    def torus2(self, xdimval, ydimval):
        if _common.libscotch.SCOTCH_archTorus2(
            self._archptr, _common.proper_int(xdimval), _common.proper_int(ydimval)
        ):
            raise LibraryError("archTorus2")

    def torus3(self, xdimval, ydimval, zdimval):
        if _common.libscotch.SCOTCH_archTorus3(
            self._archptr,
            _common.proper_int(xdimval),
            _common.proper_int(ydimval),
            _common.proper_int(zdimval),
        ):
            raise LibraryError("archTorus3")

    def torusX(self, dimntab):
        """
        The dimnbr arg is omitted and taken from dimntab's length.
        """
        if _common.libscotch.SCOTCH_archTorusX(
            self._archptr,
            _common.proper_int(len(dimntab)),
            _common.array_to_pointer(dimntab),
        ):
            raise LibraryError("archTorusX")

    def vhcub(self):
        if _common.libscotch.SCOTCH_archVhcub(self._archptr):
            raise LibraryError("archVhcub")

    def vcmplt(self):
        if _common.libscotch.SCOTCH_archVcmplt(self._archptr):
            raise LibraryError("archVcmplt")

    def dom_size(self, domn):
        return _common.libscotch.SCOTCH_archDomSize(self._archptr, domn.archdomptr)

    def dom_wght(self, domn):
        return _common.libscotch.SCOTCH_archDomWght(self._archptr, domn.archdomptr)

    def dom_dist(self, domn0, domn1):
        return _common.libscotch.SCOTCH_archDomDist(
            self._archptr, domn0.archdomptr, domn1.archdomptr
        )

    def dom_frst(self, domn):
        if _common.libscotch.SCOTCH_archDomFrst(self._archptr, domn.archdomptr):
            raise LibraryError("archDomFrst")

    def dom_term(self, domn, domnum):
        if _common.libscotch.SCOTCH_archDomTerm(
            self._archptr, domn.archdomptr, _common.proper_int(domnum)
        ):
            raise LibraryError("archDomTerm")

    def dom_num(self, domn):
        return _common.libscotch.SCOTCH_archDomNum(self._archptr, domn.archdomptr)

    def dom_bipart(self, domn, domn0, domn1):
        if _common.libscotch.SCOTCH_archDomBipart(
            self._archptr, domn.archdomptr, domn0.archdomptr, domn1.archdomptr
        ):
            raise LibraryError("archDomBipart")
