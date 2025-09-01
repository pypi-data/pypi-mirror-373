from typing import TYPE_CHECKING

from sempy.fabric._client._tom import TOMWrapperProtocol
from sempy.fabric._client._utils import _init_analysis_services

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class SetMixin(TOMWrapperProtocol):

    def set_annotation(self, tom_obj: "TOM.MetadataObject", name: str, value: str):
        """
        Set an annotation on an object within the semantic model.

        Parameters
        ----------
        tom_obj : TOM Object
            An object (i.e. table/column/measure) within a semantic model.
        name : str
            Name of the annotation.
        value : str
            Value of the annotation.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        if any(a.Name == name for a in tom_obj.Annotations):
            tom_obj.Annotations[name].Value = value
        else:
            ann = TOM.Annotation()
            ann.Name = name
            ann.Value = value
            tom_obj.Annotations.Add(ann)
