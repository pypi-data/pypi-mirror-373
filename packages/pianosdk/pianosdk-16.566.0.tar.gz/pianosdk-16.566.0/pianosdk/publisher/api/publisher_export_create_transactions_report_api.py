from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.export import Export


class PublisherExportCreateTransactionsReportApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def create_transactions_report_tz(self, aid: str, export_name: str, transactions_type: str = 'purchases', order_by: str = 'payment_date', order_direction: str = 'desc', q: str = None, date_from: datetime = None, date_to: datetime = None) -> ApiResponse[Export]:
        _url_path = '/api/v3/publisher/export/create/transactionsReport/v2'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'export_name': _encode_parameter(export_name),
            'transactions_type': _encode_parameter(transactions_type),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'q': _encode_parameter(q),
            'date_from': _encode_parameter(date_from),
            'date_to': _encode_parameter(date_to)
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
        _result = _json_deserialize(_response, Export)
        return _result

