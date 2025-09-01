from contextlib import contextmanager
import regex as re
from typing import TYPE_CHECKING, Callable, Dict, Iterator, List, Optional, Union, cast
import pandas as pd

import sempy.fabric as fabric
from sempy.fabric._client._tom import TOMWrapper, connect_semantic_model
from sempy.fabric._client._utils import _format_dax_object_name, _init_analysis_services
from sempy._utils._log import log

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class ModelCalcDependencies:
    """
    Convenience wrapper around the calculated dependencies of a semantic model. Always use the get_model_calc_dependencies function to make sure the dependencies are initialized correctly.

    Parameters
    ----------
    dependencies_df : pd.DataFrame
        A DataFrame containing dependency data for all objects within the semantic model.
        This DataFrame includes information about object names, types, expressions,
        referenced tables, and other dependency details.
    tom : TOMWrapper
        An instance of the TOMWrapper, used to interact with the semantic model.
        This allows for access to model objects and facilitates operations on tables,
        columns, and measures.
    """

    _dependencies_df: pd.DataFrame
    _tom: TOMWrapper

    def __init__(self, dependencies_df: pd.DataFrame, tom: TOMWrapper):
        self._dependencies_df = dependencies_df
        self._tom = tom

    @property
    def dependencies_df(self) -> pd.DataFrame:
        """
        Return the DataFrame of calculated dependencies.

        Returns
        -------
        pd.DataFrame
            DataFrame of calculated dependencies.
        """
        return self._dependencies_df

    def _yield_matched_objects(
        self,
        target_obj_names: List[str],
        all_objects: Iterator[Union["TOM.Table", "TOM.Column", "TOM.Measure"]],
        format_func: Optional[Callable[..., str]] = None
    ) -> Iterator[Union["TOM.Table", "TOM.Column", "TOM.Measure"]]:
        """
        Yield matched objects from a list of objects based on matching names.

        Parameters
        ----------
        target_obj_names : List[str]
            A list of object names to match.
        all_objects : List[Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]]
            A list of all objects to search.
        format_func : Optional[Callable[..., str]], default=None
            A function to format the object name before matching. The function should take an object as input and return a string.

        Yields
        ------
        Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            Matched objects.
        """
        def default_format_func(obj):
            return obj.Name

        if format_func is None:
            format_func = default_format_func

        for obj in all_objects:
            if format_func(obj) in target_obj_names:
                yield obj

    def _fetch_dependencies(
        self,
        tom_obj: "TOM.NamedMetadataObject",
        return_column: str = "Referenced Object",
        criteria: Optional[Dict[str, Union[str, List[str]]]] = None,
    ) -> List[str]:
        """
        Fetches dependencies of a given object with optional filtering criteria.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model.
        return_column : str, default="Referenced Object"
            The column name to return.
        criteria : Optional[Dict[str, List[str]]], default=None
            Optional dictionary for additional filtering criteria. Keys should be column names, and values should be the expected values.

        Returns
        -------
        List[str]
            A list of names of referenced objects.
        """
        obj_name = tom_obj.Name
        obj_type = str(tom_obj.ObjectType)

        if obj_type == "CalculationItem":
            obj_parent_name = tom_obj.Parent.Table.Name
        elif obj_type == "Table":
            obj_parent_name = obj_name
        else:
            obj_parent_name = tom_obj.Parent.Name

        if obj_type == "Table":
            expand_obj_types = ["Table", "Calc Table"]
        elif obj_type == "Column":
            expand_obj_types = ["Column", "Calc Column"]
        elif obj_type == "CalculationItem":
            expand_obj_types = ["Calculation Item"]
        else:
            expand_obj_types = [obj_type]

        filtered_df = self._dependencies_df
        filtered_df = filtered_df[
            (filtered_df["Object Name"] == obj_name)
            & (filtered_df["Object Type"].isin(expand_obj_types))
            & (filtered_df["Table Name"] == obj_parent_name)
        ]

        if criteria:
            for column, value in criteria.items():
                if isinstance(value, str):
                    value = [value]
                filtered_df = filtered_df[filtered_df[column].isin(value)]

        return filtered_df[return_column].unique().tolist()

    def _is_calculable(self, tom_obj: "TOM.NamedMetadataObject") -> bool:
        """
        Check if an object is calculable. Calculable objects include measures,
        calculated tables, calculated columns, and calculation items.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model to be checked.

        Returns
        -------
        bool
            A boolean value indicating whether the object is calculable.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        if tom_obj.ObjectType not in [
            TOM.ObjectType.Measure,
            TOM.ObjectType.Table,
            TOM.ObjectType.Column,
            TOM.ObjectType.CalculationItem
        ]:
            return False

        if (
            tom_obj.ObjectType == TOM.ObjectType.Column and
            not self._tom.is_calculated_column(tom_obj.Parent.Name, tom_obj.Name)
        ):
            return False

        if (
            tom_obj.ObjectType == TOM.ObjectType.Table and
            not self._tom.is_calculated_table(tom_obj.Name)
        ):
            return False

        return True

    def all_table_dependencies(self, tom_obj: "TOM.NamedMetadataObject",
                               transitive: bool = True) -> Iterator["TOM.Table"]:
        """
        Output an iterator of all the tables on which the specified object depends.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model.
        transitive : bool, default=True
            Whether to include transitive dependencies.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Table
            Tables on which the specified object depends.
        """
        criteria: Dict[str, Union[str, List[str]]] = {
            "Referenced Object Type": "Table"
        }

        if not transitive:
            criteria["Parent Node"] = tom_obj.Name

        dep_tables = self._fetch_dependencies(
            tom_obj,
            return_column="Referenced Table",
            criteria=criteria
        )

        dep_tables = list(set(dep_tables))

        yield from self._yield_matched_objects(dep_tables, self._tom.all_tables)

    def all_column_dependencies(self, tom_obj: "TOM.NamedMetadataObject",
                                transitive: bool = True) -> Iterator["TOM.Column"]:
        """
        Output an iterator of all the columns on which the specified object depends.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model.
        transitive : bool, default=True
            Whether to include transitive dependencies.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Column
            Columns on which the specified object depends.
        """

        criteria: Dict[str, Union[str, List[str]]] = {
            "Referenced Object Type": ["Column", "Calc Column"]
        }

        if not transitive:
            criteria["Parent Node"] = tom_obj.Name

        dep_columns = self._fetch_dependencies(
            tom_obj,
            return_column="Referenced Full Object Name",
            criteria=criteria
        )
        dep_columns = list(set(dep_columns))

        yield from self._yield_matched_objects(dep_columns, self._tom.all_columns, format_func=lambda c: cast(str, _format_dax_object_name(c.Parent.Name, c.Name)))

    def all_measure_dependencies(self, tom_obj: "TOM.NamedMetadataObject",
                                 transitive: bool = True) -> Iterator["TOM.Measure"]:
        """
        Output an iterator of all the measures on which the specified object depends.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model.
        transitive : bool, default=True
            Whether to include transitive dependencies.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Measure
            Measures on which the specified object depends.
        """

        criteria: Dict[str,  Union[str, List[str]]] = {
            "Referenced Object Type": "Measure"
        }

        if not transitive:
            criteria["Parent Node"] = tom_obj.Name

        dep_measures = self._fetch_dependencies(
            tom_obj,
            return_column="Referenced Object",
            criteria=criteria
        )

        dep_measures = list(set(dep_measures))

        yield from self._yield_matched_objects(dep_measures, self._tom.all_measures)

    def all_fully_qualified_measure_dependencies(self, tom_obj: Union[
        "TOM.Measure", "TOM.Table", "TOM.Column", "TOM.CalculationItem"
    ]) -> Iterator["TOM.Measure"]:
        """
        Output an iterator of all fully qualified measures on which the specified measure object depends.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Measure or Microsoft.AnalysisServices.Tabular.Table or Microsoft.AnalysisServices.Tabular.Column or Microsoft.AnalysisServices.Tabular.CalculationItem
            The TOM object which could have a measure within the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Measure
            All fully qualified measures on which the specified object depends.
        """  # noqa: E501

        if not self._is_calculable(tom_obj):
            raise ValueError("Object must be a measure, calculated table, "
                             "calculated column, or calculation item.")

        expr = self._tom.get_dax_expression(tom_obj)

        if not expr:
            yield from []

        for mea in self.all_measure_dependencies(tom_obj, transitive=False):
            if re.search(
                (
                    r"'?" +
                    re.escape(mea.Parent.Name) +
                    r"'?\s*\[" +
                    re.escape(mea.Name) +
                    r"\]"
                ),
                self._tom.get_dax_expression(tom_obj)
            ) is not None:
                yield mea

    def all_unqualified_column_dependencies(self, tom_obj: Union[
        "TOM.Measure", "TOM.Table", "TOM.Column", "TOM.CalculationItem"
    ]) -> Iterator["TOM.Column"]:
        """
        Output an iterator of all unqualified columns on which the specified measure object depends.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.Measure or Microsoft.AnalysisServices.Tabular.Table or Microsoft.AnalysisServices.Tabular.Column or Microsoft.AnalysisServices.Tabular.CalculationItem
            The TOM object which could have a measure within the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Column
            All unqualified columns on which the specified object depends.
        """  # noqa: E501
        if not self._is_calculable(tom_obj):
            raise ValueError("Object must be a measure, calculated table, "
                             "calculated column, or calculation item.")

        expr = self._tom.get_dax_expression(tom_obj)

        if not expr:
            yield from []

        def create_pattern(table_list, col_name):
            patterns = [
                r"(?<!" + re.escape(table) + r"\s*)(?<!" + re.escape(table) + r"'\s*)"
                for table in table_list
            ]
            combined_pattern = "".join(patterns) + re.escape(f"[{col_name}]")
            return re.compile(combined_pattern)

        for col in self.all_column_dependencies(tom_obj, transitive=False):
            table_list = [c.Parent.Name for c in self._tom.all_columns if c.Name == col.Name]
            pattern = create_pattern(table_list, col.Name)
            if pattern.search(expr) is not None:
                yield col

    def _fetch_references(
        self,
        tom_obj: "TOM.NamedMetadataObject",
        return_column: str = "Object Name",
        criteria: Optional[Dict[str, str]] = None
    ) -> List[str]:
        """
        Fetch references to a given object with optional filtering criteria.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model.
        return_column : str, default="Object Name"
            The column name to return.
        criteria : Optional[Dict[str, str]], default=None
            Optional dictionary for additional filtering criteria. Keys should be column names, and values should be the expected values.

        Returns
        -------
        List[str]
            A list of names of referencing objects.
        """
        obj_name = tom_obj.Name
        obj_type = str(tom_obj.ObjectType)

        if obj_type == "CalculationItem":
            obj_parent_name = tom_obj.Parent.Table.Name
        elif obj_type == "Table":
            obj_parent_name = obj_name
        else:
            obj_parent_name = tom_obj.Parent.Name

        if obj_type == "Table" and self._tom.is_calculated_table(obj_name):
            obj_type = "Calc Table"
        elif obj_type == "Column" and self._tom.is_calculated_column(obj_parent_name, obj_name):
            obj_type = "Calc Column"

        filtered_df = self._dependencies_df
        filtered_df = filtered_df[
            (filtered_df["Referenced Object"] == obj_name)
            & (filtered_df["Referenced Object Type"] == obj_type)
            & (filtered_df["Referenced Table"] == obj_parent_name)
        ]

        if criteria:
            for column, value in criteria.items():
                filtered_df = filtered_df[filtered_df[column] == value]

        return filtered_df[return_column].unique().tolist()

    def all_table_references(self, tom_obj: "TOM.NamedMetadataObject") -> Iterator["TOM.Table"]:
        """
        Output an iterator of all the tables which reference the specified object.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Table
            Tables which reference the specified object.
        """
        ref_tables = self._fetch_references(tom_obj, return_column="Table Name", criteria={"Object Type": "Table"}) + \
            self._fetch_references(tom_obj, return_column="Table Name", criteria={"Object Type": "Calc Table"})
        ref_tables = list(set(ref_tables))

        yield from self._yield_matched_objects(ref_tables, self._tom.all_tables)

    def all_column_references(self, tom_obj: "TOM.NamedMetadataObject") -> Iterator["TOM.Column"]:
        """
        Output an iterator of all the columns which reference the specified object.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Column
            Columns which reference the specified object.
        """
        ref_columns = self._fetch_references(tom_obj, return_column="Full Object Name", criteria={"Object Type": "Column"}) + \
            self._fetch_references(tom_obj, return_column="Full Object Name", criteria={"Object Type": "Calc Column"})
        ref_columns = list(set(ref_columns))

        yield from self._yield_matched_objects(ref_columns, self._tom.all_columns, format_func=lambda c: cast(str, _format_dax_object_name(c.Parent.Name, c.Name)))

    def all_measure_references(self, tom_obj: "TOM.NamedMetadataObject") -> Iterator["TOM.Measure"]:
        """
        Output an iterator of all the measures which reference the specified object.

        Parameters
        ----------
        tom_obj : Microsoft.AnalysisServices.Tabular.NamedMetadataObject
            The TOM object within the semantic model.

        Yields
        ------
        Microsoft.AnalysisServices.Tabular.Measure
            Measures which reference the specified object.
        """
        ref_measures = self._fetch_references(tom_obj, return_column="Object Name", criteria={"Object Type": "Measure"})
        ref_measures = list(set(ref_measures))

        yield from self._yield_matched_objects(ref_measures, self._tom.all_measures)

    def _fetch_used_in(
        self,
        tom_obj: Union["TOM.Table", "TOM.Column", "TOM.Measure"],
        criteria: Optional[Dict[str, str]] = None
    ) -> Iterator[Union["TOM.Table", "TOM.Column", "TOM.Measure"]]:
        """
        Helper function to fetch objects which reference a given object with optional filtering criteria. The output object type is determined by the input object type.

        This function is used to implement the used_in_* functions.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            An object (i.e. table/column) within a semantic model.
        criteria : Optional[Dict[str, str]], default=None
            Optional dictionary for additional filtering criteria. Keys should be column names, and values should be the expected values.

        Yields
        ------
        Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            Objects which reference the given object.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        obj_type = tom_obj.ObjectType

        if obj_type == TOM.ObjectType.Table:
            ref_objs = self._fetch_references(tom_obj, return_column="Table Name", criteria=criteria)
            yield from self._yield_matched_objects(ref_objs, self._tom.all_tables)

        elif obj_type == TOM.ObjectType.Column:
            ref_objs = self._fetch_references(tom_obj, return_column="Full Object Name", criteria=criteria)
            yield from self._yield_matched_objects(ref_objs, self._tom.all_columns, format_func=lambda c: cast(str, _format_dax_object_name(c.Parent.Name, c.Name)))

        elif obj_type == TOM.ObjectType.Measure:
            ref_objs = self._fetch_references(tom_obj, return_column="Object Name", criteria=criteria)
            yield from self._yield_matched_objects(ref_objs, self._tom.all_measures)

        else:
            raise ValueError(f"Object must be a table, column, or measure, but got {obj_type}.")

    def used_in_rls(self, tom_obj: Union["TOM.Table", "TOM.Column", "TOM.Measure"]) -> Iterator[Union["TOM.Table", "TOM.Column", "TOM.Measure"]]:
        """
        Identify the row level security filter expressions which reference a given object.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            An object (i.e. table/column) within a semantic model.

        Yields
        ------
        Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            Row allowed objects which reference the given object.
        """
        yield from self._fetch_used_in(tom_obj, criteria={"Object Type": "Rows Allowed"})

    def used_in_data_coverage_definition(self, tom_obj: Union["TOM.Table", "TOM.Column", "TOM.Measure"]) -> Iterator[Union["TOM.Table", "TOM.Column", "TOM.Measure"]]:
        """
        Identify the data coverage definition which reference a given object.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            An object (i.e. table/column) within a semantic model.

        Yields
        ------
        Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            Data coverage definition objects which reference the given object.
        """
        yield from self._fetch_used_in(tom_obj, criteria={"Object Type": "Data Coverage Definition"})

    def used_in_calc_item(self, tom_obj: Union["TOM.Table", "TOM.Column", "TOM.Measure"]) -> Iterator[Union["TOM.Table", "TOM.Column", "TOM.Measure"]]:
        """
        Identify the calculation item which reference a given object.

        Parameters
        ----------
        tom_obj : Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            An object (i.e. table/column) within a semantic model.

        Yields
        ------
        Union[Microsoft.AnalysisServices.Tabular.Table, Microsoft.AnalysisServices.Tabular.Column, Microsoft.AnalysisServices.Tabular.Measure]
            Calculation item objects which reference the given object.
        """
        yield from self._fetch_used_in(tom_obj, criteria={"Object Type": "Calculation Item"})


