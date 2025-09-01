import pandas as pd
from uuid import UUID

from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._utils import collection_to_dataframe
from sempy._utils._log import log

from typing import List, Optional, Union


@log
def list_perspectives(
    dataset: Union[str, UUID],
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None
) -> pd.DataFrame:
    """
    List all perspectives in a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `perspective <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.perspective?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing all perspectives.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset)

    extraction_def = [
        ("Perspective Name", lambda r: r[0].Name, "str"),             # noqa: E272
        ("Table Name",       lambda r: r[1].Name, "str"),             # noqa: E272
        ("Object Name",      lambda r: r[3].Name, "str"),             # noqa: E272
        ("Object Type",      lambda r: r[2],      "str"),             # noqa: E272
    ]

    collection = [
        (p, pt, objectType, object)
        for p in database.Model.Perspectives
        for pt in p.PerspectiveTables
        for (objectType, object) in [
            *[("Column", c) for c in pt.PerspectiveColumns],
            *[("Measure", m) for m in pt.PerspectiveMeasures],
            *[("Hierarchy", h) for h in pt.PerspectiveHierarchies]
        ]
    ]

    return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)
