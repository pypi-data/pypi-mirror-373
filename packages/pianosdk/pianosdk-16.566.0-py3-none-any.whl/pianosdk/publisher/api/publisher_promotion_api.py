from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.promotion import Promotion


class PublisherPromotionApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def code_exists(self, promotion_id: str, aid: str, email: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/promotion/exists'
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
            'email': _encode_parameter(email)
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
        _result = _json_deserialize(_response, bool)
        return _result

    def count(self, aid: str, expired: str = 'all') -> ApiResponse[int]:
        _url_path = '/api/v3/publisher/promotion/count'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'expired': _encode_parameter(expired)
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

    def create(self, aid: str, name: str, new_customers_only: bool = False, start_date: datetime = None, end_date: datetime = None, discount_type: str = None, percentage_discount: float = None, unlimited_uses: bool = False, uses_allowed: int = None, never_allow_zero: bool = False, fixed_promotion_code: str = None, promotion_code_prefix: str = None, term_dependency_type: str = None, apply_to_all_billing_periods: bool = False, can_be_applied_on_renewal: bool = False, billing_period_limit: int = None) -> ApiResponse[Promotion]:
        _url_path = '/api/v3/publisher/promotion/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'name': _encode_parameter(name),
            'start_date': _encode_parameter(start_date),
            'end_date': _encode_parameter(end_date),
            'new_customers_only': _encode_parameter(new_customers_only),
            'discount_type': _encode_parameter(discount_type),
            'percentage_discount': _encode_parameter(percentage_discount),
            'unlimited_uses': _encode_parameter(unlimited_uses),
            'uses_allowed': _encode_parameter(uses_allowed),
            'never_allow_zero': _encode_parameter(never_allow_zero),
            'fixed_promotion_code': _encode_parameter(fixed_promotion_code),
            'promotion_code_prefix': _encode_parameter(promotion_code_prefix),
            'term_dependency_type': _encode_parameter(term_dependency_type),
            'apply_to_all_billing_periods': _encode_parameter(apply_to_all_billing_periods),
            'can_be_applied_on_renewal': _encode_parameter(can_be_applied_on_renewal),
            'billing_period_limit': _encode_parameter(billing_period_limit)
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
        _result = _json_deserialize(_response, Promotion)
        return _result

    def delete(self, promotion_id: str, aid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/promotion/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'promotion_id': _encode_parameter(promotion_id),
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

    def generate_codes(self, promotion_id: str, aid: str, fixed_promotion_code: str = None, promotion_code_prefix: str = None, amount: int = None, asset_id: str = None) -> ApiResponse[Promotion]:
        _url_path = '/api/v3/publisher/promotion/generate'
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
            'fixed_promotion_code': _encode_parameter(fixed_promotion_code),
            'promotion_code_prefix': _encode_parameter(promotion_code_prefix),
            'amount': _encode_parameter(amount),
            'asset_id': _encode_parameter(asset_id)
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
        _result = _json_deserialize(_response, Promotion)
        return _result

    def get(self, promotion_id: str, aid: str) -> ApiResponse[Promotion]:
        _url_path = '/api/v3/publisher/promotion/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promotion_id': _encode_parameter(promotion_id),
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
        _result = _json_deserialize(_response, Promotion)
        return _result

    def list(self, aid: str, offset: int = 0, limit: int = 100, expired: str = 'active', order_by: str = None, order_direction: str = None, q: str = None) -> ApiResponse[List[Promotion]]:
        _url_path = '/api/v3/publisher/promotion/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'expired': _encode_parameter(expired),
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
        _result = _json_deserialize(_response, Promotion)
        return _result

    def total_sale(self, promotion_id: str, aid: str, currency_code: str = 'USD') -> ApiResponse[str]:
        _url_path = '/api/v3/publisher/promotion/total'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'promotion_id': _encode_parameter(promotion_id),
            'aid': _encode_parameter(aid),
            'currency_code': _encode_parameter(currency_code)
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
        _result = _json_deserialize(_response, str)
        return _result

    def update(self, promotion_id: str, aid: str, name: str, discount_type: str, start_date: datetime = None, end_date: datetime = None, new_customers_only: bool = False, percentage_discount: float = None, unlimited_uses: bool = False, uses_allowed: int = None, never_allow_zero: bool = False, fixed_promotion_code: str = None, promotion_code_prefix: str = None, term_dependency_type: str = None, apply_to_all_billing_periods: bool = None, can_be_applied_on_renewal: bool = False, billing_period_limit: int = None) -> ApiResponse[Promotion]:
        _url_path = '/api/v3/publisher/promotion/update'
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
            'name': _encode_parameter(name),
            'start_date': _encode_parameter(start_date),
            'end_date': _encode_parameter(end_date),
            'new_customers_only': _encode_parameter(new_customers_only),
            'discount_type': _encode_parameter(discount_type),
            'percentage_discount': _encode_parameter(percentage_discount),
            'unlimited_uses': _encode_parameter(unlimited_uses),
            'uses_allowed': _encode_parameter(uses_allowed),
            'never_allow_zero': _encode_parameter(never_allow_zero),
            'fixed_promotion_code': _encode_parameter(fixed_promotion_code),
            'promotion_code_prefix': _encode_parameter(promotion_code_prefix),
            'term_dependency_type': _encode_parameter(term_dependency_type),
            'apply_to_all_billing_periods': _encode_parameter(apply_to_all_billing_periods),
            'can_be_applied_on_renewal': _encode_parameter(can_be_applied_on_renewal),
            'billing_period_limit': _encode_parameter(billing_period_limit)
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
        _result = _json_deserialize(_response, Promotion)
        return _result

