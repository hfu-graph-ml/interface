from typing import Dict, List
import numpy as np
import cv2 as cv

from utils.colors import COLOR_GREEN, COLOR_RED
from capture.tracker import Tracker
from config.config import Config
from utils.fmt import fps_to_ms

from typings.capture.aruco import RawRetrieveFunc, RetrieveFunc
from typings.renderer import RenderLayer, RenderObject
from typings.error import Error, Ok, Result


class Shared:
    def __init__(self, cfg: Config, tracker: Tracker, window_name: str = 'rendering') -> None:
        self.wait_delay = fps_to_ms(cfg['capture']['fps'])
        self.window_name = window_name
        self.raw_subscription_id = -1
        self.subscription_id = -1
        self.fullscreen = False
        self.tracker = tracker
        self.running = False
        self.cfg = cfg

        # Camera dimensions
        self.camera_frame_height = 0
        self.camera_frame_width = 0

        # Render layers
        self.render_layers: Dict[int, RenderLayer] = {}

    def is_running(self) -> bool:
        '''
        Returns if the renderer is already running.

        Returns:
            If renderer is running.
        '''
        if self.running:
            return True

        self.running = True
        return False

    def subscribe(self, size: int = -1) -> RetrieveFunc:
        '''
        Subscribe to the tracker.

        Args:
            size: Size of the queue (Default: -1 => Unlimited).

        Returns:
            A function to retrieve new marker positions.
        '''
        id, params, retrieve = self.tracker.subscribe(size)
        self.camera_frame_height = params[1]
        self.camera_frame_width = params[0]
        self.subscription_id = id

        return retrieve

    def subscribe_raw(self, size: int = -1) -> RawRetrieveFunc:
        '''
        Subscribe to the tracker in raw mode.

        Args:
            size: Size of the queue (Default: -1 => Unlimited).

        Returns:
            A function to retrieve new marker positions.
        '''
        id, params, retrieve = self.tracker.subscribe_raw(size)
        self.camera_frame_height = params[1]
        self.camera_frame_width = params[0]
        self.raw_subscription_id = id

        return retrieve

    def draw_borders(self, corners: tuple, frame: cv.Mat):
        '''
        Draw the border around a marker.

        Args:
            corners: List of corner positions.
            frame: Frame to render in.
        '''
        cv.line(frame, corners[0], corners[1], COLOR_GREEN, 2)  # Top left to top right
        cv.line(frame, corners[1], corners[2], COLOR_GREEN, 2)  # Top right to bottom right
        cv.line(frame, corners[2], corners[3], COLOR_GREEN, 2)  # Bottom right to bottom left
        cv.line(frame, corners[3], corners[0], COLOR_GREEN, 2)  # Bottom left to top left

    def draw_angle(self, corners: tuple, angle: float, frame: cv.Mat, with_text: bool = True):
        '''
        Draw a circle in the top-left corner and attach the angle as text to it.

        Args:
            corners: List of corner positions.
            angle: The angle in degrees.
            frame: Frame to render in.
            with_text: If the angle should be displayed as text.
        '''
        cv.circle(frame, corners[0], 4, COLOR_RED, -1)  # Top left corner
        if with_text:
            cv.putText(frame, '{:.2f}'.format(angle),  corners[0], cv.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_RED, 2)

    def draw_center_point(self, pos: tuple, id: int, frame: cv.Mat, with_text: bool = True):
        '''
        Draw a center point with the ID as text attached to it.

        Args:
            pos: Marker center position.
            id: Marker ID.
            frame: Frame to render in.
            with_text: If the marker ID should be displayed as text.
        '''
        cv.circle(frame, pos, 4, COLOR_RED, -1)
        if with_text:
            cv.putText(frame, str(id), (pos[0] - 10, pos[1] - 45), cv.FONT_HERSHEY_SIMPLEX, 0.8, COLOR_RED, 2)

    def toggle_fullscreen(self):
        '''
        Toggle fullscreen of the rendering window.
        '''
        if self.fullscreen:
            self.fullscreen = False
            cv.setWindowProperty(self.window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
        else:
            self.fullscreen = True
            cv.setWindowProperty(self.window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    def add_render_layer(self, index: int, name: str, should_warp: bool = True) -> Error:
        '''
        Add a render layer.

        Args:
            index: Layer index. Higher indices render later.
            name: Name of the render layer.
            should_warp: If this layer should be warped by the projection transformation (Broken).

        Returns:
            An Error if an error was encountered, None if otherwise.
        '''
        if index in self.render_layers.keys():
            return Error(f'A render layer with index {index} ({self.render_layers[index]._name}) already exists')

        self.render_layers[index] = RenderLayer(index, name, should_warp)
        return None

    def add_object_to_layer(self, index: int, obj: RenderObject) -> Error:
        '''
        Add a render object to a render layer.

        Args:
            index: Index of the render layer to add to.
            obj: Render object to add.

        Returns:
            An Error if an error was encountered, None if otherwise.
        '''
        if not index in self.render_layers.keys():
            return Error('A layer at index {index} does not exist')

        self.render_layers[index].add_object(obj)
        return None

    def add_object_to_layer_at_index(self, layer_index: int, obj_index: int, obj: RenderObject) -> Error:
        '''
        Add a render object to a render layer at a specific index.

        Args:
            layer_index: The layer index to add to.
            obj_index: Object index to add object at.
            obj: Object to add.

        Returns:
            An Error if an error was encountered, None if otherwise.
        '''
        if not layer_index in self.render_layers.keys():
            return Error(f'A layer at index {layer_index} does not exist')
        return self.render_layers[layer_index].add_object_by_index(obj_index, obj)

    def get_object_on_layer_by_index(self, layer_index: int, obj_index: int) -> Result[RenderObject, Error]:
        '''
        Get a render object on a layer by index.

        Args:
            layer_index: The layer index.
            obj_index: The object index.

        Returns:
            A result consisting of a RenderObject or an Error.
        '''
        if not layer_index in self.render_layers.keys():
            return Error(f'A layer at index {layer_index} does not exist')

        return self.render_layers[layer_index].get_object(obj_index)

    def render(self, frame: cv.Mat, matrix: np.ndarray, width: int, height: int):
        '''
        Render the render layers one after each other.

        Args:
            frame: The frame to render in.
            matrix: Projection transformation matrix (Broken).
            width: Frame width.
            height: Frame height.
        '''
        # First we render all layers which should be warped
        remanining: List[RenderLayer] = []
        for layer in self.render_layers.values():
            if not layer._should_warp:
                remanining.append(layer)
                continue
            # print(f'Render {len(layer._objects)} objects on layer {layer._name}')
            layer.render(frame)

        # Warp
        if matrix.any():
            # frame = cv.warpPerspective(frame, matrix, (width, height))
            pass

        for layer in remanining:
            layer.render(frame)

    def stop(self):
        '''
        Stop the render loop.
        '''
        self.running = False
        cv.destroyAllWindows()

        self.tracker.unsubscribe(self.subscription_id)
        self.tracker.stop()
