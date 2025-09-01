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

from collections.abc import Sequence
from typing import TypeAlias, TypeVar

from typing_extensions import Unpack

from ._spec_array_object import array
from ._typing import Dtype

def matmul(x1: array[_AtLeast1D], x2: array[_AtLeast1D], /) -> array: ...
def matrix_transpose(
    x: array[_AtLeast2DT, _DTypeT],
    /,
) -> array[_AtLeast2DT, _DTypeT]: ...
def tensordot(
    x1: array,
    x2: array,
    /,
    *,
    axes: int | tuple[Sequence[int], Sequence[int]] = ...,
) -> array: ...
def vecdot(x1: array, x2: array, /, *, axis: int = ...) -> array: ...

_AtLeast1D: TypeAlias = tuple[int, Unpack[tuple[int | None, ...]]]
_Axis: TypeAlias = int | None
_AtLeast2DT = TypeVar(
    "_AtLeast2DT",
    tuple[int, int],
    tuple[int, int, int],
    tuple[int, int, int, int],
    tuple[int, int, int, int, Unpack[tuple[int, ...]]],
    tuple[int, int, int, Unpack[tuple[int, ...]]],
    tuple[int, int, Unpack[tuple[int, ...]]],
    tuple[int, _Axis],
    tuple[int, _Axis, _Axis],
    tuple[int, _Axis, _Axis, _Axis],
    tuple[int, _Axis, _Axis, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, _Axis, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, _Axis, Unpack[tuple[_Axis, ...]]],
)
_DTypeT = TypeVar("_DTypeT", bound=Dtype)
