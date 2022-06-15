from typing import List, Tuple
import numpy as np
import cv2 as cv
import os

from capture.tracker import Tracker
from renderer.shared import Shared

import config.config as config
import utils.wait as wait
import utils.fmt as fmt

from typings.renderer import ArUcoMarker, RenderObject, Corner
from typings.error import Error, Err


class Renderer(Shared):
    '''
    This class describes the renderer which renders the user interface.
    '''

    def __init__(self, cfg: config.Config, t: Tracker) -> None:
        self._wait_delay = fmt.fps_to_ms(cfg['capture']['fps'])
        self._subscription_id = -1
        self._fullscreen = False
        self._running = False
        self._tracker = t
        self._cfg = cfg

        # Dimensions
        self._frame_height = cfg['renderer']['height']
        self._frame_width = cfg['renderer']['width']

        # Camera dimensions
        self._camera_frame_height = 0
        self._camera_frame_width = 0

        # Scaling
        self._scaling_factor = 1
        self._calib_markers = [0, 1, 2, 3]

        # Objects
        self._objects: List[RenderObject] = []

    def _corner_coords(self, corner: Corner, mat: cv.Mat, scale: float = 1.0) -> Tuple[int, int]:
        '''
        Calculate corner coordinates based on the size and scaling of the provided mat.

        Parameters
        ----------
        corner : Corner
            Which corner to calculate
        mat : cv.Mat
            The mat which should be placed. Used for size
        scale : float
            The scaling (default: 1.0, no scaling)

        Returns
        -------
        coords : Tuple[int, int]
            A tuple of x, y integer values
        '''
        match corner:
            case Corner.TOP_LEFT:
                return (0, 0)
            case Corner.TOP_RIGHT:
                return (0, int(self._frame_width - mat.shape[1] * scale))
            case Corner.BOTTOM_RIGHT:
                return (int(self._frame_height - mat.shape[0] * scale), int(self._frame_width - mat.shape[1] * scale))
            case Corner.BOTTOM_LEFT:
                return (int(self._frame_height - mat.shape[0] * scale), 0)

    def _prepare_corner_markers(self):
        '''
        Read ArUco markers from disk and add them to the render object list at the right positions (in all four
        corners).
        '''
        base_path = os.path.join(self._cfg['capture']['path'], 'markers')
        for i, id in enumerate(self._cfg['capture']['calibration']['corners']):
            path = os.path.join(base_path, 'marker-{:02d}.png'.format(id))
            marker = cv.imread(path)
            # NOTE (Techassi): Don't hardcode the scaling. Add this to the config
            match i:
                case 0:
                    self._objects.append(ArUcoMarker(0, 0, marker, 0.5))
                case 1:
                    x, y = self._corner_coords(Corner.TOP_RIGHT, marker, 0.5)
                    print(y)
                    self._objects.append(ArUcoMarker(y, x, marker, 0.5))
                case 2:
                    x, y = self._corner_coords(Corner.BOTTOM_RIGHT, marker, 0.5)
                    self._objects.append(ArUcoMarker(y, x, marker, 0.5))
                case 3:
                    x, y = self._corner_coords(Corner.BOTTOM_LEFT, marker, 0.5)
                    self._objects.append(ArUcoMarker(y, x, marker, 0.5))
                case _:
                    continue  # This should never happen, and if it does: huh?

    def _prepare(self):
        '''
        Prepare multiple things before starting the renderer.
        '''
        self._prepare_corner_markers()

    def _render(self, frame: cv.Mat):
        '''
        This iterates over all registered render objects and renders them in 'frame' by calling their render method.
        '''
        for obj in self._objects:
            obj.render(frame)

    def start(self) -> Error:
        '''
        Start the render loop.
        '''
        if self._running:
            return Err('Already running')
        self._running = True

        # Prepare renderer
        self._prepare()

        window_name = 'rendering'
        cv.namedWindow(window_name, cv.WINDOW_NORMAL)

        # Subscribe to the tracker
        id, params, retrieve = self._tracker.subscribe()
        self._camera_frame_height = params[1]
        self._camera_frame_width = params[0]
        self._subscription_id = id

        # White frame sized width x height
        initial_frame = 255 * np.ones((self._frame_height, self._frame_width, 3), dtype=np.uint8)
        frame = np.copy(initial_frame)

        while self._running:
            # try:
            #     corners, ids = retrieve(False)

            #     # Copy the frame here. This reduces flickering
            #     frame = np.copy(initial_frame)

            #     for i, corners_per_marker in enumerate(corners):
            #         self._draw_center_point(corners_per_marker[0], ids[i], frame)
            # except:
            #     pass

            frame = np.copy(initial_frame)
            self._render(frame)

            cv.imshow(window_name, frame)

            idx = wait.multi_wait_or(self._wait_delay, 'q', 'f')
            if idx == -1:
                continue
            elif idx == 0:
                break
            else:
                if self._fullscreen:
                    self._fullscreen = False
                    cv.setWindowProperty(window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
                else:
                    self._fullscreen = True
                    cv.setWindowProperty(window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

        # Cleanup
        self.stop()
        return None

    def stop(self):
        '''
        Stop the render loop.
        '''
        cv.destroyAllWindows()

        self._tracker.unsubscribe(self._subscription_id)
        self._tracker.stop()
