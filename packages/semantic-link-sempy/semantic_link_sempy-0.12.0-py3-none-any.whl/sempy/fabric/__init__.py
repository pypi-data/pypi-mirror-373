from .._utils._telemetry import log_telemetry

from sempy.fabric._credentials import set_service_principal
from sempy.fabric._flat import (
    create_folder,
    create_lakehouse,
    create_tom_server,
    create_trace_connection,
    create_notebook,
    create_workspace,
    delete_folder,
    delete_item,
    evaluate_dax,
    evaluate_measure,
    execute_xmla,
    execute_tmsl,
    get_roles,
    get_row_level_security_permissions,
    get_refresh_execution_details,
    get_tmsl,
    list_items,
    list_capacities,
    list_datasets,
    list_expressions,
    list_folders,
    list_measures,
    list_refresh_requests,
    list_relationship_violations,
    list_reports,
    list_tables,
    list_translations,
    list_workspaces,
    move_folder,
    plot_relationships,
    read_table,
    refresh_dataset,
    refresh_tom_cache,
    rename_folder,
    resolve_workspace_id,
    resolve_workspace_name,
    resolve_workspace_name_and_id,
    resolve_dataset_id,
    resolve_dataset_name,
    resolve_dataset_name_and_id,
    resolve_folder_id,
    resolve_folder_path,
    resolve_item_id,
    resolve_item_name,
    run_notebook_job,
    _trace_evaluate_dax
)
from sempy.fabric._flat_list_annotations import list_annotations
from sempy.fabric._flat_list_apps import list_apps
from sempy.fabric._flat_list_calculation_items import list_calculation_items
from sempy.fabric._flat_list_columns import list_columns
from sempy.fabric._flat_list_dataflows import list_dataflows, list_dataflow_storage_accounts
from sempy.fabric._flat_list_datasources import list_datasources
from sempy.fabric._flat_list_gateways import list_gateways
from sempy.fabric._flat_list_hierarchies import list_hierarchies
from sempy.fabric._flat_list_relationships import list_relationships
from sempy.fabric._flat_list_partitions import list_partitions
from sempy.fabric._flat_list_perspectives import list_perspectives
from sempy.fabric._client import translate_semantic_model
from sempy.fabric._client._rest_client import FabricRestClient, PowerBIRestClient, CognitiveServiceRestClient
from sempy.fabric._client._tom import connect_semantic_model, get_model_calc_dependencies, ModelCalcDependencies, TOMWrapper
from sempy.fabric._dataframe._fabric_dataframe import FabricDataFrame, read_parquet
from sempy.fabric._dataframe._fabric_series import FabricSeries
from sempy.fabric._datacategory import DataCategory
from sempy.fabric._metadatakeys import MetadataKeys
from sempy.fabric._environment import get_lakehouse_id, get_workspace_id, get_artifact_id, get_notebook_workspace_id
from sempy.fabric._client._refresh_execution_details import RefreshExecutionDetails
from sempy.fabric._trace._trace import Trace
from sempy.fabric._trace._trace_connection import TraceConnection
from sempy.fabric._vertipaq import model_memory_analyzer
from sempy.fabric._bpa import run_model_bpa

__all__ = [
    "DataCategory",
    "FabricDataFrame",
    "FabricRestClient",
    "FabricSeries",
    "MetadataKeys",
    "ModelCalcDependencies",
    "PowerBIRestClient",
    "CognitiveServiceRestClient",
    "RefreshExecutionDetails",
    "TOMWrapper",
    "Trace",
    "TraceConnection",
    "connect_semantic_model",
    "create_folder",
    "create_lakehouse",
    "create_trace_connection",
    "create_notebook",
    "create_tom_server",
    "create_workspace",
    "delete_folder",
    "delete_item",
    "evaluate_dax",
    "evaluate_measure",
    "execute_xmla",
    "execute_tmsl",
    "get_lakehouse_id",
    "get_model_calc_dependencies",
    "get_notebook_workspace_id",
    "get_artifact_id",
    "get_refresh_execution_details",
    "get_roles",
    "get_row_level_permissions",
    "get_row_level_security_permissions",
    "get_tmsl",
    "get_workspace_id",
    "list_annotations",
    "list_apps",
    "list_items",
    "list_capacities",
    "list_calculation_items",
    "list_columns",
    "list_datasets",
    "list_dataflows",
    "list_datasources",
    "list_expressions",
    "list_folders",
    "list_gateways",
    "list_hierarchies",
    "list_measures",
    "list_partitions",
    "list_perspectives",
    "list_refresh_requests",
    "list_relationship_violations",
    "list_relationships",
    "list_reports",
    "list_tables",
    "list_translations",
    "list_workspaces",
    "list_dataflow_storage_accounts",
    "move_folder",
    "plot_relationships",
    "read_parquet",
    "read_table",
    "refresh_dataset",
    "refresh_tom_cache",
    "rename_folder",
    "resolve_workspace_id",
    "resolve_workspace_name",
    "resolve_workspace_name_and_id",
    "resolve_dataset_id",
    "resolve_dataset_name",
    "resolve_dataset_name_and_id",
    "resolve_folder_id",
    "resolve_folder_path",
    "resolve_item_id",
    "resolve_item_name",
    "run_model_bpa",
    "run_notebook_job",
    "set_service_principal",
    "translate_semantic_model",
    "model_memory_analyzer",
    "_trace_evaluate_dax"
]

# log telemetry
log_telemetry(activity_name="sempy.fabric")
