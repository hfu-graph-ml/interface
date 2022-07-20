from typing import List, Tuple
from queue import Queue
import numpy as np
import cv2 as cv
import threading
import math

from config.config import Config
import capture.aruco as aruco
import utils.fmt as fmt

from typings.capture.calibration import CharucoCalibrationData
from typings.capture.aruco import (
    MarkerBordersList,
    MarkerCenterList,
    RawSubscription,
    Subscription,
    Subscriber,
    CornerList,
    Corners,
    IDList,
)
from typings.error import Err, Error


class Tracker:
    '''
    This class describes a tracker which is able to track ArUco markers.
    '''

    def __init__(self, cfg: Config, calib_data: CharucoCalibrationData) -> None:
        '''
        Create a new tracker instance.

        Args:
            cfg: Configuration data.
            calib_data: Camera calibration data.
        '''
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
        self._board = aruco.board_from(3, 3, self._dict, marker_length=0.09, marker_separation=0.01)
        self._path = cfg['capture']['path']
        self._type = t

        # Tracking
        self._delay = fmt.fps_to_ms(cfg['capture']['fps'])
        self._camera_id = cfg['capture']['camera_id']
        self._subscribers: List[Subscriber] = []
        self.found_rect = False

        # Current frames
        self._color_frame = np.array([])
        self._frame = np.array([])

        # Dimensions
        self._frame_height = 0
        self._frame_width = 0

        # Misc
        self._calib = calib_data
        self._running = False
        self._thread = None

    def _setup(self) -> Tuple[any, any]:
        '''
        Setup ArUco detection params, capture device and wait delay.

        Returns:
            The capture device, ArUco detection params and wait delay.
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

    def _is_running(self) -> bool:
        '''
        Returns if the renderer is already running.

        Returns:
            If renderer is running.
        '''
        if self._running:
            return True

        self._running = True
        return False

    def _transform_markers_to_center(self, corner_list: CornerList, ids: IDList) -> MarkerCenterList:
        '''
        This functions transforms the list or corners and the list of IDs into a combined list of tuples consisting
        of the center position <x,y>, the rotation angle and the ID.

        Args:
            corner_list: A list of corners.
            ids: A list of IDs.

        Returns:
            A list of markers.
        '''
        marker_list: MarkerCenterList = []
        for i, corners_per_marker in enumerate(corner_list):
            if len(corners_per_marker[0]) != 4:
                continue

            center = self._extract_center_position(corners_per_marker[0])
            angle = self._extract_angle(corners_per_marker[0], center)
            marker_list.append((center, angle, ids[i][0]))

        return marker_list

    def _transform_markers_to_borders(self, corner_list: CornerList, ids: IDList) -> MarkerBordersList:
        '''
        This functions transforms the list or corners and the list of IDs into a combined list of tuples consisting
        of corner positions <x,y>, the center position <x,y>, the rotation angle and the ID.

        Args:
            corner_list: A list of corners.
            ids: A list of IDs.

        Returns:
            A list of markers.
        '''
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
        '''
        Extract the marker center position based on the top-left and bottom-right corner.

        Args:
            corners: List or corners.

        Returns:
            Marker center position (x,y).
        '''
        center_x = int((corners[0][0] + corners[2][0]) / 2)
        center_y = int((corners[0][1] + corners[2][1]) / 2)

        return center_x, center_y

    def _extract_borders(
        self,
        corners: Corners
    ) -> Tuple[
        Tuple[int, int],
        Tuple[int, int],
        Tuple[int, int],
        Tuple[int, int]
    ]:
        '''
        Extract marker corners. Basically this function only converts the position values from floats to integers.

        Args:
            corners: List of corners.

        Returns:
            A 4-tuple of corner positions (x,y).
        '''
        (tl, tr, br, bl) = corners
        # NOTE (Techassi): This is giga ugly but I don't know of a better way to achieve this
        return (int(tl[0]), int(tl[1])), (int(tr[0]), int(tr[1])), (int(br[0]), int(br[1])), (int(bl[0]), int(bl[1]))

    def _extract_angle(self, corners: Corners, center: Tuple[int, int]) -> float:
        '''
        Extract the angle from a single marker. The angle gets calculated by first calculating the vector between the
        center position and the top left corner position. Then we calculate the length to then calculate the unit vector
        which then can be used to calculate the angle by using arcsin.

        Args:
            corners: List of corners.
            center: Marker center position (x,y).

        Returns:
            The calculated angle of the marker.
        '''
        x, y = center[0] - corners[0][0], center[1] - corners[0][1]  # Vec from center to top left corner
        len = math.sqrt(math.pow(x, 2) + math.pow(y, 2))  # Calculate length of vec
        deg = math.degrees(math.asin(y / len))  # Use unit vec to calculate angle
        return deg

    def _run(self) -> Error:
        '''
        Run the main tracking loop. This sets up the ArUco detection params, the video capture and starts tracking.

        Returns:
            Non None if an error occured.
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

            self._color_frame = frame
            frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            self._frame = frame

            # Detect the markers
            corners, ids, rejected = cv.aruco.detectMarkers(frame, self._dict, parameters=params)

            # Refine markers
            corners, ids, rejected, recovered = cv.aruco.refineDetectedMarkers(
                frame, self._board, corners, ids, rejected,
                cameraMatrix=self._calib[0],
                distCoeffs=self._calib[1]
            )

            if len(corners) > 0:
                self.notify(corners, ids, rejected, recovered)

        # Cleanup
        cap.release()

    def get_frame(self) -> Tuple[bool, cv.Mat]:
        '''
        Get the current gray scale frame from the tracker.

        Returns:
            ok: If current frame is available.
            frame: Current frame.
        '''
        return self._frame.any(), self._frame

    def get_color_frame(self) -> Tuple[bool, cv.Mat]:
        '''
        Get the current color frame from the tracker.

        Returns:
            ok: If current frame is available.
            frame: Current frame.
        '''
        return self._frame.any(), self._color_frame

    def start(self) -> Error:
        '''
        Start the main tracking loop. This sets up the ArUco detection params, the video capture and starts tracking.

        Returns:
            Non None if an error occured.
        '''
        if self._is_running():
            return Err('Already running')

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

    def notify(self, corners: CornerList, ids: IDList, rejected, recovered):
        '''
        Notify subscribers with detected markers.

        Args:
            corners: A list of corners of detected markers.
            ids: A list of recovered markers.
        '''
        for sub in self._subscribers:
            # If the subription is raw, just pass raw values without any processing
            if sub[0]:
                sub[1].put((corners, ids, rejected, recovered))
            else:
                markers = self._transform_markers_to_borders(corners, ids)
                sub[1].put(markers)

    def subscribe(self, size: int) -> Subscription:
        '''
        External consumers can subscribe to this tracker to get real-time marker positions.

        Returns:
            subscription: A tuple consisting of the subscription ID, frame widht and height and the retrieve function.
        '''
        q = Queue(size)
        self._subscribers.append((False, q))

        return len(self._subscribers) - 1, (self._frame_width, self._frame_height), q.get

    def subscribe_raw(self, size: int) -> RawSubscription:
        '''
        External consumers can subscribe to this tracker to get real-time marker positions. This returns raw tracking
        data instead of cleaned data via the `subscribe` method.

        Returns:
            subscription: A tuple consisting of the subscription ID, frame widht and height and the retrieve function.
        '''
        q = Queue(size)
        self._subscribers.append((True, q))

        return len(self._subscribers) - 1, (self._frame_width, self._frame_height), q.get

    def unsubscribe(self, index: int) -> Error:
        '''
        External subscribers can unsubscribe from this tracker.

        Args:
            index: The subscription ID.

        Returns:
            Non None if an error occured.
        '''
        if index < 0 or index > len(self._subscribers) - 1:
            return Err('Invalid index')

        self._subscribers.pop(index)
        return None
