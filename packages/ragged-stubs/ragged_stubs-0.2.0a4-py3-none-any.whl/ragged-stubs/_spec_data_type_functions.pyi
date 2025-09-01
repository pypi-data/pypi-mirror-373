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

import dataclasses
from typing import Any, Generic, Literal, TypeVar, overload

import numpy as np
import numpy.typing as npt
import optype.numpy as onp

from ._spec_array_object import array
from ._typing import Dtype, Shape

@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.ToDType[_SCT],
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[_SCT]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: None,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Any]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: type[bool] | Literal[
        "?",
        "=?",
        "<?",
        ">?",
        "bool",
        "bool_",
        "bool8",
    ],
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.bool_]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyInt8DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.int8]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyInt16DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.int16]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyInt32DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.int32]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyInt64DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.int64]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyUInt8DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.uint8]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyUInt16DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.uint16]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyUInt32DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.uint32]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyUInt64DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.uint64]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyFloat32DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.float32]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyFloat64DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.float64]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyComplex64DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.complex64]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: onp.AnyComplex128DType,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT, Dtype[np.complex128]]: ...
@overload
def astype(
    x: array[_ShapeT],
    dtype: type[Any] | str,
    /,
    *,
    copy: bool = ...,
) -> array[_ShapeT]: ...

def can_cast(from_: object, to: npt.DTypeLike, /) -> bool: ...

@dataclasses.dataclass
class finfo_object(Generic[_FloatingT_co]):  # noqa: N801
    bits: int
    eps: _FloatingT_co
    max: _FloatingT_co
    min: _FloatingT_co
    smallest_normal: _FloatingT_co
    dtype: np.dtype[_FloatingT_co]

@overload
def finfo(
    type: onp.ToDType[_FloatingT_co],
) -> finfo_object[_FloatingT_co]: ...
@overload
def finfo(
    type: onp.ToDType[np.complexfloating[_BitT, _BitT]],
) -> finfo_object[np.floating[_BitT]]: ...
@overload
def finfo(
    type: onp.AnyFloat32DType | onp.AnyComplex64DType,
) -> finfo_object[np.float32]: ...
@overload
def finfo(
    type: onp.AnyFloat64DType | onp.AnyComplex128DType,
) -> finfo_object[np.float64]: ...

@dataclasses.dataclass
class iinfo_object(Generic[_IntegerT_co]):  # noqa: N801
    bits: int
    max: int
    min: int
    dtype: np.dtype[_IntegerT_co]

@overload
def iinfo(type: onp.ToDType[_IntegerT_co]) -> iinfo_object[_IntegerT_co]: ...
@overload
def iinfo(type: onp.AnyInt8DType) -> iinfo_object[np.int8]: ...
@overload
def iinfo(type: onp.AnyInt16DType) -> iinfo_object[np.int16]: ...
@overload
def iinfo(type: onp.AnyInt32DType) -> iinfo_object[np.int32]: ...
@overload
def iinfo(type: onp.AnyInt64DType) -> iinfo_object[np.int64]: ...
@overload
def iinfo(type: onp.AnyUInt8DType) -> iinfo_object[np.uint8]: ...
@overload
def iinfo(type: onp.AnyUInt16DType) -> iinfo_object[np.uint16]: ...
@overload
def iinfo(type: onp.AnyUInt32DType) -> iinfo_object[np.uint32]: ...
@overload
def iinfo(type: onp.AnyUInt64DType) -> iinfo_object[np.uint64]: ...

def isdtype(
    dtype: Dtype,
    kind: Dtype | str | tuple[Dtype | str, ...],
) -> bool: ...

def result_type(*arrays_and_dtypes: object) -> np.dtype[Any]: ...

_BitT = TypeVar("_BitT", bound=npt.NBitBase)
_FloatingT_co = TypeVar(
    "_FloatingT_co",
    bound=np.floating[Any],
    covariant=True,
)
_IntegerT_co = TypeVar("_IntegerT_co", bound=np.integer[Any], covariant=True)
_SCT = TypeVar("_SCT", bound=np.bool_ | np.number[Any])
_ShapeT = TypeVar("_ShapeT", bound=Shape)
