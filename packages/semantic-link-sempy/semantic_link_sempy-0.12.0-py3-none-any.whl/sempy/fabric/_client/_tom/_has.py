from sempy.fabric._client._tom import IsMixin, TOMWrapperProtocol


class HasMixin(IsMixin, TOMWrapperProtocol):

    @property
    def has_aggs(self) -> bool:
        """
        Identify if a semantic model has any aggregations.

        Returns
        -------
        bool
            Indicates if the semantic model has any aggregations.
        """

        return any(c.AlternateOf is not None for c in self.all_columns)

    @property
    def has_hybrid_table(self) -> bool:
        """
        Identify if a semantic model has a hybrid table.

        Returns
        -------
        bool
            Indicates if the semantic model has a hybrid table.
        """

        return any(self.is_hybrid_table(table_name=t.Name) for t in self.all_tables)

    @property
    def has_date_table(self) -> bool:
        """
        Identify if a semantic model has a table marked as a date table.

        Returns
        -------
        bool
            Indicates if the semantic model has a table marked as a date table.
        """

        return any(self.is_date_table(table_name=t.Name) for t in self.all_tables)

    def has_incremental_refresh_policy(self, table_name: str) -> bool:
        """
        Identify whether a table has an incremental refresh policy.

        Parameters
        ----------
        table_name : str
            Name of the table.

        Returns
        -------
        bool
            An indicator whether a table has an incremental refresh policy.
        """

        rp = self.model.Tables[table_name].RefreshPolicy
        return rp is not None
