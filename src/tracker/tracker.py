from typing import Callable, List, Tuple, TypeAlias
import cv2 as cv
import threading
import math

import config.config as config
import tracker.types as types
import utils.wait as wait

Corners: TypeAlias = List[List[List[int]]]
CornerList: TypeAlias = Tuple[Corners, ...]
IDList: TypeAlias = List[List[int]]

Callback: TypeAlias = Callable[[CornerList, IDList], None]


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

        # Event handling
        self._subscribers: List[Callback]

        # Misc
        self._debug = cfg['debug']
        self._path = cfg['path']
        self._running = False
        self._thread = None

    def calibrate():
        pass

    def start(self, camera_id: int, fps: int) -> types.Error:
        '''
        Start the main tracking loop. This sets up the ArUco detection params, the video capture and starts tracking.

        Parameters
        ----------
        camera_id : int
            The camera ID (Usually 0)
        fps : int
            The time we wait between each frame

        Returns
        -------
        err : types.Error
            Non None if an error occured
        '''
        if self._running:
            return types.Error('Already running')

        self._running = True

        window_name = 'tracking'
        wait_delay = math.floor((1 / fps)*1000)

        # Create default detection params
        params = cv.aruco.DetectorParameters_create()

        # Setup live video stream
        cap = cv.VideoCapture(camera_id)

        # Setup tracking preview window
        if self._debug:
            cv.namedWindow(window_name)

        while self._running:
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
            if len(corners) > 0:
                self.notify(corners, ids)

            # Preview the frame
            if self._debug:
                cv.imshow(window_name, frame)

            if wait.wait_or_exit(wait_delay):
                break

        # Cleanup
        cap.release()

        if self._debug:
            cv.destroyAllWindows()

    def run_threaded(self, camera_id: int, fps: int) -> types.Error:
        ''''''
        if self._running:
            return types.Error('Already running')

        # Construct a new thread
        t = threading.Thread(None, self.start, 'tracking-thread', (camera_id, fps))
        self._thread = t
        t.start()

        return None

    def stop(self):
        ''''''
        if not self._running:
            return

        self._running = False

        if self._thread != None:
            self._thread.join()

    def notify(self, corners: CornerList, ids: IDList):
        ''''''
        for sub in self._subscribers:
            sub(corners, ids)

    def subscribe(self, func: Callback):
        ''''''
        self._subscribers.append(func)
        pass

    def unsubscribe():
        ''''''
        pass
