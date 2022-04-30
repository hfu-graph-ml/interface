def host_port_from(host: str, port: int, secure: bool = False) -> str:
    '''
    Creates a http(s)://<host>:<port> string.

    Parameters
    ----------
    host : str
        The IP address or domain of the host
    port : int
        Port number
    secure : bool
        If True https:// is prefixed, otherwise http://

    Returns
    -------
    host_port : str
        The http(s)://<host>:<port> string
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

    Parameters
    ----------
    base : str
        The base URL
    paths: tuple[str, ...]
        A variable number of path segments

    Returns
    -------
    url : string
        Complete URL
    '''
    url = base
    for p in paths:
        p = p.replace('/', '')
        url = '/'.join([url, p.lower()])

    return url
