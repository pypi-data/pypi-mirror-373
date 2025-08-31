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

from .find_libs import _scotchpy_err_lib, _scotch_lib, _ptscotch_lib, scotch_minimal_version
from .common import version
from .exception import *

if version() < scotch_minimal_version:
    raise LibraryError(msg="the SCOTCH library version "
                       +".".join(map(str,version()))
                       +" is not >= to "
                       +".".join(map(str,scotch_minimal_version)))

from .graph import *
from .strat import *
from .arch import *
from .maporder import *
from .context import *
from .mesh import *

from .common import num_sizeof, version
from pathlib import Path

import warnings

STRATDEFAULT = 0x00000
STRATQUALITY = 0x00001
STRATSPEED = 0x00002
STRATBALANCE = 0x00004
STRATSAFETY = 0x00008
STRATSCALABILITY = 0x00010
STRATRECURSIVE = 0x00100
STRATREMAP = 0x00200
STRATLEVELMAX = 0x01000
STRATLEVELMIN = 0x02000
STRATLEAFSIMPLE = 0x04000
STRATSEPASIMPLE = 0x08000
STRATDISCONNECTED = 0x10000
