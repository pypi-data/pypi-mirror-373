import uuid
import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
import time
import warnings
from tqdm.auto import tqdm
from typing import Any, Dict, Iterator, Optional, TYPE_CHECKING
from sempy.fabric.exceptions import FabricHTTPException
from requests.adapters import HTTPAdapter, Retry, Response
from requests.sessions import Session
from sempy._utils._log import log_retry, log_rest_response, log_rest_request
from sempy.fabric._credentials import get_access_token, set_default_credential

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from sempy.fabric._token_provider import TokenProvider


class RetryWithLogging(Retry):
    @log_retry
    def increment(self, *args, **kwargs):
        return super().increment(*args, **kwargs)


class SessionWithLogging(Session):
    @log_rest_request
    def prepare_request(self, *args, **kwargs):
        return super().prepare_request(*args, **kwargs)


@dataclass
class OperationStatus:
    status: str
    retry_after: int
    percent_complete: int
    op_response: Response


class OperationStart:
    operation_id: str
    retry_after: int

    def __init__(self, response):
        self.operation_id = response.headers.get("x-ms-operation-id") or response.headers['Location'].split('/')[-1]
        self.retry_after = int(response.headers.get("Retry-After", 2))


class BaseRestClient(ABC):
    """
    REST client to access Fabric and PowerBI endpoints. Authentication tokens are automatically acquired from the execution environment.

    ***Experimental***: This class is experimental and may change in future versions.

    Parameters
    ----------
    token_provider : TokenProvider, default=None
        .. deprecated::
            The 'token_provider' parameter is deprecated and will be removed in a future version.
            Please use 'credential' parameter with `azure.core.credentials.TokenCredential` implementations instead.
    retry_config : dict, default=None
        Configuration for the retry strategy. The following keys are filled with default values if not provided:
        - total: int, default=10
        - allowed_methods: list, default=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"]
        - status_forcelist: list, default=[429, 502, 503, 504]
        - backoff_factor: int, default=1
        - raise_on_status: bool, default=False
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """

    def __init__(self,
                 token_provider: Optional["TokenProvider"] = None,
                 retry_config: Optional[Dict] = None,
                 credential: Optional["TokenCredential"] = None):

        # Handle deprecated token_provider parameter
        if token_provider is not None:
            warnings.warn(
                "The 'token_provider' parameter is deprecated and will be removed in a future version. "
                "Please use 'credential' parameter with `azure.core.credentials.TokenCredential` implementations instead.",
                FutureWarning,
                stacklevel=2
            )
            if credential is None:
                from azure.core.credentials import TokenCredential
                from sempy.fabric._credentials import build_access_token

                class TokenCredentialFromProvider(TokenCredential):
                    def __init__(self, token_provider: "TokenProvider"):
                        self.token_provider = token_provider

                    def get_token(self, *scopes, **kwargs):
                        return build_access_token(self.token_provider())

                credential = TokenCredentialFromProvider(token_provider)

        self.http = SessionWithLogging()

        @log_rest_response
        def validate_rest_response(response, *args, **kwargs):
            if response.status_code >= 400:
                raise FabricHTTPException(response)
        self.http.hooks["response"] = [validate_rest_response]

        retry_config = retry_config or {}
        retry_config.setdefault("total", 10)
        retry_config.setdefault("allowed_methods", ["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"])
        retry_config.setdefault("status_forcelist", [429, 502, 503, 504])
        retry_config.setdefault("backoff_factor", 1)
        retry_config.setdefault("raise_on_status", False)
        retry_strategy = RetryWithLogging(**retry_config)
        retry_adapter = HTTPAdapter(max_retries=retry_strategy)
        self.http.mount("https://", retry_adapter)

        self.credential = credential
        self.default_base_url = self._get_default_base_url()

    @abstractmethod
    def _get_default_base_url(self):
        pass

    def _get_headers(self) -> dict:
        # this could be static / a function
        correlation_id = str(uuid.uuid4())
        with set_default_credential(self.credential):
            return {
                'authorization': f'Bearer {get_access_token().token}',
                'Accept': 'application/json',
                'ActivityId': correlation_id
            }

    def request(self, method: str, path_or_url: str, *args, **kwargs):
        """
        Request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        method : str
            HTTP method.
        path_or_url : str
            The path or the url to the resource.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        headers = self._get_headers()
        headers.update(kwargs.get("headers", {}))

        # overwrite url + headers
        if path_or_url.startswith("https://"):
            url = path_or_url
        else:
            url = f"{self.default_base_url}{path_or_url}"

        kwargs["url"] = url
        kwargs["headers"] = headers

        return self.http.request(method, *args, **kwargs)

    def get(self, path_or_url: str, *args, **kwargs):
        """
        GET request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("GET", path_or_url, *args, **kwargs)

    def post(self, path_or_url: str, *args, **kwargs):
        """
        POST request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("POST", path_or_url, *args, **kwargs)

    def delete(self, path_or_url: str, *args, **kwargs):
        """
        DELETE request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("DELETE", path_or_url, *args, **kwargs)

    def head(self, path_or_url: str, *args, **kwargs):
        """
        HEAD request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("HEAD", path_or_url, *args, **kwargs)

    def patch(self, path_or_url: str, *args, **kwargs):
        """
        PATCH request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("PATCH", path_or_url, *args, **kwargs)

    def put(self, path_or_url: str, *args, **kwargs):
        """
        PUT request to the Fabric and PowerBI REST API.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        return self.request("PUT", path_or_url, *args, **kwargs)


class FabricRestClient(BaseRestClient):
    """
    REST client to access Fabric REST endpoints. Authentication tokens are automatically acquired from the execution environment.

    All methods (get, post, ...) have an additional parameter `lro_wait` that can be set to True to wait for the long-running-operation to complete.

    .. note::
        This class is ***experimental*** and may be subject to change in future versions.
        We recommend using ***only*** the functions listed below.
        Use of any other functionality is ***discouraged*** and may lead to unexpected behavior.

    .. list-table:: Supported Functions
        :header-rows: 1
        :widths: 30 30 50

        * - Resource
          - API
          - Example
        * - Capacities
          - List Capacities
          - ``GET /v1/capacities``
        * - Workspaces
          - Create Workspace
          - ``POST /v1/workspaces``
        * - Workspaces
          - Delete Workspace
          - ``DELETE /v1/workspaces/{workspaceId}``
        * - Workspaces
          - Get Workspace
          - ``GET /v1/workspaces/{workspaceId}``
        * - Workspaces
          - List Workspace
          - ``GET /v1/workspaces``
        * - Items
          - List Items
          - ``GET /v1/workspaces/{workspaceId}/items``
        * - Items
          - Create Items
          - ``POST /v1/workspaces/{workspaceId}/items``
        * - Items
          - Delete Items
          - ``DELETE /v1/workspaces/{workspaceId}/items/{itemId}``
        * - Items
          - Get Items
          - ``GET /v1/workspaces/{workspaceId}/items/{itemId}``
        * - Long Running Operations
          - Get Operation Result
          - ``GET /v1/operations/{operationId}/result``
        * - Long Running Operations
          - Get Operation State
          - ``GET /v1/operations/{operationId}``
        * - PREVIEW* Folders
          - Create Folder
          - ``POST /v1/workspaces/{workspaceId}/folders``
        * - PREVIEW* Folders
          - Delete Folder
          - ``DELETE /v1/workspaces/{workspaceId}/folders/{folderId}``
        * - PREVIEW* Folders
          - Get Folder
          - ``GET /v1/workspaces/{workspaceId}/folders/{folderId}``
        * - PREVIEW* Folders
          - List Folder
          - ``GET /v1/workspaces/{workspaceId}/folders``
        * - PREVIEW* Folders
          - Move Folder
          - ``POST /v1/workspaces/{workspaceId}/folders/{folderId}/move``
        * - PREVIEW* Folders
          - Update Folder
          - ``PATCH /v1/workspaces/{workspaceId}/folders/{folderId}``

    .. note::
        Resources labeled as PREVIEW are subject to change and may be updated or modified in future releases.

    Parameters
    ----------
    token_provider : TokenProvider, default=None
        ***DEPRECATED*** The 'token_provider' parameter is deprecated and will be removed in a future version.
        Please use 'credential' parameter with `azure.core.credentials.TokenCredential` implementations instead.
    retry_config : dict, default=None
        Configuration for the retry strategy. The following keys are filled with default values if not provided:
        - total: int, default=10
        - allowed_methods: list, default=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"]
        - status_forcelist: list, default=[429, 502, 503, 504]
        - backoff_factor: int, default=1
        - raise_on_status: bool, default=False
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    def __init__(self,
                 token_provider: Optional["TokenProvider"] = None,
                 retry_config: Optional[Dict] = None,
                 credential: Optional["TokenCredential"] = None):
        super().__init__(token_provider=token_provider, retry_config=retry_config, credential=credential)

    def _get_default_base_url(self):
        from sempy.fabric._environment import _get_fabric_rest_endpoint
        return _get_fabric_rest_endpoint()

    def request(self,
                method: str,
                path_or_url: str,
                lro_wait: Optional[bool] = False,
                lro_max_attempts: int = 10,
                lro_operation_name: Optional[str] = None,
                *args,
                **kwargs):
        """
        Request to the Fabric REST API.

        Parameters
        ----------
        method : str
            HTTP method.
        path_or_url : str
            The path or the url to the resource.
        lro_wait : bool, default=False
            If True, waits for the long-running-operation to complete.
        lro_max_attempts : int, default=10
            The maximum number of attempts to wait for the long-running-operation to complete.
        lro_operation_name : str, default=None
            The name of the operation to wait for displayed via TQDM.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        response = super().request(method, path_or_url, *args, **kwargs)

        if not lro_wait or response.status_code != 202:
            return response

        return self._wait_for_operation(lro_operation_name or path_or_url,
                                        OperationStart(response),
                                        lro_max_attempts)

    def get_paged(self, path_or_url: str, headers: Optional[Dict] = None, *args, **kwargs) -> list:
        """
        GET request to the Fabric REST API that handles pagination.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        headers : dict, default=None
            Headers to be included in the request.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        list
            The list of rows from the response.
        """
        if headers is not None:
            kwargs["headers"] = headers

        return list(self.get_paged_iterator(path_or_url, *args, **kwargs))

    def get_paged_iterator(self, path_or_url: str, *args, **kwargs) -> Iterator[Any]:
        """
        GET request to the Fabric REST API that handles pagination with iteration.

        Parameters
        ----------
        path_or_url : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Yields
        ------
        Any
            Each yield returns one individual row from the response.
        """
        headers = kwargs.pop("headers", None)
        if headers is None:
            headers = {}

        headers['Content-Type'] = 'application/json'
        response = self.get(path_or_url, *args, headers=headers, **kwargs)

        if response.status_code != 200:
            raise FabricHTTPException(response)

        while True:
            response_json = response.json()
            for row in response_json['value']:
                yield row

            continuation_uri = response_json.get("continuationUri")
            if continuation_uri is None:
                break

            response = self.get(continuation_uri, headers=headers)
            if response.status_code != 200:
                raise FabricHTTPException(response)

    def _get_operation_status(self, operation_id: str, last_percentage: int) -> OperationStatus:
        response = self.get(
            f"v1/operations/{operation_id}",
            headers={'Content-Type': 'application/json'}
        )
        response_json = response.json()

        return OperationStatus(
            response_json['status'],
            int(response.headers.get("Retry-After", 2)),
            response_json.get("percentComplete", last_percentage),
            response)

    def _wait_for_operation(self, name, operation: OperationStart, max_attempts: int = 10) -> Response:
        bar = tqdm(total=100, desc=f"Waiting {operation.retry_after} seconds for {name} operation to check for status")

        # Sometimes the response lacks `percent_complete`, so we must assure we
        # set a valid number to tqdm
        last_percentage = 0

        operation_id = operation.operation_id

        for _ in range(max_attempts):
            time.sleep(operation.retry_after)

            op_status = self._get_operation_status(operation_id, last_percentage)
            last_percentage = op_status.percent_complete

            if op_status.status in ['Failed', 'Undefined']:
                res = op_status.op_response
                raise RuntimeError(f"Operation {name} {operation_id} failed: "
                                   f"{op_status.status}. Last response was:"
                                   f"\nStatus Code: {res.status_code}"
                                   f"\nHeaders: {json.dumps(dict(res.headers), indent=2, sort_keys=True)}"
                                   f"\nBody: {json.dumps(res.json(), indent=2, sort_keys=True)}")

            if op_status.status == 'Succeeded':
                bar.set_description(f"Operation {name} successfully completed")
                bar.update(100)

                # Check if we need to retrieve the result after the LRO.
                # The LRO response will contain a "Location" header if there is a result to be retrieved.
                # Attempting to retrieve the result of an operation without an available result will result in a 400 error.
                # Reference: https://learn.microsoft.com/en-us/rest/api/fabric/articles/long-running-operation
                if "Location" not in op_status.op_response.headers:
                    return op_status.op_response

                return self.get(
                    f"v1/operations/{operation_id}/result",
                    headers={'Content-Type': 'application/json'}
                )

            bar.set_description(f"Waiting for {name} to complete: {op_status.status}")
            if op_status.percent_complete:
                bar.update(op_status.percent_complete)

        raise TimeoutError("Operation timed out.")


class PowerBIRestClient(BaseRestClient):
    """
    REST client to access PowerBI REST endpoints. Authentication tokens are automatically acquired from the execution environment.

    .. note::
        This class is ***experimental*** and may be subject to change in future versions.
        We recommend using ***only*** the functions listed below.
        Use of any other functionality is ***discouraged*** and may lead to unexpected behavior.

    .. list-table:: Supported Functions
        :header-rows: 1
        :widths: 30 30 50

        * - Resource
          - API
          - Example
        * - Apps
          - Get Apps
          - ``GET https://api.powerbi.com/v1.0/myorg/apps``
        * - Dataflow Storage Accounts
          - Get Dataflow
          - ``GET https://api.powerbi.com/v1.0/myorg/dataflowStorageAccounts``
        * - Dataflows
          - Get Dataflow
          - ``GET https://api.powerbi.com/v1.0/myorg/groups/{groupId}/dataflows/{dataflowId}``
        * - Dataflows
          - Get Dataflows
          - ``GET https://api.powerbi.com/v1.0/myorg/groups/{groupId}/dataflows``
        * - Datasets
          - Get Dataset
          - ``GET https://api.powerbi.com/v1.0/myorg/datasets/{datasetId}``
        * - Datasets
          - Get Dataset in Group
          - ``GET https://api.powerbi.com/v1.0/myorg/groups/{groupId}/datasets/{datasetId}``
        * - Datasets
          - Get Datasets
          - ``GET https://api.powerbi.com/v1.0/myorg/datasets``
        * - Gateways
          - Get Gateways
          - ``GET https://api.powerbi.com/v1.0/myorg/gateways``
        * - Groups
          - Get Group
          - ``GET https://api.powerbi.com/v1.0/myorg/groups/{groupId}``
        * - Groups
          - Get Groups
          - ``GET https://api.powerbi.com/v1.0/myorg/groups``
        * - Reports
          - Get Report
          - ``GET https://api.powerbi.com/v1.0/myorg/reports/{reportId}``
        * - Reports
          - Get Report in Group
          - ``GET https://api.powerbi.com/v1.0/myorg/groups/{groupId}/reports/{reportId}``
        * - Reports
          - Get Reports
          - ``GET https://api.powerbi.com/v1.0/myorg/reports``
        * - Reports
          - Get Reports in Group
          - ``GET https://api.powerbi.com/v1.0/myorg/groups/{groupId}/reports``

    Parameters
    ----------
    token_provider : TokenProvider, default=None
        ***DEPRECATED*** The 'token_provider' parameter is deprecated and will be removed in a future version.
        Please use 'credential' parameter with `azure.core.credentials.TokenCredential` implementations instead.
    retry_config : dict, default=None
        Configuration for the retry strategy. The following keys are filled with default values if not provided:
        - total: int, default=10
        - allowed_methods: list, default=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"]
        - status_forcelist: list, default=[429, 502, 503, 504]
        - backoff_factor: int, default=1
        - raise_on_status: bool, default=False
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    def __init__(self,
                 token_provider: Optional["TokenProvider"] = None,
                 retry_config: Optional[Dict] = None,
                 credential: Optional["TokenCredential"] = None):
        super().__init__(token_provider=token_provider, retry_config=retry_config, credential=credential)

    def _get_default_base_url(self):
        from sempy.fabric._environment import _get_fabric_rest_endpoint
        return _get_fabric_rest_endpoint()


