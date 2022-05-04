from typing import Tuple
import cv2 as cv

import utils.colors as colors


class DebugRenderer:
    def _draw_border(self, corners: list, id: int, frame: any):
        ''''''
        if len(corners) != 4:
            return

        tl, tr, br, bl = self._extract_corner_points(corners)

        # Top-left to top-right
        cv.line(frame, tl, tr, colors.GREEN, 2)

        # Top-right to bottom-right
        cv.line(frame, tr, br, colors.GREEN, 2)

        # Bottom-right to bottom-left
        cv.line(frame, br, bl, colors.GREEN, 2)

        # Bottom-left to topp-left
        cv.line(frame, bl, tl, colors.GREEN, 2)

        cv.putText(frame, str(id), (tl[0] - 15, tl[1] - 15), cv.FONT_HERSHEY_SIMPLEX, 0.5, colors.RED, 2)

    def _extract_corner_points(sel, corners: list) -> Tuple[tuple, tuple, tuple, tuple]:
        ''''''
        (tl, tr, br, bl) = corners
        return (int(tl[0]), int(tl[1])), (int(tr[0]), int(tr[1])), (int(br[0]), int(br[1])), (int(bl[0]), int(bl[1]))

    def render(self, corners: list, ids: list, frame: any):
        ''''''
        # The corner list is a three dimensional array The dimensions are:
        # 1. A list of all corners for every marker
        # 2. A list or 4 corners per marker
        # 3. A list with two elements: the X and Y position of one corner

        # We access corners[0] as we are only interested in the list of corners
        for i, corners_per_marker in enumerate(corners):
            self._draw_border(corners_per_marker[0], ids[i][0], frame)

        return frame
