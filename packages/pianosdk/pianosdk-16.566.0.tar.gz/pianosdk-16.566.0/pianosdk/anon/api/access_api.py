from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.anon.models.access_dto import AccessDTO


class AccessApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def check(self, rid: str, aid: str, tp_access_token_v2: str = None, umc: str = None, cross_app: bool = False, user_token: str = None, user_provider: str = None, user_ref: str = None) -> ApiResponse[AccessDTO]:
        _url_path = '/api/v3/access/check'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'rid': _encode_parameter(rid),
            'aid': _encode_parameter(aid),
            'tp_access_token_v2': _encode_parameter(tp_access_token_v2),
            'umc': _encode_parameter(umc),
            'cross_app': _encode_parameter(cross_app),
            'user_token': _encode_parameter(user_token),
            'user_provider': _encode_parameter(user_provider),
            'user_ref': _encode_parameter(user_ref)
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
        _result = _json_deserialize(_response, AccessDTO)
        return _result

    def list(self, aid: str, offset: int = 0, limit: int = 100, active: bool = True, expand_bundled: bool = False, cross_app: bool = False, user_token: str = None, user_provider: str = None, user_ref: str = None) -> ApiResponse[List[AccessDTO]]:
        _url_path = '/api/v3/access/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'active': _encode_parameter(active),
            'expand_bundled': _encode_parameter(expand_bundled),
            'cross_app': _encode_parameter(cross_app),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'user_token': _encode_parameter(user_token),
            'user_provider': _encode_parameter(user_provider),
            'user_ref': _encode_parameter(user_ref)
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
        _result = _json_deserialize(_response, AccessDTO)
        return _result

