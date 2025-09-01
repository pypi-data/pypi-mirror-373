from typing import TYPE_CHECKING, Any, NoReturn, TypeVar, Union

import sympy

from classiq.interface.exceptions import (
    ClassiqExpansionError,
    ClassiqInternalExpansionError,
)
from classiq.interface.generator.expressions.evaluated_expression import (
    EvaluatedExpression,
)
from classiq.interface.generator.expressions.expression import Expression
from classiq.interface.generator.expressions.expression_types import RuntimeConstant
from classiq.interface.generator.functions.classical_type import (
    Bool,
    ClassicalArray,
    ClassicalTuple,
    ClassicalType,
    Integer,
)
from classiq.interface.generator.functions.concrete_types import ConcreteQuantumType
from classiq.interface.generator.functions.port_declaration import (
    PortDeclarationDirection,
)
from classiq.interface.generator.functions.type_name import (
    TypeName,
)
from classiq.interface.helpers.backward_compatibility import zip_strict
from classiq.interface.model.classical_parameter_declaration import (
    ClassicalParameterDeclaration,
)
from classiq.interface.model.handle_binding import HandleBinding
from classiq.interface.model.port_declaration import PortDeclaration
from classiq.interface.model.quantum_function_declaration import (
    AnonQuantumOperandDeclaration,
    PositionalArg,
    QuantumOperandDeclaration,
)
from classiq.interface.model.quantum_type import (
    QuantumBit,
    QuantumBitvector,
    QuantumNumeric,
    QuantumType,
)

from classiq.evaluators.classical_expression import (
    evaluate_classical_expression,
)
from classiq.evaluators.qmod_annotated_expression import QmodAnnotatedExpression
from classiq.evaluators.qmod_node_evaluators.utils import QmodType, get_sympy_val
from classiq.evaluators.qmod_type_inference.classical_type_inference import (
    infer_classical_type,
    inject_classical_type_attributes,
)
from classiq.evaluators.qmod_type_inference.quantum_type_inference import (
    inject_quantum_type_attributes,
    validate_quantum_type_attributes,
)
from classiq.evaluators.type_type_match import check_signature_match
from classiq.model_expansions.closure import FunctionClosure
from classiq.model_expansions.scope import (
    ClassicalSymbol,
    Evaluated,
    QuantumSymbol,
    QuantumVariable,
    Scope,
)
from classiq.model_expansions.visitors.symbolic_param_inference import (
    set_generative_recursively,
)


def evaluate_parameter_types_from_args(
    closure: FunctionClosure, arguments: list[Evaluated]
) -> list[PositionalArg]:
    parameters = closure.positional_arg_declarations
    if len(parameters) != len(arguments):
        raise ClassiqExpansionError(
            f"Function {closure.name!r} takes {len(parameters)} arguments but "
            f"{len(arguments)} were given"
        )

    for parameter, argument in zip_strict(parameters, arguments, strict=True):
        if isinstance(parameter, ClassicalParameterDeclaration):
            arg_val = argument.value
            if not isinstance(arg_val, QmodAnnotatedExpression):
                closure.scope[parameter.name] = argument

    evaluated_params = [
        _evaluate_type_from_arg(parameter, argument, closure)
        for parameter, argument in zip_strict(parameters, arguments, strict=True)
    ]

    parameter_names = {parameter.name for parameter in parameters}
    for parameter, argument in zip_strict(parameters, arguments, strict=True):
        if isinstance(parameter, QuantumOperandDeclaration):
            _update_operand_signature_environment(
                argument.value, parameter_names, closure
            )

    return evaluated_params


NestedFunctionClosureT = Union[FunctionClosure, list["NestedFunctionClosureT"]]


