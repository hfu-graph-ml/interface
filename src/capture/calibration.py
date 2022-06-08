from typing import Tuple
import numpy as np
import cv2 as cv
import click
import json
import math
import time
import os

from typings.capture import CalibrationError, CharucoCalibrationResult

import config.config as config
import capture.aruco as aruco


class Calibration:
    '''
    This class describes the calibration which is required to calculate the intrisic camera matrix to apply a projection
    transform when rendering.
    '''

    def __init__(self, cfg: config.Config, verbose: bool) -> None:
        typ = aruco.type_from(
            cfg['capture']['aruco']['size'],
            cfg['capture']['aruco']['uniques']
        )
        t, ok = aruco.dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Generator object')

        self._dict = cv.aruco.Dictionary_get(t)

        cols = cfg['capture']['calibration']['cols'] + 1
        rows = cfg['capture']['calibration']['rows'] + 1

        # Create ChArUco board
        self._board = cv.aruco.CharucoBoard_create(
            cols,
            rows,
            0.04,
            0.02,
            self._dict
        )

        self._min_response = math.floor(((cols * rows) / 2) * 0.8)
        self._cfg = cfg['capture']
        self._verbose = verbose

        self._image_size = None
        self._corners = []
        self._frames = []
        self._ids = []

    def _save_images(self):
        '''
        Save the stored frames as images.
        '''
        save_path = os.path.join(self._cfg['path'], 'images')
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        for i, frame in enumerate(self._frames):
            img_name = 'img-{:02d}.png'.format(i)
            img_path = os.path.join(save_path, img_name)
            cv.imwrite(img_path, frame)

    def _capture(self, grayscale: bool = False) -> CalibrationError:
        '''
        Capture images from camera and save them afterwards.

        Parameters
        ----------
        grayscale : bool
            If the captured images should be grayscaled

        Returns
        -------
        err : CalibrationError
            Returns CalibrationError if an error was encountered, None if otherwise
        '''
        cap = cv.VideoCapture(self._cfg['camera_id'])

        n = 0
        while n < self._cfg['calibration']['number_images']:
            if self._verbose:
                click.echo('Capture image {:02d}'.format(n))

            ok, frame = cap.read()
            if not ok:
                return CalibrationError('Failed to read the frame')

            if grayscale:
                frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            self._frames.append(frame)
            n += 1

            time.sleep(self._cfg['calibration']['interval'])

        cap.release()
        return None

    def _detect(self) -> CalibrationError:
        '''
        Detect markers and interpolate the ChArUco board corners.

        Returns
        -------
        err : CalibrationError
            Returns CalibrationError if an error was encountered, None if otherwise
        '''
        for frame in self._frames:
            # First detect ArUco markers in the current frame
            corners, ids, _ = cv.aruco.detectMarkers(frame, self._dict)

            # Skip if we didn't find any corners
            if len(corners) == 0:
                continue

            # Get the ChArUco board corners based on the previously detected markers
            response, charuco_corners, charuco_ids = cv.aruco.interpolateCornersCharuco(
                corners,
                ids,
                frame,
                self._board
            )

            # If we found at least 80 percent of the total markers we store the ChArUco corners and IDs
            if response > self._min_response:
                self._corners.append(charuco_corners)
                self._ids.append(charuco_ids)

                self._image_size = frame.shape[::-1]
                return None
                # TODO (Techassi): Add option to preview the image used and draw the detected markers

        return CalibrationError('Failed to detect markers in any of the captured frames')

    def _calibrate(self) -> CharucoCalibrationResult:
        '''
        Calibrate the camera based on the detected ChArUco board.

        Returns
        -------
        result : CharucoCalibrationResult
            A tuple consisting of the camera matrix, distortion coefficients, rotation and tranlation vectors
        '''
        # Extract the camera matrix and distortion coefficients
        _, cameraMatrix, distCoeffs, rvecs, tvecs = cv.aruco.calibrateCameraCharuco(
            self._corners,
            self._ids,
            self._board,
            self._image_size,
            cameraMatrix=None,
            distCoeffs=None
        )

        return (cameraMatrix, distCoeffs, rvecs, tvecs)

    def calibrate_auto(self) -> Tuple[CharucoCalibrationResult, CalibrationError]:
        '''
        Automatically calibrate the camera and projector setup.
        '''
        # First capture a set of frames from the capture device (camera)
        err = self._capture(True)
        if err != None:
            return None, err

        # Next detect ArUco markers and ChArUco board
        err = self._detect()
        if err != None:
            return None, err

        return self._calibrate(), None

    def calibrate_manual(self):
        '''
        Calibrate the camera manually by capturing a specified number of images.
        '''
        self._capture_manual()


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o: any) -> any:
        if isinstance(o, np.ndarray):
            return o.tolist()

        return super().default(o)


def dump_calibration_result(result: CharucoCalibrationResult) -> str:
    ''''''
    return json.dumps(result, cls=CustomJSONEncoder)