class CognitiveServiceRestClient(BaseRestClient):
    """
    REST client to access Cognitive Service Language REST endpoints. Authentication tokens are not required.

    ***Experimental***: This class is experimental and may change in future versions.

    Parameters
    ----------
    token_provider : TokenProvider, default=None
        ***DEPRECATED*** The 'token_provider' parameter is deprecated and will be removed in a future version.
        Please use 'credential' parameter with `azure.core.credentials.TokenCredential` implementations instead.
    retry_config : dict, default=None
        Configuration for the retry strategy. The following keys are filled with default values if not provided:
        - total: int, default=10
        - allowed_methods: list, default=["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"]
        - status_forcelist: list, default=[429, 502, 503, 504]
        - backoff_factor: int, default=1
        - raise_on_status: bool, default=False
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """
    def __init__(self,
                 token_provider: Optional["TokenProvider"] = None,
                 retry_config: Optional[Dict] = None,
                 credential: Optional["TokenCredential"] = None):
        super().__init__(token_provider=token_provider, retry_config=retry_config, credential=credential)

    def _get_default_base_url(self):
        return "https://api.cognitive"

    def request(self, method: str, path_or_url: str, auth_required: bool = True, *args, **kwargs):
        """
        Request to the Cognitive Service REST API.

        Parameters
        ----------
        method : str
            HTTP method.
        path_or_url : str
            The path or the url to the resource.
        auth_required : bool, default=True
            If True, authentication is required.
        *args : list
            Arguments passed to the request method.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        requests.Response
            The response from the REST API.
        """
        if auth_required:
            headers = self._get_headers()
            headers.update(kwargs.get("headers", {}))
        else:
            headers = {}

        # overwrite url + headers
        if path_or_url.startswith("https://"):
            url = path_or_url
        else:
            url = f"{self.default_base_url}{path_or_url}"

        kwargs["url"] = url
        kwargs["headers"] = headers

        return self.http.request(method, *args, **kwargs)
