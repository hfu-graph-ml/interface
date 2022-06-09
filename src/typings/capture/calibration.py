from enum import Enum, unique, auto
from typing import Tuple, TypeAlias
import numpy as np

CharucoCalibrationResult: TypeAlias = Tuple[
    np.ndarray,
    np.ndarray,
    Tuple,
    Tuple
]


@unique
class CalibrationMode(Enum):
    AUTO = auto()
    SEMI_AUTO = auto()
    MANUAL = auto()
