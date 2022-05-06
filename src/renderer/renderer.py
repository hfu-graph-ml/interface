import numpy as np
import cv2 as cv
import math

from tracker.tracker import Tracker
import config.config as config
import utils.colors as colors
import utils.wait as wait

from .types import RendererError
from .shared import Shared


class Renderer(Shared):
    '''
    This class describes the renderer which renders the user interface.
    '''

    def __init__(self, cfg: config.Config, t: Tracker) -> None:
        self._fps = cfg['capture']['fps']
        self._subscription_id = -1
        self._running = False
        self._tracker = t

        # Dimensions
        self._frame_height = cfg['renderer']['height']
        self._frame_width = cfg['renderer']['width']

        # Camera dimensions
        self._camera_frame_height = 0
        self._camera_frame_width = 0

        # Scaling
        self._scaling_factor = 1

    def _calibrate():
        ''''''

    def start(self) -> RendererError:
        '''
        Start the render loop.
        '''
        if self._running:
            return RendererError('Already running')

        self._running = True

        wait_delay = math.floor((1 / self._fps)*1000)

        window_name = 'rendering'
        cv.namedWindow(window_name)

        # Subscribe to the tracker
        id, params, retrieve = self._tracker.subscribe()
        self._subscription_id = id

        while self._running:
            frame = np.zeros((self._frame_height, self._frame_width, 3))

            try:
                corners, ids = retrieve(False)

                for i, corners_per_marker in enumerate(corners):
                    if len(corners_per_marker[0]) != 4:
                        continue

                    self._draw_center_point(corners_per_marker[0], ids[i], frame)
            except:
                pass

            cv.imshow(window_name, frame)

            if wait.wait_or_exit(wait_delay):
                break

        # Cleanup
        self.stop()
        return None

    def stop(self):
        '''
        Stop the render loop.
        '''
        cv.destroyAllWindows()

        self._tracker.unsubscribe(self._subscription_id)
        self._tracker.stop()
