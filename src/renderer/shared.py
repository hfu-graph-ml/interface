from typing import Tuple
import cv2 as cv

import utils.colors as colors


class Shared:
    def _extract_corner_points(
        self,
        corners: list
    ) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        '''
        Extract individual ppoints from the list of points. Additionally convert them to integer values.

        Parameters
        ----------
        corners : list
            A list or corners

        Returns
        -------
        points : Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]
            The four extracted corner points
        '''
        (tl, tr, br, bl) = corners
        # NOTE (Techassi): This is giga ugly but I don't know of a better way to achieve this
        return (int(tl[0]), int(tl[1])), (int(tr[0]), int(tr[1])), (int(br[0]), int(br[1])), (int(bl[0]), int(bl[1]))

    def _extract_center_point(self, corners: list) -> Tuple[int, int]:
        ''''''
        center_x = int((corners[0][0] + corners[2][0]) / 2)
        center_y = int((corners[0][1] + corners[2][1]) / 2)

        return center_x, center_y

    def _draw_borders(self, corners: list, frame: any):
        ''''''
        tl, tr, br, bl = self._extract_corner_points(corners)

        cv.line(frame, tl, tr, colors.GREEN, 2)  # Top left to top right
        cv.line(frame, tr, br, colors.GREEN, 2)  # Top right to bottom right
        cv.line(frame, br, bl, colors.GREEN, 2)  # Bottom right to bottom left
        cv.line(frame, bl, tl, colors.GREEN, 2)  # Bottom left to top left

    def _draw_center_point(self, corners: list, id: int, frame: any):
        ''''''
        cx, cy = self._extract_center_point(corners)
        cv.circle(frame, (cx, cy), 4, colors.RED, -1)
        cv.putText(frame, str(id), (cx - 10, cy - 15), cv.FONT_HERSHEY_SIMPLEX, 0.8, colors.RED, 2)
