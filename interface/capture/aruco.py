from typing import Tuple
import cv2 as cv

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


def type_from(res: int, uniq: int) -> str:
    '''
    Returns a ArUco type string in the form <RES>X<RES>_<UNIQ>.

    Parameters
    ----------
    res : int
        Resolution (X and Y), e.g. 5X5
    uniq : int
        Possible number of unique markers

    Returns
    type : str
        Formatted ArUco type string
    '''
    return f'{res}X{res}_{uniq}'


def dict_from(k: str) -> Tuple[int, bool]:
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


def board_from(cols: int, rows: int, dict: int, marker_length: float = 0.04, marker_separation: float = 0.02):
    '''
    Returns a ChArUco chessboard with size `cols` x `rows` and `dict`.

    Parameters
    ----------
    cols : int
        Number of columns.
    rows : int
        Number of rows.
    dict : int
        Unique ArUco dict identifier. Use with `dict_from`.
    marker_length : float
        Chessboard square side length (normally in meters).
    marker_separation : float
        Marker side length (same unit than `marker_length`).

    Returns
    -------
    board : CharucoBoard
        The generated ChArUco chessboard.
    '''
    return cv.aruco.CharucoBoard_create(
        cols,
        rows,
        marker_length,
        marker_separation,
        dict
    )
