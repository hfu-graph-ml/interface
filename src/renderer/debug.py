from typings.capture.aruco import MarkerBordersList

from .shared import Shared


class DebugRenderer(Shared):
    '''
    This class decribes a debug renderer used to draw tracking information for debug purposes.
    '''

    def render(self, markers: MarkerBordersList, frame: any):
        '''
        Render the detected markers (corners) in the 'frame'.

        Parameters
        ----------
        corners : list
            A list or corners
        ids : list
            A list of IDs
        frame : any
            The frame to draw in
        '''
        for marker in markers:
            self._draw_borders(marker[0], frame)
            self._draw_angle(marker[0], marker[2], frame)
            self._draw_center_point(marker[1], marker[3], frame, with_text=False)
