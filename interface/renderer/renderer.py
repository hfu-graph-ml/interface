from typing import Dict, List, Tuple
from queue import Empty
import numpy as np
import cv2 as cv
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

        Args:
            corner: Which corner to calculate.
            mat: The mat which should be placed. Used for size.
            scale: The scaling (default: 1.0, no scaling).

        Returns:
            A tuple of x, y integer values.
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
        '''
        Update the amrker objects in the render tree.

        Args:
            markers: List of markers.
        '''
        for marker in markers:
            if marker[2] in [0, 1, 2, 3]:
                continue

            result = self.get_object_on_layer_by_index(0, marker[2])
            if result.is_err():
                self.add_object_to_layer_at_index(0, marker[2], Node(
                    int(marker[0][0] * self.scaling_x), int(marker[0][1] * self.scaling_y), 20, 'test', COLOR_RED))
            else:
                result.unwrap().update(int(marker[0][0] * self.scaling_x), int(marker[0][1] * self.scaling_y))

    def _initialize(self):
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

        self._initialize()

        retrieve = self.subscribe_raw()

        # White frame sized width x height
        initial_frame = 255 * np.ones((self._frame_height, self._frame_width, 3), dtype=np.uint8)
        ref_frame = np.copy(initial_frame)
        super().render(ref_frame, self.transform_matrix, self.transform_width, self.transform_height)
        params = cv.aruco.DetectorParameters_create()

        markerCorners, markerIds, _ = cv.aruco.detectMarkers(
            ref_frame,
            self.dict,
            parameters=params
        )
        if len(markerCorners) == 4:
            ret, charucoCorners, charucoIds = cv.aruco.interpolateCornersCharuco(
                markerCorners,
                markerIds,
                ref_frame,
                self.board
            )
            print(charucoCorners.shape)

        cv.namedWindow('reference', cv.WINDOW_NORMAL)
        cv.setWindowProperty('reference', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

        while self.running:
            cv.imshow('reference', ref_frame)

            try:
                (corners, ids, rejected, recovered) = retrieve(False)
                scaling = self.get_reference_scaling_naive(corners, ids, self._frame_width, self._frame_height)
                if len(scaling) == 2:
                    self.scaling_x = scaling[0]
                    self.scaling_y = scaling[1]
                    cv.destroyWindow('reference')
                    break
            except Empty:
                pass
            except Exception as e:
                print(e)
                break

            idx = wait.multi_wait_or(self.wait_delay, 'q', 'f')
            if idx == -1:
                continue
            elif idx == 0:
                break
            else:
                self.toggle_fullscreen()

        while self.running:
            frame = np.copy(initial_frame)

            # First try to retrieve the list of tuples consisting of marker coordinates (position and angle) and IDs.
            # This can faile, because the retrieval of items from the queue can raise the Empty exception when there
            # currently is no item in the queue
            try:
                (corners, ids, _, _) = retrieve(False)
                markers = self.tracker._transform_markers_to_center(corners, ids)
                self._update_markers(markers)
            except Empty:
                pass
            except Exception as e:
                print(e)
                break

            super().render(frame, self.transform_matrix, self._frame_width, self._frame_width)
            # frame = cv.warpPerspective(frame, self.transform_matrix, (self._frame_width, self._frame_width))
            # print(frame.shape)

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
        return None
