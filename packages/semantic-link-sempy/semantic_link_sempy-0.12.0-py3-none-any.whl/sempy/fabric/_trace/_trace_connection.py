import pandas as pd
import xml.etree.ElementTree as ET

from sempy.fabric._trace._trace import Trace
from sempy.fabric._client._dataset_xmla_client import DatasetXmlaClient
from typing import Dict, List, Optional, Callable


class TraceConnection:
    """
    Connection object for starting, viewing, and removing Traces.

    Python wrapper around `Microsoft Analysis Services Tabular Server <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_.

    Parameters
    ----------
    dataset_client : DatasetXmlaClient
        Client for a specific dataset.
    """
    def __init__(self, dataset_client: DatasetXmlaClient):
        self._tom_server = dataset_client._get_connected_dataset_server(readonly=False)
        self._dataset_client = dataset_client

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.disconnect_and_dispose()

    def create_trace(
        self,
        event_schema: Dict[str, List[str]],
        name: Optional[str] = None,
        filter_predicate: Optional[Callable[..., bool]] = None,
        stop_event: Optional[str] = None
    ) -> Trace:
        """
        Create a blank Trace object on this connection.

        Parameters
        ----------
        event_schema : dict
            Dictionary containing event types as keys and list of column names for that event as values.
            Both event and column names must be specified as strings, either in Space Delimited Case or PascalCase.
        name : str, default=None
            Name identifying trace. If None, the trace name will be "SemanticLinkTrace_<GUID>".
        filter_predicate : Callable
            Function that takes in `TraceEventArgs <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.traceeventargs?view=analysisservices-dotnet>`_,
            and returns a boolean based on whether or not the trace with those args should be recorded.
        stop_event : str, default=None
            Event class that signals the end of the trace. `trace.stop()` will wait for this event (with specified timeout) before returning logs.

        Returns
        -------
        Trace
            Trace object to be customized and started.
        """
        return Trace(self._tom_server, event_schema, name, filter_predicate, stop_event)

    def list_traces(self) -> pd.DataFrame:
        """
        List all stored (active or inactive) traces on a this connection.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing the ID, name, timestamp, and state of each trace.
        """
        trace_info = []
        for trace in self._tom_server.Traces:
            info = {
                "ID": trace.ID,
                "Name": trace.Name,
                "Created Timestamp": trace.CreatedTimestamp,
                "Is Started": trace.IsStarted,
            }
            trace_info.append(info)

        return pd.DataFrame(trace_info, columns=["ID", "Name", "Created Timestamp", "Is Started"])

    def drop_traces(self) -> None:
        """
        Remove all traces on a server.
        """
        trace_collection = [trace for trace in self._tom_server.Traces]
        for trace in trace_collection:
            self._stop_and_drop_trace(trace)

    def drop_trace(self, trace_name: str) -> None:
        """
        Drop the trace with the specified name from the server.

        Parameters
        ----------
        trace_name : str
            Name of trace to drop.
        """
        trace_collection = [trace for trace in self._tom_server.Traces]
        for trace in trace_collection:
            if trace.Name == trace_name:
                self._stop_and_drop_trace(trace)

    def _stop_and_drop_trace(self, trace):
        from Microsoft.AnalysisServices import DropOptions

        if trace.IsStarted:
            trace.Stop()
        trace.Drop(DropOptions.IgnoreFailures)

    def disconnect_and_dispose(self) -> None:
        """
        Clear all traces on a server.
        """
        self._tom_server.Disconnect()
        self._tom_server.Dispose()

    def discover_event_schema(self, strict_types=False) -> pd.DataFrame:
        """
        Discover all event categories, events, and corresponding columns available to use for Tracing.

        Parameters
        ----------
        strict_types : bool, default=False
            If True, will enforce strict data types for the DataFrame columns.

        Returns
        -------
        pandas.DataFrame
            DataFrame containing the schema information.
        """
        event_df = self._dataset_client._evaluate_dax("SELECT * FROM $System.DISCOVER_TRACE_EVENT_CATEGORIES")
        columns = self._parse_column_schema()

        rows = []
        for i in range(event_df.shape[0]):
            xml_data = event_df.iloc[i, 0]
            event_category_elem = ET.fromstring(xml_data)  # type: ignore
            category_rows = self._parse_event_category(event_category_elem, columns)
            rows.extend(category_rows)

        col_types = {
                "Event Category Name": "string",
                "Event Category Description": "string",
                "Event Name": "string",
                "Event ID": "int",
                "Event Description": "string",
                "Event Column Name": "string",
                "Event Column ID": "int",
                "Event Column Description": "string"
            }
        df = pd.DataFrame(rows, columns=col_types.keys())

        if strict_types:
            df = df.astype(col_types)
        else:
            import warnings
            warnings.warn(
                "Using the default `strict_types=False` may lead to unexpected behavior if the data types do not "
                "match. We will enforce `strict_types=True` in the next release.",
                UserWarning
            )

        return df

    def _parse_column_schema(self) -> dict:
        column_df = self._dataset_client._evaluate_dax("SELECT * FROM $System.DISCOVER_TRACE_COLUMNS")
        columns = {}
        for _, row in column_df.iterrows():
            col_element = ET.fromstring(row.Data)
            col_id = self._extract_element(col_element, "ID")
            columns[col_id] = {
                "Name": self._extract_element(col_element, "NAME"),
                "Description": self._extract_element(col_element, "DESCRIPTION"),
            }

        return columns

    def _parse_event_category(self, event_category_elem: ET.Element, columns: dict) -> List[dict]:
        rows = []

        # Iterate through EVENT elements
        for event_elem in event_category_elem.findall('.//EVENT'):

            # Iterate through EVENTCOLUMN elements
            for event_column_elem in event_elem.findall('.//EVENTCOLUMN'):
                event_column_id = self._extract_element(event_column_elem, "ID")

                rows.append({
                    "Event Category Name": self._extract_element(event_category_elem, "NAME"),
                    "Event Category Description": self._extract_element(event_category_elem, "DESCRIPTION"),
                    "Event Name": self._extract_element(event_elem, "NAME"),
                    "Event ID": self._extract_element(event_elem, "ID"),
                    "Event Description": self._extract_element(event_elem, "DESCRIPTION"),
                    "Event Column Name": columns[event_column_id]["Name"],
                    "Event Column ID": event_column_id,
                    "Event Column Description": columns[event_column_id]["Description"]
                })

        return rows

    def _extract_element(self, element: ET.Element, key: str) -> Optional[str]:
        result_elem = element.find(key)
        if result_elem is not None:
            return result_elem.text
        else:
            return None
