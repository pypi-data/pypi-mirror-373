import pandas as pd
import uuid
import warnings

from sempy.fabric._utils import (
    dotnet_to_pandas_date,
    clr_to_pandas_dtype,
    convert_pascal_case_to_space_delimited,
    convert_space_delimited_case_to_pascal
)

from typing import Dict, List, Optional, Callable


class Trace():
    """
    Trace object for collecting diagnostic and performance related information from the Microsoft Analysis Services Tabular server.

    Python wrapper around `Microsoft Analysis Services Trace <https://learn.microsoft.com/en-us/analysis-services/trace-events/analysis-services-trace-events?view=asallproducts-allversions>`_

    NOTE: This feature is only intended for exploratory use. Due to the asynchronous communication required between the
    Microsoft Analysis Services (AS) Server and other AS clients, trace events are registered on a best-effort basis where timings are
    dependent on server load.

    Parameters
    ----------
    server : Microsoft.AnalysisServices.Tabular.Server
        Server object to add trace to.
    event_schema : dict
        Dictionary containing event types as keys and list of column names for that event as values.
        Both event and column names must be specified as strings, either in Space Delimited Case or PascalCase.
    name : str, default=None
        Name identifying trace. If None, the trace name will be "SemanticLinkTrace_%GUID%".
    filter_predicate : Callable, default=None
        Function that takes in `TraceEventArgs <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.traceeventargs?view=analysisservices-dotnet>`_
        and returns a boolean based on whether or not the trace with those args should be recorded.
    stop_event : str, default=None
        Event class that signals the end of the trace. `trace.stop()` will wait for this event (with specified timeout) before returning logs.
    """
    def __init__(
        self,
        server,
        event_schema: Dict[str, List[str]],
        name: Optional[str] = None,
        filter_predicate: Optional[Callable[..., bool]] = None,
        stop_event: Optional[str] = None
    ):
        from Microsoft.Fabric.SemanticLink import TraceCollector

        if name is not None and not isinstance(name, str):
            raise TypeError(f"Unexpected type {type(name)} for \"name\" element: not a str")

        guid = str(uuid.uuid4())
        if name is None:
            name = f"SemanticLinkTrace_{guid}"

        self._trace_collector = TraceCollector(server, name, guid, stop_event)
        self._stop_event = stop_event
        self.add_events(event_schema)
        if filter_predicate is not None:
            self.set_filter(filter_predicate)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        self.drop()

    @property
    def is_started(self) -> bool:
        """
        Whether or not this trace is currently started.
        """
        return self._trace_collector.IsStarted()

    @property
    def name(self) -> str:
        """
        Name of the trace.
        """
        return self._trace_collector.GetName()

    def add_events(self, event_schema: Dict[str, List[str]]) -> None:
        """
        Add events and their corresponding columns to the trace.

        The trace must be stopped in order to add events.

        Parameters
        ----------
        event_schema : dict
            Dictionary containing event types as keys and list of column names for that event as values.
            Both event and column names must be specified as strings, either in Space Delimited Case or PascalCase.
        """
        from System import ArgumentException

        if self.is_started:
            raise RuntimeError("Cannot add events to trace when trace is started. Stop the trace to add new events.")

        for event_type, columns in event_schema.items():
            if not isinstance(event_type, str):
                raise TypeError(f"Unexpected type {type(event_type)} for \"event_type\" element: not a str")
            if not isinstance(columns, list):
                raise TypeError(f"Unexpected type {type(columns)} for \"columns\" element: not a list")
            for col in columns:
                if not isinstance(col, str):
                    raise TypeError(f"Unexpected type {type(col)} for \"column\" element: not a str")
            if len(columns) == 0:
                raise ValueError(f"Event '{event_type}' must have at least one column specified.")

            pascal_columns = [convert_space_delimited_case_to_pascal(col) for col in columns]
            try:
                self._trace_collector.AddEvent(event_type, pascal_columns)
            except ArgumentException as e:
                raise ValueError(f"{e.Message}\nUse trace_connection.discover_event_schema() to get a full list of event types and valid columns per event.")

    def set_filter(self, filter_predicate: Callable[..., bool]) -> None:
        """
        Set a custom filter predicate for event preprocessing.

        Parameters
        ----------
        filter_predicate : Callable
            Function that takes in `TraceEventArgs <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.traceeventargs?view=analysisservices-dotnet>`_,
            and returns a boolean based on whether or not the trace with those args should be recorded.
        """
        from System import Predicate
        from Microsoft.AnalysisServices.Tabular import TraceEventArgs

        self._trace_collector.set_FilterPredicate(Predicate[TraceEventArgs](filter_predicate))

    def start(self, delay: int = 3) -> None:
        """
        Start the trace.

        Note: After starting the trace, there may be a slight delay as the engine registers and subscribes to trace events.
        The exact time of this delay may vary, but if you see that no trace events are being logged, you can increase the `delay` parameter.

        Parameters
        ----------
        delay : int, default=3
            Number of seconds to sleep for after starting the trace to allow engine to subscribe to added trace events.
        """
        self._trace_collector.Start(delay)

    def stop(self, timeout: int = 5) -> pd.DataFrame:
        """
        Stop the trace and retrieve the trace logs.

        Parameters
        ----------
        timeout : int, default=5
            Number of seconds to wait for stop event (specified in constructor) to register.
            If stop event is not reached in this time frame, the collected trace logs will still be returned but may be incomplete.

        Returns
        -------
        pandas.DataFrame
            DataFrame where every row is data from the events added to the trace.
        """
        stop_event_reached = self._trace_collector.Stop(timeout)
        if not stop_event_reached:
            warnings.warn(f"Did not reach specified stop event '{self._stop_event}' before stopping the trace.", UserWarning)
        return self.get_trace_logs()

    def get_trace_logs(self) -> pd.DataFrame:
        """
        Retrieve the trace logs as a DataFrame.

        This can be executed while the trace is still running.

        Returns
        -------
        pandas.DataFrame
            DataFrame where every row is data from the events added to the trace.
        """
        trace_logs = self._trace_collector.GetTraceLogs()
        if len(trace_logs) == 0:
            warnings.warn("No trace logs have been recorded. Try starting the trace with a larger 'delay' parameter (default is 3 seconds) \
                           to allow the engine enough time to register and subscribe to the trace events.", UserWarning)

        df = pd.DataFrame(trace_logs)

        # add in missing columns to keep a consistent schema
        columns = [c.Key for c in self._trace_collector.GetColumnProperties()]
        df = df.reindex(columns=columns)

        df = self._convert_dtypes(df)
        df = df.rename(columns=lambda c: convert_pascal_case_to_space_delimited(c))

        return df

    def _convert_dtypes(self, df):
        column_properties = self._trace_collector.GetColumnProperties()
        conversion_map = {}
        datetime_cols = []

        for col_property in column_properties:
            column_name = col_property.Key
            property_info = col_property.Value

            # Default to string if no type is found for current column
            col_type = getattr(
                getattr(property_info, "PropertyType", None),
                "Name",
                "String"
            )

            # For tracing, the only columns that are not string are
            #    Int64: CPUTime, Duration, IntegerData, ProgressTotal
            #    Int32: Severity
            #    DateTime: CurrentTime, EndTime, StartTime
            #    Other: EventClass, EventSubclass, ObjectType, Success, XmlaMessages
            # See https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.traceeventargs?view=analysisservices-dotnet for more.
            pandas_type = clr_to_pandas_dtype(col_type)
            if pandas_type:
                conversion_map[column_name] = clr_to_pandas_dtype(col_type)
            elif col_type == 'DateTime':
                datetime_cols.append(column_name)
            else:
                # cast all other "other" types into string form (ex: <Microsoft.AnalysisServices.TraceEventClass object> --> str)
                conversion_map[column_name] = 'string'

        converted_df = df.astype(conversion_map)
        converted_df[datetime_cols] = converted_df[datetime_cols].apply(lambda c: c.apply(dotnet_to_pandas_date, milliseconds=True))
        return converted_df

    def drop(self) -> None:
        """
        Remove the current trace from its parent Server connection.
        """
        self._trace_collector.Drop()

    def add_event_handler(self, on_event_func: Callable) -> None:
        """
        Add a custom handler for trace events.

        Parameters
        ----------
        on_event_func : Callable
            Function to execute on every event.
        """
        from Microsoft.AnalysisServices.Tabular import TraceEventHandler

        trace = self._trace_collector.GetTrace()
        trace.OnEvent += TraceEventHandler(on_event_func)

    @staticmethod
    def get_default_query_trace_schema() -> Dict[str, List[str]]:
        """
        Get a default event schema for DAX Query Tracing.

        Default event classes: "QueryBegin", "QueryEnd", "VertiPaqSEQueryBegin", "VertiPaqSEQueryEnd", "VertiPaqSEQueryCacheMatch", "DirectQueryBegin", "DirectQueryEnd"
        Default event columns: "EventClass", "EventSubclass", "CurrentTime", "TextData", "SessionID", "StartTime", "EndTime", "Duration", "CpuTime", "Success"

        Returns
        -------
        dict
            Dictionary containing event types as keys and list of column names for that event as values.
        """
        se_base_cols = ["EventClass", "EventSubclass", "CurrentTime", "TextData", "SessionID"]
        dq_base_cols = ["EventClass", "CurrentTime", "TextData", "SessionID"]
        begin_cols = ["StartTime"]
        end_cols = ["StartTime", "EndTime", "Duration", "CpuTime", "Success"]

        return {
            "VertiPaqSEQueryBegin":         se_base_cols + begin_cols,
            "VertiPaqSEQueryEnd":           se_base_cols + end_cols,
            "VertiPaqSEQueryCacheMatch":    se_base_cols,
            "DirectQueryBegin":             dq_base_cols + begin_cols,
            "DirectQueryEnd":               dq_base_cols + end_cols,
            "QueryBegin":                   se_base_cols + begin_cols,
            "QueryEnd":                     se_base_cols + end_cols
        }
