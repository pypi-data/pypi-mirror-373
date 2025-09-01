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
from typing import Any, Literal, SupportsIndex, TypeAlias, TypeVar, overload

from typing_extensions import Unpack

from ._spec_array_object import array
from ._typing import Dtype

def broadcast_arrays(*arrays: array) -> list[array]: ...
def broadcast_to(
    x: array[_AtLeast1D, _DTypeT],
    /,
    shape: Sequence[SupportsIndex],
) -> array[Any, _DTypeT]: ...

@overload
def concat(
    arrays: Sequence[array[_IrregularShapeT]],
    /,
    *,
    axis: int = ...,
) -> array[_IrregularShapeT]: ...
@overload
def concat(
    arrays: Sequence[array[_AtLeast1D]],
    /,
    *,
    axis: None,
) -> array[tuple[int]]: ...
@overload
def concat(
    arrays: Sequence[array[_AtLeast1D]],
    /,
    *,
    axis: _Axis,
) -> array[_AtLeast1D]: ...

def expand_dims(
    x: array[Any, _DTypeT],
    /,
    *,
    axis: int = ...,
) -> array[Any, _DTypeT]: ...
def flip(
    x: array[_ShapeT, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
) -> array[_ShapeT, _DTypeT]: ...
def permute_dims(
    x: array[_ShapeT, _DTypeT],
    /,
    axes: tuple[int, ...],
) -> array[_ShapeT, _DTypeT]: ...

@overload
def reshape(
    x: array[Any, _DTypeT],
    /,
    shape: _RegularShapeT,
    *,
    copy: bool | None = ...,
) -> array[_RegularShapeT, _DTypeT]: ...
@overload
def reshape(
    x: array[Any, _DTypeT],
    /,
    shape: SupportsIndex,
    *,
    copy: bool | None = ...,
) -> array[tuple[int], _DTypeT]: ...
@overload
def reshape(
    x: array[Any, _DTypeT],
    /,
    shape: Sequence[SupportsIndex],
    *,
    copy: bool | None = ...,
) -> array[tuple[int, ...], _DTypeT]: ...

@overload
def roll(
    x: array[_AtLeast1DT, _DTypeT],
    /,
    shift: _RegularShapeT,
    *,
    axis: _RegularShapeT,
) -> array[_AtLeast1DT, _DTypeT]: ...
@overload
def roll(
    x: array[_AtLeast1DT, _DTypeT],
    /,
    shift: int,
    *,
    axis: int | tuple[int, ...],
) -> array[_AtLeast1DT, _DTypeT]: ...
@overload
def roll(
    x: array[_AtLeast1DT, _DTypeT],
    /,
    shift: tuple[int],
    *,
    axis: int,
) -> array[_AtLeast1DT, _DTypeT]: ...
@overload
def roll(
    x: array[_2DT, _DTypeT],
    /,
    shift: int,
    *,
    axis: None = ...,
) -> array[_2DT, _DTypeT]: ...
@overload
def roll(
    x: array[tuple[_IntT], _DTypeT],
    /,
    shift: int,
    *,
    axis: None = ...,
) -> array[tuple[Literal[1], _IntT], _DTypeT]: ...

def squeeze(
    x: array[Any, _DTypeT],
    /,
    axis: int | tuple[int, ...],
) -> array[Any, _DTypeT]: ...
def stack(
    arrays: Sequence[array[Any, _DTypeT]],
    /,
    *,
    axis: int = ...,
) -> array[Any, _DTypeT]: ...

_Axis: TypeAlias = int | None
_2DT = TypeVar("_2DT", bound=tuple[int, _Axis])
_AtLeast1D: TypeAlias = tuple[int, Unpack[tuple[int | None, ...]]]
_AtLeast1DT = TypeVar(
    "_AtLeast1DT",
    tuple[int],
    tuple[int, int],
    tuple[int, int, int],
    tuple[int, int, int, int],
    tuple[int, int, int, int, Unpack[tuple[int, ...]]],
    tuple[int, int, int, Unpack[tuple[int, ...]]],
    tuple[int, int, Unpack[tuple[int, ...]]],
    tuple[int, Unpack[tuple[int, ...]]],
    tuple[int, _Axis],
    tuple[int, _Axis, _Axis],
    tuple[int, _Axis, _Axis, _Axis],
    tuple[int, _Axis, _Axis, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, _Axis, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, Unpack[tuple[_Axis, ...]]],
)
_DTypeT = TypeVar("_DTypeT", bound=Dtype)
_IntT = TypeVar("_IntT", bound=int)
_IrregularShapeT = TypeVar(
    "_IrregularShapeT",
    tuple[int],
    tuple[int, _Axis],
    tuple[int, _Axis, _Axis],
    tuple[int, _Axis, _Axis, _Axis],
    tuple[int, _Axis, _Axis, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, _Axis, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, Unpack[tuple[_Axis, ...]]],
)
_RegularShapeT = TypeVar(
    "_RegularShapeT",
    tuple[()],
    tuple[int],
    tuple[int, int],
    tuple[int, int, int],
    tuple[int, int, int, int],
    tuple[int, int, int, int, Unpack[tuple[int, ...]]],
    tuple[int, int, int, Unpack[tuple[int, ...]]],
    tuple[int, int, Unpack[tuple[int, ...]]],
    tuple[int, Unpack[tuple[int, ...]]],
    tuple[int, ...],
)
_ShapeT = TypeVar(
    "_ShapeT",
    tuple[()],
    tuple[int],
    tuple[int, int],
    tuple[int, int, int],
    tuple[int, int, int, int],
    tuple[int, int, int, int, Unpack[tuple[int, ...]]],
    tuple[int, int, int, Unpack[tuple[int, ...]]],
    tuple[int, int, Unpack[tuple[int, ...]]],
    tuple[int, Unpack[tuple[int, ...]]],
    tuple[int, ...],
    tuple[int, _Axis],
    tuple[int, _Axis, _Axis],
    tuple[int, _Axis, _Axis, _Axis],
    tuple[int, _Axis, _Axis, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, _Axis, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, _Axis, Unpack[tuple[_Axis, ...]]],
    tuple[int, Unpack[tuple[_Axis, ...]]],
)
