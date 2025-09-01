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

import enum
from typing import Any, Final, Literal, TypeAlias

import numpy as np
from optype.dlpack import CanDLPackCompat, CanDLPackDevice
from optype.numpy import SequenceND
from typing_extensions import Buffer, CapsuleType, TypeVar, Unpack

_SCT = TypeVar(
    "_SCT",
    bound=np.bool_ | np.number[Any],
    default=np.bool_ | np.number[Any],
)

Device: TypeAlias = Literal["cpu", "cuda"]
Dtype: TypeAlias = np.dtype[_SCT]
NestedSequence: TypeAlias = SequenceND[_T_co]
PyCapsule: TypeAlias = CapsuleType
Shape: TypeAlias = tuple[int, ...] | tuple[int, Unpack[tuple[int | None, ...]]]
SupportsBufferProtocol: TypeAlias = Buffer

class SupportsDLPack(CanDLPackCompat, CanDLPackDevice[enum.Enum, int]): ...

numeric_types: Final[tuple[
    type[np.bool_],
    type[np.int8],
    type[np.int16],
    type[np.int32],
    type[np.int64],
    type[np.uint8],
    type[np.uint16],
    type[np.uint32],
    type[np.uint64],
    type[np.float32],
    type[np.float64],
    type[np.complex64],
    type[np.complex128],
]]

_T_co = TypeVar("_T_co", covariant=True)
