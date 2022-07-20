import math


def host_port_from(host: str, port: int, secure: bool = False) -> str:
    '''
    Creates a http(s)://<host>:<port> string.

    Args:
        host: The IP address or domain of the host.
        port: Port number.
        secure: If True https:// is prefixed, otherwise http://.

    Returns:
        The http(s)://<host>:<port> string.
    '''
    if not host:
        return ''

    if port < 1 or port > 65535:
        return ''

    if secure:
        return f'https://{host}:{port}'

    return f'http://{host}:{port}'


def url_from(base: str, paths: tuple) -> str:
    '''
    Creates a complete URL with 'base' as the base url and each provided 'path' appended with a /.

    Args:
        base: The base URL.
        paths: A variable number of path segments.

    Returns:
        Complete URL.
    '''
    url = base
    for p in paths:
        p = p.replace('/', '')
        url = '/'.join([url, p.lower()])

    return url


def fps_to_ms(fps: int) -> int:
    '''
    Convert FPS to a millisecond interval.

    Args:
        fps: Input FPS as integer.

    Returns:
        Interval in milliseconds as integer number.
    '''
    return math.floor((1 / fps) * 1000)
