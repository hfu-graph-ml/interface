from typing import Tuple
import numpy as np
import cv2 as cv
import math

from tracker.tracker import Tracker
import config.config as config
import utils.colors as colors
import utils.wait as wait

from .types import RendererError


class Renderer:
    '''
    This class describes the renderer which renders the user interface.
    '''

    def __init__(self, cfg: config.CaptureOptions, t: Tracker) -> None:
        self._subscription_id = -1
        self._fps = cfg['fps']
        self._running = False
        self._tracker = t

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
        id, retrieve = self._tracker.subscribe()
        self._subscription_id = id

        while self._running:
            frame = np.zeros((500, 500, 1))

            cv.imshow(window_name, frame)

            if wait.wait_or_exit(wait_delay):
                break

        # Cleanup
        cv.destroyAllWindows()
        return None

    def stop(self):
        '''
        Stop the render loop.
        '''
        self._tracker.unsubscribe(self._subscription_id)
        self._running = False
