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
from collections.abc import Iterator, Sized
from typing import (
    Any,
    Generic,
    SupportsAbs,
    SupportsComplex,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    TypeAlias,
    overload,
)

import numpy as np
import optype as op
import optype.numpy as onp
from optype.dlpack import CanDLPackCompat, CanDLPackDevice
from typing_extensions import CapsuleType, Self, TypeVar, Unpack, override

from ._typing import Device, Dtype, Shape

class array(  # noqa: N801
    CanDLPackCompat,
    CanDLPackDevice[enum.Enum, int],
    SupportsAbs[array[_ShapeT_co, _DTypeT_co]],
    SupportsComplex,
    SupportsFloat,
    SupportsIndex,
    SupportsInt,
    Sized,
    Generic[_ShapeT_co, _DTypeT_co],
):
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[_SCT]],
        obj: array[_ShapeT],
        dtype: onp.ToDType[_SCT],
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self,
        obj: array[_ShapeT_co, _DTypeT_co],
        dtype: None = ...,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.bool_]],
        obj: array[_ShapeT],
        dtype: onp.AnyBoolDType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.int8]],
        obj: array[_ShapeT],
        dtype: onp.AnyInt8DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.int16]],
        obj: array[_ShapeT],
        dtype: onp.AnyInt16DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.int32]],
        obj: array[_ShapeT],
        dtype: onp.AnyInt32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.int64]],
        obj: array[_ShapeT],
        dtype: onp.AnyInt64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.uint8]],
        obj: array[_ShapeT],
        dtype: onp.AnyUInt8DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.uint16]],
        obj: array[_ShapeT],
        dtype: onp.AnyUInt16DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.uint32]],
        obj: array[_ShapeT],
        dtype: onp.AnyUInt32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.uint64]],
        obj: array[_ShapeT],
        dtype: onp.AnyUInt64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.float32]],
        obj: array[_ShapeT],
        dtype: onp.AnyFloat32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.float64]],
        obj: array[_ShapeT],
        dtype: onp.AnyFloat64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.complex64]],
        obj: array[_ShapeT],
        dtype: onp.AnyComplex64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT, Dtype[np.complex128]],
        obj: array[_ShapeT],
        dtype: onp.AnyComplex128DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_ShapeT],
        obj: array[_ShapeT],
        dtype: type[Any] | str,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[_SCT]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.ToDType[_SCT],
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, _DTypeT],
        obj: np.ndarray[_RegularShapeT, _DTypeT],
        dtype: None = ...,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.bool_]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyBoolDType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.int8]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyInt8DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.int16]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyInt16DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.int32]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyInt32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.int64]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyInt64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.uint8]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyUInt8DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.uint16]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyUInt16DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.uint32]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyUInt32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.uint64]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyUInt64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.float32]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyFloat32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.float64]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyFloat64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.complex64]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyComplex64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT, Dtype[np.complex128]],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: onp.AnyComplex128DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[_RegularShapeT],
        obj: np.ndarray[_RegularShapeT, _NumPyDType],
        dtype: type[Any] | str,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[_SCT]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.ToDType[_SCT],
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[_NumberT]],
        obj: _NumberT,
        dtype: None = ...,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.bool_]],
        obj: bool,
        dtype: None = ...,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.int64]],
        obj: op.JustInt,
        dtype: None = ...,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.float64]],
        obj: op.JustFloat,
        dtype: None = ...,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.complex128]],
        obj: op.JustComplex,
        dtype: None = ...,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array,
        obj: object,
        dtype: None = ...,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.bool_]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyBoolDType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.int8]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyInt8DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.int16]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyInt16DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.int32]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyInt32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.int64]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyInt64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.uint8]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyUInt8DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.uint16]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyUInt16DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.uint32]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyUInt32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.uint64]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyUInt64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.float32]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyFloat32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.float64]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyFloat64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.complex64]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyComplex64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()], Dtype[np.complex128]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: onp.AnyComplex128DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[tuple[()]],
        obj: complex | np.number[Any] | np.timedelta64,
        dtype: type[Any] | str,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[_SCT]],
        obj: object,
        dtype: onp.ToDType[_SCT],
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.bool_]],
        obj: object,
        dtype: onp.AnyBoolDType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.int8]],
        obj: object,
        dtype: onp.AnyInt8DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.int16]],
        obj: object,
        dtype: onp.AnyInt16DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.int32]],
        obj: object,
        dtype: onp.AnyInt32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.int64]],
        obj: object,
        dtype: onp.AnyInt64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.uint8]],
        obj: object,
        dtype: onp.AnyUInt8DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.uint16]],
        obj: object,
        dtype: onp.AnyUInt16DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.uint32]],
        obj: object,
        dtype: onp.AnyUInt32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.uint64]],
        obj: object,
        dtype: onp.AnyUInt64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.float32]],
        obj: object,
        dtype: onp.AnyFloat32DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.float64]],
        obj: object,
        dtype: onp.AnyFloat64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.complex64]],
        obj: object,
        dtype: onp.AnyComplex64DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array[Any, Dtype[np.complex128]],
        obj: object,
        dtype: onp.AnyComplex128DType,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...
    @overload
    def __init__(
        self: array,
        obj: object,
        dtype: type[Any] | str,
        device: Device | None = ...,
        copy: bool | None = ...,
    ) -> None: ...

    @override
    def __str__(self) -> str: ...  # noqa: PYI029
    @override
    def __repr__(self) -> str: ...  # noqa: PYI029
    def __contains__(self, other: complex) -> bool: ...
    def __len__(self) -> int: ...
    def __iter__(
        self: array[tuple[int, Unpack[tuple[_Axis, ...]]], _DTypeT],
    ) -> Iterator[array[Any, _DTypeT]]: ...

    @overload
    def item(
        self: array[tuple[()], Dtype[np.complexfloating[Any, Any]]],
    ) -> complex: ...
    @overload
    def item(self: array[tuple[()], Dtype[np.floating[Any]]]) -> float: ...
    @overload
    def item(self: array[tuple[()], Dtype[np.integer[Any]]]) -> int: ...
    @overload
    def item(self: array[tuple[()], Dtype[np.bool_]]) -> bool: ...
    @overload
    def item(self: array[tuple[()]]) -> complex: ...

    @overload
    def tolist(
        self: array[Any, Dtype[np.complexfloating[Any, Any]]],
    ) -> complex | onp.SequenceND[complex]: ...
    @overload
    def tolist(
        self: array[Any, Dtype[np.floating[Any]]],
    ) -> float | onp.SequenceND[float]: ...
    @overload
    def tolist(
        self: array[Any, Dtype[np.integer[Any]]],
    ) -> int | onp.SequenceND[int]: ...
    @overload
    def tolist(
        self: array[Any, Dtype[np.bool_]],
    ) -> bool | onp.SequenceND[bool]: ...
    @overload
    def tolist(self: array[tuple[()]]) -> complex: ...
    @overload
    def tolist(
        self: array[tuple[int, Unpack[tuple[_Axis, ...]]]],
    ) -> onp.SequenceND[complex]: ...

    @property
    def dtype(self) -> _DTypeT_co: ...
    @property
    def device(self) -> Device: ...
    @property
    def mT(  # noqa: N802
        self: array[_AtLeast2DT, _DTypeT],
    ) -> array[_AtLeast2DT, _DTypeT]: ...
    @property
    def ndim(self) -> int: ...
    @property
    def shape(self) -> _ShapeT_co: ...
    @property
    def size(self) -> int: ...
    @property
    def T(self: array[_2DT, _DTypeT]) -> array[_2DT, _DTypeT]: ...  # noqa: N802
    def __abs__(self) -> Self: ...

    @overload
    def __add__(self, other: array | np.ndarray[Any, Dtype]) -> array: ...
    @overload
    def __add__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
    ) -> array[_ShapeT]: ...
    @overload
    def __add__(self, other: object) -> array: ...

    @overload
    def __and__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, _BoolOrIntDType]: ...
    @overload
    def __and__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, _BoolOrIntDType]: ...
    @overload
    def __and__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, _BoolOrIntDType]: ...

    # https://data-apis.org/array-api/latest/API_specification/generated/array_api.array.__array_namespace__.html
    def __array_namespace__(self, *, api_version: str | None = ...) -> Any: ...  # noqa: ANN401

    def __bool__(self) -> bool: ...
    def __complex__(self) -> complex: ...

    # https://data-apis.org/array-api/latest/API_specification/generated/array_api.array.__dlpack__.html
    def __dlpack__(self, *, stream: int | Any | None = ...) -> CapsuleType: ...  # noqa: ANN401

    def __dlpack_device__(self) -> tuple[enum.Enum, int]: ...

    @overload
    def __eq__(
        self,
        other: array | np.ndarray[Any, Dtype],
        /,
    ) -> array[Any, Dtype[np.bool_]]: ...
    @overload
    def __eq__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
        /,
    ) -> array[_ShapeT, Dtype[np.bool_]]: ...
    @overload
    def __eq__(self, other: object, /) -> array[Any, Dtype[np.bool_]]: ...  # pyright: ignore[reportIncompatibleMethodOverride]

    def __float__(self) -> float: ...

    @overload
    def __floordiv__(
        self: array[Any, _RealDType],
        other: array[Any, _RealDType] | np.ndarray[Any, _RealDType],
        /,
    ) -> array[Any, Dtype[_RealNumber]]: ...
    @overload
    def __floordiv__(
        self: array[_ShapeT, _RealDType],
        other: float | _RealNumber,
        /,
    ) -> array[_ShapeT, Dtype[_RealNumber]]: ...
    @overload
    def __floordiv__(
        self: array[Any, _RealDType],
        other: object,
        /,
    ) -> array[Any, Dtype[_RealNumber]]: ...

    @overload
    def __ge__(
        self,
        other: array | np.ndarray[Any, Dtype],
        /,
    ) -> array[Any, Dtype[np.bool_]]: ...
    @overload
    def __ge__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
        /,
    ) -> array[_ShapeT, Dtype[np.bool_]]: ...
    @overload
    def __ge__(self, other: object, /) -> array[Any, Dtype[np.bool_]]: ...

    def __getitem__(self, key: object) -> array[Any, _DTypeT_co]: ...

    @overload
    def __gt__(
        self,
        other: array | np.ndarray[Any, Dtype],
        /,
    ) -> array[Any, Dtype[np.bool_]]: ...
    @overload
    def __gt__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
        /,
    ) -> array[_ShapeT, Dtype[np.bool_]]: ...
    @overload
    def __gt__(self, other: object, /) -> array[Any, Dtype[np.bool_]]: ...

    def __index__(self) -> int: ...
    def __int__(self) -> int: ...
    def __invert__(
        self: array[_ShapeT, _BoolOrIntDTypeT],
    ) -> array[_ShapeT, _BoolOrIntDTypeT]: ...

    @overload
    def __le__(
        self,
        other: array | np.ndarray[Any, Dtype],
        /,
    ) -> array[Any, Dtype[np.bool_]]: ...
    @overload
    def __le__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
        /,
    ) -> array[_ShapeT, Dtype[np.bool_]]: ...
    @overload
    def __le__(self, other: object, /) -> array[Any, Dtype[np.bool_]]: ...

    @overload
    def __lshift__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, Dtype[np.integer[Any]]]: ...
    @overload
    def __lshift__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, Dtype[np.integer[Any]]]: ...
    @overload
    def __lshift__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, Dtype[np.integer[Any]]]: ...

    @overload
    def __lt__(
        self,
        other: array | np.ndarray[Any, Dtype],
        /,
    ) -> array[Any, Dtype[np.bool_]]: ...
    @overload
    def __lt__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
        /,
    ) -> array[_ShapeT, Dtype[np.bool_]]: ...
    @overload
    def __lt__(self, other: object, /) -> array[Any, Dtype[np.bool_]]: ...

    def __matmul__(self, other: array) -> array: ...

    @overload
    def __mod__(
        self: array[Any, _RealDType],
        other: array[Any, _RealDType] | np.ndarray[Any, _RealDType],
        /,
    ) -> array[Any, Dtype[_RealNumber]]: ...
    @overload
    def __mod__(
        self: array[_ShapeT, _RealDType],
        other: float | _RealNumber,
        /,
    ) -> array[_ShapeT, Dtype[_RealNumber]]: ...
    @overload
    def __mod__(
        self: array[Any, _RealDType],
        other: object,
        /,
    ) -> array[Any, Dtype[_RealNumber]]: ...

    @overload
    def __mul__(self, other: array | np.ndarray[Any, Dtype]) -> array: ...
    @overload
    def __mul__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
    ) -> array[_ShapeT]: ...
    @overload
    def __mul__(self, other: object) -> array: ...

    @overload
    def __ne__(
        self,
        other: array | np.ndarray[Any, Dtype],
        /,
    ) -> array[Any, Dtype[np.bool_]]: ...
    @overload
    def __ne__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
        /,
    ) -> array[_ShapeT, Dtype[np.bool_]]: ...
    @overload
    def __ne__(self, other: object, /) -> array[Any, Dtype[np.bool_]]: ...  # pyright: ignore[reportIncompatibleMethodOverride]

    def __neg__(
        self: array[_ShapeT, _NumericDTypeT],
    ) -> array[_ShapeT, _NumericDTypeT]: ...

    @overload
    def __or__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, _BoolOrIntDType]: ...
    @overload
    def __or__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, _BoolOrIntDType]: ...
    @overload
    def __or__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, _BoolOrIntDType]: ...

    def __pos__(
        self: array[_ShapeT, _NumericDTypeT],
    ) -> array[_ShapeT, _NumericDTypeT]: ...

    @overload
    def __pow__(
        self,
        other: array | np.ndarray[Any, Dtype],
    ) -> array[Any, _NumericDType]: ...
    @overload
    def __pow__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
    ) -> array[_ShapeT, _NumericDType]: ...
    @overload
    def __pow__(self, other: object) -> array[Any, _NumericDType]: ...

    @overload
    def __rshift__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, Dtype[np.integer[Any]]]: ...
    @overload
    def __rshift__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, Dtype[np.integer[Any]]]: ...
    @overload
    def __rshift__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, Dtype[np.integer[Any]]]: ...

    def __setitem__(self, key: object, value: object) -> None: ...

    @overload
    def __sub__(
        self: array[Any, _NumericDType],
        other: array | np.ndarray[Any, Dtype],
    ) -> array[Any, _NumericDType]: ...
    @overload
    def __sub__(
        self,
        other: array[Any, _NumericDType] | np.ndarray[Any, _NumericDType],
    ) -> array[Any, _NumericDType]: ...
    @overload
    def __sub__(
        self: array[_ShapeT, _NumericDType],
        other: complex | np.number[Any],
    ) -> array[_ShapeT, _NumericDType]: ...
    @overload
    def __sub__(
        self: array[_ShapeT],
        other: op.JustInt | op.JustFloat | op.JustComplex | np.number[Any],
    ) -> array[_ShapeT, _NumericDType]: ...
    @overload
    def __sub__(self, other: object) -> array[Any, _NumericDType]: ...

    @overload
    def __truediv__(
        self,
        other: array | np.ndarray[Any, Dtype],
        /,
    ) -> array[Any, _InexactDType]: ...
    @overload
    def __truediv__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
        /,
    ) -> array[_ShapeT, _InexactDType]: ...
    @overload
    def __truediv__(self, other: object, /) -> array[Any, _InexactDType]: ...

    @overload
    def __xor__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, _BoolOrIntDType]: ...
    @overload
    def __xor__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, _BoolOrIntDType]: ...
    @overload
    def __xor__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, _BoolOrIntDType]: ...

    # https://data-apis.org/array-api/latest/API_specification/generated/array_api.array.to_device.html
    def to_device(
        self,
        device: Device,
        /,
        *,
        stream: int | Any | None = ...,  # noqa: ANN401
    ) -> Self: ...

    @overload
    def __iadd__(self, other: array | np.ndarray[Any, Dtype]) -> array: ...
    @overload
    def __iadd__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
    ) -> array[_ShapeT]: ...
    @overload
    def __iadd__(self, other: object) -> array: ...

    @overload
    def __isub__(
        self: array[Any, _NumericDType],
        other: array | np.ndarray[Any, Dtype],
    ) -> array[Any, _NumericDType]: ...
    @overload
    def __isub__(
        self: array,
        other: array[Any, _NumericDType] | np.ndarray[Any, _NumericDType],
    ) -> array[Any, _NumericDType]: ...
    @overload
    def __isub__(
        self: array[_ShapeT, _NumericDType],
        other: complex | np.number[Any],
    ) -> array[_ShapeT, _NumericDType]: ...
    @overload
    def __isub__(
        self: array[_ShapeT],
        other: op.JustInt | op.JustFloat | op.JustComplex | np.number[Any],
    ) -> array[_ShapeT, _NumericDType]: ...
    @overload
    def __isub__(self, other: object) -> array[Any, _NumericDType]: ...

    @overload
    def __imul__(self, other: array | np.ndarray[Any, Dtype]) -> array: ...
    @overload
    def __imul__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
    ) -> array[_ShapeT]: ...
    @overload
    def __imul__(self, other: object) -> array: ...

    @overload
    def __itruediv__(
        self,
        other: array | np.ndarray[Any, Dtype],
        /,
    ) -> array[Any, _InexactDType]: ...
    @overload
    def __itruediv__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
        /,
    ) -> array[_ShapeT, _InexactDType]: ...
    @overload
    def __itruediv__(self, other: object, /) -> array[Any, _InexactDType]: ...

    @overload
    def __ifloordiv__(
        self: array[Any, _RealDType],
        other: array[Any, _RealDType] | np.ndarray[Any, _RealDType],
        /,
    ) -> array[Any, Dtype[_RealNumber]]: ...
    @overload
    def __ifloordiv__(
        self: array[_ShapeT, _RealDType],
        other: float | _RealNumber,
        /,
    ) -> array[_ShapeT, Dtype[_RealNumber]]: ...
    @overload
    def __ifloordiv__(
        self: array[Any, _RealDType],
        other: object,
        /,
    ) -> array[Any, Dtype[_RealNumber]]: ...

    @overload
    def __ipow__(
        self,
        other: array | np.ndarray[Any, Dtype],
    ) -> array[Any, _NumericDType]: ...
    @overload
    def __ipow__(
        self: array[_ShapeT],
        other: complex | np.number[Any],
    ) -> array[_ShapeT, _NumericDType]: ...
    @overload
    def __ipow__(self, other: object) -> array[Any, _NumericDType]: ...

    @overload
    def __imod__(
        self: array[Any, _RealDType],
        other: array[Any, _RealDType] | np.ndarray[Any, _RealDType],
        /,
    ) -> array[Any, Dtype[_RealNumber]]: ...
    @overload
    def __imod__(
        self: array[_ShapeT, _RealDType],
        other: float | _RealNumber,
        /,
    ) -> array[_ShapeT, Dtype[_RealNumber]]: ...
    @overload
    def __imod__(
        self: array[Any, _RealDType],
        other: object,
        /,
    ) -> array[Any, Dtype[_RealNumber]]: ...

    def __imatmul__(self, other: array) -> array: ...  # noqa: PYI034

    @overload
    def __iand__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, _BoolOrIntDType]: ...
    @overload
    def __iand__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, _BoolOrIntDType]: ...
    @overload
    def __iand__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, _BoolOrIntDType]: ...

    @overload
    def __ior__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, _BoolOrIntDType]: ...
    @overload
    def __ior__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, _BoolOrIntDType]: ...
    @overload
    def __ior__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, _BoolOrIntDType]: ...

    @overload
    def __ixor__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, _BoolOrIntDType]: ...
    @overload
    def __ixor__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, _BoolOrIntDType]: ...
    @overload
    def __ixor__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, _BoolOrIntDType]: ...

    @overload
    def __ilshift__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, Dtype[np.integer[Any]]]: ...
    @overload
    def __ilshift__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, Dtype[np.integer[Any]]]: ...
    @overload
    def __ilshift__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, Dtype[np.integer[Any]]]: ...

    @overload
    def __irshift__(
        self: array[Any, _BoolOrIntDType],
        other: array[Any, _BoolOrIntDType] | np.ndarray[Any, _BoolOrIntDType],
    ) -> array[Any, Dtype[np.integer[Any]]]: ...
    @overload
    def __irshift__(
        self: array[_ShapeT, _BoolOrIntDType],
        other: int | np.integer[Any],
    ) -> array[_ShapeT, Dtype[np.integer[Any]]]: ...
    @overload
    def __irshift__(
        self: array[Any, _BoolOrIntDType],
        other: object,
    ) -> array[Any, Dtype[np.integer[Any]]]: ...

    __radd__ = __add__
    __rmul__ = __mul__
    __rand__ = __and__
    __ror__ = __or__
    __rxor__ = __xor__

    __rsub__ = __sub__
    __rtruediv__ = __truediv__
    __rfloordiv__ = __floordiv__
    __rpow__ = __pow__
    __rmod__ = __mod__
    __rmatmul__ = __matmul__
    __rlshift__ = __lshift__
    __rrshift__ = __rshift__

