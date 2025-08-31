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
from . import strat as _strat
from .exception import LibraryError, CannotCoarsen

# Try to export networkx
_nx_found = True
try:
    import networkx as nx
except ModuleNotFoundError:
     _nx_found = False
     pass

# Detect matplotlib
_matplotlib_found = True
try:
    import matplotlib.pyplot as plt
except ModuleNotFoundError:
    _matplotlib_found = False
    pass


def build_graph(*args, grafptr=None, **kwargs):
    """
    Args and kwargs need to be given in the same fashion as Graph.build takes them.
    """
    gra = Graph(grafptr)
    gra.build(*args, **kwargs)
    return gra


def build_graph_from_csgraph(*args, grafptr=None, **kwargs):
    """
    Args and kwargs need to be given in the same fashion as Graph.build_from_csgraph takes them.
    """
    gra = Graph(grafptr)
    gra.build_from_csgraph(*args, **kwargs)
    return gra


def load_graph(*args, grafptr=None, **kwargs):
    """
    Args and kwargs need to be given in the same fashion as Graph.load takes them.
    """
    gra = Graph(grafptr)
    gra.load(*args, **kwargs)
    return gra


def graph_alloc():
    return Graph(init=False)


class Graph:
    """
    Caution, mutating the given np.arrays voids your warranty.
    The use of np.array(copy=True) is recommended otherwise.
    The constructor doesn't build a viable graph, .load or .build has to be
    called afterwards.
    `build_graph` or `load_graph` both return viable graphs.
    """

    # Dummy structure
    class _GraphStruct(ctypes.Structure):
        _fields_ = [("dummy", ctypes.c_char * _common.libscotch.SCOTCH_graphSizeof())]

    _exitval = True  # indicates if the graph is able to get inited
    _readableattrs = (
        "baseval",
        "vertnbr",
        "verttab",
        "vendtab",
        "velotab",
        "vlbltab",
        "edgenbr",
        "edgetab",
        "edlotab",
    )
    _grafptr = None
    _baseval = None
    _vertnbr = None
    _verttab = None
    _vendtab = None
    _velotab = None
    _vlbltab = None
    _edgenbr = None
    _edgetab = None
    _edlotab = None

    def __getattr__(self, name):
        name = str(name)
        if name in self._readableattrs:
            return getattr(self, "_" + name)
        raise AttributeError(f"'{type(self)}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        name = str(name)
        if name in self._readableattrs:
            raise AttributeError("The {} attribute is read-only.".format(name))
        super().__setattr__(name, value)

    def __init__(self, grafptr=None, init=True):
        if not grafptr:
            _common.libscotch.SCOTCH_graphAlloc.restype = ctypes.POINTER(
                self._GraphStruct
            )
            grafptr = _common.libscotch.SCOTCH_graphAlloc()
        self._grafptr = grafptr
        if init:
            self.init()

    def init(self):
        if not self._exitval:
            # raise Exception("You need to exit a graph before re-initing it.")
            # let's be nice
            self.exit()
        self._exitval = False
        _common.libscotch.SCOTCH_graphInit(self._grafptr)  # graphExit mirror

    def base(self, baseval):
        rv = _common.libscotch.SCOTCH_graphBase(
            self._grafptr, _common.proper_int(baseval)
        )
        self._data(store=True)
        return rv

    def build(
        self,  # gives the grafptr
        baseval=None,
        vertnbr=None,
        verttab=None,
        vendtab=None,
        velotab=None,
        vlbltab=None,
        edgenbr=None,
        edgetab=None,
        edlotab=None,
    ):
        if (edgetab is None) or (verttab is None):
            raise ValueError("Both edgetab and verttab need to be given")
        self._edgetab = _common.properly_format(edgetab)
        self._verttab = _common.properly_format(verttab)
        self._vendtab = _common.properly_format(vendtab)
        if isinstance(self._verttab, np.ndarray) and isinstance(
            self._vendtab, np.ndarray
        ):
            if self._verttab.size > self._vendtab.size + 1:
                raise ValueError("If given, verttab must not be longer than vendtab+1")
        self._edlotab = _common.properly_format(edlotab)
        self._velotab = _common.properly_format(velotab)
        if baseval:
            self._baseval = baseval
        elif not vendtab and isinstance(self._verttab, np.ndarray):
            self._baseval = verttab[0]
        else:
            raise ValueError(
                "Baseval must be given in a non-compact graph or\
                              when verttab is not an Iterable"
            )
        if vertnbr is None:
            if not isinstance(self._verttab, np.ndarray):  # verttab has no size
                raise TypeError("Vertnbr must be given when verttab is not an Iterable")
            else:
                self._vertnbr = self._verttab.size - 1
        else:  # vertnbr is given
            self._vertnbr = vertnbr
        if edgenbr is None:
            if not isinstance(self._edgetab, np.ndarray):  # verttab has no size
                raise TypeError("Edgenbr must be given when verttab is not an Iterable")
            elif vendtab is not None:  # non-compact graph
                self._edgenbr = sum(
                    [
                        self._vendtab[i] - self._verttab[i]
                        for i in range(self._vendtab.size)
                    ]
                )
            else:  # compact graph
                self._edgenbr = self._verttab[-1] - self._baseval
        else:  # edgenbr is given
            self._edgenbr = edgenbr
        self._vlbltab = _common.properly_format(vlbltab)
        if _common.libscotch.SCOTCH_graphBuild(
            self._grafptr,
            _common.proper_int(self._baseval),
            _common.proper_int(self._vertnbr),
            _common.array_to_pointer(self._verttab),
            _common.array_to_pointer(self._vendtab),
            _common.array_to_pointer(self._velotab),
            _common.array_to_pointer(self._vlbltab),
            _common.proper_int(self._edgenbr),
            _common.array_to_pointer(self._edgetab),
            _common.array_to_pointer(self._edlotab),
        ):
            raise LibraryError("graphBuild")
        if self.check():
            raise LibraryError(
                msg="Graph check revealed discrepancies in data integrity"
            )

    def build_from_csgraph(self, csg):
        return self.build(edlotab=csg.data, edgetab=csg.indices, verttab=csg.indptr)

    def load(self, stream, baseval=-1, flagval=0):
        """
        `stream` being either a file object (result of an `open()`, don't forget to close it)
        or a filename, as a string or as a bytes object (such as b"file/name").
        """
        if isinstance(stream, (str, bytes)):
            with open(stream) as st:
                return self.load(st, baseval, flagval)
        interngptr = _common.libscotch.SCOTCH_graphAlloc()
        _common.libscotch.SCOTCH_graphInit(interngptr)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphLoad(interngptr, filep, baseval, flagval):
            raise LibraryError("graphLoad")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)
        data = self._data(grafptr=interngptr, store=False)
        for key, val in data.items():
            if val is not None and isinstance(val, _common.Iterable):
                data[key] = np.array(val, copy=True)
        _common.libscotch.SCOTCH_graphExit(interngptr)
        self.build(**data)

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
        if _common.libscotch.SCOTCH_graphSave(self._grafptr, filep):
            raise LibraryError("graphSave")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def __del__(self):
        self.exit()
        _common.libscotch.SCOTCH_memFree(self._grafptr)

    def exit(self):
        if not self._exitval:
            _common.libscotch.SCOTCH_graphExit(self._grafptr)  # graphInit mirror
            self._exitval = True
            for attrname in self._readableattrs:
                setattr(self, "".join(("_", attrname)), None)

    def free(self):
        self.exit()
        self.init()

    def check(self):
        return _common.libscotch.SCOTCH_graphCheck(self._grafptr)

    def _data(self, grafptr=None, store=False):
        """
        Reads the 9 values from the C structure with SCOTCH_graphData,
        stores them in their respective attributes (if `store`)
        and returns them as a dict.
        If no grafptr is given as grafptr, this graph's grafptr is used.
        """
        argue = (
            [_common.proper_int() for k in range(2)]
            + [ctypes.pointer(_common.proper_int()) for k in range(4)]
            + [_common.proper_int()]
            + [ctypes.pointer(_common.proper_int()) for k in range(2)]
        )
        _common.libscotch.SCOTCH_graphData(
            grafptr or self._grafptr, *(ctypes.byref(arg) for arg in argue)
        )
        argue = dict(zip(self._readableattrs, argue))
        return_value = dict()
        for key, val in argue.items():
            if isinstance(val, _common.proper_int):
                if store:
                    setattr(self, "_" + key, val.value)
                return_value[key] = val.value
        arraysize = {}  # matches each array name with its size
        arraysize["verttab"] = return_value["vertnbr"]
        arraysize["vendtab"] = return_value["vertnbr"]
        arraysize["velotab"] = return_value["vertnbr"]
        arraysize["vlbltab"] = return_value["vertnbr"]
        arraysize["edgetab"] = return_value["edgenbr"]
        arraysize["edlotab"] = arraysize["edgetab"]
        if ctypes.addressof(argue["verttab"].contents) == (
            ctypes.addressof(argue["vendtab"].contents) - _common.num_sizeof()
        ):
            # if the graph is compact, it stays that way
            arraysize["verttab"] += 1
            del argue["vendtab"]
        for key, val in argue.items():
            if isinstance(val, ctypes.POINTER(_common.proper_int)):
                try:
                    arey = np.ctypeslib.as_array(val, (arraysize[key],))
                except ValueError:  # if the pointer is NULL
                    if store:
                        setattr(self, "_" + key, None)
                    return_value[key] = None
                else:  # if no ValueError has appened
                    if store:
                        setattr(self, "_" + key, arey)
                    return_value[key] = arey
        return return_value

    def data(self, as_dict=False):  # serves as grafptr
        """
        The values are returned as a 9-element tuple
        or as a dict, if requested with the `as_dict` parameter
        """
        return_value = tuple(getattr(self, attr) for attr in self._readableattrs)
        if as_dict:
            return dict(zip(self._readableattrs, return_value))
        return return_value

    def diam_pv(self):
        return_value = _common.libscotch.SCOTCH_graphDiamPV(self._grafptr)
        if return_value == -1:
            raise LibraryError("graphDiamPV")
        return return_value

    if _matplotlib_found and _nx_found:
        def draw(self, **kwargs):
            nx.draw(self.tonx(), **kwargs)
            plt.show()

    def stat(self, as_dict=False):
        """
        The values are returned as a 14-element tuple
        or as a dict, if requested with the `as_dict` parameter
        """
        argue = (
            [_common.proper_int() for k in range(3)]
            + [ctypes.c_double() for k in range(2)]
            + [_common.proper_int() for k in range(2)]
            + [ctypes.c_double() for k in range(2)]
            + [_common.proper_int() for k in range(3)]
            + [ctypes.c_double() for k in range(2)]
        )
        _common.libscotch.SCOTCH_graphStat(
            self._grafptr, *(ctypes.byref(arg) for arg in argue)
        )
        values = tuple(arg.value for arg in argue)
        if as_dict:
            values = dict(
                zip(
                    (
                        "velomin",
                        "velomax",
                        "velosum",
                        "veloavg",
                        "velodlt",
                        "degrmin",
                        "degrmax",
                        "degravg",
                        "degrdlt",
                        "edlomin",
                        "edlomax",
                        "edlosum",
                        "edloavg",
                        "edlodlt",
                    ),
                    values,
                )
            )
        return values

    def size(self, as_dict=False):
        """
        The values are returned as a 2-element tuple
        or as a dict, if requested with the `as_dict` parameter
        """
        return_value = (self.vertnbr, self.edgenbr)
        if as_dict:
            return_value = dict(zip(("vertnbr", "edgenbr"), return_value))
        return return_value

    def induce_list(self, vnumnbr, vnumtab, indgraf):
        if _common.libscotch.SCOTCH_graphInduceList(
            self._grafptr,
            _common.proper_int(vnumnbr),
            _common.array_to_pointer(vnumtab),
            indgraf._grafptr,
        ):
            raise LibraryError("graphInduceList")
        indgraf._data(store=True)

    def induce_part(self, vnumnbr, vnumtab, partval, indgraf):
        if _common.libscotch.SCOTCH_graphInducePart(
            self._grafptr,
            _common.proper_int(vnumnbr),
            _common.array_to_pointer(vnumtab),
            _common.proper_int(partval),
            indgraf._grafptr,
        ):
            raise LibraryError("graphInducePart")
        indgraf._data(store=True)

    def map_init(self, mapping, arch, parttab=None):
        if parttab is not None:
            parttabnew = _common.properly_format(parttab)
        mapping.register(self, parttab=parttabnew)
        if _common.libscotch.SCOTCH_graphMapInit(
            self._grafptr,
            mapping._mappptr,
            arch._archptr,
            _common.array_to_pointer(parttabnew),
        ):
            raise LibraryError("graphMapInit")
        if parttabnew is not None:
            if parttab is not None:
                try:
                    parttab[:] = parttabnew[:]
                except TypeError:
                    pass

    def map_exit(self, mapping):
        mapping.unregister()
        _common.libscotch.SCOTCH_graphMapExit(self._grafptr, mapping._mappptr)

    def map_compute(self, mapping, strat):
        if _common.libscotch.SCOTCH_graphMapCompute(
            self._grafptr, mapping._mappptr, strat._straptr
        ):
            raise LibraryError("graphMapCompute")

    def map_fixed_compute(self, mapping, strat):
        if _common.libscotch.SCOTCH_graphMapFixedCompute(
            self._grafptr, mapping._mappptr, strat._straptr
        ):
            raise LibraryError("graphMapFixedCompute")

    def remap_compute(self, mapping, mapo, emraval, vmlotab, strat):
        if _common.libscotch.SCOTCH_graphRemapCompute(
            self._grafptr,
            mapping._mappptr,
            mapo._mappptr,
            ctypes.c_double(emraval),
            _common.array_to_pointer(vmlotab),
            strat._straptr,
        ):
            raise LibraryError("graphRemapCompute")

    def remap_fixed_compute(self, mapping, mapo, emraval, vmlotab, strat):
        if _common.libscotch.SCOTCH_graphRemapFixedCompute(
            self._grafptr,
            mapping._mappptr,
            mapo._mappptr,
            ctypes.c_double(emraval),
            _common.array_to_pointer(vmlotab),
            strat._straptr,
        ):
            raise LibraryError("graphRemapFixedCompute")

    def map_load(self, mapping, stream):
        if isinstance(stream, (str, bytes)):
            with open(stream) as st:
                return self.map_load(mapping, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphMapLoad(
            self._grafptr, mapping._mappptr, filep
        ):
            raise LibraryError("graphMapLoad")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def map_save(self, mapping, stream):
        if isinstance(stream, (str, bytes)):
            with open(stream, "w+") as st:
                return self.map_save(mapping, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphMapSave(
            self._grafptr, mapping._mappptr, filep
        ):
            raise LibraryError("graphMapSave")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def map_view(self, mapping, stream):
        if isinstance(stream, (str, bytes)):
            with open(stream, "w+") as st:
                return self.map_view(mapping, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphMapView(
            self._grafptr, mapping._mappptr, filep
        ):
            raise LibraryError("graphMapView")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

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
        if _common.libscotch.SCOTCH_graphOrder(
            self._grafptr,
            strat._straptr,
            _common.array_to_pointer(permtab),
            _common.array_to_pointer(peritab),
            ctypes.byref(cblknbr),
            _common.array_to_pointer(rangtab),
            _common.array_to_pointer(treetab),
        ):
            raise LibraryError("graphOrder")

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
        if _common.libscotch.SCOTCH_graphOrderInit(
            self._grafptr,
            ordering._ordeptr,
            permtab,
            peritab,
            ctypes.byref(cblknbr),
            rangtab,
            treetab,
        ):
            raise LibraryError("graphOrderInit")
        rv = [
            permtab[:] if permtab is not None else None,
            peritab[:] if peritab is not None else None,
            cblknbr.value if cblknbr is not None else None,
            rangtab[:] if rangtab is not None else None,
            treetab[:] if treetab is not None else None,
        ]
        ordering.register(self, *rv)

    def order_exit(self, ordering):
        ordering.unregister()
        if _common.libscotch.SCOTCH_graphOrderExit(self._grafptr, ordering._ordeptr):
            raise LibraryError("graphOrderExit")

    def order_check(self, ordering):
        if _common.libscotch.SCOTCH_graphOrderCheck(self._grafptr, ordering._ordeptr):
            raise LibraryError("graphOrderCheck")

    def order_compute(self, ordering, strat):

        if _common.libscotch.SCOTCH_graphOrderCompute(
            self._grafptr, ordering._ordeptr, strat._straptr
        ):
            raise LibraryError("graphOrderCompute")

    def order_compute_list(self, ordering, listtab, strat):
        """
        The listnbr is taken from listtab's length.
        """
        if _common.libscotch.SCOTCH_graphOrderComputeList(
            self._grafptr,
            ordering._ordeptr,
            len(listtab),
            _common.array_to_pointer(listtab),
            strat._straptr,
        ):
            raise LibraryError("graphOrderComputeList")

    def order_load(self, ordering, stream):
        if isinstance(stream, (str, bytes)):
            with open(stream) as st:
                return self.order_load(ordering, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphOrderLoad(
            self._grafptr, ordering._ordeptr, filep
        ):
            raise LibraryError("graphOrderLoad")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def order_save(self, ordering, stream):
        if isinstance(stream, (str, bytes)):
            with open(stream, "w+") as st:
                return self.order_save(ordering, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphOrderSave(
            self._grafptr, ordering._ordeptr, filep
        ):
            raise LibraryError("graphOrderSave")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def order_save_map(self, ordering, stream):
        if isinstance(stream, (str, bytes)):
            with open(stream, "w+") as st:
                return self.order_save_map(ordering, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphOrderSaveMap(
            self._grafptr, ordering._ordeptr, filep
        ):
            raise LibraryError("graphOrderSaveMap")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def order_save_tree(self, ordering, stream):
        if isinstance(stream, (str, bytes)):
            with open(stream, "w+") as st:
                return self.order_save_tree(ordering, st)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphOrderSaveTree(
            self._grafptr, ordering._ordeptr, filep
        ):
            raise LibraryError("graphOrderSaveTree")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def coarsen(self, coarvertnbr, coarrat, flagval, coargraf, coarmulttab=None):
        """
        Raises CannotCoarsen if not because of threshold parameters,
        raises LibraryError otherwise.
        """
        coarmulttabnew = _common.array_to_c_array(
            coarmulttab, max(len(coarmulttab), 2 * self.vertnbr)
        )
        rv = _common.libscotch.SCOTCH_graphCoarsen(
            self._grafptr,
            _common.proper_int(coarvertnbr),
            ctypes.c_double(coarrat),
            _common.proper_int(flagval),
            coargraf._grafptr,
            ctypes.byref(coarmulttabnew),
        )
        coargraf._data(store=True)
        if rv:
            if rv == 1:
                raise CannotCoarsen
            raise LibraryError("graphCoarsen")
        if coarmulttab is not None:
            try:
                coarmulttab[:] = coarmulttabnew[:]  # replacing each element
            except:
                pass

    def coarsen_match(self, coarvertnbr, coarrat, flagval, finematetab=None):
        """
        Modifies finematetab in-place if successfully created,
        raises CannotCoarsen if not because of threshold parameters,
        raises LibraryError otherwise.
        Returns coarvertnbr.
        """
        finematetabnew = _common.array_to_c_array(
            finematetab, max(len(finematetab), self.vertnbr)
        )
        coarvertnbrnew = _common.proper_int(coarvertnbr)
        rv = _common.libscotch.SCOTCH_graphCoarsenMatch(
            self._grafptr,
            ctypes.byref(coarvertnbrnew),
            ctypes.c_double(coarrat),
            _common.proper_int(flagval),
            finematetabnew,
        )
        if rv:
            if rv == 1:
                raise CannotCoarsen
            raise LibraryError("graphCoarsenMatch")
        if finematetab is not None:
            try:
                finematetab.clear()
                finematetab.extend(finematetabnew)
            except TypeError:
                pass
        return coarvertnbrnew.value

    def coarsen_build(self, coarvertnbr, finematetab, coargraf, coarmulttab=None):
        finematetabnew = _common.array_to_c_array(
            finematetab, max(len(finematetab), self.vertnbr)
        )
        coarmulttabnew = _common.array_to_c_array(
            coarmulttab, max(len(coarmulttab), 2 * coarvertnbr)
        )
        if _common.libscotch.SCOTCH_graphCoarsenBuild(
            self._grafptr,
            _common.proper_int(coarvertnbr),
            finematetabnew,
            coargraf._grafptr,
            coarmulttabnew,
        ):
            raise LibraryError("graphCoarsenBuild")
        coargraf._data(store=True)
        for tab, tabnew in (
            (finematetab, finematetabnew),
            (coarmulttab, coarmulttabnew),
        ):
            if tab is not None:
                try:
                    tab.clear()
                    tab.extend(tabnew)
                except TypeError:
                    pass

    def color(self, colotab=None, flagval=0):
        """
        If colotab is given as a list or an array of integers, it is updated with the returned values.
        The colonbr value can be obtained by applying the max() function to colotab.
        """
        if colotab is None:
            colotab = [-1 for _ in range(self._vertnbr)]
        colonbr = _common.proper_int(len(colotab))
        colotbb = _common.array_to_pointer(colotab)
        if _common.libscotch.SCOTCH_graphColor(
            self._grafptr, colotbb, ctypes.byref(colonbr), _common.proper_int(flagval)
        ):
            raise LibraryError("graphColor")
        try:
            colotab[:] = colotbb[: len(colotab)]
        except TypeError:
            pass
        return colotbb[: len(colotab)]

    def tab_load(self, stream, parttab=None):

        if isinstance(stream, (str, bytes)):
            with open(stream) as st:
                return self.tab_load(parttab, st)
        if parttab is None:
            parttabnew = (_common.proper_int * self._vertnbr)()
        else:
            parttabnew = (_common.proper_int * max(len(parttab), self._vertnbr))(
                *parttab
            )
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphTabLoad(
            self._grafptr, _common.array_to_pointer(parttab), filep
        ):
            raise LibraryError("graphTabLoad")
        _common.libc.fflush(filep)
        if parttab is not None:
            try:
                parttab[:] = parttabnew[:]  # replacing each element
            except TypeError:
                pass
    if _nx_found:
        def tonx(self):
             vertnbr = self._vertnbr
             verttab = self._verttab
             edgetab = self._edgetab
             baseval = 0 if self._baseval is None else self._baseval
             edlotab = self._edlotab
             g = nx.Graph()
             g.add_nodes_from(range(baseval, vertnbr+baseval))
             for i in range(baseval, vertnbr+baseval):
               for ind in range(verttab[i-baseval],verttab[i+1-baseval]):
                   j = ind - baseval
                   g.add_edge(i,edgetab[j], weight = None if edlotab is None else edlotab[j])
             return g

    def tab_save(self, stream, parttab=None):
        if isinstance(stream, (str, bytes)):
            with open(stream, "w+") as st:
                return self.tab_save(parttab, st)
        parttabnew = _common.array_to_pointer(parttab)
        stream.flush()
        nfileno = _common.libc.dup(stream.fileno())
        filep = _common.libc.fdopen(nfileno, stream.mode.encode())
        if _common.libscotch.SCOTCH_graphTabSave(self._grafptr, parttabnew, filep):
            raise LibraryError("graphTabSave")
        _common.libc.fflush(filep)
        _common.libc.fclose(filep)

    def geom_load_chac(self, geom, grafstream, geomstream, string):
        if isinstance(grafstream, (str, bytes)):
            with open(grafstream) as st:
                return self.geom_load_chac(geom, st, geomstream, string)
        if isinstance(geomstream, (str, bytes)):
            with open(geomstream) as st:
                return self.geom_load_chac(geom, grafstream, st, string)

        interngraptr = _common.libscotch.SCOTCH_graphAlloc()
        interngeoptr = _common.libscotch.SCOTCH_geomAlloc()
        _common.libscotch.SCOTCH_graphInit(interngraptr)
        _common.libscotch.SCOTCH_geomInit(interngeoptr)
        grafstream.flush()
        geomstream.flush()
        nfilenogra = _common.libc.dup(grafstream.fileno())
        nfilenogeo = _common.libc.dup(geomstream.fileno())
        filepgra = _common.libc.fdopen(nfilenogra, grafstream.mode.encode())
        filepgeo = _common.libc.fdopen(nfilenogeo, geomstream.mode.encode())

        if _common.libscotch.SCOTCH_graphGeomLoadChac(
            interngraptr, interngeoptr, grafstream, geomstream, ctypes.c_char_p(string)
        ):
            raise LibraryError("graphGeomLoadChac")
        _common.libc.fflush(filepgra)
        _common.libc.fflush(filepgeo)
        geom._data(interngeoptr, store=True)
        data = self._data(grafptr=interngraptr, store=False)
        for key, val in data.items():
            if val is not None and isinstance(val, _common.Iterable):
                data[key] = np.array(val, copy=True)
        _common.libscotch.SCOTCH_graphExit(interngraptr)
        _common.libscotch.SCOTCH_geomExit(interngeoptr)
        self.build(**data)

    def geom_load_habo(self, geom, grafstream, geomstream, string):
        if isinstance(grafstream, (str, bytes)):
            with open(grafstream) as st:
                return self.geom_load_habo(geom, st, geomstream, string)
        if isinstance(geomstream, (str, bytes)):
            with open(geomstream) as st:
                return self.geom_load_habo(geom, grafstream, st, string)

        interngraptr = _common.libscotch.SCOTCH_graphAlloc()
        interngeoptr = _common.libscotch.SCOTCH_geomAlloc()
        _common.libscotch.SCOTCH_graphInit(interngraptr)
        _common.libscotch.SCOTCH_geomInit(interngeoptr)
        grafstream.flush()
        geomstream.flush()
        nfilenogra = _common.libc.dup(grafstream.fileno())
        nfilenogeo = _common.libc.dup(geomstream.fileno())
        filepgra = _common.libc.fdopen(nfilenogra, grafstream.mode.encode())
        filepgeo = _common.libc.fdopen(nfilenogeo, geomstream.mode.encode())

        if _common.libscotch.SCOTCH_graphGeomLoadHabo(
            interngraptr, interngeoptr, grafstream, geomstream, ctypes.c_char_p(string)
        ):
            raise LibraryError("graphGeomLoadHabo")
        _common.libc.fflush(filepgra)
        _common.libc.fflush(filepgeo)
        geom._data(interngeoptr, store=True)
        data = self._data(grafptr=interngraptr, store=False)
        for key, val in data.items():
            if val is not None and isinstance(val, _common.Iterable):
                data[key] = np.array(val, copy=True)
        _common.libscotch.SCOTCH_graphExit(interngraptr)
        _common.libscotch.SCOTCH_geomExit(interngeoptr)
        self.build(**data)

    def geom_load_scot(self, geom, grafstream, geomstream, string):
        if isinstance(grafstream, (str, bytes)):
            with open(grafstream) as st:
                return self.geom_load_scot(geom, st, geomstream, string)
        if isinstance(geomstream, (str, bytes)):
            with open(geomstream) as st:
                return self.geom_load_scot(geom, grafstream, st, string)

        interngraptr = _common.libscotch.SCOTCH_graphAlloc()
        interngeoptr = _common.libscotch.SCOTCH_geomAlloc()
        _common.libscotch.SCOTCH_graphInit(interngraptr)
        _common.libscotch.SCOTCH_geomInit(interngeoptr)
        grafstream.flush()
        geomstream.flush()
        nfilenogra = _common.libc.dup(grafstream.fileno())
        nfilenogeo = _common.libc.dup(geomstream.fileno())
        filepgra = _common.libc.fdopen(nfilenogra, grafstream.mode.encode())
        filepgeo = _common.libc.fdopen(nfilenogeo, geomstream.mode.encode())

        if _common.libscotch.SCOTCH_graphGeomLoadScot(
            interngraptr, interngeoptr, grafstream, geomstream, ctypes.c_char_p(string)
        ):
            raise LibraryError("graphGeomLoadScot")
        _common.libc.fflush(filepgra)
        _common.libc.fflush(filepgeo)
        geom._data(interngeoptr, store=True)
        data = self._data(grafptr=interngraptr, store=False)
        for key, val in data.items():
            if val is not None and isinstance(val, _common.Iterable):
                data[key] = np.array(val, copy=True)
        _common.libscotch.SCOTCH_graphExit(interngraptr)
        _common.libscotch.SCOTCH_geomExit(interngeoptr)
        self.build(**data)

    def geom_save_chac(self, geom, grafstream, geomstream, string):
        if isinstance(grafstream, (str, bytes)):
            with open(grafstream) as st:
                return self.geom_save_chac(geom, st, geomstream, string)
        if isinstance(geomstream, (str, bytes)):
            with open(geomstream) as st:
                return self.geom_save_chac(geom, grafstream, st, string)
        grafstream.flush()
        geomstream.flush()
        nfilenogra = _common.libc.dup(grafstream.fileno())
        nfilenogeo = _common.libc.dup(geomstream.fileno())
        filepgra = _common.libc.fdopen(nfilenogra, grafstream.mode.encode())
        filepgeo = _common.libc.fdopen(nfilenogeo, geomstream.mode.encode())
        if _common.libscotch.SCOTCH_graphGeomSaveChac(
            self._grafptr,
            geom._geomptr,
            grafstream,
            geomstream,
            ctypes.c_char_p(string),
        ):
            raise LibraryError("graphGeomSaveChac")
        _common.libc.fflush(filepgra)
        _common.libc.fflush(filepgeo)

    def geom_save_scot(self, geom, grafstream, geomstream, string):
        if isinstance(grafstream, (str, bytes)):
            with open(grafstream) as st:
                return self.geom_save_scot(geom, st, geomstream, string)
        if isinstance(geomstream, (str, bytes)):
            with open(geomstream) as st:
                return self.geom_save_scot(geom, grafstream, st, string)
        grafstream.flush()
        geomstream.flush()
        nfilenogra = _common.libc.dup(grafstream.fileno())
        nfilenogeo = _common.libc.dup(geomstream.fileno())
        filepgra = _common.libc.fdopen(nfilenogra, grafstream.mode.encode())
        filepgeo = _common.libc.fdopen(nfilenogeo, geomstream.mode.encode())
        if _common.libscotch.SCOTCH_graphGeomSaveScot(
            self._grafptr,
            geom._geomptr,
            grafstream,
            geomstream,
            ctypes.c_char_p(string),
        ):
            raise LibraryError("graphGeomSaveScot")
        _common.libc.fflush(filepgra)
        _common.libc.fflush(filepgeo)


for _stringmethodname, _docstring in (
    (
        "",
        "This routine computes a partition of the given graph structure, with respect to the given strategy.",
    ),
    (
        "fixed",
        "This routine computes a partition of the given graph structure with respect to the given strategy and the fixed vertices in maptab.",
    ),
    (
        "ovl",
        "This routine computes a partition with overlap of the given graph structure, with respect to the given strategy.",
    ),
):

    def _graph_part_method(graf, partnbr, strat=None, parttab=None, methname=None):
        strat = strat or _strat.Strat(init=True)
        parttabnew = _common.array_to_c_array(parttab, max(len(parttab), graf.vertnbr))
        libfunc = getattr(_common.libscotch, "SCOTCH_graphPart" + methname.capitalize())
        if libfunc(
            graf._grafptr,
            _common.proper_int(partnbr),
            strat._straptr,
            ctypes.byref(parttabnew),
        ):
            raise LibraryError("graphPart" + methname.capitalize())
        if parttab is not None:
            try:
                parttab[:] = parttabnew
            except TypeError:
                pass

    _gloname = (
        "_".join(("graph_part", _stringmethodname))
        if _stringmethodname
        else "graph_part"
    )
    globals()[_gloname] = _common.wrap(
        _common.curry(_graph_part_method, methname=_stringmethodname),
        __name__=_gloname,
        __doc__=_docstring,
    )
    setattr(
        Graph,
        "_".join(("part", _stringmethodname)) if _stringmethodname else "part",
        _common.wrap(
            _common.curry(_graph_part_method, methname=_stringmethodname),
            __name__="_".join(("part", _stringmethodname)),
            __doc__=_docstring,
        ),
    )

for _stringmethodname, _docstring in (
    ("", ""),
    ("fixed", " and the fixed vertices in maptab"),
):
    # Graph.repart
    def _graph_repart_method(
        self,
        partnbr,
        parotab,
        emraval,
        vmlotab,
        strat=None,
        parttab=None,
        methname=None,
    ):
        strat = strat or _strat.Strat(init=True)
        parttabnew = _common.array_to_c_array(parttab, max(len(parttab), self.vertnbr))
        libfunc = getattr(
            _common.libscotch, "SCOTCH_graphRepart" + methname.capitalize()
        )
        if libfunc(
            self._grafptr,
            _common.proper_int(partnbr),
            _common.array_to_pointer(parotab),
            ctypes.c_double(emraval),
            _common.array_to_pointer(vmlotab),
            strat._straptr,
            ctypes.byref(parttabnew),
        ):
            raise LibraryError("graphRepart" + methname.capitalize())
        if parttab is not None:
            try:
                parttab[:] = parttabnew
            except TypeError:
                pass

    _docstring = "".join(
        (
            "This routine computes a repartitionning of the given graph structure",
            "with respect to the given strategy",
            _docstring,
            ".",
        )
    )
    setattr(
        Graph,
        "_".join(("repart", _stringmethodname)) if _stringmethodname else "repart",
        _common.wrap(
            _common.curry(_graph_repart_method, methname=_stringmethodname),
            __name__="_".join(("repart", _stringmethodname)),
            __doc__=_docstring,
        ),
    )

    # Graph.map
    def _graph_map_method(self, arch, strat=None, parttab=None, methname=None):
        strat = strat or _strat.Strat(init=True)
        parttabnew = _common.array_to_c_array(parttab, max(len(parttab), self.vertnbr))
        libfunc = getattr(_common.libscotch, "SCOTCH_graphMap" + methname.capitalize())
        if libfunc(
            self._grafptr, arch._archptr, strat._straptr, ctypes.byref(parttabnew)
        ):
            raise LibraryError("graphMap" + methname.capitalize())
        if parttab is not None:
            try:
                parttab[:] = parttabnew
            except TypeError:
                pass

    _docstring = "".join(
        (
            "This routine computes a mapping of the given graph structure onto the",
            "given target architecture with respect to the given strategy",
            _docstring,
            ".",
        )
    )
    setattr(
        Graph,
        "_".join(("map", _stringmethodname)) if _stringmethodname else "map",
        _common.wrap(
            _common.curry(_graph_map_method, methname=_stringmethodname),
            __name__="_".join(("map", _stringmethodname)),
            __doc__=_docstring,
        ),
    )

    # Graph.remap
    def _graph_remap_method(
        self, arch, parotab, emraval, vmlotab, strat=None, parttab=None, methname=None
    ):
        strat = strat or _strat.Strat(init=True)
        parttabnew = _common.array_to_c_array(parttab, max(len(parttab), self.vertnbr))
        libfunc = getattr(
            _common.libscotch, "SCOTCH_graphRemap" + methname.capitalize()
        )
        if libfunc(
            self._grafptr,
            arch._archptr,
            _common.array_to_pointer(parotab),
            ctypes.c_double(emraval),
            _common.array_to_pointer(vmlotab),
            strat._straptr,
            ctypes.byref(parttabnew),
        ):
            raise LibraryError("graphRemap" + methname.capitalize())
        if parttab is not None:
            try:
                parttab[:] = parttabnew
            except TypeError:
                pass

    _docstring = "".join(
        (
            "This routine computes a remapping of the given graph structure onto",
            "the given target architecture with respect to the given strategy",
            _docstring,
            ".",
        )
    )
    setattr(
        Graph,
        "_".join(("remap", _stringmethodname)) if _stringmethodname else "remap",
        _common.wrap(
            _common.curry(_graph_remap_method, methname=_stringmethodname),
            __name__="_".join(("remap", _stringmethodname)),
            __doc__=_docstring,
        ),
    )
