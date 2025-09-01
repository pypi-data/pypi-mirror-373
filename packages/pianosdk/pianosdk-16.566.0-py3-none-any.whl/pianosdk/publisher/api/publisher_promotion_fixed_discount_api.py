from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.promotion_fixed_discount import PromotionFixedDiscount


class PublisherPromotionFixedDiscountApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create(self, promotion_id: str, aid: str, amount: float, currency: str) -> ApiResponse[PromotionFixedDiscount]:
        _url_path = '/api/v3/publisher/promotion/fixedDiscount/add'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promotion_id': _encode_parameter(promotion_id),
            'aid': _encode_parameter(aid),
            'amount': _encode_parameter(amount),
            'currency': _encode_parameter(currency)
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
        _result = _json_deserialize(_response, PromotionFixedDiscount)
        return _result

    def delete(self, fixed_discount_id: str, aid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/promotion/fixedDiscount/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'fixed_discount_id': _encode_parameter(fixed_discount_id),
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

    def update(self, fixed_discount_id: str, aid: str, amount: float, currency: str) -> ApiResponse[PromotionFixedDiscount]:
        _url_path = '/api/v3/publisher/promotion/fixedDiscount/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'fixed_discount_id': _encode_parameter(fixed_discount_id),
            'aid': _encode_parameter(aid),
            'amount': _encode_parameter(amount),
            'currency': _encode_parameter(currency)
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
        _result = _json_deserialize(_response, PromotionFixedDiscount)
        return _result