_Axis: TypeAlias = int | None
_2DT = TypeVar("_2DT", tuple[int, int], tuple[int, _Axis])
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
_BoolOrIntDType: TypeAlias = Dtype[np.bool_ | np.integer[Any]]
_BoolOrIntDTypeT = TypeVar("_BoolOrIntDTypeT", bound=_BoolOrIntDType)
_DTypeT = TypeVar("_DTypeT", bound=Dtype)
_DTypeT_co = TypeVar(
    "_DTypeT_co",
    bound=Dtype,
    covariant=True,
    default=np.dtype[Any],
)
_InexactDType: TypeAlias = Dtype[np.inexact[Any]]
_NumberT = TypeVar("_NumberT", bound=np.number[Any])
_NumericDType: TypeAlias = Dtype[np.number[Any]]
_NumericDTypeT = TypeVar("_NumericDTypeT", bound=_NumericDType)
_NumPyDType: TypeAlias = np.dtype[
    np.bool_ | np.number[Any] | np.datetime64 | np.timedelta64
]
_RealNumber: TypeAlias = np.integer[Any] | np.floating[Any]
_RealDType: TypeAlias = Dtype[np.bool_ | _RealNumber]
_RegularShapeT = TypeVar("_RegularShapeT", bound=tuple[int, ...])
_SCT = TypeVar("_SCT", bound=np.bool_ | np.number[Any])
_ShapeT = TypeVar("_ShapeT", bound=Shape)
_ShapeT_co = TypeVar(
    "_ShapeT_co",
    bound=Shape,
    covariant=True,
    default=tuple[Any, ...],
)
