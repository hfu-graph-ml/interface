from typing import List, Tuple
from queue import Queue
import cv2 as cv
import threading
import math

from renderer.debug import DebugRenderer
import config.config as config
import tracker.aruco as aruco
import utils.wait as wait

from .types import CornerList, Subscription, TrackingError, IDList


class Tracker:
    '''
    This class describes a tracker which is able to track ArUco markers.
    '''

    def __init__(
        self,
        tracker_options: config.TrackerOptions,
        capture_options: config.CaptureOptions,
        force_debug: bool = False
    ) -> None:
        typ = aruco.type_from(tracker_options['size'], tracker_options['uniques'])
        t, ok = aruco.dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Tracker object')

        # These values keep track how many frames failed to read
        self._max_failed_read = tracker_options['max_failed_read']
        self._failed_reads = 0

        # ArUco marker related values
        self._dict = cv.aruco.Dictionary_get(t)
        self._path = tracker_options['path']
        self._type = t

        # Tracking
        self._camera_id = capture_options['camera_id']
        self._subscribers: List[Queue] = []
        self._fps = capture_options['fps']

        # Misc
        self._running = False
        self._thread = None

        # Debugging
        self._debug = tracker_options['debug']

        # Check if the user forces debug
        if force_debug:
            self._debug = True

    def _setup(self) -> Tuple[any, any, int]:
        ''''''
        params = cv.aruco.DetectorParameters_create()
        delay = math.floor((1 / self._fps)*1000)
        cap = cv.VideoCapture(self._camera_id)

        return cap, params, delay

    def _run(self) -> TrackingError:
        '''
        Run the main tracking loop. This sets up the ArUco detection params, the video capture and starts tracking.

        Parameters
        ----------
        camera_id : int
            The camera ID (Usually 0)

        Returns
        -------
        err : types.Error
            Non None if an error occured
        '''
        self._running = True

        # Setup video capture and ArUco detection params
        cap, params, _ = self._setup()

        while self._running:
            if self._failed_reads >= self._max_failed_read:
                return TrackingError('Too many failed frame reads')

            ok, frame = cap.read()
            if not ok:
                # We don't immediatly quit this loop. We return with an
                # error when the treshold is reached
                self._failed_reads += 1
                continue

            # Detect the markers
            corners, ids, _ = cv.aruco.detectMarkers(frame, self._dict, parameters=params)
            if len(corners) > 0:
                self.notify(corners, ids)

        # Cleanup
        cap.release()

    def _run_debug(self) -> TrackingError:
        ''''''
        self._running = True

        # Setup video capture and ArUco detection params
        cap, params, delay = self._setup()
        debug_renderer = DebugRenderer()

        while self._running:
            ok, frame = cap.read()
            if not ok:
                continue

            # Detect the markers
            corners, ids, rejected = cv.aruco.detectMarkers(frame, self._dict, parameters=params)
            if len(corners) > 0:
                debug_renderer.render(corners, ids, frame)

            cv.imshow('tracking-debug', frame)

            if wait.wait_or_exit(delay):
                break

        # Cleanup
        cv.destroyAllWindows()
        cap.release()

    def start(self) -> TrackingError:
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

        if self._debug:
            return self._run_debug()

        # Construct a new thread
        t = threading.Thread(None, self._run, 'tracking-thread')
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

        return len(self._subscribers) - 1, q.get

    def unsubscribe(self, index: int) -> TrackingError:
        ''''''
        if index < 0 or index > len(self._subscribers) - 1:
            return TrackingError('Invalid index')

        self._subscribers.pop(index)
        return None
