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

from .find_libs import _ptscotch_lib
from . import common as _common
from . import strat as _strat
from .exception import LibraryError, CannotCoarsen

try:
    from mpi4py import MPI

    flag_mpi4py_available = True
except ImportError:
    flag_mpi4py_available = False


def build_dgraph(*args, dgrafptr=None, **kwargs):
    """
    Args and kwargs need to be given in the same fashion as Graph.build takes them.
    """
    if not flag_mpi4py_available:
        raise ImportError("mpi4py is required to build a distributed graph.")
    gra = DGraph(dgrafptr)
    gra.build(*args, **kwargs)
    return gra


def load_dgraph(*args, dgrafptr=None, **kwargs):
    """
    Args and kwargs need to be given in the same fashion as Graph.load takes them.
    """
    if not flag_mpi4py_available:
        raise ImportError("mpi4py is required to load a distributed graph.")
    gra = DGraph(dgrafptr)
    gra.load(*args, **kwargs)
    return gra


def dgraph_alloc():
    if not flag_mpi4py_available:
        raise ImportError("mpi4py is required to allocate a distributed graph.")
    return DGraph(init=False)


if flag_mpi4py_available:

    class DGraph:
        # dummy structure
        """
        Caution, mutating the given np.arrays voids your warranty.
        The use of np.array(copy=True) is recommended otherwise.
        The constructor doesn't build a viable cgraph, .load or .build has to be
        called afterwards.
        `build_dgraph` or `load_dgraph` both return viable dgraphs.
        """

        class _DGraphStruct(ctypes.Structure):
            _fields_ = [
                ("dummy", ctypes.c_char * _common.libptscotch.SCOTCH_dgraphSizeof())
            ]

        _exitval = True
        _readableattrs = (
            "baseval",
            "vertglbnbr",
            "vertlocnbr",
            "vertlocmax",
            "vertgstnbr",
            "vertloctab",
            "vendloctab",
            "veloloctab",
            "vlblloctab",
            "edgeglbnbr",
            "edgelocnbr",
            "edgelocsiz",
            "edgeloctab",
            "edgegsttab",
            "edloloctab",
        )

        _dgrafptr = None
        _baseval = None
        _vertglbnbr = None
        _vertlocnbr = None
        _vertlocmax = None
        _vertgstnbr = None
        _vertloctab = None
        _vendloctab = None
        _veloloctab = None
        _vlblloctab = None
        _edgelocnbr = None
        _edgeglbnbr = None
        _edgelocsiz = None
        _edgeloctab = None
        _edgegsttab = None
        _edloloctab = None
        _comm = None

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

        def __init__(self, comm, dgrafptr=None, init=True):
            if not dgrafptr:
                _common.libptscotch.SCOTCH_dgraphAlloc.restype = ctypes.POINTER(
                    self._DGraphStruct
                )
                dgrafptr = _common.libptscotch.SCOTCH_dgraphAlloc()
            self._dgrafptr = dgrafptr
            self._comm = comm
            if init:
                self.init(comm)

        def init(self, comm):
            if not self._exitval:
                self.exit()
            self._exitval = False
            # Convert MPI communicator to ctypes
            comm_ptr = MPI._addressof(comm)
            comm_obj = ctypes.c_void_p(comm_ptr)
            # Call the C function
            _common.libhelper.dgraph_load_mpi(self._dgrafptr, comm_obj)

        def build(
            self,
            baseval=None,
            vertglbnbr=None,
            vertlocnbr=None,
            vertlocmax=None,
            vertgstnbr=None,
            vertloctab=None,
            vendloctab=None,
            veloloctab=None,
            vlblloctab=None,
            edgeglbnbr=None,
            edgelocnbr=None,
            edgelocsiz=None,
            edgeloctab=None,
            edgegsttab=None,
            edloloctab=None,
        ):
            if (edgeloctab is None) or (vertloctab is None):
                raise ValueError("Both edgeloctab and vertloctab need to be given")
            self._vertglbnbr = vertglbnbr
            self._vertgstnbr = vertgstnbr
            self._edgeglbnbr = edgeglbnbr
            self._edgeloctab = _common.properly_format(edgeloctab)
            self._vertloctab = _common.properly_format(vertloctab)
            print(self._vertloctab)
            self._vendloctab = _common.properly_format(vendloctab)
            if isinstance(self._vertloctab, np.ndarray) and isinstance(
                self._vendloctab, np.ndarray
            ):
                if self._vertloctab.size > self._vendloctab.size + 1:
                    raise ValueError(
                        "If given, vertloctab must not be longer than vendloctab+1"
                    )
            self._edloloctab = _common.properly_format(edloloctab)
            self._veloloctab = _common.properly_format(veloloctab)
            self._edgegsttab = _common.properly_format(edgegsttab)
            self._vlblloctab = _common.properly_format(vlblloctab)
            if baseval:
                self._baseval = baseval
            elif not vendloctab and isinstance(self._vertloctab, np.ndarray):
                self._baseval = vertloctab[0]
            else:
                raise ValueError(
                    "Baseval must be given in a non-compact dgraph or\
                                when vertloctab is not an Iterable"
                )
            if vertlocnbr is None:
                if not isinstance(
                    self._vertloctab, np.ndarray
                ):  # vertloctab has no size
                    raise TypeError(
                        "Vertlocnbr must be given when vertloctab is not an Iterable"
                    )
                else:
                    self._vertlocnbr = self._vertloctab.size - 1
            else:  # vertlocnbr is given
                self._vertlocnbr = vertlocnbr
            if edgelocnbr is None:
                if not isinstance(
                    self._edgelocnbr, np.ndarray
                ):  # vertloctab has no size
                    raise TypeError(
                        "Edgelocnbr must be given when vertloctab is not an Iterable"
                    )
                elif vendloctab is not None:  # non-compact dgraph
                    self._edgelocnbr = sum(
                        [
                            self._vendloctab[i] - self._vertloctab[i]
                            for i in range(self._vendloctab.size)
                        ]
                    )
                else:  # compact dgraph
                    self._edgelocnbr = self._vertloctab[-1] - self._baseval
            else:  # edgelocnbr is given
                self._edgelocnbr = edgelocnbr
            if vertlocmax is None:
                self._vertlocmax = self._vertlocnbr
            else:
                self._vertlocmax = vertlocmax
            if edgegsttab is not None:
                if isinstance(edgegsttab, np.ndarray):
                    self._edgegsttab = _common.properly_format(edgegsttab)
                else:
                    raise TypeError("edgegsttab must be a numpy array")
            if edgelocsiz is None:
                self._edgelocsiz = self._edgegsttab.size
            else:
                self._edgelocsiz = edgelocsiz
            if _common.libptscotch.SCOTCH_dgraphBuild(
                self._dgrafptr,
                _common.proper_int(self._baseval),
                _common.proper_int(self._vertlocnbr),
                _common.proper_int(self._vertlocmax),
                _common.array_to_pointer(self._vertloctab),
                _common.array_to_pointer(self._vendloctab),
                _common.array_to_pointer(self._veloloctab),
                _common.array_to_pointer(self._vlblloctab),
                _common.proper_int(self._edgelocnbr),
                _common.proper_int(self._edgelocsiz),
                _common.array_to_pointer(self._edgeloctab),
                _common.array_to_pointer(self._edgegsttab),
                _common.array_to_pointer(self._edloloctab),
            ):
                raise LibraryError("dgraphBuild")
            if self.check():
                raise LibraryError(
                    msg="Graph check revealed discrepancies in data integrity"
                )

        def load(self, stream, baseval=-1, flagval=0):
            if stream is not None:
                if isinstance(stream, (str, bytes)):
                    with open(stream) as st:
                        return self.load(st, baseval, flagval)
                stream.flush()
                nfileno = _common.libc.dup(stream.fileno())
                filep = _common.libc.fdopen(nfileno, stream.mode.encode())
            else:
                filep = None
            interngptr = _common.libptscotch.SCOTCH_dgraphAlloc()
            comm_ptr = MPI._addressof(self._comm)
            comm_obj = ctypes.c_void_p(comm_ptr)
            if _common.libhelper.dgraph_load_mpi(interngptr, comm_obj) != 0:
                raise LibraryError("dgraphInit failed")
            if (
                _common.libptscotch.SCOTCH_dgraphLoad(
                    interngptr, filep, ctypes.c_int(baseval), ctypes.c_int(flagval)
                )
                != 0
            ):
                raise LibraryError("dgraphLoad failed")
            if filep is not None:
                _common.libc.fflush(filep)
                _common.libc.fclose(filep)
            data = self._data(dgrafptr=interngptr, store=False)
            for key, val in data.items():
                if val is not None and isinstance(val, _common.Iterable):
                    data[key] = np.array(val, copy=True)
            _common.libptscotch.SCOTCH_dgraphExit(interngptr)
            print(data)
            self.build(**data)

        def save(self, stream):
            if isinstance(stream, (str, bytes)):
                with open(stream, "w") as st:
                    return self.save(st)
            stream.flush()
            nfileno = _common.libc.dup(stream.fileno())
            filep = _common.libc.fdopen(nfileno, stream.mode.encode())
            if _common.libptscotch.SCOTCH_dgraphSave(self._dgrafptr, filep):
                raise LibraryError("dgraphSave")
            _common.libc.fflush(filep)
            _common.libc.fclose(filep)

        def __del__(self):
            self.exit()
            _common.libptscotch.SCOTCH_dgraphFree(self._dgrafptr)

        def exit(self):
            if not self._exitval:
                _common.libptscotch.SCOTCH_dgraphExit(
                    self._dgrafptr
                )  # graphInit mirror
                self._exitval = True
                for attrname in self._readableattrs:
                    setattr(self, "".join(("_", attrname)), None)

        def free(self):
            self.exit()
            self.init()

        def check(self):
            return _common.libptscotch.SCOTCH_dgraphCheck(self._dgrafptr)

        def _data(self, dgrafptr=None, store=False, getComm=True):
            argue = (
                [_common.proper_int() for k in range(5)]                   # baseptr .. vertgstptr
                + [ctypes.pointer(_common.proper_int()) for k in range(4)] # vertloctab .. vlblloctab
                + [_common.proper_int() for k in range(3)]                 # edgeglbptr .. edgelocptz
                + [ctypes.pointer(_common.proper_int()) for k in range(3)] #
            )
            if getComm:
              comm_ptr = MPI._addressof(self._comm)
              comm_obj = ctypes.c_void_p(comm_ptr)
            else:
              comm_obj = None

            _common.libptscotch.SCOTCH_dgraphData(
                  dgrafptr or self._dgrafptr,             # graph
                  *(ctypes.byref(arg) for arg in argue),  # fields to retrieve
                  ctypes.byref(comm_obj)                  # we want possibly the communicator
              )

            argue = dict(zip(self._readableattrs, argue))
            return_value = dict()
            for key, val in argue.items():
                if isinstance(val, _common.proper_int):
                    if store:
                        setattr(self, "_" + key, val.value)
                    return_value[key] = val.value
            arraysize = {}
            arraysize["vertloctab"] = return_value["vertlocnbr"]
            arraysize["vendloctab"] = return_value["vertlocnbr"]
            arraysize["veloloctab"] = return_value["vertlocnbr"]
            arraysize["vlblloctab"] = return_value["vertlocnbr"]
            arraysize["edgeloctab"] = return_value["edgelocsiz"]
            arraysize["edgegsttab"] = return_value["edgelocsiz"]
            arraysize["edloloctab"] = return_value["edgelocnbr"]
            if ctypes.addressof(argue["vertloctab"].contents) == (
                ctypes.addressof(argue["vendloctab"].contents) - _common.num_sizeof()
            ):
                # if the dgraph is compact, it stays that way
                arraysize["vertloctab"] += 1
                del argue["vendloctab"]
            for key, val in argue.items():
                if isinstance(val, ctypes.POINTER(_common.proper_int)):
                    try:
                        arey = np.ctypeslib.as_array(val, (arraysize[key],))
                    except ValueError:  # if the pointer is NULL
                        if store:
                            setattr(self, "_" + key, None)
                        return_value[key] = None
                    else:  # if no ValueError has happened
                        if store:
                            setattr(self, "_" + key, arey)
                        return_value[key] = arey
            return return_value

        def build_grid_3d(self, baseval, dimxval, dimyval, dimzval, incrval, flagval):

            if _common.libptscotch.SCOTCH_dgraphBuildGrid3D(
                self._dgrafptr,
                _common.proper_int(baseval),
                _common.proper_int(dimxval),
                _common.proper_int(dimyval),
                _common.proper_int(dimzval),
                _common.proper_int(incrval),
                _common.proper_int(flagval),
            ):
                raise LibraryError("dgraphBuildGrid3D")

        def data(self, as_dict=False):  # serves as grafptr
            """
            The values are returned as a 15-element tuple
            or as a dict, if requested with the `as_dict` parameter
            """
            return_value = tuple(getattr(self, attr) for attr in self._readableattrs)
            if as_dict:
                return dict(zip(self._readableattrs, return_value))
            return return_value

        def band(self, fronlocnbr, fronloctab, distval, bndgraf):
            if _common.libptscotch.SCOTCH_dgraphBand(
                self._dgrafptr,
                _common.proper_int(fronlocnbr),
                _common.array_to_pointer(fronloctab),
                _common.proper_int(distval),
                bndgraf._dgrafptr,
            ):
                raise LibraryError("dgraphBand")
            bndgraf._data(store=True)

        def coarsen(self, coarnbr, coarrrat, flagval, coargraf):

            coarsen_vert_loc_max = self.coarsen_vert_loc_max(flagval)
            multloctab = np.full(2 * coarsen_vert_loc_max, -1, _common.proper_int)
            multloctabnew = _common.array_to_c_array(multloctab)

            rv = _common.libptscotch.SCOTCH_dgraphCoarsen(
                self._dgrafptr,
                _common.proper_int(coarnbr),
                ctypes.c_double(coarrrat),
                _common.proper_int(flagval),
                coargraf._dgrafptr,
                _common.array_to_pointer(multloctabnew),
            )

            if flagval & _common.COARSENFOLD != _common.COARSENFOLD:
                  coargraf._data(store=True, getComm=True)
            else:
                if self._comm.rank >= (self._comm.size + 1) / 2:
                    coargraf._comm = MPI.COMM_NULL
            if rv:
                if rv == 1:
                    raise CannotCoarsen
                raise LibraryError("dgraphCoarsen")
            return rv, multloctabnew

        def coarsen_vert_loc_max(self, flagval):
            return _common.libptscotch.SCOTCH_dgraphCoarsenVertLocMax(
                self._dgrafptr, _common.proper_int(flagval)
            )

        def gather(self, cgrf):
            if _common.libptscotch.SCOTCH_dgraphGather(self._dgrafptr, cgrf._dgrafptr):
                raise LibraryError("dgraphGather")
            cgrf._data(store=True)

        def induce_part(self, orgpartloctab, indpartval, indvertlocnbr, indgraf):
            if _common.libptscotch.SCOTCH_dgraphInducePart(
                self._dgrafptr,
                _common.array_to_pointer(orgpartloctab),
                _common.array_to_pointer(indpartval),
                _common.proper_int(indvertlocnbr),
                indgraf._dgrafptr,
            ):
                raise LibraryError("dgraphInducePart")
            indgraf._data(store=True)

        def redist(self, partloctab, permgsttab, vertlocdlt, edgelocdlt, redgraf):
            if _common.libptscotch.SCOTCH_dgraphRedist(
                self._dgrafptr,
                _common.array_to_pointer(partloctab),
                _common.array_to_pointer(permgsttab),
                _common.proper_int(vertlocdlt),
                _common.proper_int(edgelocdlt),
                redgraf._dgrafptr,
            ):
                raise LibraryError("dgraphRedist")
            redgraf._data(store=True)

        def scatter(self, cgraf):
            if _common.libptscotch.SCOTCH_dgraphScatter(
                self._dgrafptr, cgraf._dgrafptr
            ):
                raise LibraryError("dgraphScatter")
            cgraf._data(store=True)

        def size(self, as_dict=False):
            return_value = (
                self._vertlocnbr,
                self._vertglbnbr,
                self._edgelocnbr,
                self._edgeglbnbr,
            )
            if as_dict:
                return_value = dict(
                    zip("vertlocnbr", "vertglbnbr", "edgelocnbr", "edgeglbnbr"),
                    return_value,
                )
            return return_value

        def ghst(self):
            if _common.libptscotch.SCOTCH_dgraphGhst(self._dgrafptr):
                raise LibraryError("dgraphGhst")
            self._data(store=True)

        def halo(self, datatab, typeval):
            if isinstance(typeval, MPI.Datatype):
                if _common.libptscotch.SCOTCH_dgraphHalo(
                    self._dgrafptr,
                    _common.array_to_pointer(datatab),
                    ctypes.c_void_p(typeval.Get_handle()),
                ):
                    raise LibraryError("dgraphHalo")
            else:
                raise TypeError("typeval must be an MPI.Datatype")

        def halo_async(self, datatab, typeval, requ):
            if isinstance(typeval, MPI.Datatype):
                if _common.libptscotch.SCOTCH_dgraphHaloAsync(
                    self._dgrafptr,
                    _common.array_to_pointer(datatab),
                    ctypes.c_void_p(typeval.Get_handle()),
                    requ._haloreqptr,
                ):
                    raise LibraryError("dgraphHaloAsync")
            else:
                raise TypeError("typeval must be an MPI.Datatype")

        def halo_wait(requ):
            if _common.libptscotch.SCOTCH_dgraphHaloWait(requ._haloreqptr):
                raise LibraryError("dgraphHaloWait")

        def map(self, arch, strat, partloctab):
            strat = strat or _strat.Strat(init=True)
            if _common.libptscotch.SCOTCH_dgraphMap(
                self._dgrafptr,
                arch._archptr,
                strat._stratptr,
                _common.array_to_pointer(partloctab),
            ):
                raise LibraryError("dgraphMap")

        def map_compute(self, mapping, strat):
            if _common.libptscotch.SCOTCH_dgraphMapCompute(
                self._dgrafptr, mapping._dmappptr, strat._stratptr
            ):
                raise LibraryError("dgraphMapCompute")

        def map_init(self, mapping, arch, partloctab=None):
            parttabnew = _common.array_to_c_array(
                partloctab, max(len(partloctab), self._vertlocnbr)
            )
            if _common.libptscotch.SCOTCH_dgraphMapInit(
                self._dgrafptr,
                mapping._dmappptr,
                arch._archptr,
                _common.array_to_pointer(parttabnew),
            ):
                raise LibraryError("dgraphMapInit")
            if partloctab is not None:
                try:
                    partloctab[:] = parttabnew
                except TypeError:
                    pass

        def map_exit(self, mapping):
            mapping.unregister()
            if _common.libptscotch.SCOTCH_dgraphMapExit(
                self._dgrafptr, mapping._dmappptr
            ):
                raise LibraryError("dgraphMapExit")

        def map_save(self, mapping, stream):
            if isinstance(stream, (str, bytes)):
                with open(stream, "w") as st:
                    return self.map_save(mapping, st)
            stream.flush()
            nfileno = _common.libc.dup(stream.fileno())
            filep = _common.libc.fdopen(nfileno, stream.mode.encode())
            if _common.libptscotch.SCOTCH_dgraphMapSave(
                self._dgrafptr, mapping._dmappptr, filep
            ):
                raise LibraryError("dgraphMapSave")
            _common.libc.fflush(filep)
            _common.libc.fclose(filep)

        def map_view(self, mapping, stream):
            if isinstance(stream, (str, bytes)):
                with open(stream, "w+") as st:
                    return self.map_view(mapping, st)
            stream.flush()
            nfileno = _common.libc.dup(stream.fileno())
            filep = _common.libc.fdopen(nfileno, stream.mode.encode())
            if _common.libscotch.SCOTCH_dgraphMapView(
                self._dgrafptr, mapping._mappptr, filep
            ):
                raise LibraryError("graphMapView")
            _common.libc.fflush(filep)
            _common.libc.fclose(filep)

        def part(self, partnbr, strat=None, partloctab=None):
            strat = strat or _strat.Strat(init=True)
            parttabnew = _common.array_to_c_array(
                partloctab, max(len(partloctab), self._vertlocnbr)
            )
            if _common.libptscotch.SCOTCH_dgraphPart(
                self._dgrafptr,
                _common.proper_int(partnbr),
                strat._stratptr,
                _common.array_to_pointer(parttabnew),
            ):
                raise LibraryError("dgraphPart")
            if partloctab is not None:
                try:
                    partloctab[:] = parttabnew
                except TypeError:
                    pass

        def order_init(self, ordering):
            if _common.libptscotch.SCOTCH_dgraphOrderInit(
                self._dgrafptr, ordering._ordeptr
            ):
                raise LibraryError("dgraphOrderInit")
            ordering.register(self)

        def order_exit(self, ordering):
            ordering.unregister()
            if _common.libptscotch.SCOTCH_dgraphOrderExit(
                self._dgrafptr, ordering._ordeptr
            ):
                raise LibraryError("dgraphOrderExit")

        def order_cblk_dist(self, ordering):
            return _common.libptscotch.SCOTCH_dgraphOrderCblkDist(
                self._dgrafptr, ordering._ordeptr
            )

        def order_compute(self, ordering, strat):
            if _common.libptscotch.SCOTCH_dgraphOrderCompute(
                self._dgrafptr, ordering._ordeptr, strat._stratptr
            ):
                raise LibraryError("dgraphOrderCompute")

        def order_save(self, ordering, stream):
            if isinstance(stream, (str, bytes)):
                with open(stream, "w") as st:
                    return self.order_save(ordering, st)
            stream.flush()
            nfileno = _common.libc.dup(stream.fileno())
            filep = _common.libc.fdopen(nfileno, stream.mode.encode())
            if _common.libptscotch.SCOTCH_dgraphOrderSave(
                self._dgrafptr, ordering._ordeptr, filep
            ):
                raise LibraryError("dgraphOrderSave")
            _common.libc.fflush(filep)
            _common.libc.fclose(filep)

        def order_save_map(self, ordering, stream):
            if isinstance(stream, (str, bytes)):
                with open(stream, "w") as st:
                    return self.order_save_map(ordering, st)
            stream.flush()
            nfileno = _common.libc.dup(stream.fileno())
            filep = _common.libc.fdopen(nfileno, stream.mode.encode())
            if _common.libptscotch.SCOTCH_dgraphOrderSaveMap(
                self._dgrafptr, ordering._ordeptr, filep
            ):
                raise LibraryError("dgraphOrderSaveMap")
            _common.libc.fflush(filep)
            _common.libc.fclose(filep)

        def order_save_tree(self, ordering, stream):
            if isinstance(stream, (str, bytes)):
                with open(stream, "w") as st:
                    return self.order_save_tree(ordering, st)
            stream.flush()
            nfileno = _common.libc.dup(stream.fileno())
            filep = _common.libc.fdopen(nfileno, stream.mode.encode())
            if _common.libptscotch.SCOTCH_dgraphOrderSaveTree(
                self._dgrafptr, ordering._ordeptr, filep
            ):
                raise LibraryError("dgraphOrderSaveTree")
            _common.libc.fflush(filep)
            _common.libc.fclose(filep)

        def order_perm(self, ordering, permloctab=None):
            permloctabnew = _common.array_to_c_array(permloctab, self._vertlocnbr)
            if _common.libptscotch.SCOTCH_dgraphOrderPerm(
                self._dgrafptr,
                ordering._ordeptr,
                _common.array_to_pointer(permloctabnew),
            ):
                raise LibraryError("dgraphOrderPerm")
            if permloctab is not None:
                try:
                    permloctab[:] = permloctabnew
                except TypeError:
                    pass

        def order_tree_dist(self, ordering, treeglbtab=None, sizeglbtab=None):
            treeglbtabnew = _common.array_to_c_array(treeglbtab, self._vertlocnbr)
            sizeglbtabnew = _common.array_to_c_array(sizeglbtab, self._vertlocnbr)
            if _common.libptscotch.SCOTCH_dgraphOrderTreeDist(
                self._dgrafptr,
                ordering._ordeptr,
                _common.array_to_pointer(treeglbtabnew),
                _common.array_to_pointer(sizeglbtabnew),
            ):
                raise LibraryError("dgraphOrderTreeDist")
            try:
                treeglbtab[:] = treeglbtabnew
                sizeglbtab[:] = sizeglbtabnew
            except TypeError:
                pass

        def centralized_order_exit(self, cordering):
            cordering.unregister()
            if _common.libptscotch.SCOTCH_dgraphCentralizeOrderExit(
                self._dgrafptr, cordering._cordptr
            ):
                raise LibraryError("dgraphCentralizeOrderExit")

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
            _common.libptscotch.SCOTCH_dgraphStat(
                self._dgrafptr, *(ctypes.byref(arg) for arg in argue)
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

        def centralized_order_init(
            self,
            cordering,
            permtab=None,
            peritab=None,
            cblknbr=None,
            rangtab=None,
            treetab=None,
        ):
            cblknbr = cblknbr or _common.proper_int()
            if _common.libptscotch.SCOTCH_dgraphCentralizeOrderInit(
                self._dgrafptr,
                cordering._ordeptr,
                _common.array_to_pointer(permtab),
                _common.array_to_pointer(peritab),
                cblknbr,
                _common.array_to_pointer(rangtab),
                _common.array_to_pointer(treetab),
            ):
                raise LibraryError("dgraphCentralizeOrderInit")
            rv = [
                permtab[:] if permtab is not None else None,
                peritab[:] if peritab is not None else None,
                cblknbr.value if cblknbr is not None else None,
                rangtab[:] if rangtab is not None else None,
                treetab[:] if treetab is not None else None,
            ]
            cordering.register(self, *rv)

        def order_gather(self, dordering, cordering):
            if _common.libptscotch.SCOTCH_dgraphOrderGather(
                self._dgrafptr, dordering._ordeptr, cordering._cordptr
            ):
                raise LibraryError("dgraphOrderGather")
            cordering.register(self)

        def grow(self, seedlocnbr, seedloctab, distmax, partgsttab=None):
            if _common.libptscotch.SCOTCH_dgraphGrow(
                self._dgrafptr,
                _common.proper_int(seedlocnbr),
                _common.array_to_pointer(seedloctab),
                _common.proper_int(distmax),
                _common.array_to_pointer(partgsttab),
            ):
                raise LibraryError("dgraphGrow")

    class HaloReq:

        class _HaloReqStruct(ctypes.Structure):
            _fields_ = [
                (
                    "dummy",
                    ctypes.c_char * _common.libptscotch.SCOTCH_dgraphHaloReqSizeof(),
                )
            ]

        _exitval = True
        _haloreqptr = None

        def __init__(self, haloreqptr=None, init=True):
            if not haloreqptr:
                _common.libptscotch.SCOTCH_dgraphHaloReqAlloc.restype = ctypes.POINTER(
                    self._HaloReqStruct
                )
                self._haloreqptr = _common.libptscotch.SCOTCH_dgraphHaloReqAlloc()

            self._haloreqptr = haloreqptr
            if init:
                self.init()
