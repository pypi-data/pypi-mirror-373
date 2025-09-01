from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.export import Export


class PublisherExportCreateAccessReportExportApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_access_report_export_tz(self, aid: str, export_name: str, date_from: datetime, date_to: datetime, access_status: str = 'ALL', term_type: List[str] = None, term_id: List[str] = None, next_billing_date: datetime = None, last_payment_status: str = None, end_date_from: datetime = None, end_date_to: datetime = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/accessReportExport/v2'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'access_status': _encode_parameter(access_status),
            'term_type': _encode_parameter(term_type),
            'term_id': _encode_parameter(term_id),
            'next_billing_date': _encode_parameter(next_billing_date),
            'last_payment_status': _encode_parameter(last_payment_status),
            'date_from': _encode_parameter(date_from),
            'date_to': _encode_parameter(date_to),
            'end_date_from': _encode_parameter(end_date_from),
            'end_date_to': _encode_parameter(end_date_to)
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
        _result = _json_deserialize(_response, Export)
        return _result

