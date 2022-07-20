# Std and external imports
from typing import Tuple
import requests

# Local imports
import config.config as config
import utils.fmt as fmt

# Local typing imports
from typings.client import BaseResponse, GraphResponse, RequestResult, Error
from typings.graph import Graph


class Client:
    '''
    This class describes a HTTP client, which provides methods to easily interact with the REST API.
    '''
    base_url: str = ''

    def __init__(self, cfg: config.Config) -> None:
        '''
        Create a new client instance.

        Parameters
        ----------
        cfg : config.Config
            The config.
        '''
        if not cfg:
            raise ValueError

        self.base_url = fmt.host_port_from(
            cfg['backend']['host'],
            cfg['backend']['port']
        )

    def _post(self, *paths: str, params: dict = {}, data: any = None):
        '''
        Internal method to create HTTP POST requests.
        Parameters
        ----------
        paths : tuple[str, ...]
            Variable number of path segments.
        params : dict
            A dict of query parameters (Default: {}).
        data : any
            Request body data (Default: None).

        Returns
        -------
        result : Result
            Result object.
        '''
        url = fmt.url_from(self.base_url, paths)
        if not url:
            return RequestResult(None, -1, 'Unexpected empty URL', True)

        res = requests.post(url, params=params, data=data)
        if res.status_code >= 400:
            return RequestResult(None, res.status_code, 'Unexpected status code', True)

        try:
            data = res.json()
            return RequestResult(data, res.status_code, 'Success')
        except:
            return RequestResult(None, res.status_code, 'Response data could not be decoded as JSON', True)

    def _get(self, *paths: str, params: dict = {}, data: any = None) -> RequestResult:
        '''
        Internal method to create HTTP GET requests.

        Parameters
        ----------
        paths : tuple[str, ...]
            Variable number of path segments.
        params : dict
            A dict of query parameters (Default: {}).
        data : any
            Request body data (Default: None).

        Returns
        -------
        result : Result
            Result object.
        '''
        url = fmt.url_from(self.base_url, paths)
        if not url:
            return RequestResult(None, -1, 'Unexpected empty URL', True)

        res = requests.get(url, params=params, data=data)
        if res.status_code >= 400:
            return RequestResult(None, res.status_code, 'Unexpected status code', True)

        try:
            data = res.json()
            return RequestResult(data, res.status_code, 'Success')
        except:
            return RequestResult(None, res.status_code, 'Response data could not be decoded as JSON', True)

    def get_graph(self) -> Tuple[Graph, Error]:
        '''
        Get graph data from the REST API as JSON.

        Returns
        -------
        result: Tuple[Graph, Error]
            Returns the graph data. If error is not None, an error occured and should be handled.
        '''
        res = self._get('graphs')
        if res.is_error():
            return None, Error(res.msg())

        data: GraphResponse = res.data()
        return data['graph'], None

    def update_graph(self, data: Graph) -> Tuple[BaseResponse, Error]:
        '''
        Send updated graph data to the REST API as JSON.

        Parameters
        ----------
        data : Graph
            The updated graph data.

        Returns
        -------
        res : BaseResponse
            A response indicating the success.
        '''
        if not data:
            return None, Error('Missing updated graph data')

        res = self._post('graphs', data=data)
        if res.is_error():
            return None, Error(res.msg())

        return res.data(), None
