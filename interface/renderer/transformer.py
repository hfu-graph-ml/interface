from typing import Tuple
import numpy as np
import cv2 as cv
import threading

from capture.aruco import board_from, dict_from, type_from
from capture.tracker import Tracker
from renderer.shared import Shared
from config.config import Config

from typings.capture.calibration import CharucoCalibrationData
from typings.capture.aruco import CornerList, IDList


class Transformer(Shared):
    def __init__(self, cfg: Config, calib_data: CharucoCalibrationData, tracker: Tracker) -> None:
        super().__init__(cfg, tracker)

        typ = type_from(
            cfg['capture']['aruco']['size'],
            cfg['capture']['aruco']['uniques']
        )
        t, ok = dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Tracker object')

        self.dict = cv.aruco.Dictionary_get(t)
        self.board = board_from(3, 3, self.dict, marker_length=0.09, marker_separation=0.01)

        self.corner_transform = np.zeros((4, 2), dtype="float32")
        self.transform_matrix = np.zeros([])
        self.calib_data = calib_data
        self.transform_height = 0
        self.transform_width = 0

        self.scaling_x = 1
        self.scaling_y = 1

        self.axis = np.float32([
            [-.5, -.5, 0],
            [-.5, .5, 0],
            [.5, .5, 0],
            [.5, -.5, 0],
            [-.5, -.5, 1],
            [-.5, .5, 1],
            [.5, .5, 1],
            [.5, -.5, 1]
        ])

    def get_reference_scaling_naive(self, corners: CornerList, ids: IDList, width: int, height: int) -> Tuple[float, float]:
        ''''''
        if len(corners) < 4:
            return ()

        pairs = []
        for c in zip(corners, ids):
            if c[1][0] in [0, 1, 2, 3]:
                pairs.append((c[0][0], c[1][0]))

        pairs = sorted(pairs, key=lambda x: x[1])

        # Calc width scaling
        top_width = pairs[1][0][0][0] - pairs[0][0][0][0]
        bot_width = pairs[2][0][0][0] - pairs[3][0][0][0]
        avg_width = (top_width + bot_width) / 2

        # Calc heigth scaling
        left_height = pairs[3][0][0][1] - pairs[0][0][0][1]
        right_height = pairs[2][0][0][1] - pairs[1][0][0][1]
        avg_height = (left_height + right_height) / 2

        return (width / avg_width, height / avg_height)

    def get_reference_corners(self, corners: CornerList, ids: IDList):
        '''
        This function receives a variable number of marker corner coordinates. If there are at least 4 markers, this
        tries to find the rectangle framed by four corner morkers.
        '''
        if len(corners) < 4:
            return np.array([])

        rect_corner_corners = []
        rect_corner_ids = []

        for c in zip(corners, ids):
            if c[1] in [0, 1, 2, 3]:
                rect_corner_corners.append(c[0])
                rect_corner_ids.append(c[1])

        if len(rect_corner_corners) != 4:
            return np.array([])

        ok, frame = self.tracker.get_frame()
        if not ok:
            return np.array([])

        ret, proj_corners, proj_ids = cv.aruco.interpolateCornersCharuco(
            rect_corner_corners,
            np.array(rect_corner_ids),
            frame,
            self.board
        )

        if ret != 4:
            return np.array([])

        return proj_corners

    def transform_in_intervals(self):
        '''
        Transform the projection in regular intervals in a separate thread. The transformation is needed to adjust the
        rendering based on the detected outer edge of the corner ArUco markers. To reduce the computing needed we
        don't calculate the transformation every frame, but every n seconds.
        '''
        t = threading.Thread(None, self.calc_corner_transform, 'transform-projection')
        self.transform_thread = t
        t.start()

    def calc_corner_transform(self):
        '''
        Retrieve the raw tracking data to calculate the transformation matrix.
        '''
        retrieve = self.subscribe_raw(1)
        while self.running:
            all_img_pts = []

            try:
                (corners, ids, rejected, recovered) = retrieve(False)
                if len(ids) == 0:
                    continue

                rvecs, tvecs, obj_points = cv.aruco.estimatePoseSingleMarkers(
                    corners, 1,
                    self.calib_data[0],
                    self.calib_data[1]
                )

                for rvec, tvec in zip(rvecs, tvecs):
                    try:
                        img_pts, jacobian = cv.projectPoints(
                            self.axis, rvec, tvec,
                            self.calib_data[0],
                            self.calib_data[1]
                        )
                        all_img_pts.append(img_pts)
                    except:
                        continue

                if [0] in ids and [1] in ids and [2] in ids and [3] in ids:
                    self.corner_transform[0] = all_img_pts[np.where(ids == [0])[0][0]][1][0]
                    self.corner_transform[1] = all_img_pts[np.where(ids == [1])[0][0]][2][0]
                    self.corner_transform[2] = all_img_pts[np.where(ids == [2])[0][0]][3][0]
                    self.corner_transform[3] = all_img_pts[np.where(ids == [3])[0][0]][0][0]
                    self.calc_projection_transform()
                    print('Done transform')
                    break

            except:
                continue

        self.tracker.unsubscribe(self.raw_subscription_id)

    def calc_projection_transform(self):
        ''''''
        (tl, tr, br, bl) = self.corner_transform

        # Calculate the adjusted width. For this we take the max distance of the top-left and top-right corners and the
        # maximum distance of the bottom-left and bottom-right corners. Then take the maximum of both these values.
        width_top = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        width_bot = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        width = max(int(width_top), int(width_bot))

        # Calculate the height the same way we calculated the width. This time we uss the top-left + bottom-left and
        # top-right + bottom-right distances. Take the maximum of both these values again.
        height_left = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        height_right = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        height = max(int(height_left), int(height_right))

        dst = np.array([
            [0, 0],
            [width - 1, 0],
            [width - 1, height - 1],
            [0, height - 1]
        ], dtype="float32")

        self.transform_matrix = cv.getPerspectiveTransform(self.corner_transform, dst)
        self.transform_height = height
        self.transform_width = width
