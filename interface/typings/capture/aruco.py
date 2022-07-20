from typing import Callable, List, Tuple, TypeAlias
from queue import Queue

Corners: TypeAlias = List[List[List[int]]]
CornerList: TypeAlias = Tuple[Corners, ...]
IDList: TypeAlias = List[List[int]]

SubscriptionParams: TypeAlias = Tuple[int, int]
RawRetrieveFunc: TypeAlias = Callable[[bool, float | None], Tuple[CornerList, IDList]]
RetrieveFunc: TypeAlias = Callable[[bool, float | None], Tuple[CornerList, IDList]]
RawSubscription: TypeAlias = Tuple[int, SubscriptionParams, RawRetrieveFunc]
Subscription: TypeAlias = Tuple[int, SubscriptionParams, RetrieveFunc]
Subscriber: TypeAlias = Tuple[bool, Queue]

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
