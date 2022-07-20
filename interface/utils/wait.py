import cv2 as cv


def wait_or(d: int, key: str = 'q') -> bool:
    code = cv.waitKey(d)
    if code == ord(key):
        return True

    return False


def multi_wait_or(d: int, *keys: str) -> int:
    code = cv.waitKey(d)
    for i, key in enumerate(keys):
        if code == ord(key):
            return i
    return -1
