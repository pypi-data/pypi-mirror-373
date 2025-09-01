from pydantic import BaseModel

from classiq.interface.analyzer.result import QasmCode
from classiq.interface.enum_utils import StrEnum


class QmodFormat(StrEnum):
    NATIVE = "native"
    PYTHON = "python"


class QasmToQmodParams(BaseModel):
    qasm: QasmCode
    qmod_format: QmodFormat
