from typing import TYPE_CHECKING, Iterator, Union

from sempy.fabric._client._tom import ListAllMixin, TOMWrapperProtocol
from sempy.fabric._client._utils import _init_analysis_services

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class UsedInMixin(ListAllMixin, TOMWrapperProtocol):

    def used_in_relationships(self, tom_obj: Union["TOM.Table", "TOM.Column"]) -> Iterator["TOM.Relationship"]:
        """
        Show all relationships in which a table/column is used.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column]
            An object (i.e. table/column) within a semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Relationship
            All relationships in which the table/column is used.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Table:
            for rel in self.model.Relationships:
                if rel.FromTable.Name == tom_obj.Name or rel.ToTable.Name == tom_obj.Name:
                    yield rel
        elif obj_type == TOM.ObjectType.Column:
            for rel in self.model.Relationships:
                if (
                    rel.FromTable.Name == tom_obj.Parent.Name
                    and rel.FromColumn.Name == tom_obj.Name
                ) or (
                    rel.ToTable.Name == tom_obj.Parent.Name
                    and rel.ToColumn.Name == tom_obj.Name
                ):
                    yield rel
        else:
            raise ValueError(f"Object must be a Table or Column, but got {obj_type}.")

    def used_in_levels(self, tom_obj: "TOM.Column") -> Iterator["TOM.Level"]:
        """
        Show all levels in which a column is used.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Column
            An column object within a semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Level
            All levels in which the column is used.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Column:
            for level in self.all_levels:
                if (
                    level.Parent.Table.Name == tom_obj.Parent.Name
                    and level.Column.Name == tom_obj.Name
                ):
                    yield level
        else:
            raise ValueError(f"Object must be a Column, but got {obj_type}.")

    def used_in_hierarchies(self, tom_obj: "TOM.Column") -> Iterator["TOM.Hierarchy"]:
        """
        Show all hierarchies in which a column is used.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Column
            An column object within a semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Hierarchy
            All hierarchies in which the column is used.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Column:
            for level in self.all_levels:
                if (
                    level.Parent.Table.Name == tom_obj.Parent.Name
                    and level.Column.Name == tom_obj.Name
                ):
                    yield level.Parent
        else:
            raise ValueError(f"Object must be a Column, but got {obj_type}.")

    def used_in_sort_by(self, tom_obj: "TOM.Column") -> Iterator["TOM.Column"]:
        """
        Show all columns in which a column is used for sorting.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Column
            An column object within a semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Column
            All columns in which the column is used for sorting.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Column:
            for c in self.model.Tables[tom_obj.Parent.Name].Columns:
                if c.SortByColumn == tom_obj:
                    yield c
        else:
            raise ValueError(f"Object must be a Column, but got {obj_type}.")
