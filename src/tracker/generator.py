from enum import Enum, unique
from typing import Tuple
import numpy as np
import cv2 as cv
import os

import utils.fmt as fmt

from .types import Error

MARKER_MAP = {
    '4X4_50': cv.aruco.DICT_4X4_50,
    '4X4_100': cv.aruco.DICT_4X4_100,
    '4X4_250': cv.aruco.DICT_4X4_250,
    '4X4_1000': cv.aruco.DICT_4X4_1000,
    '5X5_50': cv.aruco.DICT_5X5_50,
    '5X5_100': cv.aruco.DICT_5X5_100,
    '5X5_250': cv.aruco.DICT_5X5_250,
    '5X5_1000': cv.aruco.DICT_5X5_1000,
    '6X6_50': cv.aruco.DICT_6X6_50,
    '6X6_100': cv.aruco.DICT_6X6_100,
    '6X6_250': cv.aruco.DICT_6X6_250,
    '6X6_1000': cv.aruco.DICT_6X6_1000,
    '7X7_50': cv.aruco.DICT_7X7_50,
    '7X7_100': cv.aruco.DICT_7X7_100,
    '7X7_250': cv.aruco.DICT_7X7_250,
    '7X7_1000': cv.aruco.DICT_7X7_1000,
}


@unique
class Usage(Enum):
    CALIB = 0
    NODES = 1

    def str(self) -> str:
        return ['calib', 'nodes'][self.value]


class Generator:
    '''
    This class generates ArUco markers / tags.
    '''
    _dict: dict = None
    _type: int = -1
    _path: str = ''

    def __init__(self, size: int, uniq: int, path: str) -> None:
        typ = fmt.aruco_type_from(size, uniq)
        t, ok = self.get_type(typ)
        if not ok:
            return

        self._dict = cv.aruco.Dictionary_get(t)
        self._path = path
        self._type = t

    def get_type(self, k: str) -> Tuple[int, bool]:
        '''
        Returns ArUco dict with 'k' as key.

        Paramaters
        ----------
        k : str
            Map key to ArUco dict

        Returns
        -------
        result : Tuple[int, bool]
            Returns index and True if k exists. -1 and False otherwise
        '''
        if MARKER_MAP[k] == None:
            return -1, False

        return MARKER_MAP[k], True

    def generate(self, number: int, res: int, usage: Usage, start_id: int = 0) -> Error:
        '''
        Generate a variable number of ArUco markers.

        Parameters
        ----------
        number : int
            Number of ArUco markers to generate
        res : int
            Resolution of the markers in pixels (e.g. 300x300)
        usage : Usage
            For which purpose the marker will be used (calibration or as nodes)
        start_id : int
            The ID (index) to start at. This is usefull when generating
            calibration and node markers at the same time. This prevents
            duplicate IDs

        Returns
        -------
        err : Error
            None if no error occured
        '''
        # Make sure the generator was initialized correctly
        if self._type == -1 or self._dict == None:
            return Error('Generator initialized with invalid ArUco type')

        # Make sure the output folder exists
        path = os.path.join(self._path, usage.str())
        if not os.path.exists(path):
            os.makedirs(path)

        for i in range(0, number):
            marker_name = 'marker-{:02d}.png'.format(start_id + i)

            # Create a X by Y sized empty 2D array to write the marker to
            marker = np.zeros((res, res, 1), dtype='uint8')

            # Draw the marker in the above created array. The arguments are:
            # - The selected ArUco dict
            # - The marker name (ID)
            # - The resolution, e.g. 300 x 300 pixels
            # - The array to write the marker into
            # - The number of border bits
            cv.aruco.drawMarker(self._dict, start_id + i, res, marker, 1)

            # Construct file path and save
            marker_path = os.path.join(path, marker_name)
            ok: bool = False

            try:
                ok = cv.imwrite(marker_path, marker)
            except:
                print(f'Error while converting image: {marker_path}')
                continue

            if not ok:
                print(f'Error while saving {marker_path}')

        return None

    def generate_combined(self, number: int, res: int) -> Error:
        '''
        Generate calibration and node markers at the same time.

        Parameters
        ----------
        number : int
            Number of ArUco markers to generate
        res : int
            Resolution of the markers in pixels (e.g. 300x300)

        Returns
        -------
        err : Error
            None if no error occured
        '''
        # First generate calibration markers
        err = self.generate(4, res, Usage.CALIB)
        if err != None:
            return err

        # Generate node markers
        return self.generate(number, res, Usage.NODES, 4)
