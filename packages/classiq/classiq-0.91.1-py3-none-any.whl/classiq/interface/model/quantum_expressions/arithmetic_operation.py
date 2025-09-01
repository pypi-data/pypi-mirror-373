from collections.abc import Mapping, Sequence
from typing import Literal, cast

from classiq.interface.enum_utils import StrEnum
from classiq.interface.generator.arith.arithmetic import (
    ARITHMETIC_EXPRESSION_RESULT_NAME,
)
from classiq.interface.model.handle_binding import (
    ConcreteHandleBinding,
    HandleBinding,
)
from classiq.interface.model.quantum_expressions.quantum_expression import (
    QuantumAssignmentOperation,
)
from classiq.interface.model.quantum_statement import HandleMetadata
from classiq.interface.model.quantum_type import QuantumType

from classiq.evaluators.qmod_annotated_expression import QmodAnnotatedExpression
from classiq.model_expansions.arithmetic import NumericAttributes


class ArithmeticOperationKind(StrEnum):
    InplaceAdd = "inplace_add"
    Assignment = "assignment"
    InplaceXor = "inplace_xor"


class ArithmeticOperation(QuantumAssignmentOperation):
    kind: Literal["ArithmeticOperation"]

    operation_kind: ArithmeticOperationKind
    classical_assignment: bool = False

    @property
    def is_inplace(self) -> bool:
        return self.operation_kind in (
            ArithmeticOperationKind.InplaceXor,
            ArithmeticOperationKind.InplaceAdd,
        )

    def initialize_var_types(
        self,
        var_types: dict[str, QuantumType],
        machine_precision: int,
    ) -> None:
        super().initialize_var_types(var_types, machine_precision)
        expr_val = self.expression.value.value
        if isinstance(expr_val, QmodAnnotatedExpression):
            self._result_type = expr_val.get_quantum_type(expr_val.root)
        else:
            self._result_type = NumericAttributes.from_constant(
                cast(float, expr_val), machine_precision
            ).to_quantum_numeric()

    @property
    def wiring_inouts(
        self,
    ) -> Mapping[str, ConcreteHandleBinding]:
        inouts = dict(super().wiring_inouts)
        if self.is_inplace and not self.classical_assignment:
            inouts[self.result_name()] = self.result_var
        return inouts

    @property
    def readable_inouts(self) -> Sequence[HandleMetadata]:
        inouts = [
            HandleMetadata(handle=handle, readable_location="in an expression")
            for handle in self.var_handles
        ]
        if self.is_inplace and not self.classical_assignment:
            inouts.append(
                HandleMetadata(
                    handle=self.result_var,
                    readable_location="on the left-hand side of an in-place assignment",
                )
            )
        return inouts

    @property
    def wiring_outputs(self) -> Mapping[str, HandleBinding]:
        if self.is_inplace or self.classical_assignment:
            return {}
        return super().wiring_outputs

    @property
    def readable_outputs(self) -> Sequence[HandleMetadata]:
        if self.is_inplace or self.classical_assignment:
            return []
        return [
            HandleMetadata(
                handle=self.result_var,
                readable_location="on the left-hand side of an assignment",
            )
        ]

    @classmethod
    def result_name(cls) -> str:
        return ARITHMETIC_EXPRESSION_RESULT_NAME
