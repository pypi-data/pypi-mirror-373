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
from collections.abc import Sequence
from typing import Any, Literal, SupportsIndex, TypeAlias, TypeVar, overload

import numpy as np
import optype as op
import optype.numpy as onp
from optype.dlpack import CanDLPackDevice
from typing_extensions import Unpack

from ._spec_array_object import array
from ._typing import Device, Dtype, Shape

@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int], Dtype[_SCT]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.bool_]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int8]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int16]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int32]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int64]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint8]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint16]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint32]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint64]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float32]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float64]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex64]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex128]]: ...
@overload
def arange(
    start: object,
    /,
    stop: object = ...,
    step: object = ...,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int]]: ...

@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[_SCT]]: ...
@overload
def asarray(
    obj: array[_ShapeT, _DTypeT],
    dtype: None = ...,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, _DTypeT]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: _Bool,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.bool_]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.int8]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.int16]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.int32]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.int64]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.uint8]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.uint16]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.uint32]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.uint64]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.float32]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.float64]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.complex64]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT, Dtype[np.complex128]]: ...
@overload
def asarray(
    obj: array[_ShapeT],
    dtype: type[Any] | str,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_ShapeT]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[_SCT]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _DTypeT],
    dtype: None = ...,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, _DTypeT]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: _Bool,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.bool_]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.int8]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.int16]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.int32]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.int64]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint8]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint16]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint32]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint64]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.float32]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.float64]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex64]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex128]]: ...
@overload
def asarray(
    obj: np.ndarray[_RegularShapeT, _NumPyDType],
    dtype: type[Any] | str,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[_RegularShapeT]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[_SCT]]: ...
@overload
def asarray(
    obj: _NumberT,
    dtype: None = ...,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[_NumberT]]: ...
@overload
def asarray(
    obj: bool,
    dtype: None = ...,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.bool_]]: ...
@overload
def asarray(
    obj: op.JustInt,
    dtype: None = ...,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.int64]]: ...
@overload
def asarray(
    obj: op.JustFloat,
    dtype: None = ...,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.float64]]: ...
@overload
def asarray(
    obj: op.JustComplex,
    dtype: None = ...,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.complex128]]: ...
@overload
def asarray(
    obj: object,
    dtype: None = ...,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: _Bool,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.bool_]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.int8]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.int16]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.int32]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.int64]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.uint8]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.uint16]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.uint32]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.uint64]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.float32]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.float64]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.complex64]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()], Dtype[np.complex128]]: ...
@overload
def asarray(
    obj: complex | np.number[Any] | np.timedelta64,
    dtype: type[Any] | str,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[tuple[()]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[_SCT]]: ...
@overload
def asarray(
    obj: object,
    dtype: _Bool,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.bool_]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.int8]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.int16]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.int32]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.int64]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.uint8]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.uint16]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.uint32]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.uint64]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.float32]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.float64]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.complex64]]: ...
@overload
def asarray(
    obj: object,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array[Any, Dtype[np.complex128]]: ...
@overload
def asarray(
    obj: object,
    dtype: type[Any] | str,
    device: Device | None = ...,
    copy: bool | None = ...,
) -> array: ...

@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[_SCT]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int], Dtype[_SCT]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[_SCT]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float64]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float64]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float64]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.bool_]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.bool_]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.bool_]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int8]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int8]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int8]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int16]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int16]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int16]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int32]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int32]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int32]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int64]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int64]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int64]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint8]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint8]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint8]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint16]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint16]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint16]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint32]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint32]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint32]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint64]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint64]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint64]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float32]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float32]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float32]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex64]]: ...
@overload
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex64]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex64]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex128]]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex128]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex128]]: ...
@overload
def empty(
    shape: _RegularShapeT,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[_RegularShapeT]: ...
@overload
def empty(
    shape: SupportsIndex,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int]]: ...
@overload
def empty(
    shape: Sequence[SupportsIndex],
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int, ...]]: ...

@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[_SCT]]: ...
@overload
def empty_like(
    x: array[_ShapeT, _DTypeT],
    /,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_ShapeT, _DTypeT]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.bool_]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int8]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int16]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int32]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int64]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint8]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint16]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint32]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint64]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.float32]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.float64]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.complex64]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.complex128]]: ...
@overload
def empty_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[_ShapeT]: ...

@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[_SCT]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.float64]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.bool_]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.int8]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.int16]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.int32]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.int64]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.uint8]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.uint16]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.uint32]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.uint64]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.float32]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.complex64]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int, int], Dtype[np.complex128]]: ...
@overload
def eye(
    n_rows: int,
    n_cols: int | None = ...,
    /,
    *,
    k: int = ...,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int, int]]: ...

def from_dlpack(
    x: CanDLPackDevice[enum.Enum | int, int],
    /,
) -> array: ...

@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[_SCT]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int], Dtype[_SCT]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[_SCT]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: _SCT,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[_SCT]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: _SCT,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[_SCT]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: _SCT,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[_SCT]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: bool,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.bool_]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: bool,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.bool_]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: bool,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.bool_]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: op.JustInt,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int64]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: op.JustInt,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int64]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: op.JustInt,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int64]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: op.JustFloat,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float64]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: op.JustFloat,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float64]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: op.JustFloat,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float64]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: op.JustComplex,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex128]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: op.JustComplex,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex128]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: op.JustComplex,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex128]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.bool_]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.bool_]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.bool_]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int8]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int8]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int8]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int16]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int16]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int16]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int32]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int32]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int32]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int64]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int64]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int64]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint8]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint8]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint8]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint16]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint16]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint16]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint32]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint32]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint32]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint64]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint64]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint64]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float32]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float32]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float32]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float64]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float64]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float64]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex64]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex64]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex64]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex128]]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex128]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex128]]: ...
@overload
def full(
    shape: _RegularShapeT,
    fill_value: object,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[_RegularShapeT]: ...
@overload
def full(
    shape: SupportsIndex,
    fill_value: object,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int]]: ...
