from copy import deepcopy
from typing import Dict
from urllib.parse import urlparse, urlunparse

from pianosdk.httpwrap import RequestsClient


class Configuration:

    @property
    def http_client(self) -> RequestsClient:
        """
        The Http Client, which makes all requests
        :return:
        """
        return self._http_client

    @property
    def timeout(self) -> int:
        """
        :return: The value used for connection timeout
        """
        return self._timeout

    @property
    def max_retries(self) -> int:
        """
        :return: The number of times to retry failed endpoint call
        """
        return self._max_retries

    @property
    def backoff_factor(self) -> int:
        """
        Used for sleep `{backoff factor} * (2 ** ({number of total retries} - 1))`
        :return: A backoff factor to apply between attempts after the second try.
        """
        return self._backoff_factor

    @property
    def environment(self) -> str:
        """
        :return: API environment: `production` or `sandbox`
        """
        return self._environment

    @property
    def api_token(self) -> str:
        """
        :return: Api Token
        """
        return self._api_token

    @property
    def private_key(self) -> str:
        """
        :return: Private key
        """
        return self._private_key

    @property
    def additional_headers(self) -> Dict:
        """
        :return: Copy of additional headers added to each API request
        """
        return deepcopy(self._additional_headers)

    def __init__(self, timeout: int = 60, max_retries: int = 3, backoff_factor: int = 0,
                 api_host: str = 'production', api_token: str = 'TODO: Replace', private_key: str = 'TODO: Replace',
                 additional_headers: Dict = {}):
        """Configuration object constructor
        :param timeout: The value to use for connection timeout
        :param max_retries: The number of times to retry failed endpoint call
        :param backoff_factor: A backoff factor to apply between attempts after the second try.
        :param api_host: API host. Use `production`, `sandbox` or custom url
        :param api_token: Api Token
        :param private_key: Private key
        :param additional_headers: Additional headers to add to each API request
        """
        self._host = Configuration._environments.get(api_host, None) or Configuration._validate_host(api_host)
        self._timeout = timeout
        self._max_retries = max_retries
        self._backoff_factor = backoff_factor
        self._api_token = api_token
        self._private_key = private_key
        self._additional_headers = deepcopy(additional_headers) or {}
        self._http_client = self.create_http_client()

    _environments: Dict[str, str] = {
        'production': "https://api.piano.io",
        'sandbox': "https://sandbox.piano.io"
    }

    @staticmethod
    def _validate_host(url):
        url_data = urlparse(url)
        if url_data.scheme and url_data.netloc:
            return urlunparse(list(url_data)[:2] + [''] * 4)
        raise ValueError(f'Invalid API host {url}.')

    def get_base_url(self) -> str:
        return self._host

    def create_http_client(self) -> RequestsClient:
        return RequestsClient(timeout=self.timeout,
                              max_retries=self.max_retries,
                              backoff_factor=self.backoff_factor)
