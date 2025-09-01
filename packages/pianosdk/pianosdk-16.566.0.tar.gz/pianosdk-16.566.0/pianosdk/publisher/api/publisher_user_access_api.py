from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.access import Access
from pianosdk.publisher.models.access_dto import AccessDTO


class PublisherUserAccessApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def check_access(self, aid: str, uid: str, rid: str, cross_app: bool = False) -> ApiResponse[AccessDTO]:
        _url_path = '/api/v3/publisher/user/access/check'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'rid': _encode_parameter(rid),
            'cross_app': _encode_parameter(cross_app)
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

    def grant_access(self, aid: str, rid: str, send_email: bool = False, uid: str = None, emails: str = None, expire_date: int = None, url: str = None, message: str = None) -> ApiResponse[List[Access]]:
        _url_path = '/api/v3/publisher/user/access/grant'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'uid': _encode_parameter(uid),
            'emails': _encode_parameter(emails),
            'expire_date': _encode_parameter(expire_date),
            'send_email': _encode_parameter(send_email),
            'url': _encode_parameter(url),
            'message': _encode_parameter(message)
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
        _result = _json_deserialize(_response, Access)
        return _result

    def grant_access_to_users(self, aid: str, rid: List[str], send_email: bool = False, emails: List[str] = None, file_id: str = None, expire_date: datetime = None, message: str = None) -> ApiResponse[int]:
        _url_path = '/api/v3/publisher/user/access/grantToUsers'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'emails': _encode_parameter(emails),
            'file_id': _encode_parameter(file_id),
            'expire_date': _encode_parameter(expire_date),
            'send_email': _encode_parameter(send_email),
            'message': _encode_parameter(message)
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

    def list_access(self, aid: str, uid: str, offset: int = 0, limit: int = 100, expand_bundled: bool = False, cross_app: bool = False) -> ApiResponse[List[AccessDTO]]:
        _url_path = '/api/v3/publisher/user/access/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'uid': _encode_parameter(uid),
            'expand_bundled': _encode_parameter(expand_bundled),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'cross_app': _encode_parameter(cross_app)
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

    def revoke_access(self, access_id: str) -> ApiResponse[Access]:
        _url_path = '/api/v3/publisher/user/access/revoke'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'access_id': _encode_parameter(access_id)
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
        _result = _json_deserialize(_response, Access)
        return _result

    def update(self, access_id: str, expire_date: datetime = None) -> ApiResponse[Access]:
        _url_path = '/api/v3/publisher/user/access/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'access_id': _encode_parameter(access_id),
            'expire_date': _encode_parameter(expire_date)
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
        _result = _json_deserialize(_response, Access)
        return _result

