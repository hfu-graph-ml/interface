from typings.capture import MarkerBordersList

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
        # The corner list is a three dimensional array The dimensions are:
        # 1. A list of all corners for every marker
        # 2. A list or 4 corners per marker
        # 3. A list with two elements: the X and Y position of one corner

        # We access corners[0] as we are only interested in the list of corners
        for marker in markers:
            self._draw_borders(marker[0], frame)
            self._draw_center_point(marker[1], marker[3], frame)
