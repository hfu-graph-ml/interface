import cv2 as cv


def wait_or(d: int, key: str = 'q') -> bool:
    '''
    Wait or do when `key` is pressed.

    Args:
        d: Duration to wait in milliseconds.
        key: Key press to wait for.

    Returns:
        pressed: Returns True if `key` was pressed, False otherwise.
    '''
    code = cv.waitKey(d)
    if code == ord(key):
        return True

    return False


def multi_wait_or(d: int, *keys: str) -> int:
    '''
    Wait or do with multiple keys.

    Args:
        d: Duration to wait in milliseconds.
        keys: Keys to listen for.

    Returns:
        pressed: Returns index > 0 if one of the provided keys were pressed, -1 otherwise.
    '''
    code = cv.waitKey(d)
    for i, key in enumerate(keys):
        if code == ord(key):
            return i
    return -1
