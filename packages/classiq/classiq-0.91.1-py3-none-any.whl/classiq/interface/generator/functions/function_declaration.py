import abc
from collections.abc import Sequence

from classiq.interface.model.classical_parameter_declaration import (
    AnonClassicalParameterDeclaration,
)
from classiq.interface.model.parameter import Parameter


class FunctionDeclaration(Parameter, abc.ABC):
    """
    Facilitates the creation of a common function interface object.
    """

    @property
    @abc.abstractmethod
    def param_decls(self) -> Sequence["AnonClassicalParameterDeclaration"]:
        pass


FunctionDeclaration.model_rebuild()
