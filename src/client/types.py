from typing import Literal, TypedDict

from models.graph import Graph

Status = Literal['success', 'error']


class RequestResult:
    _is_error: bool
    _message: str
    _status: int
    _data: dict

    def __init__(self, data: dict, status: int, message: str, is_error: bool = False) -> None:
        self._is_error = is_error
        self._message = message
        self._status = status
        self._data = data

    def is_error(self) -> bool:
        '''
        Returns if the result is an error.
        '''
        return self._is_error

    def data(self) -> dict:
        '''
        Returns the response data. 'None' if error.
        '''
        return self._data

    def status(self) -> int:
        '''
        Returns the HTTP status code of the response. Returns '-1' if no request was made.
        '''
        return self._status

    def msg(self) -> str:
        '''
        Returns a result message with further details about the error or successful response.
        '''
        return self._message


class Error:
    def __init__(self, message: str) -> None:
        self.message = message


class BaseResponse(TypedDict):
    status: Status


class GraphResponse(BaseResponse, TypedDict):
    graph: Graph