def _update_operand_signature_environment(
    operand_val: NestedFunctionClosureT,
    parameter_names: set[str],
    closure: FunctionClosure,
) -> None:
    # We update the environment (parent) of the operand by adding closure.scope.data,
    # which includes the parameters that appear in the function's signature only.
    if isinstance(operand_val, list):
        for operand in operand_val:
            _update_operand_signature_environment(operand, parameter_names, closure)
        return
    if not isinstance(operand_val, FunctionClosure):
        raise ClassiqInternalExpansionError
    operand_val.signature_scope.update(
        {
            identifier: value
            for identifier, value in closure.scope.data.items()
            if identifier in parameter_names
        }
    )


def _evaluate_type_from_arg(
    parameter: PositionalArg,
    argument: Evaluated,
    closure: FunctionClosure,
) -> PositionalArg:
    # FIXME: Remove suzuki_trotter overloading (CLS-2912)
    if closure.name == "suzuki_trotter" and parameter.name == "pauli_operator":
        return parameter
    if isinstance(parameter, ClassicalParameterDeclaration):
        return _evaluate_classical_type_from_arg(parameter, argument, closure)
    if isinstance(parameter, PortDeclaration):
        return _evaluate_quantum_type_from_arg(parameter, argument, closure)
    if TYPE_CHECKING:
        assert isinstance(parameter, QuantumOperandDeclaration)
    if parameter.is_list:
        return _evaluate_op_list_type_from_arg(parameter, argument, closure)
    else:
        return _evaluate_op_type_from_arg(parameter, argument, closure)


def _evaluate_classical_type_from_arg(
    parameter: ClassicalParameterDeclaration,
    argument: Evaluated,
    closure: FunctionClosure,
) -> ClassicalParameterDeclaration:
    unified_scope = closure.scope | closure.signature_scope
    updated_classical_type = evaluate_type_in_classical_symbol(
        parameter.classical_type.model_copy(), unified_scope, parameter.name
    )
    arg_val = argument.value
    if isinstance(arg_val, QmodAnnotatedExpression):
        arg_type = arg_val.get_classical_type(arg_val.root)
    else:
        arg_type = infer_classical_type(arg_val)
    injected_classical_type = inject_classical_type_attributes(
        arg_type.without_symbolic_attributes(), updated_classical_type
    )
    if injected_classical_type is None:
        _raise_argument_type_error(
            arg_val, arg_type, parameter.name, updated_classical_type
        )
    if parameter.classical_type.is_purely_generative:
        set_generative_recursively(injected_classical_type)
    closure.scope[parameter.name] = Evaluated(
        value=(
            ClassicalSymbol(
                handle=HandleBinding(name=parameter.name),
                classical_type=injected_classical_type,
            )
            if isinstance(arg_val, QmodAnnotatedExpression)
            else arg_val
        ),
        defining_function=closure,
    )
    return ClassicalParameterDeclaration(
        name=parameter.name, classical_type=injected_classical_type
    )


def _evaluate_quantum_type_from_arg(
    parameter: PortDeclaration,
    argument: Evaluated,
    closure: FunctionClosure,
) -> PortDeclaration:
    unified_scope = closure.scope | closure.signature_scope
    updated_quantum_type: QuantumType = evaluate_type_in_quantum_symbol(
        parameter.quantum_type.model_copy(), unified_scope, parameter.name
    )
    if parameter.direction != PortDeclarationDirection.Output:
        arg_type = argument.as_type(QuantumVariable).quantum_type
        updated_output_quantum_type = inject_quantum_type_attributes(
            arg_type.without_symbolic_attributes(), updated_quantum_type
        )
        if updated_output_quantum_type is None:
            _raise_argument_type_error(
                argument.value, arg_type, parameter.name, updated_quantum_type
            )
        updated_quantum_type = updated_output_quantum_type
    validate_quantum_type_attributes(updated_quantum_type)
    closure.scope[parameter.name] = Evaluated(
        value=QuantumSymbol(
            handle=HandleBinding(name=parameter.name), quantum_type=updated_quantum_type
        ),
        defining_function=closure,
    )
    return parameter.model_copy(update={"quantum_type": updated_quantum_type})


