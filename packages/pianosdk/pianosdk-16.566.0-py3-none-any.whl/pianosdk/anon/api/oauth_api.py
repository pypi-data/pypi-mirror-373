from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.anon.models.o_auth_token import OAuthToken


class OauthApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def auth_token(self, client_id: str, client_secret: str = None, code: str = None, refresh_token: str = None, grant_type: str = None, redirect_uri: str = None, username: str = None, password: str = None, state: str = None, device_id: str = None) -> ApiResponse[OAuthToken]:
        _url_path = '/api/v3/oauth/authToken'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'client_id': _encode_parameter(client_id),
            'client_secret': _encode_parameter(client_secret),
            'code': _encode_parameter(code),
            'refresh_token': _encode_parameter(refresh_token),
            'grant_type': _encode_parameter(grant_type),
            'redirect_uri': _encode_parameter(redirect_uri),
            'username': _encode_parameter(username),
            'password': _encode_parameter(password),
            'state': _encode_parameter(state),
            'device_id': _encode_parameter(device_id)
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
        _result = _json_deserialize(_response, OAuthToken)
        return _result

