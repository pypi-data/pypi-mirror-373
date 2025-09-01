from contextlib import contextmanager
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Optional, Union, cast
from uuid import UUID
import sempy._utils._icons as icons
import sempy.fabric as fabric
import sempy.fabric._client._tom as tom_client
from sempy.fabric._client._utils import _init_analysis_services, generate_guid
from sempy.fabric._utils import is_valid_uuid
from sempy._utils._log import log
from sempy.fabric.exceptions import DatasetNotFoundException
import ast

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential

    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class TOMWrapper(
    tom_client.HasMixin,
    tom_client.IsMixin,
    tom_client.UsedInMixin,
    tom_client.TranslationMixin,
    tom_client.ListAllMixin,
    tom_client.SetMixin,
    tom_client.GetMixin,
    tom_client.InMixin,
    tom_client.ShowMixin,
):
    """
    Convenience wrapper around the TOM object model for a semantic model. Always use the connect_semantic_model function to make sure the TOM object is initialized correctly.

    `XMLA read/write endpoints <https://learn.microsoft.com/power-bi/enterprise/service-premium-connect-tools#to-enable-read-write-for-a-premium-capacity>`_ must
     be enabled if setting the readonly parameter to False.

    Parameters
    ----------
    dataset : str
        Name of the semantic model.
    workspace : str
        The Fabric workspace name.
    readonly : bool
        Whether the connection is read-only or read/write. Setting this to False enables read/write which saves the changes made back to the server.
    credential : TokenCredential, default=None
        The credential to acquire the token. If not provided, the default credential will be used.
    """

    _dataset: str
    _workspace: str
    _readonly: bool
    _tables_added: List[str]
    _table_map: Dict[str, Any]
    _column_map: Dict[str, Any]

    def __init__(self, dataset: str, workspace: str, readonly: bool,
                 credential: Optional["TokenCredential"] = None):

        # initialize .NET to make sure System and Microsoft.AnalysisServices.Tabular is defined
        _init_analysis_services()

        from Microsoft.AnalysisServices import AmoException as AmoException

        self._dataset = dataset
        self._workspace = workspace
        self._readonly = readonly
        self._tables_added = []

        self._tom_server = fabric.create_tom_server(
            dataset=dataset, readonly=readonly, workspace=workspace, credential=credential
        )
        try:
            self._model = self._tom_server.Databases.GetByName(dataset).Model
        except AmoException:
            self._tom_server.Dispose()
            raise DatasetNotFoundException(dataset, workspace)

        self._table_map = {}
        self._column_map = {}
        self._compat_level = self.model.Model.Database.CompatibilityLevel
        self.sll_tags: list[str] = []

        # Minimum campat level for lineage tags is 1540 (https://learn.microsoft.com/dotnet/api/microsoft.analysisservices.tabular.table.lineagetag?view=analysisservices-dotnet#microsoft-analysisservices-tabular-table-lineagetag)  # noqa: E501
        if self._compat_level >= 1540:
            for t in self._model.Tables:
                if len(t.LineageTag) == 0:
                    t.LineageTag = generate_guid()
                self._table_map[t.LineageTag] = t.Name

            for c in self.all_columns:
                if len(c.LineageTag) == 0:
                    c.LineageTag = generate_guid()
                self._column_map[c.LineageTag] = [c.Name, c.DataType]

    @property
    def model(self) -> "TOM.Model":
        """
        The semantic model's Tabular Object Model.
        """
        return self._model

    @property
    def dataset(self) -> str:
        """
        The name of the semantic model.
        """
        return self._dataset

    @property
    def workspace(self) -> str:
        """
        The Fabric workspace name.
        """
        return self._workspace

    def close(self):
        """
        Close the connection to the semantic model.
        """
        if self._readonly is False and self.model is not None:
            tags = [f"{icons.sll_prefix}{a}" for a in self.sll_tags]
            tags.append("SLL")

            if not any(a.Name == icons.sll_ann_name for a in self.model.Annotations):
                ann_list = list(set(tags))
                new_ann_value = str(ann_list).replace("'", '"')
                self.set_annotation(
                    tom_obj=self.model, name=icons.sll_ann_name, value=new_ann_value
                )
            else:
                try:
                    ann_value = self.get_annotation_value(
                        tom_obj=self.model, name=icons.sll_ann_name
                    )
                    ann_list = ast.literal_eval(ann_value)
                    ann_list += tags
                    ann_list = list(set(ann_list))
                    new_ann_value = str(ann_list).replace("'", '"')
                    self.set_annotation(
                        tom_obj=self.model, name=icons.sll_ann_name, value=new_ann_value
                    )
                except Exception:
                    pass
            self.model.SaveChanges()
        self._tom_server.Dispose()


@log
@contextmanager
def connect_semantic_model(
    dataset: Union[str, UUID],
    readonly: bool = True,
    workspace: Optional[Union[str, UUID]] = None,
    verbose: int = 0,
    credential: Optional["TokenCredential"] = None
) -> Iterator[TOMWrapper]:
    """
    Connect to the Tabular Object Model (TOM) within a semantic model.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or ID of the semantic model.
    readonly : bool, default=True
        Whether the connection is read-only or read/write. Setting this to False enables read/write which saves the changes made back to the server.
    workspace : str or uuid.UUID, default=None
        Name or ID of the Fabric workspace.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    verbose : int, default=0
        The verbosity level. 0 means no output.
    credential : TokenCredential, default=None
        The credential to acquire the token. If not provided, the default credential will be used.

    Yields
    ------
    TOMWrapper
        A connection to the semantic model's Tabular Object Model.
    """
    if workspace is None or is_valid_uuid(workspace):
        workspace = fabric.resolve_workspace_name(workspace)

    if is_valid_uuid(dataset):
        dataset = fabric.resolve_dataset_name(dataset, workspace)

    dataset = cast(str, dataset)
    workspace = cast(str, workspace)

    tw = TOMWrapper(dataset=dataset, workspace=workspace, readonly=readonly, credential=credential)
    try:
        yield tw
    finally:
        tw.close()
