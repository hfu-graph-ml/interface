from typing import Tuple
import cv2 as cv

from capture.tracker import Tracker
from renderer.shared import Shared
from config.config import Config
import utils.wait as wait

from typings.capture.aruco import MarkerBordersList
from typings.error import Error


class DebugRenderer(Shared):
    '''
    This class decribes a debug renderer used to draw tracking information for debug purposes.
    '''

    def __init__(self, cfg: Config, tracker: Tracker, use_color: bool) -> None:
        super().__init__(cfg, tracker, 'debug-tracking')
        self._use_color = use_color

    def _get_frame(self) -> Tuple[bool, cv.Mat]:
        ''''''
        if self._use_color:
            return self.tracker.get_color_frame()

        return self.tracker.get_frame()

    def start(self) -> Error:
        '''
        Start the render loop.
        '''
        if self.is_running():
            return Error('Already running')

        retrieve = self.subscribe()

        while self.running:
            ok, frame = self._get_frame()
            if not ok:
                continue

            try:
                markers = retrieve(False)
                for marker in markers:
                    self.draw_borders(marker[0], frame)
                    self.draw_angle(marker[0], marker[2], frame, with_text=False)
                    self.draw_center_point(marker[1], marker[3], frame)
            except:
                pass

            cv.imshow(self.window_name, frame)

            idx = wait.multi_wait_or(self.wait_delay, 'q', 'f')
            if idx == -1:
                continue
            elif idx == 0:
                break
            else:
                self.toggle_fullscreen()

        # Cleanup
        self.stop()
        return None
