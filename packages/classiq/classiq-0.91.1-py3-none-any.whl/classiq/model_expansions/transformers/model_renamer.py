import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from typing import TypeVar, cast

from classiq.interface.generator.expressions.atomic_expression_functions import (
    CLASSICAL_ATTRIBUTES,
)
from classiq.interface.generator.expressions.evaluated_expression import (
    EvaluatedExpression,
)
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.visitor import NodeType
from classiq.interface.model.handle_binding import FieldHandleBinding, HandleBinding
from classiq.interface.model.model_visitor import ModelTransformer
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumExpressionOperation,
)

from classiq.evaluators.qmod_annotated_expression import QmodAnnotatedExpression
from classiq.evaluators.qmod_expression_visitors.qmod_expression_renamer import (
    replace_expression_type_attrs,
    replace_expression_vars,
)

AST_NODE = TypeVar("AST_NODE", bound=NodeType)


def _replace_full_word(pattern: str, substitution: str, target: str) -> str:
    return re.sub(
        rf"(^|\b|\W)({re.escape(pattern)})($|\b|\W)", rf"\1{substitution}\3", target
    )


def _handle_contains_handle(handle: HandleBinding, other_handle: HandleBinding) -> int:
    if str(other_handle) in str(handle) or other_handle.qmod_expr in handle.qmod_expr:
        return 1
    if str(handle) in str(other_handle) or handle.qmod_expr in other_handle.qmod_expr:
        return -1
    return 0


@dataclass(frozen=True)
class HandleRenaming:
    source_handle: HandleBinding
    target_var_name: str

    @property
    def target_var_handle(self) -> HandleBinding:
        return HandleBinding(name=self.target_var_name)


SymbolRenaming = Mapping[HandleBinding, Sequence[HandleRenaming]]


def rewrite_expression(
    symbol_mapping: SymbolRenaming, expression: Expression
) -> Expression:
    if len(symbol_mapping) == 0:
        return expression
    expr_val = expression.value.value
    if not isinstance(expr_val, QmodAnnotatedExpression):
        return expression

    type_attr_mapping = {
        (source_handle.base_handle, source_attr): renaming.target_var_handle
        for renamings in symbol_mapping.values()
        for renaming in renamings
        if isinstance(source_handle := renaming.source_handle, FieldHandleBinding)
        and (source_attr := source_handle.field) in CLASSICAL_ATTRIBUTES
    }
    expr_val = replace_expression_type_attrs(expr_val, type_attr_mapping)

    var_mapping = {
        source_handle: renaming.target_var_handle
        for renamings in symbol_mapping.values()
        for renaming in renamings
        if not isinstance(source_handle := renaming.source_handle, FieldHandleBinding)
        or source_handle.field not in CLASSICAL_ATTRIBUTES
    }
    expr_val = replace_expression_vars(expr_val, var_mapping)

    renamed_expr = Expression(expr=str(expr_val))
    renamed_expr._evaluated_expr = EvaluatedExpression(value=expr_val)
    return renamed_expr


class _ReplaceSplitVarsHandles(ModelTransformer):
    def __init__(self, symbol_mapping: SymbolRenaming) -> None:
        self._handle_replacements = {
            part.source_handle: part.target_var_handle
            for parts in symbol_mapping.values()
            for part in parts
        }

    def visit_HandleBinding(self, handle: HandleBinding) -> HandleBinding:
        handle = handle.collapse()
        for handle_to_replace, replacement in self._handle_replacements.items():
            handle = handle.replace_prefix(handle_to_replace, replacement)
        return handle


class _ReplaceSplitVarsExpressions(ModelTransformer):
    def __init__(self, symbol_mapping: SymbolRenaming) -> None:
        self._symbol_mapping = symbol_mapping

    def visit_Expression(self, expr: Expression) -> Expression:
        return rewrite_expression(self._symbol_mapping, expr)

    def visit_QuantumExpressionOperation(
        self, op: QuantumExpressionOperation
    ) -> QuantumExpressionOperation:
        op = cast(QuantumExpressionOperation, self.generic_visit(op))
        previous_var_handles = list(op._var_handles)
        op._var_handles = _ReplaceSplitVarsHandles(self._symbol_mapping).visit(
            op._var_handles
        )
        op._var_types = {
            new_handle.name: op._var_types.get(
                new_handle.name, op._var_types[previous_handle.name]
            )
            for previous_handle, new_handle in zip(
                previous_var_handles, op._var_handles
            )
        }
        return op


class ModelRenamer:
    def rewrite(self, subject: AST_NODE, symbol_mapping: SymbolRenaming) -> AST_NODE:
        if len(symbol_mapping) == 0:
            return subject
        subject = _ReplaceSplitVarsHandles(symbol_mapping).visit(subject)
        subject = _ReplaceSplitVarsExpressions(symbol_mapping).visit(subject)
        return subject
