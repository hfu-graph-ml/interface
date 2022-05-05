from typing import Callable, List, Tuple, TypeAlias

# ArUco marker related types
Corners: TypeAlias = List[List[List[int]]]
CornerList: TypeAlias = Tuple[Corners, ...]
IDList: TypeAlias = List[List[int]]

# Queue related types
Subscription: TypeAlias = Tuple[int, Callable[[bool, float | None], any]]


class TrackerError:
    def __init__(self, message: str) -> None:
        self.message = message
