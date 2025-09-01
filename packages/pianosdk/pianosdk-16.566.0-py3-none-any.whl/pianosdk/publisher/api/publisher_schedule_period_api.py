from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.period import Period
from pianosdk.publisher.models.result import Result


class PublisherSchedulePeriodApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def add_period(self, schedule_id: str, name: str, sell_date: datetime, begin_date: datetime, end_date: datetime) -> ApiResponse[Period]:
        _url_path = '/api/v3/publisher/schedule/period/add'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'schedule_id': _encode_parameter(schedule_id),
            'name': _encode_parameter(name),
            'sell_date': _encode_parameter(sell_date),
            'begin_date': _encode_parameter(begin_date),
            'end_date': _encode_parameter(end_date)
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
        _result = _json_deserialize(_response, Period)
        return _result

    def delete_period(self, period_id: str) -> ApiResponse[Result]:
        _url_path = '/api/v3/publisher/schedule/period/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'period_id': _encode_parameter(period_id)
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
        _result = _json_deserialize(_response, Result)
        return _result

    def update_period(self, schedule_id: str, period_id: str, name: str, sell_date: datetime, begin_date: datetime, end_date: datetime) -> ApiResponse[List[Period]]:
        _url_path = '/api/v3/publisher/schedule/period/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'schedule_id': _encode_parameter(schedule_id),
            'period_id': _encode_parameter(period_id),
            'name': _encode_parameter(name),
            'sell_date': _encode_parameter(sell_date),
            'begin_date': _encode_parameter(begin_date),
            'end_date': _encode_parameter(end_date)
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
        _result = _json_deserialize(_response, Period)
        return _result

