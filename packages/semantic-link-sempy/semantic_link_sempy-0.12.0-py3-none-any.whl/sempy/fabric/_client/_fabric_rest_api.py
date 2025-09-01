import base64
import json
from dataclasses import dataclass
from typing import Any, Dict, Optional, Union, TYPE_CHECKING
from urllib.parse import quote

from sempy.fabric._client._rest_client import FabricRestClient, OperationStart
from sempy.fabric.exceptions import DatasetNotFoundException, FabricHTTPException, WorkspaceNotFoundException

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


@dataclass
class JobStatus:
    status: str
    retry_after: int


class _FabricRestAPI():
    _rest_client: FabricRestClient

    def __init__(self, credential: Optional["TokenCredential"] = None):
        self._rest_client = FabricRestClient(credential=credential)

    def get_my_workspace_id(self) -> str:
        # TODO: we should align on a single API to retrieve workspaces using a single API,
        #       but we need to wait until the API support filtering and paging
        # Using new Fabric REST endpoints
        payload = self.list_workspaces()

        workspaces = [ws for ws in payload if ws["type"] == 'Personal']

        if len(workspaces) != 1:
            raise ValueError(f"Unable to resolve My workspace ID. Zero or more than one workspaces found ({len(workspaces)})")

        return workspaces[0]['id']

    def create_workspace(self, display_name: str, capacity_id: Optional[str] = None, description: Optional[str] = None) -> str:
        payload = {"displayName": display_name}

        if capacity_id is not None:
            payload["capacityId"] = capacity_id

        if description is not None:
            payload["description"] = description

        response = self._rest_client.post("v1/workspaces", json=payload)
        if response.status_code != 201:
            raise FabricHTTPException(response)

        return response.json()["id"]

    def delete_workspace(self, workspace_id: str):
        response = self._rest_client.delete(f"v1/workspaces/{workspace_id}")
        if response.status_code != 200:
            raise FabricHTTPException(response)

    def get_workspace_name_from_id(self, workspace_id: str, strict: bool = True) -> Optional[str]:
        try:
            response = self._rest_client.get(f"v1/workspaces/{workspace_id}")
        except FabricHTTPException as e:
            # suppress the not found error in non-strict mode
            if e.status_code == 404:
                if not strict:
                    return None
                else:
                    raise WorkspaceNotFoundException(workspace_id)
            raise
        return response.json()["displayName"]

    def get_workspace_id_from_name(self, workspace_name: str, strict: bool = True) -> Optional[str]:
        workspaces = self.list_workspaces()
        for workspace in workspaces:
            if workspace.get("displayName") == workspace_name:
                return workspace["id"]
        if not strict:
            return None
        raise WorkspaceNotFoundException(workspace_name)

    def create_item(self, workspace_id: str, payload, lro_max_attempts: int, lro_operation_name: str) -> str:
        path = f"v1/workspaces/{workspace_id}/items"

        response = self._rest_client.post(path,
                                          json=payload,
                                          headers={'Content-Type': 'application/json'},
                                          lro_wait=True,
                                          lro_max_attempts=lro_max_attempts,
                                          lro_operation_name=lro_operation_name)

        if response.status_code in [200, 201]:
            return response.json()["id"]
        else:
            raise FabricHTTPException(response)

    def create_lakehouse(self,
                         workspace_id: str,
                         display_name: str,
                         description: Optional[str] = None,
                         lro_max_attempts: int = 10,
                         folder_id: Optional[str] = None,
                         enable_schema: bool = False) -> str:
        payload: Dict[str, Any] = {
            "displayName": display_name,
            "type": "Lakehouse"
        }

        if enable_schema:
            payload["creationPayload"] = {
                "enableSchemas": enable_schema
            }

        if folder_id is not None:
            payload["folderId"] = folder_id

        if description is not None:
            payload["description"] = description

        return self.create_item(workspace_id, payload, lro_max_attempts, "create lakehouse")

    def delete_item(self, workspace_id: str, artifact_id: str):
        path = f"v1/workspaces/{workspace_id}/items/{artifact_id}"

        response = self._rest_client.delete(path)

        if response.status_code != 200:
            raise FabricHTTPException(response)

    def create_notebook(self,
                        workspace_id: str,
                        display_name: str,
                        description: Optional[str] = None,
                        content: Optional[str] = None,
                        lro_max_attempts: int = 10,
                        folder_id: Optional[str] = None) -> str:
        payload: dict[str, Union[str, dict]] = {
            "displayName": display_name,
            "type": "Notebook"
        }

        if description is not None:
            payload["description"] = description

        if content is not None:
            payload["definition"] = {
                "format": "ipynb",
                "parts": [
                    {
                        "path": "artifact.content.ipynb",
                        "payload": base64.b64encode(content.encode("utf-8")).decode("utf-8"),
                        "payloadType": "InlineBase64"
                    }
                ]
            }

        if folder_id is not None:
            payload["folderId"] = folder_id

        return self.create_item(workspace_id, payload, lro_max_attempts, "create notebook")

    def run_item_job(self, workspace_id: str, item_id: str, jobType: str, executionData: Optional[dict] = None) -> OperationStart:
        response = self._rest_client.post(
            f"v1/workspaces/{workspace_id}/items/{item_id}/jobs/instances?jobType={jobType}",
            data=json.dumps({"executionData": {}},),
            headers={'Content-Type': 'application/json'}
        )

        return OperationStart(response)

    def run_notebook_job(self, workspace_id: str, notebook_id: str) -> OperationStart:
        return self.run_item_job(workspace_id, notebook_id, "RunNotebook")

    def get_job_status(self, workspace_id: str, item_id: str, run_id: str) -> JobStatus:
        response = self._rest_client.get(
            f"v1/workspaces/{workspace_id}/items/{item_id}/jobs/instances/{run_id}",
            headers={'Content-Type': 'application/json'})

        if response.status_code != 200:
            raise FabricHTTPException(response)

        return JobStatus(response.json()['status'],
                         int(response.headers.get("Retry-After", 2)))

    def list_items(self, workspace_id: str, type: Optional[str] = None,
                   root_folder_id: Optional[str] = None,
                   recursive: bool = True) -> list:
        path = f"v1/workspaces/{workspace_id}/items"
        params: dict = {
            "recursive": recursive
        }

        if type is not None:
            params["type"] = quote(type)

        if root_folder_id is not None:
            params["rootFolderId"] = quote(root_folder_id)

        return self._rest_client.get_paged(path, params=params)

    def list_workspaces(self, roles: Optional[str] = None) -> list:
        path = "v1/workspaces"
        params = {}
        if roles is not None:
            params["roles"] = roles
        return self._rest_client.get_paged(path, params=params if params else None)

    def list_capacities(self) -> list:
        return self._rest_client.get_paged("v1/capacities")

    def list_dataflows(self, workspace_id: str) -> list:
        return self._rest_client.get_paged(f"v1/workspaces/{workspace_id}/dataflows")

    def list_reports(self, workspace_id: str) -> list:
        return self._rest_client.get_paged(f"v1/workspaces/{workspace_id}/reports")

    def list_datasets(self, workspace_id: str) -> list:
        return self._rest_client.get_paged(f"v1/workspaces/{workspace_id}/semanticModels")

    def get_dataset_by_id(self, workspace_id: str, dataset_id: str) -> dict:
        response = self._rest_client.get(f"v1/workspaces/{workspace_id}/semanticModels/{dataset_id}")
        return response.json()

    def get_dataset_by_name(self, workspace_id: str, dataset_name: str) -> dict:
        for dataset in self._rest_client.get_paged_iterator(f"v1/workspaces/{workspace_id}/semanticModels"):
            if dataset.get("displayName") == dataset_name:
                return dataset
        raise DatasetNotFoundException(dataset_name, workspace_id)

    def list_folders(self, workspace_id: str,
                     root_folder_id: Optional[str] = None,
                     recursive: bool = True) -> list:
        path = f"v1/workspaces/{workspace_id}/folders"

        params: dict = {
            "recursive": recursive
        }

        if root_folder_id is not None:
            params["rootFolderId"] = quote(root_folder_id)

        return self._rest_client.get_paged(path, params=params)

    def create_folder(self, workspace_id: str, payload: dict) -> str:
        path = f"v1/workspaces/{workspace_id}/folders"

        response = self._rest_client.post(path,
                                          json=payload,
                                          headers={'Content-Type': 'application/json'})

        if response.status_code != 201:
            raise FabricHTTPException(response)

        return response.json()["id"]

    def get_folder(self, workspace_id: str, folder_id: str) -> dict:
        path = f"v1/workspaces/{workspace_id}/folders/{folder_id}"
        response = self._rest_client.get(path)

        if response.status_code != 200:
            raise FabricHTTPException(response)

        return response.json()

    def delete_folder(self, workspace_id: str, folder_id: str):
        path = f"v1/workspaces/{workspace_id}/folders/{folder_id}"

        response = self._rest_client.delete(path)

        if response.status_code != 200:
            raise FabricHTTPException(response)

    def move_folder(self, workspace_id: str, folder_id: str, target_folder_id: Optional[str] = None):
        path = f"v1/workspaces/{workspace_id}/folders/{folder_id}/move"
        payload = {}

        if target_folder_id is not None:
            payload = {
                "targetFolderId": target_folder_id
            }

        response = self._rest_client.post(path,
                                          json=payload,
                                          headers={'Content-Type': 'application/json'})

        if response.status_code != 200:
            raise FabricHTTPException(response)

    def update_folder(self, workspace_id: str, folder_id: str, payload: dict):
        path = f"v1/workspaces/{workspace_id}/folders/{folder_id}"

        response = self._rest_client.patch(path,
                                           json=payload,
                                           headers={'Content-Type': 'application/json'})

        if response.status_code != 200:
            raise FabricHTTPException(response)
