from typing import TYPE_CHECKING, Optional

from classiq.interface.exceptions import (
    ClassiqExpansionError,
    ClassiqInternalExpansionError,
)
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.helpers.text_utils import readable_list, s
from classiq.interface.model.quantum_statement import QuantumOperation

from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import ClassicalSymbol

if TYPE_CHECKING:
    from classiq.model_expansions.interpreters.base_interpreter import BaseInterpreter


class ExpressionEvaluator(Emitter[QuantumOperation]):
    def __init__(
        self,
        interpreter: "BaseInterpreter",
        expression_name: str,
        *,
        readable_expression_name: Optional[str] = None,
        simplify: bool = False,
        treat_qnum_as_float: bool = False,
        allow_link_time_vars: bool = True,
        allow_runtime_vars: bool = True,
    ) -> None:
        super().__init__(interpreter)
        self._expression_name = expression_name
        self._simplify = simplify
        self._treat_qnum_as_float = treat_qnum_as_float
        self._allow_link_time_vars = allow_link_time_vars
        self._allow_runtime_vars = allow_runtime_vars
        if (
            not allow_link_time_vars or not allow_runtime_vars
        ) and readable_expression_name is None:
            raise ClassiqInternalExpansionError
        self._readable_expression_name = readable_expression_name

    def emit(self, op: QuantumOperation, /) -> bool:
        expression = getattr(op, self._expression_name)
        if not isinstance(expression, Expression) or expression.is_evaluated():
            return False
        evaluated_expression = self._evaluate_expression(
            expression,
            simplify=self._simplify,
            treat_qnum_as_float=self._treat_qnum_as_float,
        )
        for symbol in self._get_symbols_in_expression(evaluated_expression):
            self._capture_handle(symbol.handle, PortDeclarationDirection.Inout)
        self._process_classical_parameters(evaluated_expression)
        op = op.model_copy(
            update={self._expression_name: evaluated_expression, "back_ref": op.uuid}
        )
        self._interpreter.add_to_debug_info(op)
        self._interpreter.emit(op)
        return True

    def _process_classical_parameters(self, evaluated_expression: Expression) -> None:
        link_time_vars: list[str] = []
        runtime_vars: list[str] = []
        for var_name, var_type in self._get_classical_vars_in_expression(
            evaluated_expression
        ):
            if isinstance(self._current_scope[var_name].value, ClassicalSymbol):
                runtime_vars.append(var_name)
            else:
                link_time_vars.append(var_name)
            self._capture_classical_var(var_name, var_type)
        if not self._allow_link_time_vars and len(link_time_vars) > 0:
            link_time_message = f"link-time variable{s(link_time_vars)} {readable_list(link_time_vars, quote=True)}"
        else:
            link_time_message = None
        if not self._allow_runtime_vars and len(runtime_vars) > 0:
            runtime_message = f"runtime variable{s(runtime_vars)} {readable_list(runtime_vars, quote=True)}"
        else:
            runtime_message = None
        if link_time_message is None:
            error_message = runtime_message
        elif runtime_message is None:
            error_message = link_time_message
        else:
            error_message = f"{link_time_message} and {runtime_message}"
        if error_message is not None:
            raise ClassiqExpansionError(
                f"The {self._readable_expression_name} cannot receive "
                f"{error_message}"
            )
