from enum import Enum, auto, unique
from typing import Tuple

import cv2 as cv


@unique
class Corner(Enum):
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_RIGHT = auto()
    BOTTOM_LEFT = auto()


class RenderObject:
    def __init__(self, x: int, y: int, scale: float) -> None:
        self._prev_scale = -1
        self._scale = scale
        self._x: int = x
        self._y: int = y

    def update(self, new_x: int, new_y: int):
        '''
        Update the position of the render object.
        '''
        self._x = new_x
        self._y = new_y

    def render(self, _: cv.Mat):
        '''
        The default render method renders nothing.
        '''
        pass

    def scale(self, current_mat: cv.Mat, src_mat: cv.Mat) -> cv.Mat:
        '''
        Scale 'mat' by factor.
        '''
        if self._scale == 1.0 or self._scale < 0:
            return current_mat

        if self._prev_scale == self._scale:
            return current_mat

        self._prev_scale = self._scale
        return cv.resize(src_mat, (0, 0), fx=self._scale, fy=self._scale)

    def set_scale(self, scale: float):
        '''
        Set the scaling factor.
        '''
        self._scale = scale


class Node(RenderObject):
    def __init__(self, x: int, y: int, radius: int, color: Tuple[int, int, int]) -> None:
        super().__init__(x, y, 1.0)
        self._color: Tuple[int, int, int] = color
        self._radius = radius

    def update(self, new_x: int, new_y: int):
        super().update(new_x, new_y)

    def render(self, frame: cv.Mat):
        '''
        Render a circle around the tracked marker.
        '''
        cv.circle(frame, (self._x, self._y), self._radius, self._color, 5)


class ArUcoMarker(RenderObject):
    def __init__(self, x: int, y: int, marker: cv.Mat, scale: float = 1.0) -> None:
        super().__init__(x, y, scale)
        self._src_marker = marker  # This is the original marker
        self._marker = marker  # This is the current marker being used for rendering

    def update(self, new_x: int, new_y: int):
        '''
        The marker position cannot be updated.
        '''
        pass

    def render(self, frame: cv.Mat):
        '''
        Render first scales the marker (if needed) and then inserts the pixels into the frame mat.
        '''
        self.scale()
        frame[
            self._y:self._y + self._marker.shape[0],
            self._x:self._x + self._marker.shape[1]
        ] = self._marker

    def scale(self):
        '''
        Scale the marker by calling super's scale method with the current and original marker mat.
        '''
        self._marker = super().scale(self._marker, self._src_marker)
