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

from typing import Any, Generic, TypeVar

import numpy as np
from typing_extensions import NamedTuple

from ._spec_array_object import array
from ._typing import Dtype

class unique_all_result(NamedTuple, Generic[_DTypeT_co]):  # noqa: N801
    values: array[tuple[int], _DTypeT_co]
    indices: array[tuple[int], Dtype[np.int64]]
    inverse_indices: array[tuple[int], Dtype[np.int64]]
    counts: array[tuple[int], Dtype[np.int64]]

def unique_all(x: array[Any, _DTypeT], /) -> unique_all_result[_DTypeT]: ...

class unique_counts_result(NamedTuple, Generic[_DTypeT_co]):  # noqa: N801
    values: array[tuple[int], _DTypeT_co]
    counts: array[tuple[int], Dtype[np.int64]]

def unique_counts(x: array[Any, _DTypeT], /) -> unique_counts_result[_DTypeT]:
    ...
class unique_inverse_result(NamedTuple, Generic[_DTypeT_co]):  # noqa: N801
    values: array[tuple[int], _DTypeT_co]
    inverse_indices: array[tuple[int], Dtype[np.int64]]

def unique_inverse(
    x: array[Any, _DTypeT],
    /,
) -> unique_inverse_result[_DTypeT]: ...
def unique_values(x: array[Any, _DTypeT], /) -> array[tuple[int], _DTypeT]: ...

_DTypeT = TypeVar("_DTypeT", bound=Dtype)
_DTypeT_co = TypeVar("_DTypeT_co", bound=Dtype, covariant=True)
