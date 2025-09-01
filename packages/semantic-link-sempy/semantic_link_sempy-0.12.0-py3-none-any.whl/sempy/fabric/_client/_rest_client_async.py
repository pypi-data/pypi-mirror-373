from abc import ABC, abstractmethod
from typing import Dict, Optional
import aiohttp
from aiohttp import ClientResponse
from tenacity import AsyncRetrying, stop_after_attempt, wait_exponential, retry_if_exception
from sempy.fabric._environment import _get_cognitive_service_uri
from sempy._utils._log import log_rest_request_async_mwc, log_rest_response_async, log_retry_async


class SessionWithLoggingAsync:
    def __init__(self, *args, **kwargs):
        self.session = aiohttp.ClientSession(*args, **kwargs)

    @log_rest_request_async_mwc
    async def request(self, method, url, *args, **kwargs):
        response = await self.session.request(method, url, *args, **kwargs)
        return response

    async def close(self):
        await self.session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close()
        return False


class RetryWithLoggingAsync(AsyncRetrying):
    def __init__(self, custom_retry_config, *args, **kwargs):
        def retry_if_status_code_and_method(retry_state, *args, **kwargs):
            if isinstance(retry_state, aiohttp.ClientError):
                return (
                    retry_state.status in custom_retry_config["status_forcelist"]
                    and retry_state.request_info.method in custom_retry_config["allowed_methods"]
                )
            return False
        retry_config = {
            "stop": stop_after_attempt(custom_retry_config["total"]),
            "wait": wait_exponential(multiplier=custom_retry_config["backoff_factor"]),
            "retry": retry_if_exception(retry_if_status_code_and_method),
            "reraise": custom_retry_config["raise_on_status"],
        }
        super().__init__(**retry_config)

    @log_retry_async
    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)


class BaseAsyncRestClient(ABC):
    """
    REST client to access endpoints asynchronously. Authentication tokens are automatically acquired from the execution environment.

    ***Experimental***: This class is experimental and may change in future versions.

    Parameters
    ----------
    retry_config : dict, default=None
        Configuration for the retry strategy. The following keys are filled with default values if not provided:
        - total: int, default=10
        - allowed_methods: list, default=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"]
        - status_forcelist: list, default=[429, 502, 503, 504]
        - backoff_factor: int, default=1
        - raise_on_status: bool, default=False
    """
    def __init__(self, retry_config: Optional[Dict] = None):
        retry_config = retry_config or {}
        retry_config.setdefault("total", stop_after_attempt(10))
        retry_config.setdefault("allowed_methods", ["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"])
        retry_config.setdefault("status_forcelist", [429, 502, 503, 504])
        retry_config.setdefault("backoff_factor", 1)
        retry_config.setdefault("raise_on_status", False)

        self.retry_strategy = RetryWithLoggingAsync(retry_config)
        self.http_async = SessionWithLoggingAsync()

    async def close_session(self):
        await self.http_async.close()

    @abstractmethod
    def _get_default_base_url(self):
        pass

    @abstractmethod
    def _get_headers(self):
        pass

    async def request(self, method: str, path_or_url: str, *args, **kwargs):

        @log_rest_response_async
        async def validate_rest_response(response: ClientResponse):
            if response.status >= 400:
                raise aiohttp.ClientError(f"HTTP Error: {response.status} from {response.url}")

        default_base_url = self._get_default_base_url()

        headers = self._get_headers()

        if path_or_url.startswith("https://"):
            url = path_or_url
        else:
            url = f"{default_base_url}{path_or_url}"

        response = ""
        async for attempt in self.retry_strategy:
            with attempt:
                response = await self.http_async.request(method, url, headers=headers, **kwargs)

        await validate_rest_response(response)
        return response

    async def get(self, path_or_url: str, *args, **kwargs):
        return await self.request("GET", path_or_url, *args, **kwargs)

    async def post(self, path_or_url: str, *args, **kwargs):
        return await self.request("POST", path_or_url, *args, **kwargs)

    async def delete(self, path_or_url: str, *args, **kwargs):
        return await self.request("DELETE", path_or_url, *args, **kwargs)

    async def head(self, path_or_url: str, *args, **kwargs):
        return await self.request("HEAD", path_or_url, *args, **kwargs)

    async def patch(self, path_or_url: str, *args, **kwargs):
        return await self.request("PATCH", path_or_url, *args, **kwargs)

    async def put(self, path_or_url: str, *args, **kwargs):
        return await self.request("PUT", path_or_url, *args, **kwargs)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.close_session()
        return False


class CognitiveServiceAsyncRestClient(BaseAsyncRestClient):
    """
    REST client to access Cognitive Service REST endpoints asynchronously. Authentication tokens are automatically acquired from the execution environment.

    ***Experimental***: This class is experimental and may change in future versions.

    Parameters
    ----------
    retry_config : dict, default=None
        Configuration for the retry strategy. The following keys are filled with default values if not provided:
        - total: int, default=10
        - allowed_methods: list, default=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"]
        - status_forcelist: list, default=[429, 502, 503, 504]
        - backoff_factor: int, default=1
        - raise_on_status: bool, default=False
    """
    def __init__(self, retry_config: Optional[Dict] = None):
        super().__init__()

    def _get_headers(self) -> dict:
        from synapse.ml.fabric.token_utils import TokenUtils
        openai_token = TokenUtils().get_openai_auth_header()
        if not openai_token:
            raise ValueError("OpenAI token not found")
        else:
            return {
                'Content-Type': 'application/json',
                'Authorization': openai_token
            }

    def _get_default_base_url(self) -> str:
        return _get_cognitive_service_uri()
