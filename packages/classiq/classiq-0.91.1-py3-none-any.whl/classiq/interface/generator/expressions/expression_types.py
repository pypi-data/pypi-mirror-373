from enum import IntEnum
from typing import TYPE_CHECKING, Union

import sympy

from classiq.interface.generator.expressions.proxies.classical.qmod_struct_instance import (
    QmodStructInstance,
)

if TYPE_CHECKING:
    from classiq.evaluators.qmod_annotated_expression import QmodAnnotatedExpression

RuntimeConstant = Union[
    int,
    float,
    list,
    bool,
    complex,
    IntEnum,
    QmodStructInstance,
    sympy.Basic,
]
ExpressionValue = Union[RuntimeConstant, "QmodAnnotatedExpression"]
