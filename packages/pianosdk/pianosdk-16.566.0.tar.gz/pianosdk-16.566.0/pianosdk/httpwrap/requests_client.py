from typing import Dict

from requests import session, Response
from requests.adapters import HTTPAdapter
from urllib3 import Retry

from .models import HttpRequest, HttpResponse


class RequestsClient:

    def __init__(self,
                 timeout=60,
                 max_retries=None,
                 backoff_factor=None,
                 verify=True):
        """The constructor.
        Args:
            timeout (float): The default global timeout(seconds).
        """
        self.timeout = timeout
        self.session = session()

        retries = Retry(total=max_retries, backoff_factor=backoff_factor)
        self.session.mount('http://', HTTPAdapter(max_retries=retries))
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        self.session.verify = verify

    def execute(self, request: HttpRequest) -> HttpResponse:
        """
        Execute a given HttpRequest to get a string response back
        :param request: The given HttpRequest to execute.
        :return: The response of the HttpRequest.
        """
        response = self.session.request(
            request.http_method,
            request.query_url,
            headers=request.headers,
            params=request.query_parameters,
            data=request.parameters,
            json=request.json,
            files=request.files,
            timeout=self.timeout
        )
        response.encoding = 'utf-8'

        return self._convert_response(response, request)

    @staticmethod
    def _convert_response(response: Response, http_request: HttpRequest) -> HttpResponse:
        return HttpResponse(
            response.status_code,
            response.reason,
            response.headers,
            response.text,
            http_request
        )

    @staticmethod
    def build_request(method: str,
                      query_url: str,
                      headers: Dict = None,
                      query_parameters: Dict = None,
                      parameters: Dict = None,
                      json: Dict = None,
                      files: Dict = None) -> HttpRequest:
        """
        Create a HttpRequest object for the given parameters
        :param method: The request method
        :param query_url: The URL to send the request to.
        :param headers: The headers for the HTTP Request.
        :param query_parameters: Query parameters to add in the URL.
        :param parameters: Form or body parameters to be included in the body.
        :param json: Dict to be sent with the request as body.
        :param files: Files to be sent with the request.
        :return: The generated HttpRequest for the given parameters.
        """
        return HttpRequest(method.upper(),
                           query_url,
                           headers,
                           query_parameters,
                           parameters,
                           json,
                           files)
