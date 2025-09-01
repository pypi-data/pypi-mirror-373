from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.term import Term


class PublisherTermApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def applicable(self, aid: str, promotion_id: str = None, q: str = None, order_by: str = None, order_direction: str = None) -> ApiResponse[List[Term]]:
        _url_path = '/api/v3/publisher/term/applicable'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promotion_id': _encode_parameter(promotion_id),
            'aid': _encode_parameter(aid),
            'q': _encode_parameter(q),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Term)
        return _result

    def count(self, aid: str, include_type: List[str] = None, exclude_type: List[str] = None, term_id: str = None, resource_type: str = None, source: List[str] = None, type: str = None) -> ApiResponse[int]:
        _url_path = '/api/v3/publisher/term/count'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'include_type': _encode_parameter(include_type),
            'exclude_type': _encode_parameter(exclude_type),
            'term_id': _encode_parameter(term_id),
            'resource_type': _encode_parameter(resource_type),
            'source': _encode_parameter(source),
            'type': _encode_parameter(type)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, int)
        return _result

    def delete(self, term_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/term/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'term_id': _encode_parameter(term_id)
        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response)
        return _result

    def get(self, term_id: str) -> ApiResponse[Term]:
        _url_path = '/api/v3/publisher/term/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'term_id': _encode_parameter(term_id)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Term)
        return _result

    def list(self, aid: str, offset: int = 0, limit: int = 100, rid: str = None, include_type: List[str] = None, exclude_type: List[str] = None, term_id: str = None, resource_type: str = None, source: List[str] = None, type: str = None, order_by: str = None, order_direction: str = None, q: str = None) -> ApiResponse[List[Term]]:
        _url_path = '/api/v3/publisher/term/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'include_type': _encode_parameter(include_type),
            'exclude_type': _encode_parameter(exclude_type),
            'term_id': _encode_parameter(term_id),
            'resource_type': _encode_parameter(resource_type),
            'source': _encode_parameter(source),
            'type': _encode_parameter(type),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'q': _encode_parameter(q)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, Term)
        return _result

