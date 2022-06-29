import numpy as np
import cv2 as cv
import threading
import time

from capture.tracker import Tracker
from renderer.shared import Shared
from config.config import Config

from typings.capture.calibration import CharucoCalibrationData


class Transformer(Shared):
    def __init__(self, cfg: Config, calib_data: CharucoCalibrationData, tracker: Tracker) -> None:
        super().__init__(cfg, tracker)

        self.corner_transform = np.zeros((4, 2), dtype="float32")
        self.transform_matrix = np.zeros([])
        self.calib_data = calib_data
        self.transform_height = 0
        self.transform_width = 0

        self._axis = np.float32([
            [-.5, -.5, 0],
            [-.5, .5, 0],
            [.5, .5, 0],
            [.5, -.5, 0],
            [-.5, -.5, 1],
            [-.5, .5, 1],
            [.5, .5, 1],
            [.5, -.5, 1]
        ])

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
            time.sleep(self.cfg['renderer']['transform_interval'])
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
                            self._axis, rvec, tvec,
                            self.calib_data[0],
                            self.calib_data[1]
                        )
                        all_img_pts.append(img_pts)
                    except:
                        continue

                if [0] in ids and [1] in ids and [2] in ids and [3] in ids:
                    self.corner_transform[0] = all_img_pts[np.where(ids == [0])[0][0]][1][0]
                    self.corner_transform[1] = all_img_pts[np.where(ids == [1])[0][0]][2][0]
                    self.corner_transform[2] = all_img_pts[np.where(ids == [3])[0][0]][3][0]
                    self.corner_transform[3] = all_img_pts[np.where(ids == [2])[0][0]][0][0]
                    self.calc_projection_transform()
                else:
                    print('{} Detected corner, but missing'.format(time.strftime('%H:%M:%S', time.localtime())))

            except:
                print('{} No corners detected'.format(time.strftime('%H:%M:%S', time.localtime())))
                continue

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
