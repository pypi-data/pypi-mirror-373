from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.user_payment_info import UserPaymentInfo


class PublisherPaymentMethodApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_payment_instrument(self, aid: str, uid: str, token: str, source_id: int, set_as_default: bool = None, user_billing_address: str = None, expiration_month: int = None, expiration_year: int = None, last_four_digits: str = None, additional_info: str = None, issuer_country: str = None) -> ApiResponse[str]:
        _url_path = '/api/v3/publisher/payment/method/add'
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
            'token': _encode_parameter(token),
            'set_as_default': _encode_parameter(set_as_default),
            'user_billing_address': _encode_parameter(user_billing_address),
            'expiration_month': _encode_parameter(expiration_month),
            'expiration_year': _encode_parameter(expiration_year),
            'last_four_digits': _encode_parameter(last_four_digits),
            'additional_info': _encode_parameter(additional_info),
            'issuer_country': _encode_parameter(issuer_country),
            'source_id': _encode_parameter(source_id)
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
        _result = _json_deserialize(_response, str)
        return _result

    def delete_payment_instrument(self, aid: str, uid: str, payment_method_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/payment/method/remove'
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
            'payment_method_id': _encode_parameter(payment_method_id)
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

    def get_user_payment_info(self, aid: str, uid: str, user_payment_info_id: str) -> ApiResponse[UserPaymentInfo]:
        _url_path = '/api/v3/publisher/payment/method/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'user_payment_info_id': _encode_parameter(user_payment_info_id)
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
        _result = _json_deserialize(_response, UserPaymentInfo)
        return _result

    def update_payment_instrument(self, aid: str, uid: str, token: str = None, set_as_default: bool = None, user_billing_address: str = None, expiration_month: int = None, expiration_year: int = None, last_four_digits: str = None, additional_info: str = None, issuer_country: str = None, payment_method_id: str = None) -> ApiResponse[str]:
        _url_path = '/api/v3/publisher/payment/method/update'
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
            'token': _encode_parameter(token),
            'set_as_default': _encode_parameter(set_as_default),
            'user_billing_address': _encode_parameter(user_billing_address),
            'expiration_month': _encode_parameter(expiration_month),
            'expiration_year': _encode_parameter(expiration_year),
            'last_four_digits': _encode_parameter(last_four_digits),
            'additional_info': _encode_parameter(additional_info),
            'issuer_country': _encode_parameter(issuer_country),
            'payment_method_id': _encode_parameter(payment_method_id)
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
        _result = _json_deserialize(_response, str)
        return _result

