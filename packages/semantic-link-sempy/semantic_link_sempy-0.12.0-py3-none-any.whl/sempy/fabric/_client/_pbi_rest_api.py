import json
import datetime
import time
import tqdm
from urllib.parse import urljoin, urlparse

from sempy.fabric.exceptions import FabricHTTPException, DatasetNotFoundException, WorkspaceNotFoundException
from sempy.fabric._utils import is_valid_uuid
from sempy.fabric._client._utils import _odata_quote
from sempy.fabric._client._rest_client import PowerBIRestClient
from sempy.fabric._environment import _get_workspace_path
from sempy._utils._log import log
from urllib.parse import quote
import requests

from typing import Any, Optional, List, Tuple, Dict, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class _PBIRestAPI():
    _rest_client: PowerBIRestClient

    def __init__(self, credential: Optional["TokenCredential"] = None):
        self._rest_client = PowerBIRestClient(credential=credential)

    def _parse_odata_response(self, response: requests.Response):
        if response.status_code != 200:
            raise FabricHTTPException(response)

        value = response.json().get('value')
        if value is None or len(value) == 0:
            return None
        else:
            return value

    def list_workspaces(self, filter: Optional[str] = None, top: Optional[int] = None, skip: Optional[int] = None):
        params = []

        path = "v1.0/myorg/groups"
        if filter is not None:
            params.append(f"$filter={filter}")
        if top is not None:
            params.append(f"$top={top}")
        if skip is not None:
            params.append(f"$skip={skip}")

        if len(params) > 0:
            path += "?" + "&".join(params)

        return self._parse_odata_response(self._rest_client.get(path))

    def list_gateways(self):
        path = "v1.0/myorg/gateways"
        return self._parse_odata_response(self._rest_client.get(path))

    def list_dataflows(self, workspace_name: str, workspace_id: str):
        path = _get_workspace_path(workspace_name, workspace_id) + "dataflows"
        return self._parse_odata_response(self._rest_client.get(path))

    def list_dataflow_storage_accounts(self):
        path = "/v1.0/myorg/dataflowStorageAccounts"
        return self._parse_odata_response(self._rest_client.get(path))

    def list_apps(self):
        path = "v1.0/myorg/apps"
        return self._parse_odata_response(self._rest_client.get(path))

    def get_workspace_id_from_name(self, workspace_name: str, strict: bool = True) -> Optional[str]:
        value = self.list_workspaces(f"name eq '{_odata_quote(workspace_name)}'")
        if value is None:
            if not strict:
                return None
            else:
                raise WorkspaceNotFoundException(workspace_name)
        return value[0]['id']

    def get_workspace_name_from_id(self, workspace_id: str, strict: bool = True) -> Optional[str]:
        # We got shot in the foot by an empty string, which retrieves all workspaces
        # and results in unexpected format of the response, so validate:
        if not is_valid_uuid(workspace_id):
            raise ValueError(f"Invalid UUID '{workspace_id}' in \"workspace_id\"")

        try:
            response = self._rest_client.get(f"v1.0/myorg/groups/{workspace_id}")
            return response.json()['name']
        except FabricHTTPException as e:
            if e.status_code == 401:
                if "Calling group APIs not permitted for personal workspace" in e.error_text:
                    return "My workspace"
                else:
                    # With user token, if the GUID is does not exist, PBI REST
                    # returns "Unauthorized", which goes against more common
                    # practice of 404 "Not found".
                    if not strict:
                        return None
                    raise WorkspaceNotFoundException(workspace_id)
            elif e.status_code == 404:
                # With App token (e.g. Service Principal), PBI REST returns 404
                # PowerBIEntityNotFound for non-existent workspace GUID
                if not strict:
                    return None
                raise WorkspaceNotFoundException(workspace_id)
            else:
                raise

    def get_workspace_datasets(self, workspace_name: str, workspace_id: str):
        path = _get_workspace_path(workspace_name, workspace_id) + "datasets"
        res = self._rest_client.get(path)
        return res.json()["value"]

    @staticmethod
    def create_refresh_body(
        refresh_type,
        max_parallelism,
        commit_mode,
        retry_count,
        apply_refresh_policy,
        effective_date,
        objects: Optional[List] = None
    ) -> dict:
        # validating values in 'objects' argument
        if objects is not None:
            for table in objects:
                if not isinstance(table, dict):
                    raise ValueError("Each element in the 'objects' list must be a dictionary.")
                if "table" not in table:
                    raise ValueError("Each dictionary in the 'objects' list must include a 'table' key.")
                elif not isinstance(table["table"], str):
                    raise ValueError("The 'table' value in each dictionary (if present) must be a string.")
                if "partition" in table and not isinstance(table["partition"], str):
                    raise ValueError("The 'partition' value in each dictionary (if present) must be a string.")

        # preprocessing of date value
        date_str = effective_date.strftime("%Y-%m-%dT%H:%M:%S")
        data_structure = {
            "type": refresh_type,
            "commitMode": commit_mode,
            "maxParallelism": max_parallelism,
            "retryCount": retry_count,
            "applyRefreshPolicy": apply_refresh_policy,
            "effectiveDate": date_str,
            "objects": objects
        }
        return data_structure

    def refresh_post(
            self,
            dataset_id: str,
            workspace_id: str,
            workspace_name: str,
            refresh_type: str = "automatic",
            max_parallelism: int = 10,
            commit_mode: str = "transactional",
            retry_count: int = 0,
            objects: Optional[List] = None,
            apply_refresh_policy: bool = True,
            effective_date: datetime.date = datetime.date.today(),
            verbose: int = 0
    ) -> str:

        path = _get_workspace_path(workspace_name, workspace_id)
        path += f"datasets/{dataset_id}/refreshes"
        body = _PBIRestAPI.create_refresh_body(refresh_type, max_parallelism, commit_mode, retry_count,
                                               apply_refresh_policy, effective_date, objects)
        json_dumps_params = json.dumps(body)
        response = self._rest_client.post(path, data=json_dumps_params, headers={'Content-Type': 'application/json'})
        poll_url = None
        if getattr(response, 'headers', None) is not None:
            poll_url = response.headers.get('Location')
            request_id = response.headers.get('RequestId')
            if verbose:
                print(f"request id: {request_id}")

        if poll_url is None:
            raise ValueError("Poll URL not found in the response.")
        return poll_url

    def get_refresh_execution_details(
            self,
            dataset_id: str,
            request_id: str,
            workspace_id: str,
            workspace_name: str
            ) -> dict:
        # https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-execution-details#datasetrefreshdetail

        path = _get_workspace_path(workspace_name, workspace_id)
        path += f"datasets/{dataset_id}/refreshes/{request_id}"

        response = self._rest_client.get(path)
        if response.status_code not in [200, 202]:
            raise ValueError(f"Failed to retrieve refresh status for {dataset_id}. Response code: {response.status_code} {response.text}")

        return response.json()

    def list_refresh_history(
            self,
            dataset_id: str,
            workspace_id: str,
            workspace_name: str,
            top_n: Optional[int] = None
    ) -> dict:
        # https://learn.microsoft.com/en-us/rest/api/power-bi/datasets/get-refresh-history

        path = _get_workspace_path(workspace_name, workspace_id)
        path += f"/datasets/{dataset_id}/refreshes"

        if top_n is not None:
            path = path + f"?$top={top_n}"

        response = self._rest_client.get(path)
        if response.status_code not in [200, 202]:
            raise ValueError(f"Failed to retrieve refresh status for {dataset_id}. Response code: {response.status_code} {response.text}")

        return response.json()["value"]

    def get_dataset_name_from_id(self, dataset_id: str, workspace_id: str, workspace_name: str) -> str:
        try:
            res = self._rest_client.get(f"v1.0/myorg/datasets/{dataset_id}")
        except FabricHTTPException as e:
            if e.status_code == 404:
                raise DatasetNotFoundException(dataset_id, workspace_name)
            elif e.status_code == 403:
                # APP based token (e.g. Service Principal) does not have access to the myorg/datasets endpoint,
                # so we need to use the workspace path instead
                try:
                    path = urljoin(f"{_get_workspace_path(workspace_name, workspace_id)}", f"datasets/{dataset_id}")
                    res = self._rest_client.get(path)
                except FabricHTTPException as e2:
                    if e2.status_code == 404:
                        raise DatasetNotFoundException(dataset_id, workspace_name)
                    elif e2.status_code == 401:
                        raise WorkspaceNotFoundException(workspace_id)
                    else:
                        raise e2
            else:
                raise
        return res.json()["name"]

    def execute_dax_query(self, dataset_id: str, query: str, num_rows: Optional[int] = None):
        path = f"v1.0/myorg/datasets/{dataset_id}/executeQueries"
        payload = {
            "queries": [{
                "query": f"{query}"
            }]
        }
        res = self._rest_client.post(path, json=payload)
        rows = res.json()["results"][0]["tables"][0]["rows"]

        # limit the number of rows (can't push it into executeQueries without modifying the actual DAX query)
        if num_rows:
            rows = rows[:num_rows]

        return rows

    def calculate_measure(
        self,
        dataset_id: str,
        measure: List[Dict[str, str]],
        groupby_columns: List[Dict[str, str]],
        filters: List[Dict[str, list]],
        num_rows: Optional[int],
        verbose: int
    ) -> Tuple[List[dict], List[list]]:

        # The REST API returns empty results as an error saying "Query evaluation produced no result".
        # We want to return an empty dataframe in this case to match XMLA output.

        def is_empty_result(res: requests.Response) -> bool:
            # if no response is returned, we return false to let the exception propagate
            if res is None:
                return False

            # if the response is not a valid JSON, we return false to let the exception propagate
            if "application/json" not in res.headers.get("Content-Type", ""):
                return False

            error = res.json().get("error", None)

            if error:
                # navigate through dictionary in defensive way
                value = error
                for p in ["pbi.error", "details", 0, "detail", "value"]:
                    if isinstance(p, str) and p not in value:
                        value = None
                        break
                    elif isinstance(p, int) and len(value) <= int(p):
                        value = None
                        break
                    else:
                        value = value[p]

                if value == "Query evaluation produced no result":
                    return True

            return False

        redirect_host = ""
        try:
            res = self._retrieve_measure(dataset_id, measure, groupby_columns, filters, num_rows, verbose)

        except FabricHTTPException as e:
            # Calling to public api (e.g. fabric.microsoft.com) returns 401 Unauthorized
            # Hence we need to redirect to the powerbi home cluster
            if e.status_code == 401 and (
                e.response.headers.get("Location") is not None
                or e.response.headers.get("home-cluster-uri") is not None
            ):
                redirect_host = e.response.headers.get("home-cluster-uri", "") or e.response.headers.get("Location", "")
                redirect_host = str(urlparse(redirect_host).netloc)

                if not redirect_host:
                    raise e

                redirect_host = f"https://{redirect_host}"

                try:
                    res = self._retrieve_measure(dataset_id, measure, groupby_columns, filters, num_rows, verbose,
                                                 redirect_host=redirect_host)
                except FabricHTTPException as e2:
                    if is_empty_result(e2.response):
                        return [], []
                    raise e2

            elif is_empty_result(e.response):
                return [], []

            else:
                raise e

        if is_empty_result(res):
            return [], []

        res = res.json()
        rows = res["rows"]
        columns = res["columns"]

        while "continuationToken" in res:
            cont_token = res["continuationToken"]
            res = self._retrieve_measure(dataset_id, measure, groupby_columns, filters, num_rows, verbose, cont_token=cont_token,
                                         redirect_host=redirect_host)
            res = res.json()
            rows.extend(res["rows"])

        return columns, rows

    def _retrieve_measure(
        self,
        dataset_id: str,
        measure_obj: List[Dict[str, str]],
        groupby_columns_obj: List[Dict[str, str]],
        filter_obj: List[Dict[str, list]],
        num_rows: Optional[int],
        verbose: int,
        cont_token: str = "",
        redirect_host: str = "",
    ):
        path = urljoin(redirect_host, "v1.0/myOrg/internalMetrics/query")
        payload = {
            "provider": {
                "datasetId": dataset_id
            },
            "metrics": measure_obj,
            "groupBy": groupby_columns_obj,
            "filters": filter_obj,
            "paginationSettings": {
                "continuationToken": cont_token
            },
            "top": num_rows
        }

        if verbose > 0:
            print(f"Executing REST query with payload: {json.dumps(payload, indent=2)}")
        return self._rest_client.post(path, json=payload, headers={"App-Name": "SemPy"})

    @log
    def upload_pbix(self, dataset_name: str, pbix: bytes, workspace_id: str, workspace_name: str, skip_report: bool = True):
        path = _get_workspace_path(workspace_name, workspace_id)

        path = f"{path}/imports?datasetDisplayName={quote(dataset_name)}"
        path += f"&nameConflict=CreateOrOverwrite&skipReport={skip_report}&overrideReportLabel=true&overrideModelLabel=true"

        payload: Any = {}
        files = [('', (dataset_name, pbix, 'application/octet-stream'))]

        response = self._rest_client.post(path, data=payload, files=files)

        if response.status_code != 202:
            raise Exception(f"Importing of '{dataset_name}' not accepted. Response code: {response.status_code}")

        attempts = 0
        sleep_factor = 1.5
        while attempts < 10:
            response = self._rest_client.get(path, data=payload, files=files)
            if response.status_code == 200:
                time.sleep(30)
                break
            time.sleep(sleep_factor ** attempts)
            attempts += 1

        if attempts == 10:
            raise TimeoutError("Dataset upload to workspace timed out.")

    def get_dataset_storage_mode(self, dataset_id: str) -> str:
        response = self._rest_client.get(f"/v1.0/myorg/datasets/{dataset_id}")

        if response.status_code != 200:
            raise FabricHTTPException(response)

        storage_mode = response.json().get("targetStorageMode", "")
        if not storage_mode:
            raise ValueError(f"Unknown storage mode of dataset {dataset_id}")

        return storage_mode

    def update_dataset_storage_mode(self, dataset_id: str, target_storage_mode: Union[str, int]):
        if type(target_storage_mode) is str:
            target_storage_mode = target_storage_mode.lower()

        # standardize the input storage mode
        if target_storage_mode in [1, "small", "abf"]:
            target_storage_mode = "Abf"
        elif target_storage_mode in [2, "large", "premiumfiles"]:
            target_storage_mode = "PremiumFiles"

        # validate the input storage mode
        if target_storage_mode not in ["Abf", "PremiumFiles"]:
            raise ValueError("Invalid target_storage_mode. Valid options: "
                             "{1 | 'Small' | 'Abf', 2 | 'Large' | 'PremiumFiles'}")

        # no need to update
        if self.get_dataset_storage_mode(dataset_id) == target_storage_mode:
            return

        # update
        path = f"v1.0/myorg/datasets/{dataset_id}"

        response = self._rest_client.patch(path, json={"targetStorageMode": target_storage_mode})

        if response.status_code != 200:
            raise Exception(f"Failed to update targetStorageMode for {dataset_id}. Response code: {response.status_code}")

        # wait for update to finish
        for _ in tqdm.tqdm(range(20), f"Waiting for storage conversion to finish of {dataset_id}"):
            storage_mode = self.get_dataset_storage_mode(dataset_id)

            if storage_mode == target_storage_mode:
                return

            time.sleep(2)

        raise TimeoutError("Updating targetStorageMode timed out.")

    def list_reports(self, workspace_name: str, workspace_id: str):
        path = _get_workspace_path(workspace_name, workspace_id) + "reports"
        res = self._rest_client.get(path)

        if res.status_code != 200:
            raise ValueError(f"Failed to retrieve reports from workspace '{workspace_id}': {res.status_code}")

        return res.json()["value"]
