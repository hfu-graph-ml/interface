from enum import Enum, auto, unique
from typing import Dict, Tuple
import cv2 as cv

from typings.error import Err, Error, Ok, Result


@unique
class Corner(Enum):
    TOP_LEFT = auto()
    TOP_RIGHT = auto()
    BOTTOM_RIGHT = auto()
    BOTTOM_LEFT = auto()


class RenderObject:
    '''
    This is the base class of each RenderObject. It provides some shared attributes and methods.
    '''

    def __init__(self, x: int, y: int, name: str, scale: float) -> None:
        self._prev_scale = -1
        self._scale = scale
        self._name = name
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
    '''
    This renders a node around a tracked (and detected) marker.
    '''

    def __init__(self, x: int, y: int, radius: int, name: str, color: Tuple[int, int, int]) -> None:
        super().__init__(x, y, name, 1.0)
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
    '''
    This renders an ArUco marker at the specified loaction and scale.
    '''

    def __init__(self, x: int, y: int, marker: cv.Mat, name: str, scale: float = 1.0) -> None:
        super().__init__(x, y, name, scale)
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


class ArUcoMarkerTracking(RenderObject):
    '''
    This renders ArUco marker tracking debug information. This outlines the marker, draws a center dot and prints
    out the angle of the marker.
    '''

    def __init__(self, x: int, y: int, name: str, scale: float) -> None:
        super().__init__(x, y, name, scale)


class ConfettiParticle(RenderObject):
    '''
    This renders a confetti particle.
    '''

    def __init__(self, x: int, y: int, name: str, scale: float) -> None:
        super().__init__(x, y, name, scale)


class RenderLayer:
    def __init__(self, index: int, name: str, should_warp: bool) -> None:
        self._objects: Dict[int, RenderObject] = {}
        self._should_warp = should_warp
        self._index = index
        self._name = name

    def add_object(self, obj: RenderObject):
        self._objects[len(self._objects)] = obj

    def add_object_by_index(self, index: int, obj: RenderObject) -> Error:
        if index in self._objects.keys():
            return Error(f'Object with index {index} already exists on layer {self._name}')

        self._objects[index] = obj

    def get_object(self, index: int) -> Result[RenderObject, Error]:
        if not index in self._objects.keys():
            return Err(Error(f'No object at index {index}'))

        return Ok(self._objects[index])

    def render(self, frame: cv.Mat):
        for obj in self._objects.values():
            obj.render(frame)
