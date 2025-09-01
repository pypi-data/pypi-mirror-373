import pandas as pd
from uuid import UUID

from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._utils import collection_to_dataframe
from sempy._utils._log import log
from sempy.fabric._credentials import with_credential

from typing import List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


@log
@with_credential
def list_annotations(
    dataset: Union[str, UUID],
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None,
    credential: Optional["TokenCredential"] = None
) -> pd.DataFrame:
    """
    List all annotations in a dataset.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `annotation <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.annotation?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing all annotations.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset)

    extraction_def = [
        ("Object Name",        lambda r: r[0], "str"),  # noqa: E272
        ("Parent Object Name", lambda r: r[1], "str"),  # noqa: E272
        ("Object Type",        lambda r: r[2], "str"),  # noqa: E272
        ("Annotation Name",    lambda r: r[3], "str"),  # noqa: E272
        ("Annotation Value",   lambda r: r[4], "str"),  # noqa: E272
    ]

    model = database.Model

    collection = [
        # model annotations
        *[(model.Name, None, "Model", a.Name, a.Value) for a in model.Annotations],
        # 1-level below model
        *[(t.Name, model.Name, "Table",        a.Name, a.Value) for t in model.Tables        for a in t.Annotations],  # noqa: E272
        *[(x.Name, model.Name, "Data Source",  a.Name, a.Value) for x in model.DataSources   for a in x.Annotations],  # noqa: E272
        *[(x.Name, model.Name, "Relationship", a.Name, a.Value) for x in model.Relationships for a in x.Annotations],  # noqa: E272
        *[(x.Name, model.Name, "Translation",  a.Name, a.Value) for x in model.Cultures      for a in x.Annotations],  # noqa: E272
        *[(x.Name, model.Name, "Expression",   a.Name, a.Value) for x in model.Expressions   for a in x.Annotations],  # noqa: E272
        *[(x.Name, model.Name, "Perspective",  a.Name, a.Value) for x in model.Perspectives  for a in x.Annotations],  # noqa: E272
        *[(x.Name, model.Name, "Role",         a.Name, a.Value) for x in model.Roles         for a in x.Annotations],  # noqa: E272
        # 2-level below model \ table
        *[
            (p.Name, t.Name, "Partition", a.Name, a.Value)
            for t in model.Tables
            for p in t.Partitions
            for a in p.Annotations
        ],
        *[
            (c.Name, t.Name, "Column", a.Name, a.Value)
            for t in model.Tables
            for c in t.Columns
            for a in c.Annotations
        ],
        *[
            (m.Name, t.Name, "Measure", a.Name, a.Value)
            for t in model.Tables
            for m in t.Measures
            for a in m.Annotations
        ],
        *[
            (h.Name, t.Name, "Hierarchy", a.Name, a.Value)
            for t in model.Tables
            for h in t.Hierarchies
            for a in h.Annotations
        ],
    ]

    return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)
