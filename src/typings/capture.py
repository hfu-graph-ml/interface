from typing import Callable, List, Tuple, TypeAlias
import numpy as np

# ArUco marker related types
Corners: TypeAlias = List[List[List[int]]]
CornerList: TypeAlias = Tuple[Corners, ...]
IDList: TypeAlias = List[List[int]]

# List of tuples of markers which consist of a Tuple for the <x, y> center position, the angle as a float value between
# 0 and 360 degrees and and integer ID.
MarkerCenterList: TypeAlias = List[
    Tuple[
        Tuple[int, int],
        float,
        int
    ]
]

MarkerBordersList: TypeAlias = List[
    Tuple[
        Tuple[
            Tuple[int, int],
            Tuple[int, int],
            Tuple[int, int],
            Tuple[int, int],
        ],
        Tuple[int, int],
        float,
        int
    ]
]

CharucoCalibrationResult: TypeAlias = Tuple[
    np.ndarray,
    np.ndarray,
    Tuple,
    Tuple
]

# Queue related types
SubscriptionParams: TypeAlias = Tuple[int, int]
Subscription: TypeAlias = Tuple[int, SubscriptionParams, Callable[[bool, float | None], Tuple[CornerList, IDList]]]


class TrackerError:
    def __init__(self, message: str) -> None:
        self.message = message


class GeneratorError:
    def __init__(self, message: str) -> None:
        self.message = message


class CalibrationError:
    def __init__(self, message: str) -> None:
        self.message = message
