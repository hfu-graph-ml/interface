from .shared import Shared


class DebugRenderer(Shared):
    '''
    This class decribes a debug renderer used to draw tracking information for debug purposes.
    '''

    def render(self, corners: list, ids: list, frame: any):
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
        for i, corners_per_marker in enumerate(corners):
            if len(corners_per_marker[0]) != 4:
                continue

            self._draw_center_point(corners_per_marker[0], ids[i], frame)
            self._draw_borders(corners_per_marker[0], frame)
