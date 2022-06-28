import cv2 as cv

import utils.colors as colors

from capture.tracker import Tracker
from config.config import Config
from utils.fmt import fps_to_ms

from typings.capture.aruco import RawRetrieveFunc, RetrieveFunc


class Shared:
    def __init__(self, cfg: Config, tracker: Tracker, window_name: str = 'rendering') -> None:
        self._wait_delay = fps_to_ms(cfg['capture']['fps'])
        self._window_name = window_name
        self._subscription_id = -1
        self._fullscreen = False
        self._tracker = tracker
        self._running = False
        self._cfg = cfg

        # Camera dimensions
        self._camera_frame_height = 0
        self._camera_frame_width = 0

    def _is_running(self) -> bool:
        '''
        Returns if the renderer is already running.

        Returns
        -------
        running: bool
            If renderer is running
        '''
        if self._running:
            return True

        self._running = True
        return False

    def _subscribe(self) -> RetrieveFunc:
        '''
        Subscribe to the tracker.

        Returns
        -------
        fn : RetrieveFunc
            Function to retrieve new marker positions
        '''
        id, params, retrieve = self._tracker.subscribe()
        self._camera_frame_height = params[1]
        self._camera_frame_width = params[0]
        self._subscription_id = id

        return retrieve

    def _subscribe_raw(self) -> RawRetrieveFunc:
        '''
        Subscribe to the tracker in raw mode.

        Returns
        -------
        fn : RawRetrieveFunc
            Function to retrieve new marker positions
        '''
        id, params, retrieve = self._tracker.subscribe_raw()
        self._camera_frame_height = params[1]
        self._camera_frame_width = params[0]
        self._subscription_id = id

        return retrieve

    def _draw_borders(self, corners: tuple, frame: cv.Mat):
        '''
        Draw the border around a marker.
        '''
        cv.line(frame, corners[0], corners[1], colors.GREEN, 2)  # Top left to top right
        cv.line(frame, corners[1], corners[2], colors.GREEN, 2)  # Top right to bottom right
        cv.line(frame, corners[2], corners[3], colors.GREEN, 2)  # Bottom right to bottom left
        cv.line(frame, corners[3], corners[0], colors.GREEN, 2)  # Bottom left to top left

    def _draw_angle(self, corners: tuple, angle: float, frame: cv.Mat):
        '''
        Draw a circle in the top-left corner and attach the angle as text to it.
        '''
        cv.circle(frame, corners[0], 4, colors.RED, -1)  # Top left corner
        cv.putText(frame, '{:.2f}'.format(angle),  corners[0], cv.FONT_HERSHEY_SIMPLEX, 0.8, colors.RED, 2)

    def _draw_center_point(self, pos: tuple, id: int, frame: cv.Mat, with_text: bool = True):
        '''
        Draw a center point with the ID as text attached to it.
        '''
        cv.circle(frame, pos, 4, colors.RED, -1)
        if with_text:
            cv.putText(frame, str(id), (pos[0] - 10, pos[1] - 45), cv.FONT_HERSHEY_SIMPLEX, 0.8, colors.RED, 2)

    def _toggle_fullscreen(self):
        '''
        Toggle fullscreen of the rendering window.
        '''
        if self._fullscreen:
            self._fullscreen = False
            cv.setWindowProperty(self._window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_NORMAL)
        else:
            self._fullscreen = True
            cv.setWindowProperty(self._window_name, cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)

    def stop(self):
        '''
        Stop the render loop.
        '''
        cv.destroyAllWindows()

        self._tracker.unsubscribe(self._subscription_id)
        self._tracker.stop()
