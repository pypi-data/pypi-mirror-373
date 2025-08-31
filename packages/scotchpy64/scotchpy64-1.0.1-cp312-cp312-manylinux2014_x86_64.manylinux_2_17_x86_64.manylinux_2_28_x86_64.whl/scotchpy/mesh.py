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
from .exception import LibraryError
from . import strat as _strat


def build_mesh(*args, meshptr=None, **kwargs):
    """
    args and kwargs need to be given in the same fashion as Mesh.build takes them.
    """
    mesh = Mesh(meshptr)
    mesh.build(*args, **kwargs)
    return mesh


def load_mesh(*args, meshptr=None, **kwargs):
    """
    args and kwargs need to be given in the same fashion as Mesh.load takes them.
    """
    mesh = Mesh(meshptr)
    mesh.load(*args, **kwargs)
    return mesh


def mesh_alloc():
    return Mesh(init=False)


class Mesh:
    """
    Caution, mutating the given np.arrays will void your warranty.
    The use of no.array(copy=True) is recommended otherwise.
    The constructor doesn't build a viable mesh, .load() or .build() must be called afterwards.
    'build_mesh' and 'load_mesh' both return viable meshes.
    """

    class _MeshStruct(ctypes.Structure):
        _fields_ = [("dummy", ctypes.c_char * _common.libscotch.SCOTCH_meshSizeof())]

    _exitval = True
    _readableattrs = (
        "velmbas",
        "vnodbas",
        "velmnbr",
        "vnodnbr",
        "verttab",
        "vendtab",
        "velotab",
        "vnlotab",
        "vlbltab",
        "edgenbr",
        "edgetab",
    )

    _meshptr = None
    _velmbas = None
    _vnodbas = None
    _velmnbr = None
    _vnodnbr = None
    _verttab = None
    _vendtab = None
    _velotab = None
    _vnlotab = None
    _vlbltab = None
    _edgenbr = None
    _edgetab = None
    _degrnbr = None  # not sure if needed

    def __getattr__(self, name):
        name = str(name)
        if name in self._readableattrs:
            return getattr(self, "_" + name)
        raise AttributeError(f"'{type(self)}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        name = str(name)
        if name in self._readableattrs:
            raise AttributeError("attribute {} is read-only".format(name))
        super().__setattr__(name, value)

    def __init__(self, init=True):
        _common.libscotch.SCOTCH_meshAlloc.restype = ctypes.POINTER(self._MeshStruct)
        meshptr = _common.libscotch.SCOTCH_meshAlloc()
        self._meshptr = meshptr
        if init:
            self.init()

    def init(self):
        if not self._exitval:
            self.exit()
        self._exitval = False
        _common.libscotch.SCOTCH_meshInit(self._meshptr)

    def __del__(self):
        self.exit()
        _common.libscotch.SCOTCH_memFree(self._meshptr)

    def exit(self):
        if not self._exitval:
            _common.libscotch.SCOTCH_meshExit(self._meshptr)
            self._exitval = True

    def _data(self, meshptr, store=False):
        """
        Reads the 12 values from the C structure with SCOCTCH_meshData,
        stores them in their respective attributes if store is True.
        and returns them as a dict.
        If no meshptr is given, the meshptr of the instance is used.
        """
        argue = (
            [_common.proper_int() for k in range(4)]
            + [ctypes.pointer(_common.proper_int()) for k in range(5)]
            + [_common.proper_int()]
            + [ctypes.pointer(_common.proper_int())]
            + [_common.proper_int()]
        )
        _common.libscotch.SCOTCH_meshData(
            meshptr or self._meshptr, *(ctypes.byref(arg) for arg in argue)
        )

        argue = dict(zip(self._readableattrs, argue))
        return_value = dict()
        for key, val in argue.items():
            if isinstance(val, _common.proper_int):
                if store:
                    setattr(self, "_" + key, val.value)
                return_value[key] = val.value
        vertnbr = return_value["velmnbr"] + return_value["vnodnbr"]
        arraysize = {}  # matches each array name with its size
        arraysize["vendtab"] = vertnbr
        arraysize["velotab"] = return_value["velmnbr"]
        arraysize["vnlotab"] = return_value["vnodnbr"]
        arraysize["vlbltab"] = vertnbr
        arraysize["edgetab"] = return_value["edgenbr"]
        if ctypes.addressof(argue["vendtab"]) == (
            ctypes.addressof(argue["verttab"].contents) + _common.num_sizeof()
        ):
            # if the mesh is compact, it stays the same
            arraysize["verttab"] = vertnbr + 1
            del argue["vendtab"]
        else:
            arraysize["verttab"] = vertnbr
        for key, val in argue.items():
            if isinstance(val, ctypes.POINTER(_common.proper_int)):
                try:
                    arey = np.ctypeslib.as_array(val, shape=(arraysize[key],))
                except ValueError:
                    if store:
                        setattr(self, "_" + key, None)
                    return_value[key] = None
                else:
                    if store:
                        setattr(self, "_" + key, arey)
                    return_value[key] = arey
        return return_value

    def build(
        self,
        velmbas=None,
        vnodbas=None,
        velmnbr=None,
        vnodnbr=None,
        verttab=None,
        vendtab=None,
        velotab=None,
        vnlotab=None,
        vlbltab=None,
        edgenbr=None,
        edgetab=None,
    ):
        if (verttab is None) or (edgetab is None):
            raise ValueError("Both verttab and edgetab need to be given")
        self._verttab = _common.properly_format(verttab)
        self._edgetab = _common.properly_format(edgetab)
        self._vendtab = _common.properly_format(vendtab)
        if isinstance(self._verttab, np.ndarray) and isinstance(
            self._vendtab, np.ndarray
        ):
            if self._verttab.size > self._vendtab.size + 1:
                raise ValueError(
                    "if given, verttab and vendtab must not be longer than edgetab"
                )
        self._velotab = _common.properly_format(velotab)
        self._vnlotab = _common.properly_format(vnlotab)
        self._vlbltab = _common.properly_format(vlbltab)
        if (velmbas is not None) and (vnodbas is not None):
            self._velmbas = velmbas
            self._vnodbas = vnodbas
        else:
            raise ValueError("Both velmbas and vnodbas need to be given")
        if vnodnbr is None:
            if not isinstance(self._verttab, np.ndarray):
                raise TypeError("Vnodnbr must be given when vnlotab is not an Iterable")
            elif vnlotab:
                self._vnodnbr = self._vnlotab.size
            else:
                self._vnodnbr = velmbas + velmnbr
        if velmnbr is None:
            if not isinstance(self._verttab, np.ndarray):
                raise TypeError("Velmnbr must be given when velotab is not an Iterable")
        self._velmnbr = velmnbr

        if edgenbr is None:
            if not isinstance(self._edgetab, np.ndarray):  # verttab has no size
                raise TypeError("Edgenbr must be given when verttab is not an Iterable")
            elif vendtab:  # non-compact mesh
                self._edgenbr = sum(
                    [
                        self._vendtab[i] - self._verttab[i]
                        for i in range(self._verttab.size)
                    ]
                )
            else:  # compact mesh
                self._edgenbr = self._verttab[-1] - self._baseval
        else:  # edgenbr is given
            self._edgenbr = edgenbr
        self._vlbltab = _common.properly_format(vlbltab)
        if _common.libscotch.SCOTCH_meshBuild(
            self._meshptr,
            _common.proper_int(velmbas),
            _common.proper_int(vnodbas),
            _common.proper_int(velmnbr),
            _common.proper_int(vnodnbr),
            _common.array_to_pointer(verttab),
            _common.array_to_pointer(vendtab),
            _common.array_to_pointer(velotab),
            _common.array_to_pointer(vnlotab),
            _common.array_to_pointer(vlbltab),
            _common.proper_int(edgenbr),
            _common.array_to_pointer(edgetab),
        ):
            raise LibraryError("meshBuild")
        if self.check():
            raise ValueError("Mesh is not valid")

    def check(self):
        return _common.libscotch.SCOTCH_meshCheck(self._meshptr)

    def data(self, as_dict=False):
        return_value = tuple(getattr(self, attr) for attr in self._readableattrs)
        if as_dict:
            return dict(zip(self._readableattrs, return_value))
        return return_value

    def load(self, stream, baseval=-1):
        if isinstance(stream, str):
            with open(stream) as st:
                return self.Load(
                    st,
                )
        internmptr = _common.libscotch.SCOTCH_meshAlloc()
        _common.libscotch.SCOTCH_meshInit(internmptr)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_meshLoad(internmptr, filep, baseval):
            raise LibraryError("meshLoad")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)
        data = self._data(meshptr=internmptr, store=False)
        for key, val in data.items():
            if val is not None and isinstance(val, _common.Iterable):
                data[key] = np.array(val, copy=True)
        _common.libscotch.SCOTCH_meshExit(internmptr)
        self.build(**data)

    def save(self, stream):
        if isinstance(stream, str):
            with open(stream, "w+") as st:
                return self.save(st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_meshSave(self._meshptr, filep):
            raise LibraryError("meshSave")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def size(self, as_dict=False):
        return_value = (self.velmnbr, self.vnodnbr, self.edgenbr)
        if as_dict:
            return dict(zip(("velmnbr", "vnodnbr", "edgenbr"), return_value))
        return return_value

    def stat(self, as_dict=False):
        argue = (
            [_common.proper_int() for k in range(3)]
            + [ctypes.c_double() for k in range(2)]
            + [_common.proper_int() for k in range(2)]
            + [ctypes.c_double() for k in range(2)]
            + [_common.proper_int() for k in range(2)]
            + [ctypes.c_double() for k in range(2)]
        )
        _common.libscotch.SCOTCH_meshStat(
            self._meshptr, *(ctypes.byref(arg) for arg in argue)
        )
        values = tuple(arg.value for arg in argue)
        if as_dict:
            return dict(
                zip(
                    (
                        "vnlomin",
                        "vnlomax",
                        "vnlosum",
                        "vnloavg",
                        "vnloadl",
                        "edegmin",
                        "edegmax",
                        "edegavg",
                        "edegdlt",
                        "ndegmin",
                        "ndegmax",
                        "ndegavg",
                        "ndegdlt",
                    ),
                    values,
                )
            )
        return values

    def graph(self, graf):
        if _common.libscotch.SCOTCH_meshGraph(self._meshptr, graf._grafptr):
            raise LibraryError("meshGraph")

    def graph_dual(self, graf, ncomval):
        if _common.libscotch.SCOTCH_meshGraphDual(
            self._meshptr, graf._grafptr, _common.proper_int(ncomval)
        ):
            raise LibraryError("meshGraphDual")

    def order(
        self,
        strat=None,
        permtab=None,
        peritab=None,
        cblknbr=None,
        rangtab=None,
        treetab=None,
    ):
        strat = strat or _strat.Strat(init=True)
        cblknbr = cblknbr or _common.proper_int()
        if _common.libscotch.SCOTCH_meshOrder(
            self._meshptr,
            strat._straptr,
            permtab,
            peritab,
            ctypes.byref(cblknbr),
            rangtab,
            treetab,
        ):
            raise LibraryError("meshOrder")

    def order_init(
        self,
        ordering,
        permtab=None,
        peritab=None,
        cblknbr=None,
        rangtab=None,
        treetab=None,
    ):
        cblknbr = cblknbr or _common.proper_int()
        if _common.libscotch.SCOTCH_meshOrderInit(
            self._meshptr,
            ordering._ordeptr,
            ctypes.byref(permtab),
            ctypes.byref(peritab),
            ctypes.byref(cblknbr),
            ctypes.byref(rangtab),
            ctypes.byref(treetab),
        ):
            raise LibraryError("meshOrderInit")
        rv = (permtab[:], peritab[:], cblknbr.value, rangtab[:], treetab[:])
        ordering.register(self, *rv)

    def order_exit(self, ordering):
        ordering.unregister()
        _common.libscotch.SCOTCH_meshOrderExit(self._meshptr, ordering._ordeptr)

    def order_check(self, ordering):
        if _common.libscotch.SCOTCH_meshOrderCheck(self._meshptr, ordering._ordeptr):
            raise LibraryError("meshOrderCheck")

    def order_compute(self, ordering, strat):
        if _common.libscotch.SCOTCH_meshOrderCompute(
            self._meshptr, ordering._ordeptr, strat._straptr
        ):
            raise LibraryError("meshOrderCompute")
        self._data(store=True)

    def order_save(self, ordering, stream):
        if isinstance(stream, str):
            with open(stream, "w+") as st:
                return self.order_save(ordering, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_meshOrderSave(
            self._meshptr, ordering._ordeptr, filep
        ):
            raise LibraryError("meshOrderSave")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def order_save_map(self, ordering, stream):
        if isinstance(stream, str):
            with open(stream, "w+") as st:
                return self.order_save_map(ordering, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_meshOrderSaveMap(
            self._meshptr, ordering._ordeptr, filep
        ):
            raise LibraryError("meshOrderSaveMap")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def order_save_tree(self, ordering, stream):
        if isinstance(stream, str):
            with open(stream, "w+") as st:
                return self.order_save_tree(ordering, st)  # issue???
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_meshOrderSaveTree(
            self._meshptr, ordering._ordeptr, filep
        ):
            raise LibraryError("meshOrderSaveTree")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def geom_load_habo(self, geom, meshstream, geomstream, string):
        if isinstance(meshstream, str):
            with open(meshstream) as mst:
                return self.geom_load_habo(geom, mst, geomstream, string)
        if isinstance(geomstream, str):
            with open(geomstream) as gst:
                return self.geom_load_habo(geom, meshstream, gst, string)

        internmptr = _common.libscotch.SCOTCH_meshAlloc()
        interngptr = _common.libscotch.SCOTCH_geomAlloc()
        _common.libscotch.SCOTCH_meshInit(internmptr)
        _common.libscotch.SCOTCH_geomInit(interngptr)
        meshstream.flush()
        geomstream.flush()
        nfilenogeo = _common.libc.dup(geomstream.fileno())
        nfilenomes = _common.libc.dup(meshstream.fileno())
        filepgeo = _common.libc.fdopen(nfilenogeo, geomstream.mode.encode())
        filepmes = _common.libc.fdopen(nfilenomes, meshstream.mode.encode())
        if _common.libscotch.SCOTCH_meshGeomLoadHabo(
            internmptr, interngptr, filepmes, filepgeo, string
        ):
            raise LibraryError("meshGeomLoadHabo")
        _common.libc.fflush(filepgeo)
        _common.libc.fflush(filepmes)
        geom._data(interngptr, store=True)
        data = self._data(meshptr=internmptr, store=False)
        for key, val in data.items():
            if val is not None and isinstance(val, _common.Iterable):
                data[key] = np.array(val, copy=True)
        _common.libscotch.SCOTCH_meshExit(internmptr)
        _common.libscotch.SCOTCH_geomExit(interngptr)
        self.build(**data)

    def geom_load_scot(self, geom, meshstream, geomstream, string):
        if isinstance(meshstream, str):
            with open(meshstream) as mst:
                return self.geom_load_scot(geom, mst, geomstream, string)
        if isinstance(geomstream, str):
            with open(geomstream) as gst:
                return self.geom_load_scot(geom, meshstream, gst, string)

        internmptr = _common.libscotch.SCOTCH_meshAlloc()
        interngptr = _common.libscotch.SCOTCH_geomAlloc()
        _common.libscotch.SCOTCH_meshInit(internmptr)
        _common.libscotch.SCOTCH_geomInit(interngptr)
        meshstream.flush()
        geomstream.flush()
        nfilenogeo = _common.libc.dup(geomstream.fileno())
        nfilenomes = _common.libc.dup(meshstream.fileno())
        filepgeo = _common.libc.fdopen(nfilenogeo, geomstream.mode.encode())
        filepmes = _common.libc.fdopen(nfilenomes, meshstream.mode.encode())
        if _common.libscotch.SCOTCH_meshGeomLoadScot(
            internmptr, interngptr, filepmes, filepgeo, string
        ):
            raise LibraryError("meshGeomLoadScot")
        _common.libc.fflush(filepgeo)
        _common.libc.fflush(filepmes)
        geom._data(interngptr, store=True)
        data = self._data(meshptr=internmptr, store=False)
        for key, val in data.items():
            if val is not None and isinstance(val, _common.Iterable):
                data[key] = np.array(val, copy=True)
        _common.libscotch.SCOTCH_meshExit(internmptr)
        _common.libscotch.SCOTCH_geomExit(interngptr)
        self.build(**data)

    def geom_save_scot(self, geom, meshstream, geomstream, string):
        if isinstance(meshstream, str):
            with open(meshstream, "w+") as mst:
                return self.geom_save_scot(geom, mst, geomstream, string)
        if isinstance(geomstream, str):
            with open(geomstream, "w+") as gst:
                return self.geom_save_scot(geom, meshstream, gst, string)

        meshstream.flush()
        geomstream.flush()
        nfilenogeo = _common.libc.dup(geomstream.fileno())
        nfilenomes = _common.libc.dup(meshstream.fileno())
        filepgeo = _common.libc.fdopen(nfilenogeo, geomstream.mode.encode())
        filepmes = _common.libc.fdopen(nfilenomes, meshstream.mode.encode())
        if _common.libscotch.SCOTCH_meshGeomSaveScot(
            self._meshptr, geom._geomptr, filepmes, filepgeo, string
        ):
            raise LibraryError("meshGeomSaveScot")
        _common.libc.fflush(filepgeo)
        _common.libc.fflush(filepmes)
        _common.libc.fclose(filepgeo)
        _common.libc.fclose(filepmes)
