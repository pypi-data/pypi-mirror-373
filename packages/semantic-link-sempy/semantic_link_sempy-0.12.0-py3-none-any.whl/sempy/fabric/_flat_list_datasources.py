import pandas as pd
from uuid import UUID

from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._client._utils import _init_analysis_services
from sempy.fabric._utils import collection_to_dataframe
from sempy._utils._log import log

from typing import List, Optional, Union


@log
def list_datasources(
    dataset: Union[str, UUID],
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None
) -> pd.DataFrame:
    """
    List all datasources in a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `datasource <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.datasource?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing all datasources.
    """
    _init_analysis_services()

    from Microsoft.AnalysisServices.Tabular import DataSourceType

    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset)

    extraction_def = [
        ("Data Source Name",   lambda r: r.Name,            "str"),  # noqa: E272
        ("Type",               lambda r: r.Type.ToString(), "str"),  # noqa: E272
        ("MaxConnections",     lambda r: r.MaxConnections,  "str"),  # noqa: E272
        ("Description",        lambda r: r.Description,     "str"),  # noqa: E272

        # Provider Data Source
        ("Account",            lambda r: r.Account                      if r.Type == DataSourceType.Provider else None, "str"),  # noqa: E272
        ("Connection String",  lambda r: r.ConnectionString             if r.Type == DataSourceType.Provider else None, "str"),  # noqa: E272
        ("Impersonation Mode", lambda r: r.ImpersonationMode.ToString() if r.Type == DataSourceType.Provider else None, "str"),  # noqa: E272
        ("Isolation",          lambda r: r.Isolation.ToString()         if r.Type == DataSourceType.Provider else None, "str"),  # noqa: E272
        ("Provider",           lambda r: r.Provider                     if r.Type == DataSourceType.Provider else None, "str"),  # noqa: E272

        # Structured Data Source
        ("Connection Details Protocol", lambda r: r.ConnectionDetails.Protocol if r.Type == DataSourceType.Structured else None, "str"),  # noqa: E272
        ("Credential Username",         lambda r: r.Credential.Username        if r.Type == DataSourceType.Structured else None, "str"),  # noqa: E272
    ]

    collection = database.Model.DataSources

    return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)
