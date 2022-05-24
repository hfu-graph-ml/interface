import numpy as np
import cv2 as cv

from capture.tracker import Tracker
import config.config as config
import utils.wait as wait
import utils.fmt as fmt

from typings.renderer import RendererError
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
        self._calib_markers = [0, 1, 2, 3]

    def _draw_node():
        pass

    def start(self) -> RendererError:
        '''
        Start the render loop.
        '''
        if self._running:
            return RendererError('Already running')

        self._running = True

        wait_delay = fmt.fps_to_ms(self._fps)

        window_name = 'rendering'
        cv.namedWindow(window_name)

        # Subscribe to the tracker
        id, params, retrieve = self._tracker.subscribe()
        self._camera_frame_height = params[1]
        self._camera_frame_width = params[0]
        self._subscription_id = id

        # White frame sized width x height
        initial_frame = 255 * np.ones((self._frame_height, self._frame_width, 3), dtype=np.uint8)
        frame = np.copy(initial_frame)

        while self._running:
            try:
                corners, ids = retrieve(False)

                # Copy the frame here. This reduces flickering
                frame = np.copy(initial_frame)

                for i, corners_per_marker in enumerate(corners):
                    self._draw_center_point(corners_per_marker[0], ids[i], frame)
            except:
                pass

            cv.imshow(window_name, frame)

            if wait.wait_or(wait_delay):
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
