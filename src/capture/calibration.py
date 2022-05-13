import cv2 as cv
import click
import time
import os

import config.config as config
import utils.wait as wait
import utils.fmt as fmt


class Calibration:
    '''
    This class describes the calibration which is required to calculate the intrisic camera matrix to apply a projection
    transform when rendering.
    '''

    def __init__(self, cfg: config.Config) -> None:
        self._number_images = cfg['capture']['calibration']['number_images']
        self._delay = fmt.fps_to_ms(cfg['capture']['fps'])
        self._camera_id = cfg['capture']['camera_id']
        self._path = cfg['capture']['path']
        self._frames = []

    def _save_images(self):
        '''
        Save the stored frames as images.
        '''
        save_path = os.path.join(self._path, 'images')
        if not os.path.exists(save_path):
            os.makedirs(save_path)

        for i, frame in enumerate(self._frames):
            img_name = 'img-{:02d}.png'.format(i)
            img_path = os.path.join(save_path, img_name)
            cv.imwrite(img_path, frame)

    def _capture(self):
        '''
        Capture images from camera and save them afterwards.
        '''
        cap = cv.VideoCapture(self._camera_id)

        n = 0
        while n < self._number_images:
            ok, frame = cap.read()
            if not ok:
                click.echo('Failed to read the frame')
                break

            self._frames.append(frame)
            n += 1
            time.sleep(0.5)

        cap.release()
        self._save_images()

    def _capture_manual(self):
        '''
        Capture images from camera and save them afterwards. This function waits for user input.
        '''
        window_name = 'calibration-preview'
        cap = cv.VideoCapture(self._camera_id)
        cv.namedWindow(window_name)

        n = 0
        while n < self._number_images:
            ok, frame = cap.read()
            if not ok:
                click.echo('Failed to read the frame')
                break

            cv.imshow(window_name, frame)

            i = wait.multi_wait_or(self._delay, 'q', 'n')
            if i == -1:
                continue

            if i == 1:
                self._frames.append(frame)
                n += 1
                continue

            break

        cv.destroyAllWindows()
        cap.release()
        self._save_images()

    def calibrate_auto(self):
        ''''''
        self._capture()

    def calibrate_manual(self):
        '''
        Calibrate the camera manually by capturing a specified number of images.
        '''
        self._capture_manual()
