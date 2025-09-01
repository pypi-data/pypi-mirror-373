from typing import TYPE_CHECKING, Union

from sempy.fabric._client._tom import TOMWrapperProtocol
from sempy.fabric._client._utils import _init_analysis_services

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class GetMixin(TOMWrapperProtocol):

    def get_annotation_value(self, tom_obj: "TOM.MetadataObject", name: str) -> Union[str, None]:
        """
        Obtain the annotation value for a given annotation on an object within the semantic model.

        Parameters
        ----------
        tom_obj : TOM Object
            An object (i.e. table/column/measure) within a semantic model.
        name : str
            Name of the annotation.

        Returns
        -------
        str
            The annotation value.
        """
        if any(a.Name == name for a in tom_obj.Annotations):
            value = tom_obj.Annotations[name].Value
        else:
            value = None

        return value

    def get_extended_property_value(self, tom_obj: "TOM.MetadataObject", name: str) -> Union[str, None]:
        """
        Retrieve the value of an extended property for an object within the semantic model.

        Parameters
        ----------
        tom_obj : TOM Object
            An object (i.e. table/column/measure) within a semantic model.
        name : str
            Name of the annotation.

        Returns
        -------
        str
            The extended property value.
        """
        if any(a.Name == name for a in tom_obj.ExtendedProperties):
            value = tom_obj.ExtendedProperties[name].Value
        else:
            value = None

        return value

    def get_row_count(self, tom_obj: Union["TOM.Partition", "TOM.Table"]) -> int:
        """
        Obtain the row count of a table or partition within a semantic model.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Partition, Microsoft.AnalysisServices.Tabular.Table]
            The table/partition object within the semantic model.

        Returns
        -------
        int
            Number of rows within the TOM object.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Table:
            result = self.get_annotation_value(tom_obj=tom_obj, name="Vertipaq_RowCount")
        elif obj_type == TOM.ObjectType.Partition:
            result = self.get_annotation_value(tom_obj=tom_obj, name="Vertipaq_RecordCount")
        else:
            raise ValueError(f"Object must be a Table or Partition, but got {obj_type}.")

        return int(result) if result is not None else 0

    def get_records_per_segment(self, tom_obj: "TOM.Partition") -> int:
        """
        Obtain the records per segment of a partition within a semantic model.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Partition
            The partition object within the semantic model.

        Returns
        -------
        float
            Number of records per segment within the partition.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Partition:
            result = self.get_annotation_value(tom_obj=tom_obj, name="Vertipaq_RecordsPerSegment")
        else:
            raise ValueError(f"Object must be a Partition, but got {obj_type}.")

        return int(result) if result is not None else 0

    def get_used_size(self, tom_obj: Union["TOM.Hierarchy", "TOM.Relationship"]) -> int:
        """
        Obtain the used size of a hierarchy or relationship within a semantic model.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Hierarchy, Microsoft.AnalysisServices.Tabular.Relationship]
            The hierarhcy/relationship object within the semantic model.

        Returns
        -------
        int
            Used size of the TOM object.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Hierarchy or obj_type == TOM.ObjectType.Relationship:
            result = self.get_annotation_value(tom_obj=tom_obj, name="Vertipaq_UsedSize")
        else:
            raise ValueError(f"Object must be a Hierarchy or Relationship, but got {obj_type}.")

        return int(result) if result is not None else 0

    def get_data_size(self, tom_obj: "TOM.Column") -> int:
        """
        Obtain the data size of a column within a semantic model.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Column
            The column object within the semantic model.

        Returns
        -------
        int
            Data size of the TOM column.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Column:
            result = self.get_annotation_value(tom_obj=tom_obj, name="Vertipaq_DataSize")
        else:
            raise ValueError(f"Object must be a Column, but got {obj_type}.")

        return int(result) if result is not None else 0

    def get_dictionary_size(self, tom_obj: "TOM.Column") -> int:
        """
        Obtain the dictionary size of a column within a semantic model.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Column
            The column object within the semantic model.

        Returns
        -------
        int
            Dictionary size of the TOM column.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Column:
            result = self.get_annotation_value(tom_obj=tom_obj, name="Vertipaq_DictionarySize")
        else:
            raise ValueError(f"Object must be a Column, but got {obj_type}.")

        return int(result) if result is not None else 0

    def get_total_size(self, tom_obj: Union["TOM.Table", "TOM.Column"]) -> int:
        """
        Obtain the data size of a table/column within a semantic model.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column]
            The table/column object within the semantic model.

        Returns
        -------
        int
            Total size of the TOM table/column.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Column or obj_type == TOM.ObjectType.Table:
            result = self.get_annotation_value(tom_obj=tom_obj, name="Vertipaq_TotalSize")
        else:
            raise ValueError(f"Object must be a Column or Table, but got {obj_type}.")

        return int(result) if result is not None else 0

    def get_cardinality(self, tom_obj: "TOM.Column") -> int:
        """
        Obtain the cardinality of a column within a semantic model.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Column
            The column object within the semantic model.

        Returns
        -------
        int
            Cardinality of the TOM column.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Column:
            result = self.get_annotation_value(tom_obj=tom_obj, name="Vertipaq_Cardinality")
        else:
            raise ValueError(f"Object must be a Column, but got {obj_type}.")

        return int(result) if result is not None else 0

    def get_dax_expression(
        self,
        tom_obj: Union[
            "TOM.Measure", "TOM.Table", "TOM.Column", "TOM.CalculationItem"
        ]
    ) -> str:
        """
        Get the DAX expression of a given object.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Measure or Microsoft.AnalysisServices.Tabular.Table or Microsoft.AnalysisServices.Tabular.Column or Microsoft.AnalysisServices.Tabular.CalculationItem
            The object for which to get the DAX expression.

        Returns
        -------
        str
            The DAX expression of the object. An empty string is returned if no expression is found.
        """  # noqa: E501
        import Microsoft.AnalysisServices.Tabular as TOM

        if (
            tom_obj.ObjectType == TOM.ObjectType.Measure or
            tom_obj.ObjectType == TOM.ObjectType.CalculationItem or
            (
                tom_obj.ObjectType == TOM.ObjectType.Column and
                tom_obj.Type == TOM.ColumnType.Calculated
            )
        ):
            return tom_obj.Expression

        if tom_obj.ObjectType == TOM.ObjectType.Table:
            if tom_obj.Partitions.Count > 0:
                part = next(p for p in tom_obj.Partitions)
                if part.SourceType == TOM.PartitionSourceType.Calculated:
                    return part.Source.Expression

        return ""

    def _get_table(self, name: str) -> "TOM.Table":
        """
        Obtain the table object by the table name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the table.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Table
            The table object of the given name within the semantic model.
        """
        for t in self.model.Tables:
            if t.Name == name:
                return t

        raise ValueError(f"Table '{name}' not found.")

    def _get_column(self, name: str, parent_name: str) -> "TOM.Column":
        """
        Obtain the column object by the column name and parent table name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the column.
        parent_name : str
            Name of the parent table.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Column
            The column object of the given name within the semantic model.
        """
        table = self._get_table(parent_name)

        for c in table.Columns:
            if c.Name == name:
                return c

        raise ValueError(f"Column '{name}' not found in table '{parent_name}'.")

    def _get_measure(self, name: str, parent_name: str) -> "TOM.Measure":
        """
        Obtain the measure object by the measure name and parent table name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the measure.
        parent_name : str
            Name of the parent table.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Measure
            The measure object of the given name within the semantic model.
        """
        table = self._get_table(parent_name)

        for m in table.Measures:
            if m.Name == name:
                return m

        raise ValueError(f"Measure '{name}' not found in table '{parent_name}'.")

    def _get_partition(self, name: str, parent_name: str) -> "TOM.Partition":
        """
        Obtain the partition object by the partition name and parent table name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the partition.
        parent_name : str
            Name of the parent table.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Partition
            The partition object of the given name within the semantic model.
        """
        table = self._get_table(parent_name)

        for p in table.Partitions:
            if p.Name == name:
                return p

        raise ValueError(f"Partition '{name}' not found in table '{parent_name}'.")

    def _get_hierarchy(self, name: str, parent_name: str) -> "TOM.Hierarchy":
        """
        Obtain the hierarchy object by the hierarchy name and parent table name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the hierarchy.
        parent_name : str
            Name of the parent table.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Hierarchy
            The hierarchy object of the given name within the semantic model.
        """
        table = self._get_table(parent_name)

        for h in table.Hierarchies:
            if h.Name == name:
                return h

        raise ValueError(f"Hierarchy '{name}' not found in table '{parent_name}'.")

    def _get_level(self, name: str, parent_name: str, hierarchy_name: str) -> "TOM.Level":
        """
        Obtain the level object by the level name, parent table name, and hierarchy name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the level.
        parent_name : str
            Name of the parent table.
        hierarchy_name : str
            Name of the hierarchy.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Level
            The level object of the given name within the semantic model.
        """
        hierarchy = self._get_hierarchy(name=hierarchy_name, parent_name=parent_name)

        for level in hierarchy.Levels:
            if level.Name == name:
                return level

        raise ValueError(f"Level '{name}' not found in hierarchy '{hierarchy_name}' of table '{parent_name}'.")

    def _get_perspective(self, name: str) -> "TOM.Perspective":
        """
        Obtain the perspective object by the perspective name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the perspective.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.Perspective
            The perspective object of the given name within the semantic model.
        """
        for perspective in self.model.Perspectives:
            if perspective.Name == name:
                return perspective

        raise ValueError(f"Perspective '{name}' not found.")

    def _get_perspective_table(self, name: str, perspective_name: str) -> "TOM.PerspectiveTable":
        """
        Obtain the perspective table object by the perspective table name and the perspective name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the perspective table.
        perspective_name : str
            Name of the perspective.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.PerspectiveTable
            The perspective table object of the given name within the semantic model.
        """
        perspective = self._get_perspective(perspective_name)

        for perspective_table in perspective.PerspectiveTables:
            if perspective_table.Name == name:
                return perspective_table

        raise ValueError(f"Perspective table '{name}' not found in perspective {perspective_name}.")

    def _get_perspective_column(self, name: str, perspective_name: str, table_name: str) -> "TOM.PerspectiveColumn":
        """
        Obtain the perspective column object by the perspective column name, perspective name, and table name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the perspective column.
        perspective_name : str
            Name of the perspective.
        table_name : str
            Name of the perspective table.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.PerspectiveColumn
            The perspective column object of the given name within the semantic model.
        """
        perspective_table = self._get_perspective_table(table_name, perspective_name)

        for perspective_column in perspective_table.PerspectiveColumns:
            if perspective_column.Name == name:
                return perspective_column

        raise ValueError(f"Perspective column '{name}' not found in table '{table_name}' within perspective '{perspective_name}'.")

    def _get_perspective_hierarchy(self, name: str, perspective_name: str, table_name: str) -> "TOM.PerspectiveHierarchy":
        """
        Obtain the perspective hierarchy object by the perspective hierarchy name, perspective name, and table name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the perspective hierarchy.
        perspective_name : str
            Name of the perspective.
        table_name : str
            Name of the perspective table.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.PerspectiveHierarchy
            The perspective hierarchy object of the given name within the semantic model.
        """
        perspective_table = self._get_perspective_table(table_name, perspective_name)

        for perspective_hierarchy in perspective_table.PerspectiveHierarchies:
            if perspective_hierarchy.Name == name:
                return perspective_hierarchy

        raise ValueError(f"Perspective hierarchy '{name}' not found in table '{table_name}' within perspective '{perspective_name}'.")

    def _get_perspective_measure(self, name: str, perspective_name: str, table_name: str) -> "TOM.PerspectiveMeasure":
        """
        Obtain the perspective measure object by the perspective measure name, perspective name, and table name within the semantic model.

        Parameters
        ----------
        name : str
            Name of the perspective measure.
        perspective_name : str
            Name of the perspective.
        table_name : str
            Name of the perspective table.

        Returns
        -------
        Microsoft.AnalysisServices.Tabular.PerspectiveMeasure
            The perspective measure object of the given name within the semantic model.
        """
        perspective_table = self._get_perspective_table(table_name, perspective_name)

        for perspective_measure in perspective_table.PerspectiveMeasures:
            if perspective_measure.Name == name:
                return perspective_measure

        raise ValueError(f"Perspective measure '{name}' not found in table '{table_name}' within perspective '{perspective_name}'.")
