import cv2 as cv


def wait_or(d: int, key: str = 'q') -> bool:
    # Fallback to 16 ms => 60 FPS
    if d <= 0:
        d = 16

    code = cv.waitKey(d)
    if code == ord(key):
        return True

    return False