def _evaluate_op_list_type_from_arg(
    parameter: QuantumOperandDeclaration, argument: Evaluated, closure: FunctionClosure
) -> QuantumOperandDeclaration:
    arg_val = argument.value
    if not isinstance(arg_val, list) or any(
        not isinstance(op, FunctionClosure) for op in arg_val
    ):
        if isinstance(arg_val, FunctionClosure):
            _raise_argument_type_error(
                "<lambda>",
                arg_val.as_operand_declaration(is_list=False),
                parameter.name,
                parameter,
            )
        raise ClassiqInternalExpansionError("Non-lambda argument to lambda parameter")
    for idx, operand in enumerate(arg_val):
        check_signature_match(
            parameter.positional_arg_declarations,
            operand.positional_arg_declarations,
            f"operand #{idx + 1} in parameter {parameter.name!r} "
            f"in function {closure.name!r}",
        )
    return parameter


def _evaluate_op_type_from_arg(
    parameter: QuantumOperandDeclaration, argument: Evaluated, closure: FunctionClosure
) -> QuantumOperandDeclaration:
    arg_val = argument.value
    if not isinstance(arg_val, FunctionClosure):
        if isinstance(arg_val, list):
            if len(arg_val) == 0:
                _raise_argument_type_error(
                    arg_val,
                    AnonQuantumOperandDeclaration(is_list=True),
                    parameter.name,
                    parameter,
                )
            first_lambda = arg_val[0]
            if isinstance(first_lambda, FunctionClosure):
                _raise_argument_type_error(
                    arg_val,
                    first_lambda.as_operand_declaration(is_list=True),
                    parameter.name,
                    parameter,
                )
        raise ClassiqInternalExpansionError("Non-lambda argument to lambda parameter")
    check_signature_match(
        parameter.positional_arg_declarations,
        arg_val.positional_arg_declarations,
        f"operand {parameter.name!r} in function {closure.name!r}",
    )
    return parameter


def _raise_argument_type_error(
    arg_val: Any,
    arg_type: Union[QmodType, AnonQuantumOperandDeclaration],
    param_name: str,
    param_type: Union[QmodType, AnonQuantumOperandDeclaration],
) -> NoReturn:
    raise ClassiqExpansionError(
        f"Argument {str(arg_val)!r} of type "
        f"{arg_type.qmod_type_name} is incompatible with parameter "
        f"{param_name!r} of type {param_type.qmod_type_name}"
    )


def evaluate_type_in_quantum_symbol(
    type_to_update: QuantumType, scope: Scope, param_name: str
) -> ConcreteQuantumType:
    if isinstance(type_to_update, QuantumBitvector):
        return _evaluate_qarray_in_quantum_symbol(type_to_update, scope, param_name)
    elif isinstance(type_to_update, QuantumNumeric):
        return _evaluate_qnum_in_quantum_symbol(type_to_update, scope, param_name)
    elif isinstance(type_to_update, TypeName):
        return _evaluate_qstruct_in_quantum_symbol(type_to_update, scope, param_name)
    else:
        assert isinstance(type_to_update, QuantumBit)
        return type_to_update


def _evaluate_qarray_in_quantum_symbol(
    type_to_update: QuantumBitvector, scope: Scope, param_name: str
) -> QuantumBitvector:
    new_element_type = evaluate_type_in_quantum_symbol(
        type_to_update.element_type, scope, param_name
    )
    type_to_update.element_type = new_element_type
    if type_to_update.length is not None:
        type_to_update.length = _eval_expr(
            type_to_update.length,
            scope,
            int,
            Integer,
            type_to_update.type_name,
            "length",
            param_name,
        )
    return type_to_update


