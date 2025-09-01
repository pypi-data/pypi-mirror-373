from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.id.models.token_response import TokenResponse


class IdentityTokenApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def token_verify_session(self, client_id: str, authorization: str = None, user_agent: str = None) -> ApiResponse[TokenResponse]:
        _url_path = '/id/api/v1/identity/token/validation'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'client_id': _encode_parameter(client_id),
            'user_agent': _encode_parameter(user_agent)
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

        _request = self.config.http_client.build_request('GET',
                                                         _query_url,
                                                         headers=_headers,
                                                         query_parameters=_query_parameters,
                                                         parameters=_parameters,
                                                         json=_body,
                                                         files=_files)
        _response = self._execute_request(_request)
        _result = _json_deserialize(_response, TokenResponse)
        return _result

