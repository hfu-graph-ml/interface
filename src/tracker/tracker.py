from typing import List
from queue import Queue
import cv2 as cv
import threading
import math

import config.config as config
import tracker.aruco as aruco
import utils.wait as wait

from .types import CornerList, Subscription, TrackingError, IDList


class Tracker:
    '''
    This class describes a tracker which is able to track ArUco markers.
    '''

    def __init__(self, cfg: config.TrackerOptions) -> None:
        typ = aruco.type_from(cfg['size'], cfg['uniques'])
        t, ok = aruco.dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Tracker object')

        # These values keep track how many frames failed to read
        self._failed_read_threshold = cfg['failed_read_threshold']
        self._failed_reads = 0

        # ArUco marker related values
        self._dict = cv.aruco.Dictionary_get(t)
        self._type = t

        # Tracking handling
        self._subscribers: List[Queue] = []

        # Misc
        self._debug = cfg['debug']
        self._path = cfg['path']
        self._running = False
        self._thread = None

    def _start(self, camera_id: int, fps: int) -> TrackingError:
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
            return TrackingError('Already running')

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
                return TrackingError('Too many failed frame reads')

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

        # Cleanup
        cap.release()

    def start(self, camera_id: int, fps: int) -> TrackingError:
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
            return TrackingError('Already running')

        # Construct a new thread
        t = threading.Thread(None, self._start, 'tracking-thread', (camera_id, fps))
        self._thread = t
        t.start()

        return None

    def stop(self):
        ''''''
        if not self._running:
            return

        self._running = False
        self._thread.join()

    def notify(self, corners: CornerList, ids: IDList):
        ''''''
        for sub in self._subscribers:
            sub.put((corners, ids))

    def subscribe(self) -> Subscription:
        ''''''
        q = Queue()
        self._subscribers.append(q)

        return (len(self._subscribers) - 1, q.get)

    def unsubscribe(self, index: int) -> TrackingError:
        ''''''
        if index < 0 or index > len(self._subscribers) - 1:
            return TrackingError('Invalid index')

        self._subscribers.pop(index)
        return None
