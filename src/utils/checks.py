def is_in(v: any, l: list) -> bool:
    '''
    Returns if 'v' is in 'l'.

    Parameters
    ----------
    v : any
        Value to check
    l : list
        List of values to check against

    Returns
    -------
    is_in : bool
        If 'v' is in 'l'
    '''
    return v in l


def is_between(v: int | float, s: int | float, e: int | float, inclusive: bool = False) -> bool:
    '''
    Returns if 'v' is between 's' and 'e'. If 'inclusive' is True 's' and 'e' are inclusive.

    Parameters
    ----------
    v : int | float
        Value to check
    s : int | float
        Start value
    e : int | float
        End value

    Returns
    -------
    is_between : bool
        If 'v' is between 's' and 'e'
    '''
    if inclusive:
        return v >= s and v <= e

    return v > s and v < e
