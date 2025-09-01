from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.user_billing_address import UserBillingAddress


class PublisherUserBillingAddressApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create(self, aid: str, uid: str, country: str, region: str, postal_code: str, type: int, city: str = None, address_line1: str = None, address_line2: str = None, address_line3: str = None) -> ApiResponse[UserBillingAddress]:
        _url_path = '/api/v3/publisher/user/billingAddress/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'country': _encode_parameter(country),
            'region': _encode_parameter(region),
            'city': _encode_parameter(city),
            'postal_code': _encode_parameter(postal_code),
            'address_line1': _encode_parameter(address_line1),
            'address_line2': _encode_parameter(address_line2),
            'address_line3': _encode_parameter(address_line3),
            'type': _encode_parameter(type)
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
        _result = _json_deserialize(_response, UserBillingAddress)
        return _result

    def delete(self, aid: str, uid: str, address_pub_id: str) -> ApiResponse[UserBillingAddress]:
        _url_path = '/api/v3/publisher/user/billingAddress/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'address_pub_id': _encode_parameter(address_pub_id)
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
        _result = _json_deserialize(_response, UserBillingAddress)
        return _result

    def get(self, aid: str, uid: str, address_pub_id: str) -> ApiResponse[UserBillingAddress]:
        _url_path = '/api/v3/publisher/user/billingAddress/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'address_pub_id': _encode_parameter(address_pub_id)
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
        _result = _json_deserialize(_response, UserBillingAddress)
        return _result

    def get_by_payment(self, aid: str, user_payment_id: str) -> ApiResponse[UserBillingAddress]:
        _url_path = '/api/v3/publisher/user/billingAddress/getByPayment'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'user_payment_id': _encode_parameter(user_payment_id)
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
        _result = _json_deserialize(_response, UserBillingAddress)
        return _result

    def get_by_payment_info(self, aid: str, user_payment_info_id: str) -> ApiResponse[UserBillingAddress]:
        _url_path = '/api/v3/publisher/user/billingAddress/getByPaymentInfo'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'user_payment_info_id': _encode_parameter(user_payment_info_id)
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
        _result = _json_deserialize(_response, UserBillingAddress)
        return _result

    def list(self, aid: str, uid: str) -> ApiResponse[List[UserBillingAddress]]:
        _url_path = '/api/v3/publisher/user/billingAddress/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid)
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
        _result = _json_deserialize(_response, UserBillingAddress)
        return _result

