import warnings

from classiq.interface.exceptions import ClassiqDeprecationWarning

from classiq.qmod.builtins.structs import (
    FockHamiltonianProblem,
    MoleculeProblem,
)
from classiq.qmod.qfunc import qfunc
from classiq.qmod.qmod_parameter import CArray, CInt
from classiq.qmod.qmod_variable import QArray, QBit


@qfunc(external=True)
def molecule_ucc(
    molecule_problem: MoleculeProblem,
    excitations: CArray[CInt],
    qbv: QArray[QBit],
) -> None:
    warnings.warn(
        (
            "The function `molecule_ucc` is deprecated and will no "
            "longer be supported starting on 2025-09-18 at the earliest. "
            "For more information on Classiq's chemistry application, see "
            "https://docs.classiq.io/latest/explore/applications/chemistry/classiq_chemistry_application/classiq_chemistry_application/."
        ),
        category=ClassiqDeprecationWarning,
        stacklevel=2,
    )
    pass


@qfunc(external=True)
def molecule_hva(
    molecule_problem: MoleculeProblem,
    reps: CInt,
    qbv: QArray[QBit],
) -> None:
    warnings.warn(
        (
            "The function `molecule_hva` is deprecated and will no "
            "longer be supported starting on 2025-09-18 at the earliest. "
            "For more information on Classiq's chemistry application, see "
            "https://docs.classiq.io/latest/explore/applications/chemistry/classiq_chemistry_application/classiq_chemistry_application/."
        ),
        category=ClassiqDeprecationWarning,
        stacklevel=2,
    )
    pass


@qfunc(external=True)
def molecule_hartree_fock(
    molecule_problem: MoleculeProblem,
    qbv: QArray[QBit],
) -> None:
    warnings.warn(
        (
            "The function `molecule_hartree_fock` is deprecated and will no "
            "longer be supported starting on 2025-09-18 at the earliest. "
            "For more information on Classiq's chemistry application, see "
            "https://docs.classiq.io/latest/explore/applications/chemistry/classiq_chemistry_application/classiq_chemistry_application/."
        ),
        category=ClassiqDeprecationWarning,
        stacklevel=2,
    )
    pass


@qfunc(external=True)
def fock_hamiltonian_ucc(
    fock_hamiltonian_problem: FockHamiltonianProblem,
    excitations: CArray[CInt],
    qbv: QArray[QBit],
) -> None:
    warnings.warn(
        (
            "The function `fock_hamiltonian_ucc` is deprecated and will no "
            "longer be supported starting on 2025-09-18 at the earliest. "
            "For more information on Classiq's chemistry application, see "
            "https://docs.classiq.io/latest/explore/applications/chemistry/classiq_chemistry_application/classiq_chemistry_application/."
        ),
        category=ClassiqDeprecationWarning,
        stacklevel=2,
    )
    pass


@qfunc(external=True)
def fock_hamiltonian_hva(
    fock_hamiltonian_problem: FockHamiltonianProblem,
    reps: CInt,
    qbv: QArray[QBit],
) -> None:
    warnings.warn(
        (
            "The function `fock_hamiltonian_hva` is deprecated and will no "
            "longer be supported starting on 2025-09-18 at the earliest. "
            "For more information on Classiq's chemistry application, see "
            "https://docs.classiq.io/latest/explore/applications/chemistry/classiq_chemistry_application/classiq_chemistry_application/."
        ),
        category=ClassiqDeprecationWarning,
        stacklevel=2,
    )
    pass


@qfunc(external=True)
def fock_hamiltonian_hartree_fock(
    fock_hamiltonian_problem: FockHamiltonianProblem,
    qbv: QArray[QBit],
) -> None:
    warnings.warn(
        (
            "The function `fock_hamiltonian_hartree_fock` is deprecated and will no "
            "longer be supported starting on 2025-09-18 at the earliest. "
            "For more information on Classiq's chemistry application, see "
            "https://docs.classiq.io/latest/explore/applications/chemistry/classiq_chemistry_application/classiq_chemistry_application/."
        ),
        category=ClassiqDeprecationWarning,
        stacklevel=2,
    )
    pass
