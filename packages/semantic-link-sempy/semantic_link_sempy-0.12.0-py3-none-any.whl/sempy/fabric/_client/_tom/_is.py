import numpy as np

import sempy.fabric as fabric
from sempy.fabric._client._tom import ListAllMixin, TOMWrapperProtocol


class IsMixin(ListAllMixin, TOMWrapperProtocol):

    def is_hybrid_table(self, table_name: str) -> bool:
        """
        Identify if a table is a hybrid table.

        Parameters
        ----------
        table_name : str
            Name of the table.

        Returns
        -------
        bool
            Indicates if the table is a hybrid table.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        t = self.model.Tables[table_name]
        return (
            any(
                p.Mode == TOM.ModeType.Import
                for p in t.Partitions
            )
            and any(
                p.Mode == TOM.ModeType.DirectQuery
                for p in t.Partitions
            )
        )

    def is_date_table(self, table_name: str) -> bool:
        """
        Identify if a table is marked as a date table.

        Parameters
        ----------
        table_name : str
            Name of the table.

        Returns
        -------
        bool
            Indicates if the table is marked as a date table.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        return any(
            c.IsKey and c.DataType == TOM.DataType.DateTime
            for c in self.all_columns
            if c.Parent.Name == table_name and c.Parent.DataCategory == "Time"
        )

    def is_agg_table(self, table_name: str) -> bool:
        """
        Identify if a table has aggregations.

        Parameters
        ----------
        table_name : str
            Name of the table.

        Returns
        -------
        bool
            Indicates if the table has any aggregations.
        """
        return any(c.AlternateOf is not None for c in self.model.Tables[table_name].Columns)

    @property
    def is_direct_lake(self) -> bool:
        """
        Identify if a semantic model is in Direct Lake mode.

        Returns
        -------
        bool
            Indicates if the semantic model is in Direct Lake mode.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        return any(
            p.Mode == TOM.ModeType.DirectLake
            for t in self.all_tables
            for p in t.Partitions
        )

    def is_field_parameter(self, table_name: str) -> bool:
        """
        Identify if a table is a field parameter.

        Parameters
        ----------
        table_name : str
            Name of the table.

        Returns
        -------
        bool
            Indicates if the table is a field parameter.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        t = self.model.Tables[table_name]
        return (
            self.is_calculated_table(table_name=table_name)
            and t.Columns.Count == 4
            and any(
                hasattr(p.Source, "Expression") and p.Source.Expression is not None
                and "NAMEOF(" in p.Source.Expression.replace(" ", "")
                for p in t.Partitions
            )
            and all(
                "[Value" in c.SourceColumn
                for c in t.Columns
                if c.Type == TOM.ColumnType.Data
            )
            and any(
                ep.Name == "ParameterMetadata"
                for c in t.Columns
                for ep in c.ExtendedProperties
            )
        )

    def is_auto_date_table(self, table_name: str) -> bool:
        """
        Identify if a table is an auto date/time table.

        Parameters
        ----------
        table_name : str
            Name of the table.

        Returns
        -------
        bool
            Indicates if the table is an auto-date table.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        t = self.model.Tables[table_name]
        return (
            t.Name.startswith(("LocalDateTable_", "DateTableTemplate_"))
            and any(
                p.SourceType == TOM.PartitionSourceType.Calculated
                for p in t.Partitions
            )
        )

    @property
    def is_direct_lake_using_view(self) -> bool:
        """
        Identify whether a semantic model is in Direct lake mode and uses views from the lakehouse.

        Returns
        -------
        bool
            An indicator whether a semantic model is in Direct lake mode and uses views from the lakehouse.
        """
        if not self.is_direct_lake:
            return False

        df = fabric.evaluate_dax(
            dataset=self.dataset,
            workspace=self.workspace,
            dax_string="""
                SELECT [TableName] AS [Table Name],[FallbackReason] AS [FallbackReasonID]
                FROM $SYSTEM.TMSCHEMA_DELTA_TABLE_METADATA_STORAGES
                """,
        )

        value_mapping = {
            0: "No reason for fallback",
            1: "This table is not framed",
            2: "This object is a view in the lakehouse",
            3: "The table does not exist in the lakehouse",
            4: "Transient error",
            5: "Using OLS will result in fallback to DQ",
            6: "Using RLS will result in fallback to DQ",
        }

        # Create a new column based on the mapping
        df["Fallback Reason Detail"] = np.vectorize(value_mapping.get, otypes=[str])(
            df["FallbackReasonID"]
        )

        return any(df["FallbackReasonID"] == 2)

    def is_calculated_column(self, table_name: str, column_name: str) -> bool:
        """
        Identify if a column is a calculated column.

        Parameters
        ----------
        table_name : str
            Name of the table in which the column resides.
        column_name : str
            Name of the column.

        Returns
        -------
        bool
            A boolean value indicating whether the column is a calculated column.
        """

        import Microsoft.AnalysisServices.Tabular as TOM

        c = self.model.Tables[table_name].Columns[column_name]
        return c.Type == TOM.ColumnType.Calculated

    def is_calculated_table(self, table_name: str) -> bool:
        """
        Identify if a table is a calculated table.

        Parameters
        ----------
        table_name : str
            Name of the table.

        Returns
        -------
        bool
            A boolean value indicating whether the table is a calculated table.
        """

        import Microsoft.AnalysisServices.Tabular as TOM

        t = self.model.Tables[table_name]
        return (
            t.ObjectType == TOM.ObjectType.Table
            and any(
                p.SourceType == TOM.PartitionSourceType.Calculated
                for p in t.Partitions
            )
        )
