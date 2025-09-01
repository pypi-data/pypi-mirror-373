# Copyright 2025 hingebase

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

from typing import TypeVar, overload

import numpy as np

@overload
def regularise_to_float(
    t: np.dtype[_CanFloat16],
) -> np.dtype[_CanFloat16 | np.float16]: ...
@overload
def regularise_to_float(
    t: np.dtype[_CanFloat32],
) -> np.dtype[_CanFloat32 | np.float32]: ...
@overload
def regularise_to_float(
    t: np.dtype[_CanFloat64],
) -> np.dtype[_CanFloat64 | np.float64]: ...
@overload
def regularise_to_float(t: np.dtype[_SCT]) -> np.dtype[_SCT]: ...

_CanFloat16 = TypeVar("_CanFloat16", np.int8, np.uint8, np.bool_)
_CanFloat32 = TypeVar("_CanFloat32", np.int16, np.uint16)
_CanFloat64 = TypeVar("_CanFloat64", np.int32, np.uint32, np.int64, np.uint64)
_SCT = TypeVar("_SCT", bound=np.generic)
