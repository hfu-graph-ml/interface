from typing import List, TypedDict


class Node(TypedDict):
    name: str
    id: int


class Edge(TypedDict):
    connects: List[int]
    score: float


class Graph(TypedDict):
    nodes: List[Node]
    edges: List[Edge]
