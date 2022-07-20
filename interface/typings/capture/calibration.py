from enum import Enum, unique, auto
from typing import Tuple, TypeAlias
from typing_extensions import Self
import numpy as np

from typings.error import Err, Error, Ok, Result

CharucoCalibrationData: TypeAlias = Tuple[
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

    @staticmethod
    def from_str(mode: str) -> Result[Self, Error]:
        '''
        Returns the enum from the provided string or returns an error if no corresponding enum exists.
        '''
        match mode.lower():
            case 'auto':
                return Ok(CalibrationMode.AUTO)
            case 'semi':
                return Ok(CalibrationMode.SEMI_AUTO)
            case 'manual':
                return Ok(CalibrationMode.MANUAL)
            case _:
                return Err(Error('Invalid mode'))
