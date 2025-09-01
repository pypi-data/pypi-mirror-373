import pandas as pd
from uuid import UUID
from sempy.fabric._cache import _get_or_create_workspace_client
from sempy.fabric._utils import collection_to_dataframe
from sempy._utils._log import log
from typing import List, Optional, Union


@log
def list_calculation_items(
    dataset: Union[str, UUID],
    additional_xmla_properties: Optional[Union[str, List[str]]] = None,
    workspace: Optional[Union[str, UUID]] = None
) -> pd.DataFrame:
    """
    List all calculation items for each group in a dataset.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    additional_xmla_properties : str or List[str], default=None
        Additional XMLA `calculationitem <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.calculationitem?view=analysisservices-dotnet>`_
        properties to include in the returned dataframe.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Returns
    -------
    pandas.DataFrame
        Dataframe listing all calculation groups.
    """
    workspace_client = _get_or_create_workspace_client(workspace)
    database = workspace_client.get_dataset(dataset)

    def format_string_def_expression(r):
        if r[1].FormatStringDefinition is None:
            return None
        else:
            return r[1].FormatStringDefinition.Expression

    extraction_def = [
        ("Calculation Group Name",   lambda r: r[0].Name,                        "str"),   # noqa: E272
        ("Hidden",                   lambda r: r[0].IsHidden,                    "bool"),  # noqa: E272
        ("Precedence",               lambda r: r[0].CalculationGroup.Precedence, "int"),   # noqa: E272
        ("Description",              lambda r: r[0].Description,                 "str"),   # noqa: E272
        ("Calculation Item Name",    lambda r: r[1].Name,                        "str"),   # noqa: E272
        ("Ordinal",                  lambda r: r[1].Ordinal,                     "int"),   # noqa: E272
        ("Expression",               lambda r: r[1].Expression,                  "str"),   # noqa: E272
        ("Format String Expression", format_string_def_expression,               "str"),   # noqa: E272
        ("State",                    lambda r: r[1].State,                       "str"),   # noqa: E272
        ("Error Message",            lambda r: r[1].ErrorMessage,                "str"),   # noqa: E272
    ]

    collection = [
        (t, c)
        for t in database.Model.Tables if t.CalculationGroup is not None
        for c in t.CalculationGroup.CalculationItems
    ]

    return collection_to_dataframe(collection, extraction_def, additional_xmla_properties)
