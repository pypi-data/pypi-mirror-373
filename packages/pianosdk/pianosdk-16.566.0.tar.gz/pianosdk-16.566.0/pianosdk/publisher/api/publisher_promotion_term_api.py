from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.term import Term


class PublisherPromotionTermApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def add_term(self, term_id: str, aid: str, promotion_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/promotion/term/add'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'term_id': _encode_parameter(term_id),
            'aid': _encode_parameter(aid),
            'promotion_id': _encode_parameter(promotion_id)
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

    def delete_terms(self, term_id: str, aid: str, promotion_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/promotion/term/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'term_id': _encode_parameter(term_id),
            'aid': _encode_parameter(aid),
            'promotion_id': _encode_parameter(promotion_id)
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

    def term_list(self, promotion_id: str, aid: str, offset: int = 0, limit: int = 100, order_by: str = None, order_direction: str = None, q: str = None) -> ApiResponse[List[Term]]:
        _url_path = '/api/v3/publisher/promotion/term/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promotion_id': _encode_parameter(promotion_id),
            'aid': _encode_parameter(aid),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit)
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

