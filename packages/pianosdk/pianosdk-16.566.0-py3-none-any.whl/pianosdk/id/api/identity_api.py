from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.id.models.token_response import TokenResponse


class IdentityApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def refresh_token_or_exchange_code(self, client_id: str = None, refresh_token: str = None, grant_type: str = None, code: str = None, client_secret: str = None, redirect_uri: str = None, code_verifier: str = None) -> ApiResponse[TokenResponse]:
        _url_path = '/id/api/v1/identity/token'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'client_id': _encode_parameter(client_id),
            'refresh_token': _encode_parameter(refresh_token),
            'grant_type': _encode_parameter(grant_type),
            'code': _encode_parameter(code),
            'client_secret': _encode_parameter(client_secret),
            'redirect_uri': _encode_parameter(redirect_uri),
            'code_verifier': _encode_parameter(code_verifier)
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
        _result = _json_deserialize(_response, TokenResponse)
        return _result

