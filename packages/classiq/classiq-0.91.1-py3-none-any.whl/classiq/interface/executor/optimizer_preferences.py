from classiq.interface.enum_utils import StrEnum


class CostType(StrEnum):
    MIN = "MIN"
    AVERAGE = "AVERAGE"
    CVAR = "CVAR"


class OptimizerType(StrEnum):
    COBYLA = "COBYLA"
    SPSA = "SPSA"
    L_BFGS_B = "L_BFGS_B"
    NELDER_MEAD = "NELDER_MEAD"
    ADAM = "ADAM"
    SLSQP = "SLSQP"
