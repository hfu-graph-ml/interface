from enum import Enum, unique
import numpy as np
import cv2 as cv
import os

import tracker.aruco as aruco

from .types import TrackingError


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

    def __init__(self, size: int, uniq: int, path: str) -> None:
        typ = aruco.type_from(size, uniq)
        t, ok = aruco.dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Generator object')

        self._dict = cv.aruco.Dictionary_get(t)
        self._path = path
        self._type = t

    def generate(self, number: int, res: int, usage: Usage, start_id: int = 0) -> TrackingError:
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
            return TrackingError('Generator initialized with invalid ArUco type')

        if number <= 0:
            return TrackingError('Invalid number of markers')

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

    def generate_combined(self, number: int, res: int) -> TrackingError:
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
