from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.bulk_user_import import BulkUserImport
from pianosdk.publisher.models.bulk_user_import_processing_request_dto import BulkUserImportProcessingRequestDto


class PublisherUserBulkImportApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def delete(self, aid: str, bulk_user_import_id: str) -> ApiResponse[bool]:
        _url_path = '/api/v3/publisher/user/bulkImport/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'bulk_user_import_id': _encode_parameter(bulk_user_import_id)
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

    def download(self, aid: str, bulk_user_import_id: str) -> ApiResponse[str]:
        _url_path = '/api/v3/publisher/user/bulkImport/download'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'bulk_user_import_id': _encode_parameter(bulk_user_import_id)
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
        _result = _json_deserialize(_response, str)
        return _result

    def list_completed(self, aid: str, offset: int = 0, limit: int = 100, order_by: str = None, order_direction: str = None) -> ApiResponse[List[BulkUserImport]]:
        _url_path = '/api/v3/publisher/user/bulkImport/listCompleted'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
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
        _result = _json_deserialize(_response, BulkUserImport)
        return _result

    def list_processing(self, aid: str) -> ApiResponse[List[BulkUserImportProcessingRequestDto]]:
        _url_path = '/api/v3/publisher/user/bulkImport/listProcessing'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
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
        _result = _json_deserialize(_response, BulkUserImportProcessingRequestDto)
        return _result

