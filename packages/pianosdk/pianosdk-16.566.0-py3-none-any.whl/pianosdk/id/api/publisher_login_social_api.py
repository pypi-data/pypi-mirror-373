from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.id.models.social_additional_input_request import SocialAdditionalInputRequest


class PublisherLoginSocialApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def social_code(self, aid: str, api_token: str, response_id: str) -> ApiResponse[Dict]:
        _url_path = '/id/api/v1/publisher/login/social/code'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'api_token': _encode_parameter(api_token),
            'response_id': _encode_parameter(response_id)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

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

    def social_code_additional(self, aid: str, api_token: str, form_id: str = None, additional_input_state: str = None, body: SocialAdditionalInputRequest = None) -> ApiResponse[Dict]:
        _url_path = '/id/api/v1/publisher/login/social/codeAdditional'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'api_token': _encode_parameter(api_token),
            'form_id': _encode_parameter(form_id),
            'additional_input_state': _encode_parameter(additional_input_state)
        }

        _headers = {
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

    def social_code_confirm(self, aid: str, api_token: str, linking_state: str, email: str = None, password: str = None, confimed_token: str = None) -> ApiResponse[Dict]:
        _url_path = '/id/api/v1/publisher/login/social/codeConfirm'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'api_token': _encode_parameter(api_token),
            'email': _encode_parameter(email),
            'password': _encode_parameter(password),
            'confimed_token': _encode_parameter(confimed_token),
            'linking_state': _encode_parameter(linking_state)
        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {

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

