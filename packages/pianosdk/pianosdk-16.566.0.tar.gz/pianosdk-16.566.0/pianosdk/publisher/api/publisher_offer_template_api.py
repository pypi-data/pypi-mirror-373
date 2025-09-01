from datetime import datetime
from io import StringIO
from typing import TextIO, Dict, List, Union

from pianosdk.api_response import ApiResponse
from pianosdk.base_api import BaseApi
from pianosdk.configuration import Configuration
from pianosdk.httpwrap import HttpCallBack
from pianosdk.utils import _json_deserialize, _encode_parameter
from pianosdk.publisher.models.offer_template import OfferTemplate
from pianosdk.publisher.models.offer_template_categories import OfferTemplateCategories
from pianosdk.publisher.models.offer_template_histories import OfferTemplateHistories
from pianosdk.publisher.models.offer_template_version import OfferTemplateVersion
from pianosdk.publisher.models.template_config import TemplateConfig


class PublisherOfferTemplateApi(BaseApi):
    def __init__(self, config: Configuration, http_callback: HttpCallBack = None) -> None:
        super().__init__(config, http_callback)

    def archive(self, aid: str, offer_template_id: str, history_comment: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/offer/template/archive'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id),
            'history_comment': _encode_parameter(history_comment)
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

    def convert_boilerplate_to_offer_template(self, aid: str, offer_template_id: str, name: str, category_id: str, description: str = None) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/convertBoilerplateToTemplate'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'category_id': _encode_parameter(category_id)
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
        _result = _json_deserialize(_response, OfferTemplateVersion)
        return _result

    def count(self, aid: str) -> ApiResponse[int]:
        _url_path = '/api/v3/publisher/offer/template/count'
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

    def create(self, aid: str, name: str, description: str = None, category_id: str = None, history_comment: str = None) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/create'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'category_id': _encode_parameter(category_id),
            'history_comment': _encode_parameter(history_comment)
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
        _result = _json_deserialize(_response, OfferTemplateVersion)
        return _result

    def delete(self, aid: str, offer_template_id: str) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/offer/template/delete'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id)
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

    def get(self, aid: str, offer_template_id: str) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/get'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id)
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
        _result = _json_deserialize(_response, OfferTemplateVersion)
        return _result

    def get_default_code(self, aid: str, offer_template_id: str) -> ApiResponse[TemplateConfig]:
        _url_path = '/api/v3/publisher/offer/template/defaultCode'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id)
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
        _result = _json_deserialize(_response, TemplateConfig)
        return _result

    def get_duplicate(self, aid: str, offer_template_id: str, history_comment: str = None, duplicate_variants: bool = None) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/duplicate'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id),
            'history_comment': _encode_parameter(history_comment),
            'duplicate_variants': _encode_parameter(duplicate_variants)
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
        _result = _json_deserialize(_response, OfferTemplateVersion)
        return _result

    def get_history(self, aid: str, offer_template_id: str) -> ApiResponse[OfferTemplateHistories]:
        _url_path = '/api/v3/publisher/offer/template/getHistory'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id)
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
        _result = _json_deserialize(_response, OfferTemplateHistories)
        return _result

    def list(self, aid: str, offset: int = 0, limit: int = 100, q: str = None, order_by: str = None, order_direction: str = None, status: str = None, variant_status: str = None, filters: List[str] = None) -> ApiResponse[List[OfferTemplate]]:
        _url_path = '/api/v3/publisher/offer/template/list'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'status': _encode_parameter(status),
            'variant_status': _encode_parameter(variant_status),
            'filters': _encode_parameter(filters)
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
        _result = _json_deserialize(_response, OfferTemplate)
        return _result

    def list_boilerplates(self, aid: str, categories: List[str], offset: int = 0, limit: int = 100, q: str = None, order_by: str = None, order_direction: str = None, status: str = None, template_type: str = None, ensure_templates_exists: bool = None, engine: str = None) -> ApiResponse[List[OfferTemplateCategories]]:
        _url_path = '/api/v3/publisher/offer/template/listBoilerplates'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'status': _encode_parameter(status),
            'templateType': _encode_parameter(template_type),
            'categories': _encode_parameter(categories),
            'ensure_templates_exists': _encode_parameter(ensure_templates_exists),
            'engine': _encode_parameter(engine)
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
        _result = _json_deserialize(_response, OfferTemplateCategories)
        return _result

    def list_by_category(self, aid: str, categories: List[str], offset: int = 0, limit: int = 100, status: str = None, template_type: str = None, q: str = None, order_by: str = None, order_direction: str = None, ensure_templates_exists: bool = None, engine: str = None) -> ApiResponse[List[OfferTemplateCategories]]:
        _url_path = '/api/v3/publisher/offer/template/listByCategory'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'status': _encode_parameter(status),
            'templateType': _encode_parameter(template_type),
            'categories': _encode_parameter(categories),
            'q': _encode_parameter(q),
            'offset': _encode_parameter(offset),
            'limit': _encode_parameter(limit),
            'order_by': _encode_parameter(order_by),
            'order_direction': _encode_parameter(order_direction),
            'ensure_templates_exists': _encode_parameter(ensure_templates_exists),
            'engine': _encode_parameter(engine)
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
        _result = _json_deserialize(_response, OfferTemplateCategories)
        return _result

    def make_global(self, aid: str, offer_template_id: str) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/makeGlobal'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id)
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
        _result = _json_deserialize(_response, OfferTemplateVersion)
        return _result

    def restore(self, aid: str, offer_template_id: str, history_comment: str = None) -> ApiResponse[Dict]:
        _url_path = '/api/v3/publisher/offer/template/restore'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id),
            'history_comment': _encode_parameter(history_comment)
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

    def update(self, aid: str, offer_template_id: str, name: str, description: str = None, category_id: str = None, thumbnail_image_url: str = None, history_comment: str = None) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/update'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'category_id': _encode_parameter(category_id),
            'thumbnail_image_url': _encode_parameter(thumbnail_image_url),
            'history_comment': _encode_parameter(history_comment)
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
        _result = _json_deserialize(_response, OfferTemplateVersion)
        return _result

    def update_full(self, aid: str, offer_template_id: str, name: str, category_id: str, description: str = None, thumbnail_image_url: str = None, action: str = None, version_name: str = None, version: int = None, content1_type: str = None, content1_value: str = None, content2_type: str = None, content2_value: str = None, content3_type: str = None, content3_value: str = None, external_css_list: str = None, content_field_list: str = None, history_comment: str = None, is_validate: bool = None) -> ApiResponse[OfferTemplateVersion]:
        _url_path = '/api/v3/publisher/offer/template/updatefull'
        _query_url = self.config.get_base_url() + _url_path
        _query_parameters = {

        }

        _headers = {
            'api_token': self.config.api_token,
            'Accept': 'application/json'
        }

        _parameters = {
            'aid': _encode_parameter(aid),
            'offer_template_id': _encode_parameter(offer_template_id),
            'name': _encode_parameter(name),
            'description': _encode_parameter(description),
            'category_id': _encode_parameter(category_id),
            'thumbnail_image_url': _encode_parameter(thumbnail_image_url),
            'action': _encode_parameter(action),
            'version_name': _encode_parameter(version_name),
            'version': _encode_parameter(version),
            'content1_type': _encode_parameter(content1_type),
            'content1_value': _encode_parameter(content1_value),
            'content2_type': _encode_parameter(content2_type),
            'content2_value': _encode_parameter(content2_value),
            'content3_type': _encode_parameter(content3_type),
            'content3_value': _encode_parameter(content3_value),
            'external_css_list': _encode_parameter(external_css_list),
            'content_field_list': _encode_parameter(content_field_list),
            'history_comment': _encode_parameter(history_comment),
            'is_validate': _encode_parameter(is_validate)
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
        _result = _json_deserialize(_response, OfferTemplateVersion)
        return _result

