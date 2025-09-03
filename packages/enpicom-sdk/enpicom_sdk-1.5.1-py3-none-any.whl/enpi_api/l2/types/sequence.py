from enum import Enum
from typing import NewType

SequenceId = NewType("SequenceId", int)
"""The unique identifier of a sequence."""


class Chain(str, Enum):
    """Chain of a sequence."""

    ALPHA = "alpha"
    BETA = "beta"
    DELTA = "delta"
    GAMMA = "gamma"
    HEAVY = "heavy"
    IOTA = "iota"
    KAPPA = "kappa"
    LAMBDA = "lambda"