@overload
def full(
    shape: Sequence[SupportsIndex],
    fill_value: object,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int, ...]]: ...

@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[_SCT]]: ...
@overload
def full_like(
    x: array[_ShapeT, _DTypeT],
    /,
    fill_value: object,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_ShapeT, _DTypeT]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.bool_]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int8]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int16]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int32]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int64]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint8]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint16]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint32]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint64]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.float32]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.float64]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.complex64]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.complex128]]: ...
@overload
def full_like(
    x: array[_ShapeT],
    /,
    fill_value: object,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[_ShapeT]: ...

@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[_SCT]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: None = ...,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.inexact[Any]]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: _Bool,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.bool_]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.int8]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.int16]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.int32]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.int64]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.uint8]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.uint16]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.uint32]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.uint64]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.float32]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.float64]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.complex64]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D, Dtype[np.complex128]]: ...
@overload
def linspace(
    start: object,
    stop: object,
    /,
    num: int,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
    endpoint: bool = ...,
) -> array[onp.AtLeast1D]: ...

def meshgrid(
    *arrays: array,
    indexing: Literal["xy", "ij"] = ...,
) -> list[array]: ...

@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[_SCT]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int], Dtype[_SCT]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[_SCT]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float64]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float64]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float64]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.bool_]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.bool_]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.bool_]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int8]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int8]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int8]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int16]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int16]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int16]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int32]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int32]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int32]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int64]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int64]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int64]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint8]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint8]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint8]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint16]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint16]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint16]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint32]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint32]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint32]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint64]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint64]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint64]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float32]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float32]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float32]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex64]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex64]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex64]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex128]]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex128]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex128]]: ...
@overload
def ones(
    shape: _RegularShapeT,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[_RegularShapeT]: ...
@overload
def ones(
    shape: SupportsIndex,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int]]: ...
@overload
def ones(
    shape: Sequence[SupportsIndex],
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int, ...]]: ...

@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[_SCT]]: ...
@overload
def ones_like(
    x: array[_ShapeT, _DTypeT],
    /,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_ShapeT, _DTypeT]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.bool_]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int8]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int16]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int32]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int64]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint8]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint16]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint32]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint64]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.float32]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.float64]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.complex64]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.complex128]]: ...
@overload
def ones_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[_ShapeT]: ...

def tril(
    x: array[Any, _DTypeT],
    /,
    *,
    k: int = ...,
) -> array[tuple[int, int] | tuple[int, int, int], _DTypeT]: ...

def triu(
    x: array[Any, _DTypeT],
    /,
    *,
    k: int = ...,
) -> array[tuple[int, int] | tuple[int, int, int], _DTypeT]: ...

@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[_SCT]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int], Dtype[_SCT]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[_SCT]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float64]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float64]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyFloat64DType | None = ...,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float64]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.bool_]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.bool_]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.bool_]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int8]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int8]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int8]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int16]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int16]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int16]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int32]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int32]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int32]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.int64]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.int64]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.int64]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint8]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint8]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint8]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint16]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint16]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint16]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint32]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint32]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint32]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.uint64]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.uint64]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.uint64]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.float32]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.float32]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.float32]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex64]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex64]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex64]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[_RegularShapeT, Dtype[np.complex128]]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int], Dtype[np.complex128]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[tuple[int, ...], Dtype[np.complex128]]: ...
@overload
def zeros(
    shape: _RegularShapeT,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[_RegularShapeT]: ...
@overload
def zeros(
    shape: SupportsIndex,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int]]: ...
@overload
def zeros(
    shape: Sequence[SupportsIndex],
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[tuple[int, ...]]: ...

@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.ToDType[_SCT],
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[_SCT]]: ...
@overload
def zeros_like(
    x: array[_ShapeT, _DTypeT],
    /,
    *,
    dtype: None = ...,
    device: Device | None = ...,
) -> array[_ShapeT, _DTypeT]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: _Bool,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.bool_]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt8DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int8]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt16DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int16]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int32]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyInt64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.int64]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt8DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint8]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt16DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint16]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint32]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyUInt64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.uint64]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyFloat32DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.float32]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyFloat64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.float64]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyComplex64DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.complex64]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: onp.AnyComplex128DType,
    device: Device | None = ...,
) -> array[_ShapeT, Dtype[np.complex128]]: ...
@overload
def zeros_like(
    x: array[_ShapeT],
    /,
    *,
    dtype: type[Any] | str,
    device: Device | None = ...,
) -> array[_ShapeT]: ...

_Bool: TypeAlias = type[bool] | Literal[
    "?",
    "=?",
    "<?",
    ">?",
    "bool",
    "bool_",
    "bool8",
]
_DTypeT = TypeVar("_DTypeT", bound=Dtype)
_NumberT = TypeVar("_NumberT", bound=np.number[Any])
_NumPyDType: TypeAlias = np.dtype[
    np.bool_ | np.number[Any] | np.datetime64 | np.timedelta64
]
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
_SCT = TypeVar("_SCT", bound=np.bool_ | np.number[Any])
_ShapeT = TypeVar("_ShapeT", bound=Shape)
