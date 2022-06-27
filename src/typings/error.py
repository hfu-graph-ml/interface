from typing import Generic, TypeVar

R = TypeVar('R')
E = TypeVar('E')


class Error:
    def __init__(self, msg: str) -> None:
        self._message = msg

    def string(self) -> str:
        return self._message


class Result(Generic[R, E]):
    def __init__(self, res: R = None, err: E = None) -> None:
        self._res = res
        self._err = err

    def is_ok(self) -> bool:
        return self._res != None

    def is_err(self) -> bool:
        return self._err != None

    def unpack(self) -> R:
        return self._res

    def error(self) -> E:
        return self._err


def Ok(res: R) -> Result[R, E]:
    return Result[R, E](res)


def Err(err: E) -> Result[R, E]:
    return Result[E, R](None, err)
