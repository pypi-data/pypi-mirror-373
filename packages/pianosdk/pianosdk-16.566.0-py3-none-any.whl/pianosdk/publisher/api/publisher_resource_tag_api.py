from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.resource import Resource
from pianosdk.publisher.models.resource_tag import ResourceTag


class PublisherResourceTagApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def attach_tag(self, resource_tag_id: str, aid: str, rid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/resource/tag/attach'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'resource_tag_id': _encode_parameter(resource_tag_id),
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid)
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

    def create_tag(self, aid: str, rid: str, name: str, type: str = 'standard') -> ApiResponse[ResourceTag]:
        _url_path = '/api/v3/publisher/resource/tag/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'type': _encode_parameter(type),
            'name': _encode_parameter(name)
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
        _result = _json_deserialize(_response, ResourceTag)
        return _result

    def delete_tag(self, resource_tag_id: str, aid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/resource/tag/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'resource_tag_id': _encode_parameter(resource_tag_id),
            'aid': _encode_parameter(aid)
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

    def detach_tag(self, resource_tag_id: str, aid: str, rid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/resource/tag/detach'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'resource_tag_id': _encode_parameter(resource_tag_id),
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid)
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

    def get_tag(self, resource_tag_id: str, aid: str) -> ApiResponse[ResourceTag]:
        _url_path = '/api/v3/publisher/resource/tag/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'resource_tag_id': _encode_parameter(resource_tag_id),
            'aid': _encode_parameter(aid)
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
        _result = _json_deserialize(_response, ResourceTag)
        return _result

    def list_bundles_for_tags(self, aid: str, included_tag_id: List[str], offset: int = 0, limit: int = 25, type: str = 'NA', order_direction: str = 'asc', order_by: str = 'name', q: str = None, disabled: bool = False, bundle_type: int = None) -> ApiResponse[List[Resource]]:
        _url_path = '/api/v3/publisher/resource/tag/bundles'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'included_tag_id': _encode_parameter(included_tag_id),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'disabled': _encode_parameter(disabled),
            'type': _encode_parameter(type),
            'bundle_type': _encode_parameter(bundle_type)
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
        _result = _json_deserialize(_response, Resource)
        return _result

    def list_tags(self, aid: str, tag_type: int, offset: int = 0, limit: int = 25, rid: str = None, q: str = None, order_by: str = None, order_direction: str = None) -> ApiResponse[List[ResourceTag]]:
        _url_path = '/api/v3/publisher/resource/tag/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'tag_type': _encode_parameter(tag_type)
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
        _result = _json_deserialize(_response, ResourceTag)
        return _result

