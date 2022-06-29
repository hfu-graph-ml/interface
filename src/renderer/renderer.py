from typing import Dict, List, Tuple
import numpy as np
import cv2 as cv
import time
import glob
import os

from renderer.transformer import Transformer
from capture.tracker import Tracker
from utils.colors import COLOR_RED
from config.config import Config

import utils.wait as wait

from typings.renderer import ArUcoMarker, Node, RenderObject, Corner
from typings.capture.calibration import CharucoCalibrationData
from typings.capture.aruco import MarkerCenterList
from typings.error import Error


class Renderer(Transformer):
    '''
    This class describes the renderer which renders the user interface.
    '''

    def __init__(self, cfg: Config, calib_data: CharucoCalibrationData, tracker: Tracker) -> None:
        super().__init__(cfg, calib_data, tracker)

        # Dimensions
        self._frame_height = cfg['renderer']['height']
        self._frame_width = cfg['renderer']['width']

        # Objects
        self._objects: Dict[int, RenderObject] = {}
        self._marker_images: List[cv.Mat] = []

    def _load_aruco_marker_images(self):
        '''
        Load all ArUco marker images and save them in a list for future uses.
        '''
        base_path = os.path.join(self.cfg['capture']['path'], 'markers', '*.png')
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
                return (10, 10)
            case Corner.TOP_RIGHT:
                return (10, int(self._frame_width - mat.shape[1] * scale) - 10)
            case Corner.BOTTOM_RIGHT:
                return (
                    int(self._frame_height - mat.shape[0] * scale) - 10,
                    int(self._frame_width - mat.shape[1] * scale) - 10
                )
            case Corner.BOTTOM_LEFT:
                return (int(self._frame_height - mat.shape[0] * scale) - 10, 10)

    def _prepare_corner_markers(self):
        '''
        Read ArUco markers from disk and add them to the render object list at the right positions (in all four
        corners).
        '''
        # We expect the user to provide the IDs of the corners in the following order: top-left, top-right, bottom-right
        # and bottom-left

        # NOTE (Techassi): Don't hardcode the scaling. Add this to the config

        # Top-left
        self.add_object_to_layer(10, ArUcoMarker(10, 10, self._marker_images[0], '', 0.5))

        # Top-right
        x, y = self._corner_coords(Corner.TOP_RIGHT, self._marker_images[1], 0.5)
        self.add_object_to_layer(10, ArUcoMarker(y, x, self._marker_images[1], '', 0.5))

        # Bottom-right
        x, y = self._corner_coords(Corner.BOTTOM_RIGHT, self._marker_images[2], 0.5)
        self.add_object_to_layer(10, ArUcoMarker(y, x, self._marker_images[2], '', 0.5))

        # Bottom-left
        x, y = self._corner_coords(Corner.BOTTOM_LEFT, self._marker_images[3], 0.5)
        self.add_object_to_layer(10, ArUcoMarker(y, x, self._marker_images[3], '', 0.5))

    def _update_markers(self, markers: MarkerCenterList):
        ''''''
        for marker in markers:
            if marker[3] in [0, 1, 2, 3]:
                continue

            result = self.get_object_on_layer_by_index(0, marker[3])
            if result.is_err():
                self.add_object_to_layer_at_index(0, marker[3], Node(marker[1][0], marker[1][1], 20, 'test', COLOR_RED))
            else:
                result.unwrap().update(marker[1][0], marker[1][1])

    def _prepare(self):
        '''
        Prepare multiple things before starting the renderer.
        '''
        self.add_render_layer(10, 'corner-markers', False)
        self.add_render_layer(0, 'default')

        self._load_aruco_marker_images()
        self._prepare_corner_markers()

        cv.namedWindow(self.window_name, cv.WINDOW_NORMAL)

    def start(self) -> Error:
        '''
        Start the render loop.
        '''
        if self.is_running():
            return Error('Already running')

        self._prepare()
        self.transform_in_intervals()

        retrieve = self.subscribe()

        # White frame sized width x height
        initial_frame = 255 * np.ones((self._frame_height, self._frame_width, 3), dtype=np.uint8)

        while self.running:
            frame = np.copy(initial_frame)

            # First try to retrieve the list of tuples consisting of marker coordinates (position and angle) and IDs.
            # This can faile, because the retrieval of items from the queue can raise the Empty exception when there
            # currently is no item in the queue
            try:
                markers = retrieve(False)
                print(len(markers))
                self._update_markers(markers)
            except:
                pass

            super().render(frame, self.transform_matrix, self.transform_width, self.transform_height)

            cv.imshow(self.window_name, frame)

            idx = wait.multi_wait_or(self.wait_delay, 'q', 'f')
            if idx == -1:
                continue
            elif idx == 0:
                break
            else:
                self.toggle_fullscreen()

        # Cleanup
        self.stop()
        self.transform_thread.join()
        return None