@log
@contextmanager
def get_model_calc_dependencies(dataset: str, workspace: Optional[str] = None) -> Iterator[ModelCalcDependencies]:
    """
    Calculate all dependencies for all objects in a semantic model.

    Parameters
    ----------
    dataset : str
        Name of the semantic model.
    workspace : str, default=None
        The Fabric workspace name.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.

    Yields
    ------
    ModelCalcDependencies
        A wrapper of all calculated dependencies for all objects in the semantic model.
    """
    # Resolve workspace and retrieve dependency data
    workspace = fabric.resolve_workspace_name(workspace)
    dep = fabric.evaluate_dax(
        dataset=dataset,
        workspace=workspace,
        dax_string="""
        SELECT
            [TABLE] AS [Table Name],
            [OBJECT] AS [Object Name],
            [OBJECT_TYPE] AS [Object Type],
            [EXPRESSION] AS [Expression],
            [REFERENCED_TABLE] AS [Referenced Table],
            [REFERENCED_OBJECT] AS [Referenced Object],
            [REFERENCED_OBJECT_TYPE] AS [Referenced Object Type]
        FROM $SYSTEM.DISCOVER_CALC_DEPENDENCY
        """
    )

    # Format data columns
    dep["Object Type"] = dep["Object Type"].str.replace("_", " ").str.title()
    dep["Referenced Object Type"] = dep["Referenced Object Type"].str.replace("_", " ").str.title()
    dep["Full Object Name"] = _format_dax_object_name(dep["Table Name"], dep["Object Name"])
    dep["Referenced Full Object Name"] = _format_dax_object_name(dep["Referenced Table"], dep["Referenced Object"])
    dep["Parent Node"] = dep["Object Name"]

    # Initialize dependency DataFrame with 'Done' status
    df = dep.copy()
    objs = {"Measure", "Calc Column", "Calculation Item", "Calc Table"}
    df["Done"] = df["Referenced Object Type"].apply(lambda x: x not in objs).astype(bool)

    # Expand dependencies iteratively
    while not df["Done"].all():
        incomplete_rows = df[~df["Done"]]
        for _, row in incomplete_rows.iterrows():
            referenced_full_name = row["Referenced Full Object Name"]
            referenced_object_type = row["Referenced Object Type"]
            dep_filt = dep[(dep["Full Object Name"] == referenced_full_name) & (dep["Object Type"] == referenced_object_type)]

            # Expand dependencies and update 'Done' status as needed
            new_rows = []
            for _, dependency in dep_filt.iterrows():
                is_done = dependency["Referenced Object Type"] not in objs
                new_row = {
                    "Table Name": row["Table Name"],
                    "Object Name": row["Object Name"],
                    "Object Type": row["Object Type"],
                    "Referenced Table": dependency["Referenced Table"],
                    "Referenced Object": dependency["Referenced Object"],
                    "Referenced Object Type": dependency["Referenced Object Type"],
                    "Done": is_done,
                    "Full Object Name": row["Full Object Name"],
                    "Referenced Full Object Name": dependency["Referenced Full Object Name"],
                    "Parent Node": row["Referenced Object"],
                }
                new_rows.append(new_row)

            df = pd.concat([df, pd.DataFrame(new_rows)], ignore_index=True)
            df.loc[df.index == row.name, "Done"] = True

    # Finalize DataFrame and yield result
    df = df.drop(columns=["Done"])

    with connect_semantic_model(dataset, workspace=workspace) as tom:
        yield ModelCalcDependencies(df, tom)
