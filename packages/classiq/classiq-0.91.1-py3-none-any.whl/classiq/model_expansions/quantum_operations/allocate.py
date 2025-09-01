from typing import TYPE_CHECKING, Any, Union

import sympy

from classiq.interface.debug_info.debug_info import FunctionDebugInfo
from classiq.interface.exceptions import ClassiqExpansionError, ClassiqValueError
from classiq.interface.generator.expressions.evaluated_expression import (
    EvaluatedExpression,
)
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.expressions.expression_types import ExpressionValue
from classiq.interface.generator.functions.classical_type import Bool, Integer, Real
from classiq.interface.helpers.text_utils import s
from classiq.interface.model.allocate import Allocate
from classiq.interface.model.handle_binding import NestedHandleBinding
from classiq.interface.model.quantum_type import (
    QuantumBitvector,
    QuantumNumeric,
)

from classiq.evaluators.qmod_annotated_expression import QmodAnnotatedExpression
from classiq.evaluators.qmod_node_evaluators.utils import get_sympy_type
from classiq.evaluators.qmod_type_inference.quantum_type_inference import (
    inject_quantum_type_attributes_inplace,
)
from classiq.model_expansions.quantum_operations.emitter import Emitter
from classiq.model_expansions.scope import QuantumSymbol

if TYPE_CHECKING:
    from classiq.model_expansions.interpreters.base_interpreter import BaseInterpreter


def _assign_attr(
    op_update_dict: dict[str, Expression], attr: str, size_value: ExpressionValue
) -> None:
    op_update_dict[attr] = Expression(expr=str(size_value))
    op_update_dict[attr]._evaluated_expr = EvaluatedExpression(value=size_value)


