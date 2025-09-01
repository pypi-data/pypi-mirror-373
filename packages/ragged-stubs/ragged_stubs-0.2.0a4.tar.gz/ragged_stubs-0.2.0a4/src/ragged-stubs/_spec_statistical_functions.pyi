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

from typing import Any, Literal, TypeAlias, TypeVar, overload

import numpy as np
import numpy.typing as npt
from typing_extensions import Unpack

from ._spec_array_object import array
from ._typing import Dtype

@overload
def max(  # noqa: A001
    x: array[Any, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, _DTypeT]: ...
@overload
def max(  # noqa: A001
    x: array[_ShapeT, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[True],
) -> array[_ShapeT, _DTypeT]: ...
@overload
def max(  # noqa: A001
    x: array[Any, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: bool,
) -> array[Any, _DTypeT]: ...

@overload
def mean(
    x: array[_AtLeast1D, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, _DTypeT]: ...
@overload
def mean(
    x: array[_AtLeast1DT, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[True],
) -> array[_AtLeast1DT, _DTypeT]: ...
@overload
def mean(
    x: array[_AtLeast1D, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: bool,
) -> array[Any, _DTypeT]: ...

@overload
def min(  # noqa: A001
    x: array[Any, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, _DTypeT]: ...
@overload
def min(  # noqa: A001
    x: array[_ShapeT, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[True],
) -> array[_ShapeT, _DTypeT]: ...
@overload
def min(  # noqa: A001
    x: array[Any, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: bool,
) -> array[Any, _DTypeT]: ...

@overload
def prod(
    x: array,
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    dtype: npt.DTypeLike = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, Dtype[np.int64 | np.uint64 | np.float64 | np.complex128]]: ...
@overload
def prod(
    x: array[_ShapeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    dtype: npt.DTypeLike = ...,
    keepdims: Literal[True],
) -> array[
    _ShapeT,
    Dtype[np.int64 | np.uint64 | np.float64 | np.complex128],
]: ...
@overload
def prod(
    x: array,
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    dtype: npt.DTypeLike = ...,
    keepdims: bool,
) -> array[Any, Dtype[np.int64 | np.uint64 | np.float64 | np.complex128]]: ...

@overload
def std(
    x: array[_AtLeast1D, _InexactDTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, _InexactDTypeT]: ...
@overload
def std(
    x: array[_AtLeast1D, Dtype[np.int8 | np.uint8 | np.bool_]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, Dtype[np.float16]]: ...
@overload
def std(
    x: array[_AtLeast1D, Dtype[np.int16 | np.uint16]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, Dtype[np.float32]]: ...
@overload
def std(
    x: array[_AtLeast1D, Dtype[np.int32 | np.uint32 | np.int64 | np.uint64]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, Dtype[np.float64]]: ...
@overload
def std(
    x: array[_AtLeast1DT, _InexactDTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[True],
) -> array[_AtLeast1DT, _InexactDTypeT]: ...
@overload
def std(
    x: array[_AtLeast1DT, Dtype[np.int8 | np.uint8 | np.bool_]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[True],
) -> array[_AtLeast1DT, Dtype[np.float16]]: ...
@overload
def std(
    x: array[_AtLeast1DT, Dtype[np.int16 | np.uint16]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[True],
) -> array[_AtLeast1DT, Dtype[np.float32]]: ...
@overload
def std(
    x: array[_AtLeast1DT, Dtype[np.int32 | np.uint32 | np.int64 | np.uint64]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[True],
) -> array[_AtLeast1DT, Dtype[np.float64]]: ...
@overload
def std(
    x: array[_AtLeast1D, _InexactDTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: bool,
) -> array[Any, _InexactDTypeT]: ...
@overload
def std(
    x: array[_AtLeast1D, Dtype[np.int8 | np.uint8 | np.bool_]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: bool,
) -> array[Any, Dtype[np.float16]]: ...
@overload
def std(
    x: array[_AtLeast1D, Dtype[np.int16 | np.uint16]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: bool,
) -> array[Any, Dtype[np.float32]]: ...
@overload
def std(
    x: array[_AtLeast1D, Dtype[np.int32 | np.uint32 | np.int64 | np.uint64]],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: bool,
) -> array[Any, Dtype[np.float64]]: ...

@overload
def sum(  # noqa: A001
    x: array,
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    dtype: npt.DTypeLike = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, Dtype[np.int64 | np.uint64 | np.float64 | np.complex128]]: ...
@overload
def sum(  # noqa: A001
    x: array[_ShapeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    dtype: npt.DTypeLike = ...,
    keepdims: Literal[True],
) -> array[
    _ShapeT,
    Dtype[np.int64 | np.uint64 | np.float64 | np.complex128],
]: ...
@overload
def sum(  # noqa: A001
    x: array,
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    dtype: npt.DTypeLike = ...,
    keepdims: bool,
) -> array[Any, Dtype[np.int64 | np.uint64 | np.float64 | np.complex128]]: ...

@overload
def var(
    x: array[_AtLeast1D, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[False] = ...,
) -> array[Any, _DTypeT]: ...
@overload
def var(
    x: array[_AtLeast1DT, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: Literal[True],
) -> array[_AtLeast1DT, _DTypeT]: ...
@overload
def var(
    x: array[_AtLeast1D, _DTypeT],
    /,
    *,
    axis: int | tuple[int, ...] | None = ...,
    keepdims: bool,
) -> array[Any, _DTypeT]: ...

_AtLeast1D: TypeAlias = tuple[int, Unpack[tuple[int | None, ...]]]
_Axis: TypeAlias = int | None
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
_InexactDTypeT = TypeVar("_InexactDTypeT", bound=Dtype[np.inexact[Any]])
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
