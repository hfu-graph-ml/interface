def confirmation_prompt(text: str, default: bool | None = False) -> bool:
    '''
    This displays a confirmation prompt in which the user has to select 'y' or 'n'.

    Parameters
    ----------
    text : str
        The text message to display
    default : bool | None
        The default value returned. If None the user HAS to select either 'y' or 'n'

    Returns
    -------
    result : bool
        True if input is 'y' or False if input is 'n'
    '''
    valid = False
    text = '{} [{}]: '.format(text, "y/n" if default is None else ("Y/n" if default else "y/N"))

    while not valid:
        inp = input(text).lower()

        if inp == '' and default != None:
            return default

        valid = inp in ['y', 'n']

    return inp == 'y'
