import time
from typing import Dict, List, Tuple
import numpy as np
import cv2 as cv
import threading
import glob
import os

from capture.tracker import Tracker
from renderer.shared import Shared

import config.config as config
import utils.colors as colors
import utils.wait as wait
import utils.fmt as fmt

from typings.renderer import ArUcoMarker, Node, RenderObject, Corner
from typings.capture.aruco import MarkerCenterList, RetrieveFunc
from typings.error import Error, Err


class Renderer(Shared):
    '''
    This class describes the renderer which renders the user interface.
    '''

    def __init__(self, cfg: config.Config, t: Tracker) -> None:
        self._wait_delay = fmt.fps_to_ms(cfg['capture']['fps'])
        self._window_name = 'rendering'
        self._subscription_id = -1
        self._fullscreen = False
        self._running = False
        self._tracker = t
        self._cfg = cfg

        # Dimensions
        self._frame_height = cfg['renderer']['height']
        self._frame_width = cfg['renderer']['width']

        self._adjusted = False

        # Camera dimensions
        self._camera_frame_height = 0
        self._camera_frame_width = 0

        # Objects
        self._objects: Dict[int, RenderObject] = {}
        self._marker_images: List[cv.Mat] = []

    def _toggle_fullscreen(self):
        '''
        Toggle fullscreen of the rendering window.
        '''
        if self._fullscreen:
            self._fullscreen = False
            cv.setWindowProperty(self._window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
        else:
            self._fullscreen = True
            cv.setWindowProperty(self._window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    def _load_aruco_marker_images(self):
        '''
        Load all ArUco marker images and save them in a list for future uses.
        '''
        base_path = os.path.join(self._cfg['capture']['path'], 'markers', '*.png')
        img_paths = sorted(glob.glob(base_path))
        for img_path in img_paths:
            mat = cv.imread(img_path)
            self._marker_images.append(mat)

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
        # We expect the user to provide the IDs of the corners in the following order: top-left, top-right, bottom-right
        # and bottom-left

        # NOTE (Techassi): Don't hardcode the scaling. Add this to the config

        # Top-left
        self._objects[0] = ArUcoMarker(0, 0, self._marker_images[0], 0.5)

        # Top-right
        x, y = self._corner_coords(Corner.TOP_RIGHT, self._marker_images[1], 0.5)
        self._objects[1] = ArUcoMarker(y, x, self._marker_images[1], 0.5)

        # Bottom-right
        x, y = self._corner_coords(Corner.BOTTOM_RIGHT, self._marker_images[2], 0.5)
        self._objects[2] = ArUcoMarker(y, x, self._marker_images[2], 0.5)

        # Bottom-left
        x, y = self._corner_coords(Corner.BOTTOM_LEFT, self._marker_images[3], 0.5)
        self._objects[3] = ArUcoMarker(y, x, self._marker_images[3], 0.5)

    def _transform_projection_in_intervals(self):
        ''''''
        t = threading.Thread(None, self._transform_projection, 'transform-projection')
        self._transform_thread = t
        t.start()

    def _transform_projection(self):
        ''''''
        _, _, retrieve = self._tracker.subscribe()
        while True:
            try:
                markers = retrieve(False)
            except:
                continue

            time.sleep()

    def _update_markers(self, markers: MarkerCenterList):
        ''''''
        for marker in markers:
            if marker[2] in [0, 1, 2, 3]:
                continue

            if marker[2] not in self._objects:
                self._objects[marker[2]] = Node(marker[0][0], marker[0][1], 20, colors.RED)
            else:
                self._objects[marker[2]].update(marker[0][0], marker[0][1])

    def _subscribe(self) -> RetrieveFunc:
        '''
        Subscribe to the tracker.
        '''
        id, params, retrieve = self._tracker.subscribe()
        self._camera_frame_height = params[1]
        self._camera_frame_width = params[0]
        self._subscription_id = id

        return retrieve

    def _prepare(self):
        '''
        Prepare multiple things before starting the renderer.
        '''
        self._load_aruco_marker_images()
        self._prepare_corner_markers()

        cv.namedWindow(self._window_name, cv.WINDOW_NORMAL)

    def _render(self, frame: cv.Mat):
        '''
        This iterates over all registered render objects and renders them in 'frame' by calling their render method.
        '''
        for obj in self._objects.values():
            obj.render(frame)

    def start(self) -> Error:
        '''
        Start the render loop.
        '''
        if self._running:
            return Err('Already running')
        self._running = True

        self._prepare()
        retrieve = self._subscribe()

        # White frame sized width x height
        initial_frame = 255 * np.ones((self._frame_height, self._frame_width, 3), dtype=np.uint8)
        frame = np.copy(initial_frame)

        while self._running:
            # First try to retrieve the list of tuples consisting of marker coordinates (position and angle) and IDs.
            # This can faile, because the retrieval of items from the queue can raise the Empty exception when there
            # currently is no item in the queue
            try:
                markers = retrieve(False)
                self._update_markers(markers)
            except:
                pass

            frame = np.copy(initial_frame)
            self._render(frame)

            cv.imshow(self._window_name, frame)

            idx = wait.multi_wait_or(self._wait_delay, 'q', 'f')
            if idx == -1:
                continue
            elif idx == 0:
                break
            else:
                self._toggle_fullscreen()

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
