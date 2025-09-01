from uuid import UUID
import warnings
import pandas as pd
from IPython.display import display, HTML
from typing import TYPE_CHECKING, Dict, List, Literal, Optional, Union

import sempy.fabric as fabric
from sempy._utils._log import log
from sempy._utils import _icons as icons
from sempy.fabric._client._utils import _format_dax_object_name as format_dax_object_name
from sempy.fabric._credentials import with_credential
from sempy.fabric._flat import resolve_dataset_name_and_id, resolve_workspace_name_and_id

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class VertipaqAnalyzer:

    VERTIPAQ_VIEW = pd.DataFrame([
        {
            "ViewName": "Model",
            "ColumnName": "Dataset Name",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The name of the semantic model",
        },
        {
            "ViewName": "Model",
            "ColumnName": "Total Size",
            "Type": icons.data_type_long,
            "Format": icons.size_format,
            "Tooltip": "The size of the model (in bytes)",
        },
        {
            "ViewName": "Model",
            "ColumnName": "Table Count",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of tables in the semantic model",
        },
        {
            "ViewName": "Model",
            "ColumnName": "Column Count",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of columns in the semantic model",
        },
        {
            "ViewName": "Model",
            "ColumnName": "Compatibility Level",
            "Type": icons.data_type_long,
            "Format": icons.no_format,
            "Tooltip": "The compatibility level of the semantic model",
        },
        {
            "ViewName": "Model",
            "ColumnName": "Default Mode",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The default query mode of the semantic model",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Table Name",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The name of the table",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Type",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The type of table"
        },
        {
            "ViewName": "Table",
            "ColumnName": "Row Count",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of rows in the table",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Total Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "Data Size + Dictionary Size + Hierarchy Size (in bytes)",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Data Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of the data for all the columns in this table (in bytes)",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Dictionary Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of the column's dictionary for all columns in this table (in bytes)",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Hierarchy Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of hierarchy structures for all columns in this table (in bytes)",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Relationship Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of the relationships in the table (in bytes)",
        },
        {
            "ViewName": "Table",
            "ColumnName": "User Hierarchy Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of user hierarchy structures for all columns in this table (in bytes)",
        },
        {
            "ViewName": "Table",
            "ColumnName": "% DB",
            "Type": icons.data_type_double,
            "Format": icons.pct_format,
            "Tooltip": "The size of the table relative to the size of the semantic model",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Partitions",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of partitions in the table",
        },
        {
            "ViewName": "Table",
            "ColumnName": "Columns",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of columns in the table",
        },
        {
            "ViewName": "Partition",
            "ColumnName": "Table Name",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The name of the table",
        },
        {
            "ViewName": "Partition",
            "ColumnName": "Partition Name",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The name of the partition within the table",
        },
        {
            "ViewName": "Partition",
            "ColumnName": "Mode",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The query mode of the partition",
        },
        {
            "ViewName": "Partition",
            "ColumnName": "Record Count",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of rows in the partition",
        },
        {
            "ViewName": "Partition",
            "ColumnName": "Segment Count",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of segments within the partition",
        },
        {
            "ViewName": "Partition",
            "ColumnName": "Records per Segment",
            "Type": icons.data_type_double,
            "Format": icons.int_format,
            "Tooltip": "The number of rows per segment",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Table Name",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The name of the table",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Column Name",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The name of the column",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Type",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The type of column",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Cardinality",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of unique rows in the column",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Total Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "Data Size + Dictionary Size + Hierarchy Size (in bytes)",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Data Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of the data for the column (in bytes)",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Dictionary Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of the column's dictionary (in bytes)",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Hierarchy Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of hierarchy structures (in bytes)",
        },
        {
            "ViewName": "Column",
            "ColumnName": "% Table",
            "Type": icons.data_type_double,
            "Format": icons.pct_format,
            "Tooltip": "The size of the column relative to the size of the table",
        },
        {
            "ViewName": "Column",
            "ColumnName": "% DB",
            "Type": icons.data_type_double,
            "Format": icons.pct_format,
            "Tooltip": "The size of the column relative to the size of the semantic model",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Data Type",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The data type of the column",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Encoding",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The encoding type for the column",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Is Resident",
            "Type": icons.data_type_bool,
            "Format": icons.no_format,
            "Tooltip": "Indicates whether the column is in memory or not",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Temperature",
            "Type": icons.data_type_double,
            "Format": icons.int_format,
            "Tooltip": "A decimal indicating the frequency and recency of queries against the column",
        },
        {
            "ViewName": "Column",
            "ColumnName": "Last Accessed",
            "Type": icons.data_type_timestamp,
            "Format": icons.no_format,
            "Tooltip": "The time the column was last queried",
        },
        {
            "ViewName": "Hierarchy",
            "ColumnName": "Table Name",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The name of the table",
        },
        {
            "ViewName": "Hierarchy",
            "ColumnName": "Hierarchy Name",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The name of the hierarchy",
        },
        {
            "ViewName": "Hierarchy",
            "ColumnName": "Used Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of user hierarchy structures (in bytes)",
        },
        {
            "ViewName": "Relationship",
            "ColumnName": "From Object",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The from table/column in the relationship",
        },
        {
            "ViewName": "Relationship",
            "ColumnName": "To Object",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The to table/column in the relationship",
        },
        {
            "ViewName": "Relationship",
            "ColumnName": "Multiplicity",
            "Type": icons.data_type_string,
            "Format": icons.no_format,
            "Tooltip": "The cardinality on each side of the relationship",
        },
        {
            "ViewName": "Relationship",
            "ColumnName": "Used Size",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The size of the relationship (in bytes)",
        },
        {
            "ViewName": "Relationship",
            "ColumnName": "Max From Cardinality",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of unique values in the column used in the from side of the relationship",
        },
        {
            "ViewName": "Relationship",
            "ColumnName": "Max To Cardinality",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of unique values in the column used in the to side of the relationship",
        },
        {
            "ViewName": "Relationship",
            "ColumnName": "Missing Rows",
            "Type": icons.data_type_long,
            "Format": icons.int_format,
            "Tooltip": "The number of rows in the 'from' table which do not map to the key column in the 'to' table",
        },
    ])

    def __init__(self,
                 dataset: Union[str, UUID],
                 workspace: Optional[Union[str, UUID]] = None
                 ):
        from sempy.fabric import connect_semantic_model

        self._workspace_name, self._workspace_id = resolve_workspace_name_and_id(workspace)
        self._dataset_name, self._dataset_id = resolve_dataset_name_and_id(dataset, self._workspace_id)

        with connect_semantic_model(
            dataset=self._dataset_id, workspace=self._workspace_id, readonly=True
        ) as tom:
            self._compat_level = tom._compat_level
            self._is_direct_lake = tom.is_direct_lake
            self._default_mode = tom.model.DefaultMode
            self._table_count = tom.model.Tables.Count
            self._column_count = len(list(tom.all_columns))
            self._table_total_size = None  # Placeholder for table total size
            self._db_total_size = None  # Placeholder for database total size

    def _transform_df(
            self,
            df: pd.DataFrame,
            columns_to_rename: Optional[Dict[str, str]] = None,
            columns_to_keep: Optional[List[str]] = None,
            columns_to_drop: Optional[List[str]] = None,
            sort_by: Optional[str] = None,
            ascending: bool = False
            ) -> pd.DataFrame:
        if columns_to_rename:
            df = df.rename(columns=columns_to_rename)

        if columns_to_keep:
            df = df[df.columns.intersection(columns_to_keep)]

        if columns_to_drop:
            df = df.drop(columns=columns_to_drop)

        if sort_by:
            df = df.sort_values(by=sort_by, ascending=ascending)

        df = df.reset_index(drop=True)

        return df

    def _style_columns_based_on_types(self, df: pd.DataFrame, column_format_mapping: Dict[str, str]) -> pd.DataFrame:
        """Style columns based on their types"""

        def _convert_size(byte_size: int) -> str:
            if byte_size < 1024:
                return f"{byte_size} B"
            elif byte_size < 1024 ** 2:
                return f"{byte_size / 1024:.2f} KB"
            elif byte_size < 1024 ** 3:
                return f"{byte_size / 1024 ** 2:.2f} MB"
            else:
                return f"{byte_size / 1024 ** 3:.2f} GB"

        format_funcs = {
            icons.int_format: lambda x: "{:,}".format(x) if pd.notnull(x) else "",
            icons.pct_format: lambda x: "{:.2f}%".format(x) if pd.notnull(x) else "",
            icons.size_format: lambda x: _convert_size(x) if pd.notnull(x) else "",
            "": lambda x: "{}".format(x),
        }

        for col, format in column_format_mapping.items():
            if format in format_funcs:
                df[col] = df[col].map(format_funcs[format])

        return df

    def _analyze_table(self):
        """Analyze table data"""
        df_table = fabric.list_tables(dataset=self._dataset_id, workspace=self._workspace_id, advanced=True, include_internal=True)

        columns_to_keep = self.VERTIPAQ_VIEW.query("ViewName == 'Table'")["ColumnName"].tolist()
        df_table = self._transform_df(
            df_table,
            columns_to_rename={"Name": "Table Name"},
            columns_to_keep=columns_to_keep,
            sort_by="Total Size",
            ascending=False
        )

        return df_table

    def _analyze_column(self):
        """Analyze column data"""
        df_column = fabric.list_columns(dataset=self._dataset_id, workspace=self._workspace_id, extended=True)

        self._table_total_size = df_column.groupby("Table Name")["Total Size"].transform("sum")
        self._db_total_size = df_column["Total Size"].sum()

        insert_index = df_column.columns.get_loc("Encoding")
        df_column.insert(insert_index, "% Table", round((df_column["Total Size"] / self._table_total_size) * 100, 2))
        df_column.insert(insert_index + 1, "% DB", round((df_column["Total Size"] / self._db_total_size) * 100, 2))
        df_column["Column Object"] = format_dax_object_name(df_column["Table Name"], df_column["Column Name"])
        df_column = df_column[df_column["Type"] != "RowNumber"]

        columns_to_keep = self.VERTIPAQ_VIEW.query("ViewName == 'Column'")["ColumnName"].tolist()
        df_column = self._transform_df(
            df_column,
            columns_to_keep=columns_to_keep,
            columns_to_rename={"Column Cardinality": "Cardinality"},
        )
        df_column_size = self._transform_df(df_column, sort_by="Total Size", ascending=False)
        df_column_temperature = self._transform_df(df_column, sort_by="Temperature", ascending=False)

        return df_column_size, df_column_temperature

    def _analyze_hierarchy(self):
        """Analyze hierarchy data"""
        df_hierarchy = fabric.list_hierarchies(dataset=self._dataset_id, workspace=self._workspace_id, extended=True)

        df_hierarchy = (
            df_hierarchy[df_hierarchy["Level Ordinal"] == 0]
            .fillna({"Used Size": 0})
        )
        df_hierarchy["Used Size"] = df_hierarchy["Used Size"].astype(int)

        columns_to_keep = self.VERTIPAQ_VIEW.query("ViewName == 'Hierarchy'")["ColumnName"].tolist()
        df_hierarchy = self._transform_df(
            df_hierarchy,
            columns_to_keep=columns_to_keep,
            sort_by="Used Size",
            ascending=False
        )

        return df_hierarchy

    def _analyze_partition(self):
        """Analyze partition data"""
        df_partition = fabric.list_partitions(dataset=self._dataset_id, workspace=self._workspace_id, extended=True)

        columns_to_keep = self.VERTIPAQ_VIEW.query("ViewName == 'Partition'")["ColumnName"].tolist()
        df_partition = self._transform_df(
            df_partition,
            columns_to_keep=columns_to_keep,
            sort_by="Record Count",
            ascending=False
        )

        df_partition["Records per Segment"] = round(
            df_partition["Record Count"] / df_partition["Segment Count"], 2
        )  # Remove after records per segment is fixed

        return df_partition

    def _analyze_relationship(self):
        """Analyze relationship data"""
        if self._is_direct_lake:
            warnings.warn(
                f"{icons.warning} The '{self._dataset_name}' semantic model within the '{self._workspace_name}' workspace is a Direct Lake model. "
                "Model Memory Analyzer does not support calculating missing rows in relationships on a Direct Lake model yet."
            )
            df_relationship = fabric.list_relationships(dataset=self._dataset_id, workspace=self._workspace_id, extended=True, calculate_missing_rows=False)
            df_relationship["Missing Rows"] = 0
        else:
            df_relationship = fabric.list_relationships(dataset=self._dataset_id, workspace=self._workspace_id, extended=True, calculate_missing_rows=True)

        df_relationship["Used Size"] = df_relationship["Used Size"].fillna(0).astype("int")

        df_relationship.insert(0, "From Object", format_dax_object_name(df_relationship["From Table"], df_relationship["From Column"]))
        df_relationship.insert(1, "To Object", format_dax_object_name(df_relationship["To Table"], df_relationship["To Column"]))

        columns_to_keep = self.VERTIPAQ_VIEW.query("ViewName == 'Relationship'")["ColumnName"].tolist()
        df_relationship = self._transform_df(
            df_relationship,
            columns_to_keep=columns_to_keep,
            sort_by="Used Size",
            ascending=False
        )

        return df_relationship

    def _analyze_model(self):
        """Analyze model data"""
        df_model = pd.DataFrame(
            {
                "Dataset Name": self._dataset_name,
                "Total Size": self._db_total_size,
                "Table Count": self._table_count,
                "Column Count": self._column_count,
                "Compatibility Level": self._compat_level,
                "Default Mode": self._default_mode,
            },
            index=[0],
        )
        df_model.reset_index(drop=True, inplace=True)
        df_model["Default Mode"] = df_model["Default Mode"].astype(str)

        return df_model

    def analyze(self):
        """Analyze the semantic model"""
        if self._table_count == 0:
            warnings.warn(
                f"{icons.warning} The '{self._dataset_name}' semantic model within the '{self._workspace_name}' workspace has no tables."
                "Model Memory Analyzer can only be run if the semantic model has tables."
            )
            return

        previous_mode = pd.options.mode.copy_on_write
        pd.options.mode.copy_on_write = True

        try:
            df_table = self._analyze_table()
            df_column_size, df_column_temperature = self._analyze_column()
            df_partition = self._analyze_partition()
            df_hierarchy = self._analyze_hierarchy()
            df_relationship = self._analyze_relationship()
            df_model = self._analyze_model()
        finally:
            pd.options.mode.copy_on_write = previous_mode

        analysis_data = {
            "Model Summary": df_model,
            "Tables": df_table,
            "Partitions": df_partition,
            "Columns (Total Size)": df_column_size,
            "Columns (Temperature)": df_column_temperature,
            "Relationships": df_relationship,
            "Hierarchies": df_hierarchy
        }

        return analysis_data

    def visualize(self, analysis_data: Dict[str, pd.DataFrame]):
        """Visualize the analysis data"""

        def _generate_html() -> str:
            """Generate the HTML for the tabs and tab content"""
            tab_html = '<div class="tab">'
            content_html = ''

            for i, (tab_name, view_name) in enumerate(analysis_views.items()):
                if i == 0:
                    tab_html += f'<button class="tablinks active" onclick="openTab(event, \'tab0\')">{tab_name}</button>'
                else:
                    tab_html += f'<button class="tablinks" onclick="openTab(event, \'tab{i}\')">{tab_name}</button>'

                df = analysis_data[tab_name].copy()
                styled_df = self._style_columns_based_on_types(
                    df,
                    column_format_mapping={row["ColumnName"]: row["Format"] for _, row in self.VERTIPAQ_VIEW.query(f"ViewName == '{view_name}'").iterrows()}
                )
                df_html = styled_df.to_html()
                for col in styled_df.columns:
                    df_tooltip = self.VERTIPAQ_VIEW.query(f"ViewName == '{view_name}' and ColumnName == '{col}'")
                    if not df_tooltip.empty:
                        tooltip = df_tooltip.iloc[0]["Tooltip"]
                        df_html = df_html.replace(f"<th>{col}</th>", f'<th title="{tooltip}">{col}</th>')
                    else:
                        warnings.warn(f"{icons.warning} Tooltip not found for column '{col}' in view '{view_name}'")

                if i == 0:
                    content_html += f'<div id="tab0" class="tabcontent active"><h3>{tab_name}</h3>{df_html}</div>'
                else:
                    content_html += f'<div id="tab{i}" class="tabcontent"><h3>{tab_name}</h3>{df_html}</div>'

            tab_html += '</div>'

            return tab_html + content_html

        def _generate_style():
            """Generate basic styles for the tabs and tab content"""
            return """
<style>
    .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
    .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }
    .tab button:hover { background-color: #ddd; }
    .tab button.active { background-color: #ccc; }
    .tabcontent { display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }
    .tabcontent.active { display: block; }
</style>
"""

        def _generate_script():
            """Generate the script to handle the tab switching"""
            return """
<script>
function openTab(evt, tabName) {
    var i, tabcontent, tablinks;
    tabcontent = document.getElementsByClassName("tabcontent");
    for (i = 0; i < tabcontent.length; i++) {
        tabcontent[i].style.display = "none";
    }
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }
    document.getElementById(tabName).style.display = "block";
    evt.currentTarget.className += " active";
}
</script>
"""

        analysis_views = {
            "Model Summary": "Model",
            "Tables": "Table",
            "Partitions": "Partition",
            "Columns (Total Size)": "Column",
            "Columns (Temperature)": "Column",
            "Relationships": "Relationship",
            "Hierarchies": "Hierarchy"
        }  # {"Tab Name": "View Name"}

        analysis_html = _generate_style() + _generate_html() + _generate_script()

        # display the HTML
        display(HTML(analysis_html))


