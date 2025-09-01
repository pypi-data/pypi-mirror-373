from enum import Enum
from typing import Any

import sympy

from classiq.interface.exceptions import ClassiqInternalExpansionError
from classiq.interface.generator.constant import Constant
from classiq.interface.generator.expressions.expression_types import RuntimeConstant
from classiq.interface.generator.expressions.proxies.classical.qmod_struct_instance import (
    QmodStructInstance,
)

from classiq.evaluators.classical_expression import evaluate_classical_expression
from classiq.model_expansions.scope import Evaluated, Scope


def qmod_val_to_python(val: RuntimeConstant) -> Any:
    if isinstance(val, (int, float, bool, complex, Enum)):
        return val
    if isinstance(val, list):
        return [qmod_val_to_python(item) for item in val]
    if isinstance(val, QmodStructInstance):
        return {
            field_name: qmod_val_to_python(field_val)
            for field_name, field_val in val.fields.items()
        }
    if isinstance(val, sympy.Expr):
        return val.evalf()
    raise ClassiqInternalExpansionError(
        f"Could not convert Qmod value {str(val)!r} of type {type(val).__name__} to Python"
    )


def evaluate_constants(constants: list[Constant]) -> Scope:
    result = Scope()
    for constant in constants:
        expr_val = evaluate_classical_expression(constant.value, result).value
        result[constant.name] = Evaluated(value=expr_val)

    return result


def evaluate_constants_as_python(constants: list[Constant]) -> dict[str, Any]:
    evaluated = evaluate_constants(constants)
    return {
        constant.name: qmod_val_to_python(evaluated[constant.name].value)
        for constant in constants
    }
