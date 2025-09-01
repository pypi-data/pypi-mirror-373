from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.user_address import UserAddress
from pianosdk.publisher.models.user_address_history import UserAddressHistory


class PublisherUserAddressApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_user_address(self, aid: str, uid: str, country_id: str, city: str, postal_code: str, address1: str, region_id: str = None, company_name: str = None, first_name: str = None, last_name: str = None, address2: str = None, phone: str = None, region_name: str = None) -> ApiResponse[UserAddress]:
        _url_path = '/api/v3/publisher/user/address/create'
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
            'region_id': _encode_parameter(region_id),
            'country_id': _encode_parameter(country_id),
            'city': _encode_parameter(city),
            'postal_code': _encode_parameter(postal_code),
            'company_name': _encode_parameter(company_name),
            'first_name': _encode_parameter(first_name),
            'last_name': _encode_parameter(last_name),
            'address1': _encode_parameter(address1),
            'address2': _encode_parameter(address2),
            'phone': _encode_parameter(phone),
            'region_name': _encode_parameter(region_name)
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
        _result = _json_deserialize(_response, UserAddress)
        return _result

    def delete_user_address(self, aid: str, uid: str, user_address_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/user/address/delete'
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
            'user_address_id': _encode_parameter(user_address_id)
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

    def list_user_address(self, aid: str, uid: str, offset: int = 0, limit: int = 100) -> ApiResponse[List[UserAddress]]:
        _url_path = '/api/v3/publisher/user/address/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
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
        _result = _json_deserialize(_response, UserAddress)
        return _result

    def list_user_address_history(self, aid: str, offset: int = 0, limit: int = 100, date_from: datetime = None, date_to: datetime = None) -> ApiResponse[List[UserAddressHistory]]:
        _url_path = '/api/v3/publisher/user/address/history'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'date_from': _encode_parameter(date_from),
            'date_to': _encode_parameter(date_to),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit)
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
        _result = _json_deserialize(_response, UserAddressHistory)
        return _result

    def update_user_address(self, aid: str, uid: str, user_address_id: str, country_id: str, city: str, postal_code: str, address1: str, region_id: str = None, company_name: str = None, first_name: str = None, last_name: str = None, address2: str = None, phone: str = None, region_name: str = None, additional_fields: str = None) -> ApiResponse[UserAddress]:
        _url_path = '/api/v3/publisher/user/address/update'
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
            'user_address_id': _encode_parameter(user_address_id),
            'region_id': _encode_parameter(region_id),
            'country_id': _encode_parameter(country_id),
            'city': _encode_parameter(city),
            'postal_code': _encode_parameter(postal_code),
            'company_name': _encode_parameter(company_name),
            'first_name': _encode_parameter(first_name),
            'last_name': _encode_parameter(last_name),
            'address1': _encode_parameter(address1),
            'address2': _encode_parameter(address2),
            'phone': _encode_parameter(phone),
            'region_name': _encode_parameter(region_name),
            'additional_fields': _encode_parameter(additional_fields)
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
        _result = _json_deserialize(_response, UserAddress)
        return _result

