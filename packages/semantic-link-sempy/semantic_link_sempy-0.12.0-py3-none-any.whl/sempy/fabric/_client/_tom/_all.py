from sempy.fabric._client._tom import TOMWrapperProtocol
from sempy.fabric._client._utils import _init_analysis_services

from typing import TYPE_CHECKING, Iterator

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class ListAllMixin(TOMWrapperProtocol):

    @property
    def all_tables(self) -> Iterator["TOM.Table"]:
        """
        Output an iterator of all tables in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Table
            All tables within the semantic model.
        """
        for t in self.model.Tables:
            yield t

    @property
    def all_columns(self) -> Iterator["TOM.Column"]:
        """
        Output an iterator of all columns within all tables in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Column
            All columns within the semantic model.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        for t in self.all_tables:
            for c in t.Columns:
                if c.Type != TOM.ColumnType.RowNumber:
                    yield c

    @property
    def all_calculated_columns(self) -> Iterator["TOM.Column"]:
        """
        Output an iterator of all calculated columns within all tables in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Column
            All calculated columns within the semantic model.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        for t in self.all_tables:
            for c in t.Columns:
                if c.Type == TOM.ColumnType.Calculated:
                    yield c

    @property
    def all_calculated_tables(self) -> Iterator["TOM.Table"]:
        """
        Output an iterator of all calculated tables in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Table
            All calculated tables within the semantic model.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        for t in self.all_tables:
            if any(p.SourceType == TOM.PartitionSourceType.Calculated for p in t.Partitions):
                yield t

    @property
    def all_calculation_groups(self) -> Iterator["TOM.Table"]:
        """
        Output an iterator of all calculation groups in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Table
            All calculation groups within the semantic model.
        """

        for t in self.all_tables:
            if t.CalculationGroup is not None:
                yield t

    @property
    def all_measures(self) -> Iterator["TOM.Measure"]:
        """
        Output an iterator of all measures in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Measure
            All measures within the semantic model.
        """

        for t in self.all_tables:
            for m in t.Measures:
                yield m

    @property
    def all_partitions(self) -> Iterator["TOM.Partition"]:
        """
        Output an iterator of all partitions in the semantic model.

        Yields
        -------
        Microsoft.AnalysisServices.Tabular.Partition
            All partitions within the semantic model.
        """

        for t in self.all_tables:
            for p in t.Partitions:
                yield p

    @property
    def all_hierarchies(self) -> Iterator["TOM.Hierarchy"]:
        """
        Output an iterator of all hierarchies in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Hierarchy
            All hierarchies within the semantic model.
        """

        for t in self.all_tables:
            for h in t.Hierarchies:
                yield h

    @property
    def all_levels(self) -> Iterator["TOM.Level"]:
        """
        Output an iterator of all levels in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Level
            All levels within the semantic model.
        """

        for table in self.all_tables:
            for hierarchy in table.Hierarchies:
                for level in hierarchy.Levels:
                    yield level

    @property
    def all_calculation_items(self) -> Iterator["TOM.CalculationItem"]:
        """
        Output an iterator of all calculation items in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.CalculationItem
            All calculation items within the semantic model.
        """

        for t in self.all_tables:
            if t.CalculationGroup is not None:
                for ci in t.CalculationGroup.CalculationItems:
                    yield ci

    @property
    def all_rls(self) -> Iterator["TOM.TablePermission"]:
        """
        Output an iterator of all row level security expressions in the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.TablePermission
            All row level security expressions within the semantic model.
        """

        for r in self.model.Roles:
            for tp in r.TablePermissions:
                yield tp

    @property
    def all_hybrid_tables(self) -> Iterator["TOM.Table"]:
        """
        Output an iterator of the hybrid tables within a semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Table
            All hybrid tables within a semantic model.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        for t in self.all_tables:
            if (
                any(p.Mode == TOM.ModeType.Import for p in t.Partitions)
                and any(p.Mode == TOM.ModeType.DirectQuery for p in t.Partitions)
            ):
                yield t

    @property
    def all_date_tables(self) -> Iterator["TOM.Table"]:
        """
        Output an iterator of the tables which are marked as date tables within a semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Table
            All tables marked as date tables within a semantic model.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        for t in self.all_tables:
            if (
                t.DataCategory == "Time"
                and any(c.IsKey and c.DataType == TOM.DataType.DateTime for c in t.Columns)
            ):
                yield t

    def all_annotations(self, tom_obj: "TOM.MetadataObject") -> Iterator["TOM.Annotation"]:
        """
        Output an iterator of all annotations for a given object within a semantic model.

        Parameters
        ----------
        tom_obj : TOM Object
            An object (i.e. table/column/measure) within a semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Annotation
            TOM objects of all the annotations on a particular object within the semantic model.
        """

        for a in tom_obj.Annotations:
            yield a

    def all_extended_properties(self, tom_obj: "TOM.MetadataObject") -> Iterator["TOM.ExtendedProperty"]:
        """
        Output an iterator of all extended properties on an object within the semantic model.

        Parameters
        ----------
        tom_obj : TOM Object
            An object (i.e. table/column/measure) within a semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.ExtendedProperty
            TOM Objects of all the extended properties.
        """

        for a in tom_obj.ExtendedProperties:
            yield a
