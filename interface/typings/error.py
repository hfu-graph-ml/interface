from typing import Generic, TypeVar

R = TypeVar('R')
E = TypeVar('E')


class Error:
    '''
    This is a generic error class.
    '''

    def __init__(self, msg: str) -> None:
        self._message = msg

    def string(self) -> str:
        '''
        Returns the error message as a string.
        '''
        return self._message


class Result(Generic[R, E]):
    '''
    Result represents either `R` when there was no error or `E` when there was.
    '''

    def __init__(self, res: R = None, err: E = None) -> None:
        self._res = res
        self._err = err

    def is_ok(self) -> bool:
        '''
        Returns if the result is okay.
        '''
        return self._res != None

    def is_err(self) -> bool:
        '''
        Returns if the result is an error.
        '''
        return self._err != None

    def unwrap(self) -> R:
        '''
        Unpacks the the result. The user should check with `is_ok` before unpacking the result as this function will
        throw an exception.
        '''
        if self._res == None or self._err != None:
            raise Exception('Cannot unpack None result')

        return self._res

    def error(self) -> E:
        '''
        Returns the error if present otherwise `None`.
        '''
        return self._err


def Ok(res: R) -> Result[R, E]:
    return Result[R, E](res)


def Err(err: E) -> Result[R, E]:
    return Result[E, R](None, err)
