import ast
from enum import IntEnum
from typing import Any

import sympy

from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.expressions.proxies.classical.classical_proxy import (
    ClassicalProxy,
)
from classiq.interface.generator.expressions.proxies.classical.qmod_struct_instance import (
    QmodStructInstance,
)
from classiq.interface.generator.expressions.proxies.classical.utils import (
    get_proxy_type,
)
from classiq.interface.generator.functions.classical_type import ClassicalArray, Integer

from classiq.evaluators.qmod_annotated_expression import QmodAnnotatedExpression
from classiq.evaluators.qmod_expression_visitors.qmod_expression_bwc import (
    QmodExpressionBwc,
)
from classiq.evaluators.qmod_expression_visitors.qmod_expression_evaluator import (
    evaluate_qmod_expression,
)
from classiq.model_expansions.closure import FunctionClosure
from classiq.model_expansions.scope import (
    ClassicalVariable,
    Evaluated,
    QuantumVariable,
    Scope,
)
from classiq.qmod.model_state_container import QMODULE


def process_scope_val(val: Any) -> Any:
    if isinstance(val, list):
        if len(val) > 0 and isinstance(val[0], FunctionClosure):
            return ClassicalArray(
                element_type=Integer(), length=Expression(expr=str(len(val)))
            )
        return val
    if isinstance(val, (int, float, bool, IntEnum, QmodStructInstance)):
        return val
    if isinstance(val, ClassicalProxy):
        return get_proxy_type(val)
    if isinstance(val, ClassicalVariable):
        return val.classical_type
    if isinstance(val, QuantumVariable):
        return val.quantum_type
    if isinstance(val, QmodAnnotatedExpression):
        return val.get_type(val.root)
    if isinstance(val, sympy.Basic):
        return val
    return None


def evaluate_classical_expression(expr: Expression, scope: Scope) -> Evaluated:
    if expr.is_evaluated():
        return Evaluated(value=expr.value.value)
    expr_ast = ast.parse(expr.expr)
    expr_ast = QmodExpressionBwc().visit(expr_ast)
    expr_val = evaluate_qmod_expression(
        ast.unparse(expr_ast),
        classical_struct_declarations=list(QMODULE.type_decls.values()),
        enum_declarations=list(QMODULE.enum_decls.values()),
        scope={
            name: processed_val
            for name, val in scope.items()
            if (processed_val := process_scope_val(val.value)) is not None
        },
    )
    if expr_val.has_value(expr_val.root):
        expr_val = expr_val.get_value(expr_val.root)
    return Evaluated(value=expr_val)