class AllocateEmitter(Emitter[Allocate]):
    def __init__(
        self, interpreter: "BaseInterpreter", allow_symbolic_attrs: bool = False
    ) -> None:
        super().__init__(interpreter)
        self._allow_symbolic_attrs = allow_symbolic_attrs

    def emit(self, allocate: Allocate, /) -> bool:
        target: QuantumSymbol = self._interpreter.evaluate(allocate.target).as_type(
            QuantumSymbol
        )

        if isinstance(target.handle, NestedHandleBinding):
            raise ClassiqValueError(
                f"Cannot allocate partial quantum variable {str(target.handle)!r}"
            )

        op_update_dict: dict[str, Expression] = {}

        if allocate.size is None:
            if allocate.is_signed is not None or allocate.fraction_digits is not None:
                raise ClassiqValueError(
                    "Numeric attributes cannot be specified without size"
                )
            self._handle_without_size(target, op_update_dict)

        elif allocate.is_signed is None and allocate.fraction_digits is None:
            self._handle_with_size(target, allocate.size, op_update_dict)

        elif allocate.is_signed is not None and allocate.fraction_digits is not None:
            self._handle_with_numeric_attrs(
                target,
                allocate.size,
                allocate.is_signed,
                allocate.fraction_digits,
                op_update_dict,
            )

        else:
            raise ClassiqValueError(
                "Sign and fraction digits must be specified together"
            )

        if isinstance(target.quantum_type, QuantumNumeric):
            target.quantum_type.set_bounds((0, 0))

        allocate = allocate.model_copy(update=op_update_dict)
        self._register_debug_info(allocate)
        self.emit_statement(allocate)
        return True

    def _handle_without_size(
        self,
        target: QuantumSymbol,
        op_update_dict: dict[str, Expression],
    ) -> None:
        if target.quantum_type.has_size_in_bits:
            expr = str(target.quantum_type.size_in_bits)
        elif self._allow_symbolic_attrs:
            expr = f"{target.handle}.size"
        else:
            raise ClassiqValueError(
                f"Could not infer the size of variable {str(target.handle)!r}"
            )
        op_update_dict["size"] = self._evaluate_expression(Expression(expr=expr))

    def _handle_with_size(
        self,
        target: QuantumSymbol,
        size: Expression,
        op_update_dict: dict[str, Expression],
    ) -> None:
        size_value = self._interpret_size(size, str(target.handle))
        _assign_attr(op_update_dict, "size", size_value)

        if not isinstance(
            size_value, QmodAnnotatedExpression
        ) and not inject_quantum_type_attributes_inplace(
            QuantumBitvector(length=op_update_dict["size"]), target.quantum_type
        ):
            raise ClassiqExpansionError(
                f"Cannot allocate {op_update_dict['size']} qubits for variable "
                f"{str(target)!r} of type {target.quantum_type.qmod_type_name}"
            )

    def _handle_with_numeric_attrs(
        self,
        target: QuantumSymbol,
        size: Expression,
        is_signed: Expression,
        fraction_digits: Expression,
        op_update_dict: dict[str, Expression],
    ) -> None:
        var_name = str(target.handle)
        if not isinstance(target.quantum_type, QuantumNumeric):
            raise ClassiqValueError(
                f"Non-numeric variable {var_name!r} cannot be allocated with numeric attributes"
            )

        size_value = self._interpret_size(size, var_name)
        _assign_attr(op_update_dict, "size", size_value)
        is_signed_value = self._interpret_is_signed(is_signed)
        _assign_attr(op_update_dict, "is_signed", is_signed_value)
        fraction_digits_value = self._interpret_fraction_digits(fraction_digits)
        _assign_attr(op_update_dict, "fraction_digits", fraction_digits_value)
        self._validate_numeric_atrributes(
            var_name, size_value, is_signed_value, fraction_digits_value
        )

        if not (
            isinstance(size_value, QmodAnnotatedExpression)
            or isinstance(is_signed_value, QmodAnnotatedExpression)
            or isinstance(fraction_digits_value, QmodAnnotatedExpression)
        ) and not inject_quantum_type_attributes_inplace(
            QuantumNumeric(
                size=op_update_dict["size"],
                is_signed=op_update_dict["is_signed"],
                fraction_digits=op_update_dict["fraction_digits"],
            ),
            target.quantum_type,
        ):
            raise ClassiqExpansionError(
                f"Cannot allocate {op_update_dict['size']} qubits for variable "
                f"{var_name!r} of type {target.quantum_type.qmod_type_name}"
            )

    def _validate_numeric_atrributes(
        self,
        var_name: str,
        size_value: Any,
        is_signed_value: Any,
        fraction_digits_value: Any,
    ) -> None:
        if (
            isinstance(size_value, int)
            and isinstance(is_signed_value, bool)
            and isinstance(fraction_digits_value, int)
        ):
            if size_value < 0:
                raise ClassiqValueError(
                    f"Cannot allocate {size_value} qubit{s(size_value)} for variable "
                    f"{var_name!r}"
                )
            if fraction_digits_value < 0:
                raise ClassiqValueError(
                    f"Variable {var_name!r} cannot have a negative number of fraction "
                    f"digits (got {fraction_digits_value})"
                )
            if size_value < fraction_digits_value:
                raise ClassiqValueError(
                    f"Cannot allocate {size_value} qubit{s(size_value)} for variable "
                    f"{var_name!r} with {fraction_digits_value} fraction digits"
                )

    def _interpret_size(
        self, size: Expression, var_name: str
    ) -> Union[int, float, sympy.Basic, QmodAnnotatedExpression]:
        size_value = self._interpreter.evaluate(size).value
        if not (
            (
                isinstance(size_value, QmodAnnotatedExpression)
                and isinstance(size_value.get_type(size_value.root), (Integer, Real))
            )
            or isinstance(size_value, (int, float))
            or (
                isinstance(size_value, sympy.Basic)
                and isinstance(get_sympy_type(size_value), (Integer, Real))
            )
        ):
            raise ClassiqValueError(
                f"The number of allocated qubits must be an integer. Got "
                f"{str(size_value)!r}"
            )
        if (
            isinstance(size_value, QmodAnnotatedExpression)
            and not self._allow_symbolic_attrs
        ):
            raise ClassiqValueError(
                f"Could not infer the size of variable {var_name!r}"
            )
        return size_value

    def _interpret_is_signed(
        self, is_signed: Expression
    ) -> Union[bool, sympy.Basic, QmodAnnotatedExpression]:
        is_signed_value = self._interpreter.evaluate(is_signed).value
        if not self._allow_symbolic_attrs and not (
            isinstance(is_signed_value, bool)
            or (
                isinstance(is_signed_value, sympy.Basic)
                and isinstance(get_sympy_type(is_signed_value), Bool)
            )
        ):
            raise ClassiqValueError(
                f"The sign of a variable must be boolean. Got "
                f"{str(is_signed_value)!r}"
            )
        return is_signed_value

    def _interpret_fraction_digits(
        self, fraction_digits: Expression
    ) -> Union[int, float, sympy.Expr, QmodAnnotatedExpression]:
        fraction_digits_value = self._interpreter.evaluate(fraction_digits).value
        if not self._allow_symbolic_attrs and not (
            isinstance(fraction_digits_value, (int, float))
            or (
                isinstance(fraction_digits_value, sympy.Expr)
                and fraction_digits_value.is_integer
            )
        ):
            raise ClassiqValueError(
                f"The fraction digits of a variable must be an integer. Got "
                f"{str(fraction_digits_value)!r}"
            )
        return fraction_digits_value

    def _register_debug_info(self, allocate: Allocate) -> None:
        if (
            allocate.uuid in self._debug_info
            and self._debug_info[allocate.uuid].name != ""
        ):
            return
        parameters: dict[str, str] = {}
        if allocate.size is not None:
            parameters["num_qubits"] = allocate.size.expr
        self._debug_info[allocate.uuid] = FunctionDebugInfo(
            name="allocate",
            port_to_passed_variable_map={"ARG": str(allocate.target)},
            node=allocate._as_back_ref(),
        )
