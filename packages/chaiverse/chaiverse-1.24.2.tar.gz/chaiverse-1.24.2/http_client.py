from copy import copy
import requests as requests_lib
from requests.adapters import HTTPAdapter, Retry

from chaiverse import config
from chaiverse.cli_utils.login_cli import get_developer_key_from_cache


# Increased retry from 3 to 6 only if initial connect failed, and it will not cause any side effects.
# This requests is intended to be directly imported to replace the requests library
requests = requests_lib.Session()
retries = Retry(connect=6, backoff_factor=1)
requests.mount('http://', HTTPAdapter(max_retries=retries))
requests.mount('https://', HTTPAdapter(max_retries=retries))


class _ChaiverseHTTPClient():
    def __init__(self, developer_key=None, hostname=None, debug_mode=False):
        if developer_key is None:
            developer_key = get_developer_key_from_cache()
        self.developer_key = developer_key
        self.hostname = hostname
        self.debug_mode = debug_mode

    @property
    def headers(self):
        headers = {"Authorization": f"Bearer {self.developer_key}"} if self.developer_key else {}
        return headers

    def get(self, endpoint, **kwargs):
        url, kwargs = self._format_url(endpoint, hostname=self.hostname, **kwargs)
        response = self._request(requests.get, url=url, **kwargs)
        return response

    def put(self, endpoint, **kwargs):
        url, kwargs = self._format_url(endpoint, hostname=self.hostname)
        response = self._request(requests.put, url=url, **kwargs)
        return response

    def post(self, endpoint, **kwargs):
        url, kwargs = self._format_url(endpoint, hostname=self.hostname, **kwargs)
        response = self._request(requests.post, url=url, **kwargs)
        return response

    def delete(self, endpoint):
        url, kwargs = self._format_url(endpoint, hostname=self.hostname)
        response = self._request(requests.delete, url=url)
        return response

    def _request(self, func, url, **kwargs):
        response = func(url=url, headers=self.headers, **kwargs)
        if not self.debug_mode:
            assert response.status_code == 200, response.text
            response = response.json()
        return response

    @staticmethod
    def _format_url(endpoint, hostname=config.BASE_SUBMITTER_URL, **kwargs):
        url = hostname + endpoint
        # Keep only the kwargs we don't template
        for key, value in copy(kwargs).items():
            if key in url:
                format_arg = {key: value}
                url = url.format(**format_arg) if key in url else url
                kwargs.pop(key)
        return url, kwargs


class SubmitterClient(_ChaiverseHTTPClient):
    def __init__(
            self,
            developer_key=None,
            hostname=None,
            debug_mode=False
    ):
        hostname = config.BASE_SUBMITTER_URL if not hostname else hostname
        super().__init__(developer_key, hostname, debug_mode)


class TrainerClient(_ChaiverseHTTPClient):
    def __init__(
            self,
            developer_key=None,
            hostname=None,
            debug_mode=False
    ):
        hostname = config.BASE_TRAINING_URL if not hostname else hostname
        super().__init__(developer_key, hostname, debug_mode)


class FeedbackClient(_ChaiverseHTTPClient):
    def __init__(
            self,
            developer_key=None,
            hostname=None,
            debug_mode=False
    ):
        hostname = config.BASE_FEEDBACK_URL if not hostname else hostname
        super().__init__(developer_key, hostname, debug_mode)


class AuthClient(_ChaiverseHTTPClient):
    def __init__(
            self,
            hostname=None,
            debug_mode=False
    ):
        hostname = config.BASE_AUTH_URL if not hostname else hostname
        super().__init__("", hostname, debug_mode)
