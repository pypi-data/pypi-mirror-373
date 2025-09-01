import ast
from typing import cast

from classiq.interface.exceptions import ClassiqExpansionError
from classiq.interface.generator.arith.argument_utils import (
    unsigned_integer_interpretation,
)
from classiq.interface.generator.arith.register_user_input import RegisterArithmeticInfo
from classiq.interface.model.quantum_type import QuantumScalar

from classiq.evaluators.qmod_annotated_expression import QmodAnnotatedExpression
from classiq.evaluators.qmod_node_evaluators.utils import is_classical_type
from classiq.model_expansions.scope import QuantumSymbol

CONTROL_INOUT_NAME = "ctrl"


def resolve_num_condition(
    condition: QmodAnnotatedExpression,
) -> tuple[QuantumSymbol, str]:
    expr_ast = cast(ast.Compare, condition.root)
    ctrl, ctrl_val = expr_ast.left, expr_ast.comparators[0]
    if is_classical_type(condition.get_type(ctrl)):
        ctrl, ctrl_val = ctrl_val, ctrl
    ctrl_sym = QuantumSymbol(
        handle=condition.get_var(ctrl), quantum_type=condition.get_quantum_type(ctrl)
    )
    return ctrl_sym, _calculate_ctrl_state(
        ctrl_sym, float(condition.get_value(ctrl_val))
    )


def _calculate_ctrl_state(ctrl: QuantumSymbol, ctrl_val: float) -> str:
    ctrl_type = cast(QuantumScalar, ctrl.quantum_type)
    is_signed = ctrl_type.sign_value
    fraction_places = ctrl_type.fraction_digits_value

    reg = RegisterArithmeticInfo(
        size=ctrl.quantum_type.size_in_bits,
        is_signed=is_signed,
        fraction_places=fraction_places,
    )
    uint_ctrl_val = unsigned_integer_interpretation(ctrl_val, reg)

    _validate_control_value_sign(ctrl, ctrl_val, is_signed)
    _validate_control_var_qubits(ctrl, uint_ctrl_val, fraction_places, ctrl_val)

    return _to_twos_complement(uint_ctrl_val, ctrl.quantum_type.size_in_bits)


def _validate_control_value_sign(
    ctrl: QuantumSymbol, ctrl_val: float, is_signed: bool
) -> None:
    if not is_signed and ctrl_val < 0:
        raise ClassiqExpansionError(
            f"Variable {str(ctrl)!r} is not signed but control value "
            f"{ctrl_val} is negative"
        )


def _validate_control_var_qubits(
    ctrl: QuantumSymbol,
    ctrl_val: int,
    fraction_places: int,
    orig_ctrl_val: float,
) -> None:
    required_qubits = _min_unsigned_bit_length(ctrl_val)
    fraction_places_message = (
        f" with {fraction_places} fraction digits" if fraction_places else ""
    )
    if ctrl.quantum_type.size_in_bits < required_qubits:
        raise ClassiqExpansionError(
            f"Variable {str(ctrl)!r} has {ctrl.quantum_type.size_in_bits} qubits{fraction_places_message} but control value "
            f"{str(orig_ctrl_val if fraction_places else int(orig_ctrl_val))!r} requires at least {required_qubits} qubits{fraction_places_message}"
        )


def _min_unsigned_bit_length(number: int) -> int:
    if number < 0:
        raise ClassiqExpansionError(
            f"Quantum register is not signed but control value "
            f"'{number}' is negative"
        )
    try:
        return 1 if number == 0 else number.bit_length()
    except AttributeError as e:
        raise e


def _to_twos_complement(value: int, bits: int) -> str:
    if value >= 0:
        return bin(value)[2:].zfill(bits)[::-1]
    return _to_negative_twos_complement(value, bits)


def _to_negative_twos_complement(value: int, bits: int) -> str:
    mask = (1 << bits) - 1
    value = (abs(value) ^ mask) + 1
    return bin(value)[:1:-1].rjust(bits, "1")
