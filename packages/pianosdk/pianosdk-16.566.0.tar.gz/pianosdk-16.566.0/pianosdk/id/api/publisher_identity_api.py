from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.id.models.publisher_login_request import PublisherLoginRequest
from pianosdk.id.models.publisher_password_request import PublisherPasswordRequest
from pianosdk.id.models.publisher_register_request import PublisherRegisterRequest
from pianosdk.id.models.token_response import TokenResponse


class PublisherIdentityApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_password(self, authorization: str = None, body: PublisherPasswordRequest = None) -> ApiResponse[Dict]:
        _url_path = '/id/api/v1/publisher/identity/password'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'Authorization': authorization,
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = body and body.dict()
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

    def delete_session(self, aid: str, uid: str, jti: List[str], authorization: str = None) -> ApiResponse[Dict]:
        _url_path = '/id/api/v1/publisher/identity/session'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'jti': _encode_parameter(jti)
        }

        _headers = {
            'Authorization': authorization,
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = None
        _files = None

        _request = self.config.http_client.build_request('DELETE',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response)
        return _result

    def login(self, authorization: str = None, body: PublisherLoginRequest = None) -> ApiResponse[TokenResponse]:
        _url_path = '/id/api/v1/publisher/identity/login'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'Authorization': authorization,
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = body and body.dict()
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, TokenResponse)
        return _result

    def register(self, authorization: str = None, body: PublisherRegisterRequest = None) -> ApiResponse[TokenResponse]:
        _url_path = '/id/api/v1/publisher/identity/register'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'Authorization': authorization,
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

        }

        _body = body and body.dict()
        _files = None

        _request = self.config.http_client.build_request('POST',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, TokenResponse)
        return _result

