from typing import Callable, List, TypeAlias
import cv2 as cv
import math

import config.config as config
import tracker.types as types
import utils.wait as wait

Callback: TypeAlias = Callable[[any, int, any], None]


class Tracker:
    '''
    This class describes a tracker which is able to track ArUco markers.
    '''

    def __init__(self, cfg: config.TrackerOptions) -> None:
        typ = types.aruco_type_from(cfg['size'], cfg['uniques'])
        t, ok = types.aruco_dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Tracker object')

        # These values keep track how many frames failed to read
        self._failed_read_threshold = cfg['failed_read_threshold']
        self._failed_reads = 0

        # ArUco marker related values
        self._dict = cv.aruco.Dictionary_get(t)
        self._type = t

        # Event subscribers
        self._subscribers: List[Callback]

        # Misc
        self._path = cfg['path']
        self._threaded = False

    def calibrate():
        pass

    def run(self, camera_id: int, fps: int) -> types.Error:
        window_name = 'tracking'
        wait_delay = math.floor((1 / fps)*1000)

        # Create default detection params
        params = cv.aruco.DetectorParameters_create()

        # Setup live video stream
        cap = cv.VideoCapture(camera_id)

        # Setup tracking preview window
        cv.namedWindow(window_name)

        while True:
            if self._failed_reads >= self._failed_read_threshold:
                return types.Error('Too many failed frame reads')

            ok, frame = cap.read()
            if not ok:
                # We don't immediatly quit this loop. We return with an
                # error when the treshold is reached
                self._failed_reads += 1
                continue

            # Detect the markers
            corners, ids, rejected = cv.aruco.detectMarkers(frame, self._dict, parameters=params)
            # Next publish to all subscribers
            print(corners, ids, rejected)

            # Preview the frame
            cv.imshow(window_name, frame)

            if wait.wait_or_exit(wait_delay):
                break

        # Cleanup
        cap.release()
        cv.destroyAllWindows()

    def run_threaded():
        pass

    def subscribe():
        pass

    def unsubscribe():
        pass
