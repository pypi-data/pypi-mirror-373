from typing import TYPE_CHECKING, Union

from sempy.fabric._client._tom import TOMWrapperProtocol
from sempy.fabric._client._utils import _init_analysis_services

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class InMixin(TOMWrapperProtocol):

    def in_perspective(
        self,
        tom_obj: Union["TOM.Table", "TOM.Column", "TOM.Measure", "TOM.Hierarchy"],
        perspective_name: str,
    ) -> bool:
        """
        Indicate whether an object is contained within a given perspective.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure, Microsoft.AnalysisServices.Tabular.Hierarchy]
            An object (i.e. table/column/measure) within a semantic model.
        perspective_name : str
            Name of the perspective.

        Returns
        -------
        bool
            An indication as to whether the object is contained within the given perspective.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        valid_objects = {
            TOM.ObjectType.Table: "PerspectiveTables",
            TOM.ObjectType.Column: "PerspectiveColumns",
            TOM.ObjectType.Measure: "PerspectiveMeasures",
            TOM.ObjectType.Hierarchy: "PerspectiveHierarchies",
        }

        obj_type = tom_obj.ObjectType
        if obj_type not in valid_objects:
            raise ValueError(
                f"Only the following object types are valid for perspectives: {valid_objects}."
            )

        model = tom_obj.Model
        if not model.Perspectives.ContainsName(perspective_name):
            raise ValueError(
                f"Perspective '{perspective_name}' does not exist in the model."
            )

        perspective = model.Perspectives[perspective_name]
        if obj_type == TOM.ObjectType.Table:
            return perspective.PerspectiveTables.ContainsName(tom_obj.Name)
        else:
            perspective_table_name = tom_obj.Parent.Name
            if not perspective.PerspectiveTables.ContainsName(perspective_table_name):
                return False

            perspective_table = perspective.PerspectiveTables[perspective_table_name]
            attribute_name = valid_objects[obj_type]
            return getattr(perspective_table, attribute_name).ContainsName(tom_obj.Name)
