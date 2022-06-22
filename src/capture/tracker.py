from typing import List, Tuple
from queue import Queue
import cv2 as cv
import threading
import math

from renderer.debug import DebugRenderer
import config.config as config
import capture.aruco as aruco
import utils.wait as wait
import utils.fmt as fmt

from typings.capture.aruco import (
    MarkerBordersList,
    MarkerCenterList,
    Subscription,
    CornerList,
    Corners,
    IDList,
)
from typings.error import Err, Error


class Tracker:
    '''
    This class describes a tracker which is able to track ArUco markers.
    '''

    def __init__(self, cfg: config.Config, force_debug: bool = False) -> None:
        typ = aruco.type_from(
            cfg['capture']['aruco']['size'],
            cfg['capture']['aruco']['uniques']
        )
        t, ok = aruco.dict_from(typ)
        if not ok:
            raise Exception('Failed to instantiate Tracker object')

        # These values keep track how many frames failed to read
        self._max_failed_read = cfg['capture']['tracker']['max_failed_read']
        self._failed_reads = 0

        # ArUco marker related values
        self._dict = cv.aruco.Dictionary_get(t)
        self._path = cfg['capture']['path']
        self._type = t

        # Tracking
        self._delay = fmt.fps_to_ms(cfg['capture']['fps'])
        self._camera_id = cfg['capture']['camera_id']
        self._subscribers: List[Queue] = []

        # Dimensions
        self._frame_height = 0
        self._frame_width = 0

        # Misc
        self._running = False
        self._thread = None

        # Debugging
        self._debug = cfg['capture']['tracker']['debug']

        # Check if the user forces debug
        if force_debug:
            self._debug = True

    def _setup(self) -> Tuple[any, any]:
        '''
        Setup ArUco detection params, capture device and wait delay.

        Returns
        -------
        values : Tuple[any, any, int]
            The capture device, ArUco detection params and wait delay
        '''
        params = cv.aruco.DetectorParameters_create()
        cap = cv.VideoCapture(self._camera_id)
        cap.set(cv.CAP_PROP_AUTOFOCUS, 0)
        cap.set(cv.CAP_PROP_AUTO_WB, 0)
        cap.set(cv.CAP_PROP_FRAME_HEIGHT, self._frame_height)
        cap.set(cv.CAP_PROP_FRAME_WIDTH, self._frame_width)

        # Retrieve frame height and width
        self._frame_height = int(cap.get(cv.CAP_PROP_FRAME_HEIGHT))
        self._frame_width = int(cap.get(cv.CAP_PROP_FRAME_WIDTH))

        return cap, params

    def _transform_markers_to_center(self, corner_list: CornerList, ids: IDList) -> MarkerCenterList:
        '''
        This functions transforms the list or corners and the list of IDs into a combined list of tuples consisting
        of the center position <x,y>, the rotation angle and the ID.

        Parameters
        ----------
        corner_list : CornerList
            A lsit of corners
        ids : IDList
            A list of IDs

        Returns
        -------
        marker_list : MarkerCenterList
            A list of markers
        '''
        marker_list: MarkerCenterList = []
        for i, corners_per_marker in enumerate(corner_list):
            if len(corners_per_marker[0]) != 4:
                continue

            pos = self._extract_center_position(corners_per_marker[0])
            ang = self._extract_angle(corners_per_marker[0], pos)
            marker_list.append((pos, ang, ids[i][0]))

        return marker_list

    def _transform_markers_to_borders(self, corner_list: CornerList, ids: IDList) -> MarkerBordersList:
        ''''''
        marker_list: MarkerBordersList = []
        for i, corners_per_marker in enumerate(corner_list):
            if len(corners_per_marker[0]) != 4:
                continue

            center = self._extract_center_position(corners_per_marker[0])
            angle = self._extract_angle(corners_per_marker[0], center)
            borders = self._extract_borders(corners_per_marker[0])
            marker_list.append((borders, center, angle, ids[i][0]))

        return marker_list

    def _extract_center_position(self, corners: Corners) -> Tuple[int, int]:
        ''''''
        center_x = int((corners[0][0] + corners[2][0]) / 2)
        center_y = int((corners[0][1] + corners[2][1]) / 2)

        return center_x, center_y

    def _extract_borders(
        self,
        corners: Corners
    ) -> Tuple[Tuple[int, int], Tuple[int, int], Tuple[int, int], Tuple[int, int]]:
        ''''''
        (tl, tr, br, bl) = corners
        # NOTE (Techassi): This is giga ugly but I don't know of a better way to achieve this
        return (int(tl[0]), int(tl[1])), (int(tr[0]), int(tr[1])), (int(br[0]), int(br[1])), (int(bl[0]), int(bl[1]))

    def _extract_angle(self, corners: Corners, center: Tuple[int, int]) -> float:
        '''
        Extract the angle from a single marker. The angle gets calculated by first calculating the vector between the
        center position and the top left corner position. Then we calculate the length to then calculate the unit vector
        which then can be used to calculate the angle by using arcsin.
        '''
        x, y = center[0] - corners[0][0], center[1] - corners[0][1]  # Vec from center to top left corner
        len = math.sqrt(math.pow(x, 2) + math.pow(y, 2))  # Calculate length of vec
        deg = math.degrees(math.asin(y / len))  # Use unit vec to calculate angle
        return deg

    def _run(self) -> Error:
        '''
        Run the main tracking loop. This sets up the ArUco detection params, the video capture and starts tracking.

        Returns
        -------
        err : Error
            Non None if an error occured
        '''
        self._running = True

        # Setup video capture and ArUco detection params
        cap, params = self._setup()

        while self._running:
            if self._failed_reads >= self._max_failed_read:
                return Err('Too many failed frame reads')

            ok, frame = cap.read()
            if not ok:
                # We don't immediatly quit this loop. We return with an
                # error when the treshold is reached
                self._failed_reads += 1
                continue

            # Gray-scale frame
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)

            # Detect the markers
            corners, ids, _ = cv.aruco.detectMarkers(frame, self._dict, parameters=params)
            if len(corners) > 0:
                markers = self._transform_markers_to_center(corners, ids)
                self.notify(markers)

        # Cleanup
        cap.release()

    def _run_debug(self) -> Error:
        '''
        Run in debug mode.

        Returns
        -------
        err : Error
            Non None if an error occured
        '''
        self._running = True

        # Setup video capture and ArUco detection params
        cap, params = self._setup()
        debug_renderer = DebugRenderer()

        while self._running:
            ok, frame = cap.read()
            if not ok:
                continue

            # Detect the markers
            corners, ids, rejected = cv.aruco.detectMarkers(frame, self._dict, parameters=params)
            if len(corners) > 0:
                markers = self._transform_markers_to_borders(corners, ids)
                debug_renderer.render(markers, frame)

            cv.imshow('tracking-debug', frame)

            if wait.wait_or(self._delay):
                break

        # Cleanup
        cv.destroyAllWindows()
        cap.release()

    def start(self) -> Error:
        '''
        Start the main tracking loop. This sets up the ArUco detection params, the video capture and starts tracking.

        Returns
        -------
        err : Error
            Non None if an error occured
        '''
        if self._running:
            return Err('Already running')

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

    def notify(self, markers: MarkerCenterList):
        '''
        Notify subscribers with detected markers.

        Parameters
        ----------
        corners : CornerList
            A list of detected markers
        '''
        for sub in self._subscribers:
            sub.put(markers)

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

    def unsubscribe(self, index: int) -> Error:
        '''
        External subscribers can unsubscribe from this tracker.

        Parameters
        ----------
        index : int
            The subscription ID

        Returns
        -------
        err : Error
            Non None if an error occured
        '''
        if index < 0 or index > len(self._subscribers) - 1:
            return Err('Invalid index')

        self._subscribers.pop(index)
        return None
