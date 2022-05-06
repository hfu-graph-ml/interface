from typing import Callable, List, Tuple, TypeAlias

# ArUco marker related types
Corners: TypeAlias = List[List[List[int]]]
CornerList: TypeAlias = Tuple[Corners, ...]
IDList: TypeAlias = List[List[int]]

# Queue related types
SubscriptionParams: TypeAlias = Tuple[int, int]
Subscription: TypeAlias = Tuple[int, SubscriptionParams, Callable[[bool, float | None], Tuple[CornerList, IDList]]]


class TrackerError:
    def __init__(self, message: str) -> None:
        self.message = message