def _evaluate_qnum_in_quantum_symbol(
    type_to_update: QuantumNumeric, scope: Scope, param_name: str
) -> QuantumNumeric:
    if type_to_update.size is None:
        return type_to_update
    type_to_update.size = _eval_expr(
        type_to_update.size,
        scope,
        int,
        Integer,
        type_to_update.type_name,
        "size",
        param_name,
    )

    if type_to_update.is_signed is not None:
        type_to_update.is_signed = _eval_expr(
            type_to_update.is_signed,
            scope,
            bool,
            Bool,
            type_to_update.type_name,
            "sign",
            param_name,
        )
    else:
        type_to_update.is_signed = Expression(expr="False")

    if type_to_update.fraction_digits is not None:
        type_to_update.fraction_digits = _eval_expr(
            type_to_update.fraction_digits,
            scope,
            int,
            Integer,
            type_to_update.type_name,
            "fraction digits",
            param_name,
        )
    else:
        type_to_update.fraction_digits = Expression(expr="0")

    return type_to_update


_EXPR_TYPE = TypeVar("_EXPR_TYPE", bound=RuntimeConstant)


def _eval_expr(
    expression: Expression,
    scope: Scope,
    expected_type: type[_EXPR_TYPE],
    expected_qmod_type: type,
    type_name: str,
    attr_name: str,
    param_name: str,
) -> Expression:
    val = evaluate_classical_expression(Expression(expr=expression.expr), scope).value
    if isinstance(val, sympy.Basic):
        val = get_sympy_val(val)
    if expected_type is int and isinstance(val, float) and int(val) == val:
        val = int(val)
    if not isinstance(val, expected_type) and (
        not isinstance(val, QmodAnnotatedExpression)
        or not isinstance(val.get_type(val.root), expected_qmod_type)
    ):
        raise ClassiqExpansionError(
            f"When inferring the type of parameter {param_name!r}: "
            f"{type_name} {attr_name} must be {expected_qmod_type.__name__}, got "
            f"{str(val)!r}"
        )
    expr = Expression(expr=str(val))
    expr._evaluated_expr = EvaluatedExpression(value=val)
    return expr


def _evaluate_qstruct_in_quantum_symbol(
    type_to_update: TypeName, scope: Scope, param_name: str
) -> TypeName:
    new_fields = {
        field_name: evaluate_type_in_quantum_symbol(field_type, scope, param_name)
        for field_name, field_type in type_to_update.fields.items()
    }
    type_to_update.set_fields(new_fields)
    return type_to_update


def evaluate_types_in_quantum_symbols(
    symbols: list[QuantumSymbol], scope: Scope
) -> list[QuantumSymbol]:
    return [
        QuantumSymbol(
            handle=symbol.handle,
            quantum_type=evaluate_type_in_quantum_symbol(
                symbol.quantum_type, scope, str(symbol.handle)
            ),
        )
        for symbol in symbols
    ]


def evaluate_type_in_classical_symbol(
    type_to_update: ClassicalType, scope: Scope, param_name: str
) -> ClassicalType:
    updated_type: ClassicalType
    if isinstance(type_to_update, ClassicalArray):
        length = type_to_update.length
        if length is not None:
            length = _eval_expr(
                length, scope, int, Integer, "classical array", "length", param_name
            )
        updated_type = ClassicalArray(
            element_type=evaluate_type_in_classical_symbol(
                type_to_update.element_type, scope, param_name
            ),
            length=length,
        )
    elif isinstance(type_to_update, ClassicalTuple):
        updated_type = ClassicalTuple(
            element_types=[
                evaluate_type_in_classical_symbol(element_type, scope, param_name)
                for element_type in type_to_update.element_types
            ],
        )
    elif (
        isinstance(type_to_update, TypeName)
        and type_to_update.has_classical_struct_decl
    ):
        updated_type = TypeName(name=type_to_update.name)
        updated_type.set_classical_struct_decl(
            type_to_update.classical_struct_decl.model_copy(
                update=dict(
                    variables={
                        field_name: evaluate_type_in_classical_symbol(
                            field_type, scope, param_name
                        )
                        for field_name, field_type in type_to_update.classical_struct_decl.variables.items()
                    }
                )
            )
        )
    else:
        updated_type = type_to_update
    if type_to_update.is_generative:
        updated_type.set_generative()
    return updated_type
