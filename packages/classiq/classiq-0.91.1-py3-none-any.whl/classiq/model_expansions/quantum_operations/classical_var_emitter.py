import re

from classiq.interface.exceptions import ClassiqExpansionError
from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.quantum_expressions.arithmetic_operation import (
    ArithmeticOperation,
)

from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import ClassicalSymbol


class ClassicalVarEmitter(Emitter[ArithmeticOperation]):
    def emit(self, op: ArithmeticOperation, /) -> bool:
        result_symbol = self._interpreter.evaluate(op.result_var).value
        if not isinstance(result_symbol, ClassicalSymbol):
            return False
        op.classical_assignment = True
        match = re.search(r"measure\((.*?)\)", op.expression.expr)
        if match is not None:
            var = match.group(1)
            if "[" in var or "." in var:
                raise ClassiqExpansionError("'measure' must receive a whole variable")
            op.set_var_handles([HandleBinding(name=var)])
        self.emit_statement(op)
        return True
