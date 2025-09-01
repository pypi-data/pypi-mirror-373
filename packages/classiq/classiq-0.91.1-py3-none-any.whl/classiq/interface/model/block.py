from typing import TYPE_CHECKING, Literal, Optional

import pydantic

from classiq.interface.model.quantum_statement import QuantumOperation

if TYPE_CHECKING:
    from classiq.interface.model.statement_block import StatementBlock


class Block(QuantumOperation):
    kind: Literal["Block"]

    statements: "StatementBlock"

    label: Optional[str] = pydantic.Field(default=None)
