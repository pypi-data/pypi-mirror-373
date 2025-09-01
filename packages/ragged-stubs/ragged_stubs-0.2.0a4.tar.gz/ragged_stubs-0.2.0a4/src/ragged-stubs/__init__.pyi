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

__all__ = [  # noqa: RUF022
    "__array_api_version__",
    # _spec_array_object
    "array",
    # _spec_constants
    "e",
    "inf",
    "nan",
    "newaxis",
    "pi",
    # _spec_creation_functions
    "arange",
    "asarray",
    "empty",
    "empty_like",
    "eye",
    "from_dlpack",
    "full",
    "full_like",
    "linspace",
    "meshgrid",
    "ones",
    "ones_like",
    "tril",
    "triu",
    "zeros",
    "zeros_like",
    # _spec_data_type_functions
    "astype",
    "can_cast",
    "finfo",
    "iinfo",
    "isdtype",
    "result_type",
    # _spec_elementwise_functions
    "abs",
    "acos",
    "acosh",
    "add",
    "asin",
    "asinh",
    "atan",
    "atan2",
    "atanh",
    "bitwise_and",
    "bitwise_left_shift",
    "bitwise_invert",
    "bitwise_or",
    "bitwise_right_shift",
    "bitwise_xor",
    "ceil",
    "conj",
    "cos",
    "cosh",
    "divide",
    "equal",
    "exp",
    "expm1",
    "floor",
    "floor_divide",
    "greater",
    "greater_equal",
    "imag",
    "isfinite",
    "isinf",
    "isnan",
    "less",
    "less_equal",
    "log",
    "log1p",
    "log2",
    "log10",
    "logaddexp",
    "logical_and",
    "logical_not",
    "logical_or",
    "logical_xor",
    "multiply",
    "negative",
    "not_equal",
    "positive",
    "pow",
    "real",
    "remainder",
    "round",
    "sign",
    "sin",
    "sinh",
    "square",
    "sqrt",
    "subtract",
    "tan",
    "tanh",
    "trunc",
    # _spec_indexing_functions
    "take",
    # _spec_linear_algebra_functions
    "matmul",
    "matrix_transpose",
    "tensordot",
    "vecdot",
    # _spec_manipulation_functions
    "broadcast_arrays",
    "broadcast_to",
    "concat",
    "expand_dims",
    "flip",
    "permute_dims",
    "reshape",
    "roll",
    "squeeze",
    "stack",
    # _spec_searching_functions
    "argmax",
    "argmin",
    "nonzero",
    "where",
    # _spec_set_functions
    "unique_all",
    "unique_counts",
    "unique_inverse",
    "unique_values",
    # _spec_sorting_functions
    "argsort",
    "sort",
    # _spec_statistical_functions
    "max",
    "mean",
    "min",
    "prod",
    "std",
    "sum",
    "var",
    # _spec_utility_functions
    "all",
    "any",
]

from typing import Final

from ._spec_array_object import array
from ._spec_constants import (
    e,
    inf,
    nan,
    newaxis,
    pi,
)
from ._spec_creation_functions import (
    arange,
    asarray,
    empty,
    empty_like,
    eye,
    from_dlpack,
    full,
    full_like,
    linspace,
    meshgrid,
    ones,
    ones_like,
    tril,
    triu,
    zeros,
    zeros_like,
)
from ._spec_data_type_functions import (
    astype,
    can_cast,
    finfo,
    iinfo,
    isdtype,
    result_type,
)
from ._spec_elementwise_functions import (
    abs,  # noqa: A004
    acos,
    acosh,
    add,
    asin,
    asinh,
    atan,
    atan2,
    atanh,
    bitwise_and,
    bitwise_invert,
    bitwise_left_shift,
    bitwise_or,
    bitwise_right_shift,
    bitwise_xor,
    ceil,
    conj,
    cos,
    cosh,
    divide,
    equal,
    exp,
    expm1,
    floor,
    floor_divide,
    greater,
    greater_equal,
    imag,
    isfinite,
    isinf,
    isnan,
    less,
    less_equal,
    log,
    log1p,
    log2,
    log10,
    logaddexp,
    logical_and,
    logical_not,
    logical_or,
    logical_xor,
    multiply,
    negative,
    not_equal,
    positive,
    pow,  # noqa: A004
    real,
    remainder,
    round,  # noqa: A004
    sign,
    sin,
    sinh,
    sqrt,
    square,
    subtract,
    tan,
    tanh,
    trunc,
)
from ._spec_indexing_functions import (
    take,
)
from ._spec_linear_algebra_functions import (
    matmul,
    matrix_transpose,
    tensordot,
    vecdot,
)
from ._spec_manipulation_functions import (
    broadcast_arrays,
    broadcast_to,
    concat,
    expand_dims,
    flip,
    permute_dims,
    reshape,
    roll,
    squeeze,
    stack,
)
from ._spec_searching_functions import (
    argmax,
    argmin,
    nonzero,
    where,
)
from ._spec_set_functions import (
    unique_all,
    unique_counts,
    unique_inverse,
    unique_values,
)
from ._spec_sorting_functions import (
    argsort,
    sort,
)
from ._spec_statistical_functions import (
    max,  # noqa: A004
    mean,
    min,  # noqa: A004
    prod,
    std,
    sum,  # noqa: A004
    var,
)
from ._spec_utility_functions import (
    all,  # noqa: A004
    any,  # noqa: A004
)

__array_api_version__: Final[str]
