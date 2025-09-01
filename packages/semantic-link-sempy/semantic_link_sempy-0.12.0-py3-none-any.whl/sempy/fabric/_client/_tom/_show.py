import re
from rich.console import Console

from sempy._utils import _icons as icons
from sempy.fabric._client._tom import TOMWrapperProtocol
from sempy.fabric._client._utils import _format_dax_object_name


class ShowMixin(TOMWrapperProtocol):

    def show_incremental_refresh_policy(self, table_name: str):
        """
        Print the incremental refresh policy for a table.

        Parameters
        ----------
        table_name : str
            Name of the table.
        """

        import Microsoft.AnalysisServices.Tabular as TOM

        console = Console()

        rp = self.model.Tables[table_name].RefreshPolicy
        if rp is None:
            # No refresh policy available for the table
            console.print(
                f"{icons.yellow_dot} The '{table_name}' table in the '{self.dataset}' semantic model within the '{self.workspace}' workspace does not have an incremental refresh policy."
            )
            return

        # Display refresh policy details
        console.print(f"Table Name: {table_name}")

        # Handle Rolling Window and Incremental Granularity
        rw_granularity = f"{str(rp.RollingWindowGranularity).lower()}{'s' if rp.RollingWindowPeriods > 1 else ''}"
        ic_granularity = f"{str(rp.IncrementalGranularity).lower()}{'s' if rp.IncrementalPeriods > 1 else ''}"

        console.print(
            f"Archive data starting [bold]{rp.RollingWindowPeriods} {rw_granularity}[/bold] before refresh date."
        )
        console.print(
            f"Incrementally refresh data [bold]{rp.IncrementalPeriods} {ic_granularity}[/bold] before refresh date."
        )

        # DirectQuery mode check for real-time updates (Premium only)
        direct_query_message = f"{icons.checked}" if rp.Mode == TOM.RefreshPolicyMode.Hybrid else f"{icons.unchecked}"
        console.print(f"{direct_query_message} Get the latest data in real time with DirectQuery (Premium only)")

        # Check for complete days-only refresh
        complete_days_message = f"{icons.checked}" if rp.IncrementalPeriodsOffset == -1 else f"{icons.unchecked}"
        console.print(f"{complete_days_message} Only refresh complete days")

        # Detect data changes check based on PollingExpression
        if len(rp.PollingExpression) > 0:
            pattern = r"\[([^\]]+)\]"
            match = re.search(pattern, rp.PollingExpression)
            if match:
                column_name = match.group(1)
                formatted_column = _format_dax_object_name(table_name, column_name)
                console.print(f"{icons.checked} Detect data changes: [bold]{formatted_column}[/bold]")
        else:
            console.print(f"{icons.unchecked} Detect data changes")
