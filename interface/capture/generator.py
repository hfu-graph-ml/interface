import numpy as np
import cv2 as cv
import os

import config.config as config
import capture.aruco as aruco

from typings.error import Err, Error


class Generator:
    '''
    This class generates ArUco markers / tags.
    '''

    def __init__(self, cfg: config.Config) -> None:
        typ = aruco.type_from(
            cfg['capture']['aruco']['size'],
            cfg['capture']['aruco']['uniques']
        )
        t, ok = aruco.dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Generator object')

        self._dict = cv.aruco.Dictionary_get(t)
        self._path = cfg['capture']['path']
        self._type = t

    def generate(self, number: int, res: int) -> Error:
        '''
        Generate a variable number of ArUco markers.

        Args:
            number: Number of ArUco markers to generate.
            res: Resolution of the markers in pixels (e.g. 300x300).
            usage: For which purpose the marker will be used (calibration or as nodes).
            start_id : The ID (index) to start at. This is usefull when generating
                calibration and node markers at the same time. This prevents
                duplicate IDs.

        Returns:
            An Error if an error was encountered, None if otherwise.
        '''
        # Make sure the generator was initialized correctly
        if self._type == -1 or self._dict == None:
            return Err('Generator initialized with invalid ArUco type')

        if number <= 0:
            return Err('Invalid number of markers')

        # Make sure the output folder exists
        path = os.path.join(self._path, 'markers')
        if not os.path.exists(path):
            os.makedirs(path)

        for i in range(0, number):
            marker_name = 'marker-{:02d}.png'.format(i)

            # Create a X by Y sized empty 2D array to write the marker to
            marker = np.zeros((res, res, 1), dtype='uint8')

            # Draw the marker in the above created array. The arguments are:
            # - The selected ArUco dict
            # - The marker name (ID)
            # - The resolution, e.g. 300 x 300 pixels
            # - The array to write the marker into
            # - The number of border bits
            cv.aruco.drawMarker(self._dict, i, res, marker, 1)

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


class BoardGenerator():
    '''
    This class generates ArUco chessboard patterns (ChArUco).
    '''

    def __init__(self, cfg: config.Config) -> None:
        typ = aruco.type_from(
            cfg['capture']['aruco']['size'],
            cfg['capture']['aruco']['uniques']
        )
        t, ok = aruco.dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Generator object')

        self._dict = cv.aruco.Dictionary_get(t)
        self._path = cfg['capture']['path']
        self._type = t

    def generate(self, cols: int, rows: int, res_width: int, res_height: int) -> Error:
        '''
        Generate ChArUco board.

        Args:
            cols: The number of columns.
            rows: The number of rows.
            res_width: Width of the generated image in pixels.
            res_height: Height of the generated image in pixels.

        Returns:
            An Error if an error was encountered, None if otherwise.
        '''
        # Make sure the generator was initialized correctly
        if self._type == -1 or self._dict == None:
            return Err('Generator initialized with invalid ArUco type')

        # Make sure the output folder exists
        path = os.path.join(self._path, 'boards')
        if not os.path.exists(path):
            os.makedirs(path)

        board = aruco.board_from(
            cols + 1,
            rows + 1,
            self._dict
        )

        # Construct final path, draw board and save
        board_path = os.path.join(path, 'board.png')
        img = board.draw((res_width, res_height))
        cv.imwrite(board_path, img)
