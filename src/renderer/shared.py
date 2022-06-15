import cv2 as cv

import utils.colors as colors


class Shared:
    def _draw_borders(self, corners: tuple, frame:  cv.Mat):
        ''''''

        cv.line(frame, corners[0], corners[1], colors.GREEN, 2)  # Top left to top right
        cv.line(frame, corners[1], corners[2], colors.GREEN, 2)  # Top right to bottom right
        cv.line(frame, corners[2], corners[3], colors.GREEN, 2)  # Bottom right to bottom left
        cv.line(frame, corners[3], corners[0], colors.GREEN, 2)  # Bottom left to top left

    def _draw_center_point(self, pos: tuple, id: int, frame:  cv.Mat):
        ''''''
        cv.circle(frame, pos, 4, colors.RED, -1)
        cv.putText(frame, str(id), (pos[0] - 10, pos[1] - 45), cv.FONT_HERSHEY_SIMPLEX, 0.8, colors.RED, 2)
