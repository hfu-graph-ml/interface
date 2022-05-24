from typing import Tuple

import cv2 as cv


class RendererError:
    def __init__(self, message: str) -> None:
        self.message = message


class RenderObject:
    def __init__(self, x: int, y: int) -> None:
        self._x: int = x
        self._y: int = y

    def update(self, new_x: int, new_y: int):
        self._x = new_x
        self._y = new_y

    def render(self, _: cv.Mat):
        # The default render method renders nothing
        pass


class Node(RenderObject):
    def __init__(self, x: int, y: int, radius: int, color: Tuple[int, int, int]) -> None:
        super().__init__()
        self._color: Tuple[int, int, int] = color
        self._radius = radius

    def update(self, new_x: int, new_y: int):
        super().update(new_x, new_y)

    def render(self, frame: cv.Mat):
        # Render a circle around the tracked marker
        cv.circle(frame, (self._x, self._y), self._radius, self._color, 2)