@log
@with_credential
def model_memory_analyzer(
    dataset: Union[str, UUID],
    workspace: Optional[Union[str, UUID]] = None,
    export: Optional[Literal["html", "table", "zip"]] = "html",
    return_dataframe: Optional[bool] = False,
    credential: Optional["TokenCredential"] = None
) -> Optional[Dict[str, pd.DataFrame]]:
    """
    Display an HTML visualization of the Vertipaq Analyzer statistics from a semantic model.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or ID of the semantic model.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or ID in which the semantic model exists.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    export : {"html", "table", "zip"}, default="html"
        The export format for the analysis data.
        - "html": Displays the analysis data as an HTML table. (default)
        - "table": Exports the analysis data to delta tables (appended) in your lakehouse.
        - "zip": Exports the analysis data to a zip file in your lakehouse.
    return_dataframe : bool, default=False
        Whether to return the analysis data as a DataFrame.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    Optional[Dict[str, pandas.DataFrame]]
        The analysis data as a dictionary of DataFrames if return_dataframe is True.
        The dictionary keys are:
        - "Model Summary"
        - "Tables"
        - "Partitions"
        - "Columns"
        - "Relationships"
        - "Hierarchies"
    """

    assert export in ["html", "table", "zip"], f"Invalid export format '{export}'. Choose from 'html', 'table', or 'zip'."

    if export == "table":
        raise NotImplementedError("Export to table is not yet supported.")
    elif export == "zip":
        raise NotImplementedError("Export to zip is not yet supported.")

    warnings.filterwarnings(
        "ignore", message="createDataFrame attempted Arrow optimization*"
    )

    analyzer = VertipaqAnalyzer(dataset=dataset, workspace=workspace)
    analysis_data = analyzer.analyze()

    if analysis_data is not None:
        if export == "html":
            analyzer.visualize(analysis_data)

        if return_dataframe:
            analysis_data["Columns"] = analysis_data.pop("Columns (Total Size)")
            analysis_data.pop("Columns (Temperature)")

            return analysis_data

    return None
