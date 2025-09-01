from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.export import Export
from pianosdk.publisher.models.promo_code import PromoCode


class PublisherPromotionCodeApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def count(self, promotion_id: str, aid: str, q: str = None, state: str = None) -> ApiResponse[int]:
        _url_path = '/api/v3/publisher/promotion/code/count'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promotion_id': _encode_parameter(promotion_id),
            'aid': _encode_parameter(aid),
            'q': _encode_parameter(q),
            'state': _encode_parameter(state)
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

    def create(self, promotion_id: str, aid: str, code: str) -> ApiResponse[PromoCode]:
        _url_path = '/api/v3/publisher/promotion/code/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promotion_id': _encode_parameter(promotion_id),
            'aid': _encode_parameter(aid),
            'code': _encode_parameter(code)
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
        _result = _json_deserialize(_response, PromoCode)
        return _result

    def delete(self, promo_code_id: List[str], aid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/promotion/code/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'promo_code_id': _encode_parameter(promo_code_id),
            'aid': _encode_parameter(aid)
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

    def export(self, promotion_id: str, aid: str, export_name: str, state: List[str] = None, order_by: str = None, order_direction: str = None, q: str = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/promotion/code/export'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'promotion_id': _encode_parameter(promotion_id),
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'state': _encode_parameter(state),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'q': _encode_parameter(q)
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
        _result = _json_deserialize(_response, Export)
        return _result

    def get(self, promo_code_id: str, aid: str) -> ApiResponse[PromoCode]:
        _url_path = '/api/v3/publisher/promotion/code/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promo_code_id': _encode_parameter(promo_code_id),
            'aid': _encode_parameter(aid)
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
        _result = _json_deserialize(_response, PromoCode)
        return _result

    def list(self, promotion_id: str, aid: str, offset: int = 0, limit: int = 100, state: List[str] = None, order_by: str = None, order_direction: str = None, q: str = None) -> ApiResponse[List[PromoCode]]:
        _url_path = '/api/v3/publisher/promotion/code/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promotion_id': _encode_parameter(promotion_id),
            'aid': _encode_parameter(aid),
            'state': _encode_parameter(state),
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
        _result = _json_deserialize(_response, PromoCode)
        return _result

    def update(self, promo_code_id: str, aid: str, promotion_id: str, code: str) -> ApiResponse[PromoCode]:
        _url_path = '/api/v3/publisher/promotion/code/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'promo_code_id': _encode_parameter(promo_code_id),
            'aid': _encode_parameter(aid),
            'promotion_id': _encode_parameter(promotion_id),
            'code': _encode_parameter(code)
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
        _result = _json_deserialize(_response, PromoCode)
        return _result

