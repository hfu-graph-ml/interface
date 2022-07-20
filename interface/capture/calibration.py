import numpy as np
import cv2 as cv
import pickle
import click
import json
import math
import time
import os

from typings.capture.calibration import CharucoCalibrationData, CalibrationMode
from typings.error import Error, Err, Ok, Result

import config.config as config
import capture.aruco as aruco


class Calibration:
    '''
    This class describes the calibration which is required to calculate the intrisic camera matrix to apply a projection
    transform when rendering.
    '''

    def __init__(self, cfg: config.Config, verbose: bool = False) -> None:
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
        self._board = aruco.board_from(
            cols,
            rows,
            self._dict
        )

        self._min_response = math.floor(((cols * rows) / 2) * 0.8)
        self._verbose = verbose
        self._cfg = cfg

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

    def _capture(self, grayscale: bool = False) -> Error:
        '''
        Capture images from camera and save them afterwards.

        Parameters
        ----------
        grayscale : bool
            If the captured images should be grayscaled.

        Returns
        -------
        err : Error
            Returns Error if an error was encountered, None if otherwise.
        '''
        cap = cv.VideoCapture(self._cfg['capture']['camera_id'])

        n = 0
        while n < self._cfg['capture']['calibration']['number_images']:
            if self._verbose:
                click.echo('Capture image {:02d}'.format(n))

            ok, frame = cap.read()
            if not ok:
                return Error('Failed to read the frame')

            if grayscale:
                frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            self._frames.append(frame)
            n += 1

            time.sleep(self._cfg['capture']['calibration']['interval'])

        cap.release()
        return None

    def _detect(self) -> Error:
        '''
        Detect markers and interpolate the ChArUco board corners.

        Returns
        -------
        err : Error
            Returns Error if an error was encountered, None if otherwise.
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

        return Error('Failed to detect markers in any of the captured frames')

    def _calibrate(self) -> CharucoCalibrationData:
        '''
        Calibrate the camera based on the detected ChArUco board.

        Returns
        -------
        result : CharucoCalibrationResult
            A tuple consisting of the camera matrix, distortion coefficients, rotation and tranlation vectors.
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

    def _calibrate_auto(self) -> Result[CharucoCalibrationData, Error]:
        '''
        Automatically calibrate the camera and projector setup.

        Returns
        -------
        result : Result[CharucoCalibrationData, Error]
        '''
        # Setup calibration renderer and start to render
        r = 0

        # Capture a set of frames from the capture device (camera)
        err = self._capture(True)
        if err != None:
            return Err(err)

        # Next detect ArUco markers and ChArUco board
        err = self._detect()
        if err != None:
            return Err(err)

        data = self._calibrate()
        return Ok(data)

    def _calibrate_semi(self) -> Result[CharucoCalibrationData, Error]:
        '''
        Calibrate the camera semi-automatic. This is done by capturing multiple images at an even interval while the
        user moves the ChArUco board manually.

        Returns
        -------
        result : Result[CharucoCalibrationData, Error]
        '''
        # First capture a set of frames from the capture device (camera)
        err = self._capture(True)
        if err != None:
            return Err(err)

        # Next detect ArUco markers and ChArUco board
        err = self._detect()
        if err != None:
            return Err(err)

        data = self._calibrate()
        return Ok(data)

    def _calibrate_manual(self):
        '''
        Calibrate the camera manually by capturing a specified number of images.
        '''
        self._capture_manual()

    def calibrate(self, mode: CalibrationMode = CalibrationMode.AUTO) -> Result[CharucoCalibrationData, Error]:
        '''
        Calibrate the camera via the provided calibration mode.

        Parameters
        ----------
        mode : CalibrationMode
            Calibration mode. Can be AUTO, SEMI_AUTO or MANUAL.

        Returns
        -------
        result : Result[CharucoCalibrationData, Error]
        '''
        match mode:
            case CalibrationMode.AUTO:
                return self._calibrate_auto()
            case CalibrationMode.SEMI_AUTO:
                return self._calibrate_semi()
            case CalibrationMode.MANUAL:
                return self._calibrate_manual()
            case _:
                return Err(Error('Invalid calibration mode'))

    def calibrate_save(self, mode: CalibrationMode = CalibrationMode.AUTO) -> Result[CharucoCalibrationData, Error]:
        '''
        Calibrate the camera via the provided calibration mode. This method additionally saves the calibration data
        in the .data/calib.json file.

        Parameters
        ----------
        mode : CalibrationMode
            Calibration mode. Can be AUTO, SEMI_AUTO or MANUAL.

        Returns
        -------
        result : Tuple[CharucoCalibrationResult, Error]
        '''
        result = self.calibrate(mode)

        if result.is_err():
            return result

        file_path = os.path.join(self._cfg['capture']['path'], 'calib.pckl')
        err = dump_calibration_result(file_path, result.unwrap())
        if err != None:
            return Err(err)

        return result


def dump_calibration_result(path: str, data: CharucoCalibrationData) -> Error:
    '''
    Dump the provided ChArUco calibration result as a pickle file.

    Parameters
    ----------
    path : str
        Path where the calibration data pickle file should be stored.
    data : CharucoCalibrationResult
        The ChArUco calibration result.

    Returns
    -------
    err : Error
    '''
    try:
        file = open(path, 'wb')
        pickle.dump(data, file)
        file.close()
        return None
    except:
        return Error('Failed to dump calibration data')


def read_calibration_result(path: str) -> Result[CharucoCalibrationData, Error]:
    '''
    Read  ChArUco calibration result data from a JSON formatted file at 'path'.

    Parameters
    ----------
    path : str
        Path to the calibration data pickle file.

    Returns
    -------
    result : Result[CharucoCalibrationData, Error]
    '''
    try:
        file = open(path, 'rb')
        result = pickle.load(file)
        return Ok(result)
    except:
        return Err(Error('Failed to read calibration data'))
