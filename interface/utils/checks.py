def is_in(v: any, l: list) -> bool:
    '''
    Returns if 'v' is in 'l'.

    Args:
        v: Value to check.
        l: List of values to check against.

    Returns:
        If 'v' is in 'l'.
    '''
    return v in l


def is_between(v: int | float, s: int | float, e: int | float, inclusive: bool = False) -> bool:
    '''
    Returns if 'v' is between 's' and 'e'. If 'inclusive' is True 's' and 'e' are inclusive.

    Args:
        v: Value to check.
        s: Start value.
        e: End value.

    Returns:
        If 'v' is between 's' and 'e'.
    '''
    if inclusive:
        return v >= s and v <= e

    return v > s and v < e
