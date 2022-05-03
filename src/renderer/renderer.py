from typing import Tuple
import cv2 as cv
import math

import config.config as config
import utils.colors as colors
import utils.wait as wait

from tracker.tracker import Tracker
from renderer.types import RendererError


class Renderer:
    def __init__(self, cfg: config.RendererOptions, t: Tracker) -> None:
        self._subscription_id = -1
        self._fps = cfg['fps']
        self._running = False
        self._thread = None
        self._tracker = t

    def _draw_corners(self, corners: list, ids: list, frame: any):
        ''''''
        # The corner list is a three dimensional array The dimensions are:
        # 1. A list of all corners for every marker
        # 2. A list or 4 corners per marker
        # 3. A list with two elements: the X and Y position of one corner

        # We access corners[0] as we are only interested in the list of corners
        for i, corners_per_marker in enumerate(corners):
            self._draw_border(corners_per_marker[0], ids[i][0], frame)

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

    def start(self) -> RendererError:
        ''''''
        if self._running:
            return RendererError('Already running')

        self._running = True

        window_name = 'rendering'
        wait_delay = math.floor((1 / self._fps)*1000)

        # Setup live video stream
        cap = cv.VideoCapture(0)

        # Setup rendering window
        cv.namedWindow(window_name)

        # Subscribe to the tracker
        id, retrieve = self._tracker.subscribe()
        self._subscription_id = id

        while self._running:
            ok, frame = cap.read()
            if not ok:
                continue

            # We wrap this call in a try catch because it throws an Exception when
            # we access an empty queue. This is the case when there are no markers
            # in the capture frame or none is detected
            try:
                # Retrieve tracked markers
                corners, ids = retrieve(False)
                self._draw_corners(corners, ids, frame)
            except:
                pass

            cv.imshow(window_name, frame)

            if wait.wait_or_exit(wait_delay):
                break

        # Cleanup
        cv.destroyAllWindows()
        cap.release()
        return None

    def stop(self):
        ''''''
        self._tracker.unsubscribe(self._subscription_id)
        self._running = False
