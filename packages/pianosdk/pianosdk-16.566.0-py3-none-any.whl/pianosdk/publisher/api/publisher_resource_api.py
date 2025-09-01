from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.resource import Resource


class PublisherResourceApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def attach_resource_to_fixed_bundle(self, aid: str, included_rid: List[str], bundle_rid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/resource/attach'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'included_rid': _encode_parameter(included_rid),
            'bundle_rid': _encode_parameter(bundle_rid)
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
        _result = _json_deserialize(_response)
        return _result

    def count(self, aid: str) -> ApiResponse[int]:
        _url_path = '/api/v3/publisher/resource/count'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
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
        _result = _json_deserialize(_response, int)
        return _result

    def create_resource(self, aid: str, name: str, rid: str = None, description: str = None, type: str = 'standard', image_url: str = None, bundle_type: str = None, resource_tag_id: List[str] = None, publish_date: datetime = None, resource_url: str = None, external_id: str = None) -> ApiResponse[Resource]:
        _url_path = '/api/v3/publisher/resource/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'type': _encode_parameter(type),
            'image_url': _encode_parameter(image_url),
            'bundle_type': _encode_parameter(bundle_type),
            'resource_tag_id': _encode_parameter(resource_tag_id),
            'publish_date': _encode_parameter(publish_date),
            'resource_url': _encode_parameter(resource_url),
            'external_id': _encode_parameter(external_id)
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
        _result = _json_deserialize(_response, Resource)
        return _result

    def delete_resource(self, aid: str, rid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/resource/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
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

    def detach_resource_from_fixed_bundle(self, aid: str, rid: str, bundle_rid: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/resource/detach'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'bundle_rid': _encode_parameter(bundle_rid)
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
        _result = _json_deserialize(_response)
        return _result

    def get_resource(self, aid: str, rid: str) -> ApiResponse[Resource]:
        _url_path = '/api/v3/publisher/resource/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid)
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

    def list_bundles(self, aid: str, rid: str, offset: int = 0, limit: int = 25, order_direction: str = 'asc', order_by: str = 'name', bundle_type: List[int] = None) -> ApiResponse[List[Resource]]:
        _url_path = '/api/v3/publisher/resource/bundles'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
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

    def list_resources(self, aid: str, offset: int = 0, limit: int = 25, type: str = 'NA', order_direction: str = 'asc', order_by: str = 'name', included_tag_id: List[str] = None, excluded_rid: List[str] = None, included_rid: List[str] = None, q: str = None, disabled: bool = False, bundle_type: int = None) -> ApiResponse[List[Resource]]:
        _url_path = '/api/v3/publisher/resource/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'included_tag_id': _encode_parameter(included_tag_id),
            'excluded_rid': _encode_parameter(excluded_rid),
            'included_rid': _encode_parameter(included_rid),
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

    def update_resource(self, aid: str, rid: str, name: str = None, new_rid: str = None, image_url: str = None, description: str = None, disabled: bool = None, publish_date: datetime = None, included_rid: List[str] = None, fixed_bundle_rid: List[str] = None, add_term_id: List[str] = None, del_term_id: List[str] = None, included_tag_id: List[str] = None, included_tag_name: List[str] = None, resource_url: str = None, external_id: str = None, is_fbia_resource: bool = None) -> ApiResponse[Resource]:
        _url_path = '/api/v3/publisher/resource/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'rid': _encode_parameter(rid),
            'name': _encode_parameter(name),
            'new_rid': _encode_parameter(new_rid),
            'image_url': _encode_parameter(image_url),
            'description': _encode_parameter(description),
            'disabled': _encode_parameter(disabled),
            'publish_date': _encode_parameter(publish_date),
            'included_rid': _encode_parameter(included_rid),
            'fixed_bundle_rid': _encode_parameter(fixed_bundle_rid),
            'add_term_id': _encode_parameter(add_term_id),
            'del_term_id': _encode_parameter(del_term_id),
            'included_tag_id': _encode_parameter(included_tag_id),
            'included_tag_name': _encode_parameter(included_tag_name),
            'resource_url': _encode_parameter(resource_url),
            'external_id': _encode_parameter(external_id),
            'is_fbia_resource': _encode_parameter(is_fbia_resource)
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
        _result = _json_deserialize(_response, Resource)
        return _result

