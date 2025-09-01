import os
from typing import Dict, Optional, cast
from urllib.parse import quote, urlparse

from fabric.analytics.environment.context import FabricContext
from fabric.analytics.environment.plugin_provider import NoAvailableProvider

on_fabric: Optional[bool] = None
on_jupyter: Optional[bool] = None
on_spark: Optional[bool] = None
on_aiskill: Optional[bool] = None
jupyter_config: Optional[Dict[str, str]] = None


def _on_fabric() -> bool:
    """True if running on Fabric (spark or jupyter or ai skill)"""
    global on_fabric
    if on_fabric is None:
        on_fabric = _on_spark() or _on_jupyter() or _on_aiskill()
    return on_fabric


def _on_jupyter() -> bool:
    global on_jupyter
    if on_jupyter is None:
        try:
            from fabric.analytics.environment.notebook_plugin.utils import is_pure_python_env
            on_jupyter = is_pure_python_env()
        except ImportError:
            on_jupyter = False
    return on_jupyter


def _on_spark() -> bool:
    global on_spark
    if on_spark is None:
        try:
            from fabric.analytics.environment.notebook_plugin.utils import is_fabric_spark
            on_spark = is_fabric_spark()
        except ImportError:
            on_spark = False
    return on_spark


def _on_aiskill() -> bool:
    global on_aiskill
    if on_aiskill is None:
        on_aiskill = os.environ.get("trident.aiskill.env", "").lower() == "true"
    return on_aiskill


def get_workspace_id() -> str:
    """
    Return workspace id or default Lakehouse's workspace id.

    Returns
    -------
    str
        Workspace id guid if no default Lakehouse is set; otherwise, the default Lakehouse's workspace id guid.
    """

    ctx = FabricContext()
    try:
        return (
            ctx.artifact_context.attached_lakehouse_workspace_id
            or ctx.workspace_id
            or ""
        )
    except NoAvailableProvider:
        return _get_fabric_context("trident.workspace.id")


def get_lakehouse_id() -> str:
    """
    Return lakehouse id of the lakehouse that is connected to the workspace.

    Returns
    -------
    str
        Lakehouse id guid.
    """
    ctx = FabricContext()
    try:
        return ctx.artifact_context.attached_lakehouse_id or ""
    except NoAvailableProvider:
        return _get_fabric_context("trident.lakehouse.id")


def get_notebook_workspace_id() -> str:
    """
    Return notebook workspace id.

    Returns
    -------
    str
        Workspace id guid.
    """
    ctx = FabricContext()
    try:
        return ctx.workspace_id or ""
    except NoAvailableProvider:
        return _get_fabric_context("trident.artifact.workspace.id")


def get_artifact_id() -> str:
    """
    Return artifact id.

    Returns
    -------
    str
        Artifact (most commonly notebook) id guid.
    """
    ctx = FabricContext()
    try:
        return ctx.artifact_context.artifact_id or ""
    except NoAvailableProvider:
        return _get_fabric_context("trident.artifact.id")


def _get_artifact_type() -> str:
    """
    Return artifact type.

    Returns
    -------
    str
        Artifact type e.g. "SynapseNotebook".
    """
    ctx = FabricContext()
    try:
        return ctx.artifact_context.artifact_type or ""
    except NoAvailableProvider:
        return _get_fabric_context('trident.artifact.type')


def _get_onelake_endpoint() -> str:
    """
    Return onelake endpoint for the lakehouse.

    Returns
    -------
    str
        Onelake endpoint.
    """
    ctx = FabricContext()
    try:
        onelake_url = ctx.onelake_endpoint or ""
    except NoAvailableProvider:
        onelake_url = ""

    if not onelake_url:
        onelake_url = _get_fabric_context("fs.defaultFS")

    return urlparse(onelake_url).netloc.split("@")[-1]


def _get_fabric_context(key: str) -> str:
    """
    Retrieves the value from the Fabric context.

    Parameters
    ----------
    key : str
        The key for the Fabric context value.

    Returns
    -------
    str
        The retrieved value associated with the given key
    """
    if not _on_fabric():
        return ""

    global jupyter_config
    jupyter_config = jupyter_config or {}

    if key not in jupyter_config:
        try:
            from synapse.ml.internal_utils.session_utils import \
                get_fabric_context  # type: ignore
            jupyter_config.update(get_fabric_context())
        except (ImportError, AttributeError):
            return ""

    return jupyter_config.get(key, "")


def _get_pbi_uri() -> str:
    return _get_fabric_rest_endpoint().replace("https://", "powerbi://")


def _get_cognitive_service_uri() -> str:
    from packaging import version
    from synapse.ml.fabric.service_discovery import get_fabric_env_config
    from synapse.ml.internal_utils import __version__

    from sempy.fabric._utils import validate_url

    if version.parse(__version__) >= version.parse("1.0.21"):
        cfg = get_fabric_env_config(with_tokens=False)
    else:
        cfg = get_fabric_env_config()

    if not cfg or not cfg.fabric_env_config:
        url = ""
    else:
        url = cfg.fabric_env_config.get_cognitive_workload_endpoint() or ""
    return validate_url(url)


def _get_fabric_rest_endpoint() -> str:
    from sempy.fabric._utils import normalize_url

    ctx = FabricContext()
    try:
        url = ctx.pbi_shared_host or ""
    except NoAvailableProvider:
        from synapse.ml.fabric.service_discovery import get_fabric_env_config
        url = get_fabric_env_config(with_tokens=False).fabric_env_config.shared_host

    if not url:
        raise ValueError("Cannot retrieve Fabric REST endpoint.")

    # always end with "/" to avoid joining issues
    return normalize_url(url).rstrip("/") + "/"


def _get_workspace_url(workspace: str) -> str:
    url = f"{_get_pbi_uri()}v1.0/myorg/"
    if workspace == "My workspace":
        return url
    else:
        return f"{url}{quote(workspace, safe='')}"


def _get_workspace_path(workspace_name: str, workspace_id: str):
    if workspace_name == "My workspace":
        # retrieving datasets from "My workspace" (does not have a group GUID) requires a different query
        return "v1.0/myorg/"
    else:
        return f"v1.0/myorg/groups/{workspace_id}/"


def _get_onelake_abfss_path(workspace_id: Optional[str] = None, dataset_id: Optional[str] = None) -> str:
    workspace_id = get_workspace_id() if workspace_id is None else workspace_id
    dataset_id = get_lakehouse_id() if dataset_id is None else dataset_id
    onelake_endpoint = _get_onelake_endpoint()
    return f"abfss://{workspace_id}@{onelake_endpoint}/{dataset_id}"


def _get_environment() -> str:
    ctx = FabricContext()
    try:
        environment = cast(str, ctx.internal_context.rollout_stage)
    except NoAvailableProvider:
        environment = cast(str, _get_fabric_context("spark.trident.pbienv"))

    if not environment:
        environment = "msit"

    return cast(str, environment.lower().strip())


def _get_fabric_run_id() -> str:
    return _get_fabric_context("trident.aiskill.fabric_run_id") or ""


def _get_root_activity_id() -> str:
    return _get_fabric_context("trident.aiskill.root_activity_id") or ""
