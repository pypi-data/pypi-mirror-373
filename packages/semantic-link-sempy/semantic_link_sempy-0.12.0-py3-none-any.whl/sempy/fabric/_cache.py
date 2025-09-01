import threading
from uuid import UUID

from sempy.fabric._client import WorkspaceClient
from sempy.fabric._client._fabric_rest_api import _FabricRestAPI
from typing import cast, Dict, Optional, Union


_workspace_clients: Dict[str, WorkspaceClient] = dict()
_workspace_clients_lock = threading.RLock()
_fabric_rest_api: Optional[_FabricRestAPI] = None
_fabric_rest_api_lock = threading.RLock()


def _get_or_create_workspace_client(workspace: Optional[Union[str, UUID]] = None) -> WorkspaceClient:
    # Resolve the workspace ID if the input is None to avoid creating
    # duplicate clients of the default workspace
    if workspace is None:
        from sempy.fabric._environment import get_workspace_id
        workspace = get_workspace_id()

    workspace = cast(str, str(workspace))

    if workspace in _workspace_clients:
        return _workspace_clients[workspace]

    with _workspace_clients_lock:
        if workspace in _workspace_clients:
            return _workspace_clients[workspace]

        client = WorkspaceClient(workspace)
        _workspace_clients[client.get_workspace_name()] = client
        _workspace_clients[client.get_workspace_id()] = client

    return client


def _get_fabric_rest_api() -> _FabricRestAPI:
    global _fabric_rest_api

    if _fabric_rest_api is not None:
        return _fabric_rest_api

    with _fabric_rest_api_lock:

        if _fabric_rest_api is not None:
            return _fabric_rest_api

        # cache FabricRestAPI client to re-use HTTP socket
        _fabric_rest_api = _FabricRestAPI()

    return _fabric_rest_api
