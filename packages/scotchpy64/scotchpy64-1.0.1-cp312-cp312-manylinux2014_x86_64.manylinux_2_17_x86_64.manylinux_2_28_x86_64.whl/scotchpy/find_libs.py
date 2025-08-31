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
import sys
from importlib import resources

# To find the extension
def _find_lib(name, directory = None):
    """
    _find_lib(name, dir) searches for library name in directory
    """
    if sys.platform == "darwin":
         ext = ".dylib"
    else:
         ext = ".so"
    if not directory or not os.path.isdir(directory):
         dir_path = str(resources.files(__package__))
    else:
         dir_path = directory
    for f in os.listdir(dir_path):
        if f.endswith(ext) and (name in f):
            f_with_dir = os.path.join(dir_path, f)
            if os.path.exists(f_with_dir):
                return f_with_dir
    return ""

def _check_lib(name, directory = None):
    """
    Checks that lib `name` in in the directory directory
    """
    if sys.platform == "darwin":
         ext = ".dylib"
    else:
         ext = ".so"
    if not directory or not os.path.isdir(directory):
        dirname = str(resources.files(__package__))
    else:
        dirname = directory
    join_name=os.path.join(dirname, "lib"+ name + ext)
    if os.path.exists(join_name):
        return join_name
    if sys.platform == "darwin":
        join_name_alt=os.path.join(dirname, name + ext)
        if os.path.exists(join_name_alt):
            return join_name_alt
    return ""

# Package with MPI support
_ptscotch_lib = _check_lib("ptscotch", os.environ.get("SCOTCHPY_SCOTCH"))
_libptscotch_mpi4py_lib = _find_lib("libptscotch_mpi4py", os.environ.get("SCOTCHPY_ERR"))
if _ptscotch_lib:
    if not _libptscotch_mpi4py_lib:
        raise Exception("The libptscotch has been found but not the libptscotchmpi4py extension")

# Search for extension
_scotchpy_err_lib = _find_lib("scotchpy_err", os.environ.get("SCOTCHPY_ERR"))
if not _scotchpy_err_lib:
    raise Exception("The scotch_err_py library is not included in the package")

# Search for the Scotch library
_scotch_lib = _check_lib("scotch", os.environ.get("SCOTCHPY_SCOTCH"))
if not _scotch_lib:
    raise Exception("The scotch library is not included in the package")

# Minimal SCOTCH Library version
scotch_minimal_version = (7, 0, 6)
