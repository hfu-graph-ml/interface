from typing import Tuple
import cv2 as cv

import utils.colors as colors


class Renderer:
    def __init__(self) -> None:
        pass

    def draw_corners(self, corners: list, ids: list, frame: any):
        ''''''
        # Corners is a tuple with 2 items: A list or corners and a dtype.
        # The corner list is a three dimensional array The dimensions are:
        # 1. A list of all corners for every marker
        # 2. A list or 4 corners per marker
        # 3. A list with two elements: the X and Y position of one corner

        # We access corners[0] as we are only interested in the list of corners
        for i, corners_per_marker in enumerate(corners[0]):
            self.draw_border(corners_per_marker, ids[i], frame)

    def draw_border(self, corners: list, id: int, frame: any):
        ''''''
        if len(corners) != 4:
            return

        tl, tr, br, bl = self.extract_corner_points(corners)

        # Top-left to top-right
        cv.line(frame, tl, tr, colors.GREEN, 2)

        # Top-right to bottom-right
        cv.line(frame, tr, br, colors.GREEN, 2)

        # Bottom-right to bottom-left
        cv.line(frame, br, bl, colors.GREEN, 2)

        # Bottom-left to topp-left
        cv.line(frame, bl, tl, colors.GREEN, 2)

    def extract_corner_points(sel, corners: list) -> Tuple[tuple, tuple, tuple, tuple]:
        (tl, tr, br, bl) = corners
        return (int(tl[0]), int(tl[1])), (int(tr[0]), int(tr[1])), (int(br[0]), int(br[1])), (int(bl[0]), int(bl[1]))
