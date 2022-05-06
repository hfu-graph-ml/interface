from typing import List, Tuple
from queue import Queue
import cv2 as cv
import threading
import itertools
import math

from renderer.debug import DebugRenderer
import config.config as config
import tracker.aruco as aruco
import utils.wait as wait

from .types import CornerList, Subscription, TrackerError, IDList


class Tracker:
    '''
    This class describes a tracker which is able to track ArUco markers.
    '''

    def __init__(self, cfg: config.Config, force_debug: bool = False) -> None:
        typ = aruco.type_from(cfg['tracker']['size'], cfg['tracker']['uniques'])
        t, ok = aruco.dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Tracker object')

        # These values keep track how many frames failed to read
        self._max_failed_read = cfg['tracker']['max_failed_read']
        self._failed_reads = 0

        # ArUco marker related values
        self._dict = cv.aruco.Dictionary_get(t)
        self._path = cfg['tracker']['path']
        self._type = t

        # Tracking
        self._camera_id = cfg['capture']['camera_id']
        self._subscribers: List[Queue] = []
        self._fps = cfg['capture']['fps']

        # Dimensions
        self._frame_height = 0
        self._frame_width = 0

        # Misc
        self._running = False
        self._thread = None

        # Debugging
        self._debug = cfg['tracker']['debug']

        # Check if the user forces debug
        if force_debug:
            self._debug = True

    def _setup(self) -> Tuple[any, any, int]:
        '''
        Setup ArUco detection params, capture device and wait delay.

        Returns
        -------
        values : Tuple[any, any, int]
            The capture device, ArUco detection params and wait delay
        '''
        params = cv.aruco.DetectorParameters_create()
        delay = math.floor((1 / self._fps)*1000)
        cap = cv.VideoCapture(self._camera_id)

        # Retrieve frame height and width
        self._frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        self._frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))

        return cap, params, delay

    def _run(self) -> TrackerError:
        '''
        Run the main tracking loop. This sets up the ArUco detection params, the video capture and starts tracking.

        Returns
        -------
        err : TrackerError
            Non None if an error occured
        '''
        self._running = True

        # Setup video capture and ArUco detection params
        cap, params, _ = self._setup()

        while self._running:
            if self._failed_reads >= self._max_failed_read:
                return TrackerError('Too many failed frame reads')

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

    def _run_debug(self) -> TrackerError:
        '''
        Run in debug mode.

        Returns
        -------
        err : TrackerError
            Non None if an error occured
        '''
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
                ids = list(itertools.chain.from_iterable(ids))
                debug_renderer.render(corners, ids, frame)

            cv.imshow('tracking-debug', frame)

            if wait.wait_or_exit(delay):
                break

        # Cleanup
        cv.destroyAllWindows()
        cap.release()

    def start(self) -> TrackerError:
        '''
        Start the main tracking loop. This sets up the ArUco detection params, the video capture and starts tracking.

        Returns
        -------
        err : TrackerError
            Non None if an error occured
        '''
        if self._running:
            return TrackerError('Already running')

        if self._debug:
            return self._run_debug()

        # Construct a new thread
        t = threading.Thread(None, self._run, 'tracking-thread')
        self._thread = t
        t.start()

        return None

    def stop(self):
        '''
        Stop the tracker. This stops the tracking loop and joins the thread to wait until it terminates.
        '''
        if not self._running:
            return

        self._running = False
        self._thread.join()

    def notify(self, corners: CornerList, ids: IDList):
        '''
        Notify subscribers with detected markers.

        Parameters
        ----------
        corners : CornerList
            A list of detected corners
        ids : IDList
            A list of IDs
        '''
        ids = list(itertools.chain.from_iterable(ids))
        for sub in self._subscribers:
            sub.put((corners, ids))

    def subscribe(self) -> Subscription:
        '''
        External consumers can subscribe to this tracker to get real-time marker positions.

        Returns
        -------
        subscription : Subscription
            A tuple with the subscription ID and the retrieve function
        '''
        q = Queue()
        self._subscribers.append(q)

        return len(self._subscribers) - 1, (self._frame_width, self._frame_height), q.get

    def unsubscribe(self, index: int) -> TrackerError:
        '''
        External subscribers can unsubscribe from this tracker.

        Parameters
        ----------
        index : int
            The subscription ID

        Returns
        -------
        err : TrackerError
            Non None if an error occured
        '''
        if index < 0 or index > len(self._subscribers) - 1:
            return TrackerError('Invalid index')

        self._subscribers.pop(index)
        return None
