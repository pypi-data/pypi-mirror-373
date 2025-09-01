# flake8: noqa: E501
from __future__ import annotations
import itertools
import re
from typing import Any, Callable, Iterable, List, Optional, Union, cast

from sempy.fabric._bpa._types import Category, Field, Severity
from sempy.fabric._client._tom import TOMWrapper, ModelCalcDependencies
from sempy.fabric._client._utils import (
    _format_dax_object_name,
    _format_relationship_name
)


class BestPracticeRule:
    """
    A class to define a Best Practice Analyzer rule.

    Parameters
    ----------
    category : Category
        The category of the rule.
    fields : Field or list of Field
        The field(s) to which the rule applies.
    severity : Severity
        The severity of the rule.
    name : str
        The name of the rule.
    expression : Callable[[Any, TOMWrapper, ModelCalcDependencies], bool]
        A function that accepts a TOM object, a TOM wrapper and a model
        dependencies object as the input, and evaluates if the TOM object has
        any violation.
    description : str
        A description of the rule.
    href : str, default=None
        A URL pointing to a resource of more information about the rule.
    """
    def __init__(self,
                 category: Category,
                 fields: Union[Field, List[Field]],
                 severity: Severity,
                 name: str,
                 expression: Callable[[Any, TOMWrapper, ModelCalcDependencies], bool],
                 description: str,
                 href: Optional[str] = None):
        self._name = name
        self._display_name = name
        self._description = description
        self._display_description = description
        self._category = category
        self._display_category = category.value
        self._fields = fields if isinstance(fields, list) else [fields]
        self._severity = severity
        self._expression = expression
        self._href = href

    def __call__(self, obj: Any, tom: TOMWrapper, deps: ModelCalcDependencies) -> bool:
        return self._expression(obj, tom, deps)

    def set_display_name(self, display_name: str) -> None:
        self._display_name = display_name

    def set_display_description(self, display_description: str) -> None:
        self._display_description = display_description

    def set_display_category(self, display_category: str) -> None:
        self._display_category = display_category

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def category(self) -> Category:
        return self._category

    @property
    def fields(self) -> List[Field]:
        return self._fields

    @property
    def severity(self) -> Severity:
        return self._severity

    @property
    def href(self) -> Optional[str]:
        return self._href

    @property
    def display_name(self) -> str:
        return self._display_name

    @property
    def display_description(self) -> str:
        return self._display_description

    @property
    def display_category(self) -> str:
        return self._display_category

    @staticmethod
    def get_default_rules() -> List[BestPracticeRule]:
        """
        Shows the default rules for the semantic model BPA used by the BestPracticeAnalyzer.

        Returns
        -------
        list of BestPracticeRule
            A list containing the default rules for the BestPracticeAnalyzer.
        """
        from sempy.fabric._client._utils import _init_analysis_services
        _init_analysis_services()

        import Microsoft.AnalysisServices.Tabular as TOM  # type: ignore

        return [
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.COLUMN,
                Severity.WARNING,
                "Do not use floating point data types",
                lambda obj, tom, deps: obj.DataType == TOM.DataType.Double,
                'The "Double" floating point data type should be avoided, as it can result in unpredictable roundoff errors and decreased performance in certain scenarios. Use "Int64" or "Decimal" where appropriate (but note that "Decimal" is limited to 4 digits after the decimal sign).',
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.COLUMN,
                Severity.WARNING,
                "Avoid using calculated columns",
                lambda obj, tom, deps: obj.Type == TOM.ColumnType.Calculated,
                "Calculated columns do not compress as well as data columns so they take up more memory. They also slow down processing times for both the table as well as process recalc. Offload calculated column logic to your data warehouse and turn these calculated columns into data columns.",
                href="https://www.elegantbi.com/post/top10bestpractices",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.RELATIONSHIP,
                Severity.WARNING,
                "Check if bi-directional and many-to-many relationships are valid",
                lambda obj, tom, deps: (
                    obj.FromCardinality == TOM.RelationshipEndCardinality.Many
                    and obj.ToCardinality == TOM.RelationshipEndCardinality.Many
                )
                or str(obj.CrossFilteringBehavior) == "BothDirections",
                "Bi-directional and many-to-many relationships may cause performance degradation or even have unintended consequences. Make sure to check these specific relationships to ensure they are working as designed and are actually necessary.",
                href="https://www.sqlbi.com/articles/bidirectional-relationships-and-ambiguity-in-dax",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.ROW_LEVEL_SECURITY,
                Severity.INFO,
                "Check if dynamic row level security (RLS) is necessary",
                lambda obj, tom, deps: any(
                    re.search(pattern, obj.FilterExpression, flags=re.IGNORECASE)
                    for pattern in [r"USERPRINCIPALNAME\s*\(\)", r"USERNAME\s*\(\)"]
                ),
                "Usage of dynamic row level security (RLS) can add memory and performance overhead. Please research the pros/cons of using it.",
                href="https://docs.microsoft.com/power-bi/admin/service-admin-rls",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.TABLE,
                Severity.WARNING,
                "Avoid using many-to-many relationships on tables used for dynamic row level security",
                lambda obj, tom, deps: any(
                    r.FromCardinality == TOM.RelationshipEndCardinality.Many
                    and r.ToCardinality == TOM.RelationshipEndCardinality.Many
                    for r in tom.used_in_relationships(obj)
                )
                and any(t.Name == obj.Name for t in tom.all_rls),
                "Using many-to-many relationships on tables which use dynamic row level security can cause serious query performance degradation. This pattern's performance problems compound when snowflaking multiple many-to-many relationships against a table which contains row level security. Instead, use one of the patterns shown in the article below where a single dimension table relates many-to-one to a security table.",
                href="https://www.elegantbi.com/post/dynamicrlspatterns",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.RELATIONSHIP,
                Severity.WARNING,
                "Many-to-many relationships should be single-direction",
                lambda obj, tom, deps: (
                    obj.FromCardinality == TOM.RelationshipEndCardinality.Many
                    and obj.ToCardinality == TOM.RelationshipEndCardinality.Many
                )
                and obj.CrossFilteringBehavior
                == TOM.CrossFilteringBehavior.BothDirections,
                "Many-to-many relationships should be single-direction"
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.COLUMN,
                Severity.WARNING,
                "Set IsAvailableInMdx to false on non-attribute columns",
                lambda obj, tom, deps: not tom.is_direct_lake
                and obj.IsAvailableInMDX
                and (obj.IsHidden or obj.Parent.IsHidden)
                and obj.SortByColumn is None
                and not any(tom.used_in_sort_by(obj))
                and not any(tom.used_in_hierarchies(obj)),
                "To speed up processing time and conserve memory after processing, attribute hierarchies should not be built for columns that are never used for slicing by MDX clients. In other words, all hidden columns that are not used as a Sort By Column or referenced in user hierarchies should have their IsAvailableInMdx property set to false. The IsAvailableInMdx property is not relevant for Direct Lake models.",
                href="https://blog.crossjoin.co.uk/2018/07/02/isavailableinmdx-ssas-tabular",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.PARTITION,
                Severity.WARNING,
                "Set 'Data Coverage Definition' property on the DirectQuery partition of a hybrid table",
                lambda obj, tom, deps: tom.is_hybrid_table(table_name=obj.Parent.Name)
                and obj.Mode == TOM.ModeType.DirectQuery
                and obj.DataCoverageDefinition is None,
                "Setting the 'Data Coverage Definition' property may lead to better performance because the engine knows when it can only query the import-portion of the table and when it needs to query the DirectQuery portion of the table.",
                href="https://learn.microsoft.com/analysis-services/tom/table-partitions?view=asallproducts-allversions",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.MODEL,
                Severity.WARNING,
                "Dual mode is only relevant for dimension tables if DirectQuery is used for the corresponding fact table",
                lambda obj, tom, deps: not any(
                    p.Mode == TOM.ModeType.DirectQuery for p in tom.all_partitions
                )
                and any(p.Mode == TOM.ModeType.Dual for p in tom.all_partitions),
                "Only use Dual mode for dimension tables/partitions where a corresponding fact table is in DirectQuery. Using Dual mode in other circumstances (i.e. rest of the model is in Import mode) may lead to performance issues especially if the number of measures in the model is high.",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.TABLE,
                Severity.WARNING,
                "Set dimensions tables to dual mode instead of import when using DirectQuery on fact tables",
                lambda obj, tom, deps: sum(
                    1 for p in obj.Partitions if p.Mode == TOM.ModeType.Import
                )
                == 1
                and obj.Partitions.Count == 1
                and tom.has_hybrid_table
                and any(
                    r.ToCardinality == TOM.RelationshipEndCardinality.One
                    and r.ToTable.Name == obj.Name
                    for r in tom.used_in_relationships(obj)
                ),
                "When using DirectQuery, dimension tables should be set to Dual mode in order to improve query performance.",
                href="https://learn.microsoft.com/power-bi/transform-model/desktop-storage-mode#propagation-of-the-dual-setting",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.PARTITION,
                Severity.WARNING,
                "Minimize Power Query transformations",
                lambda obj, tom, deps: obj.SourceType == TOM.PartitionSourceType.M
                and any(
                    re.search(p, obj.Source.Expression)
                    for p in [
                        r'Table.Combine\s*\("',
                        r'Table.Join\s*\("',
                        r'Table.NestedJoin\s*\("',
                        r'Table.AddColumn\s*\("',
                        r'Table.Group\s*\("',
                        r'Table.Sort\s*\("',
                        r'Table.Pivot\s*\("',
                        r'Table.Unpivot\s*\("',
                        r'Table.UnpivotOtherColumns\s*\("',
                        r'Table.Distinct\s*\("',
                        r'\[Query=\("SELECT',
                        r"Value.NativeQuery",
                        r"OleDb.Query",
                        r"Odbc.Query",
                    ]
                ),
                "Minimize Power Query transformations in order to improve model processing performance. It is a best practice to offload these transformations to the data warehouse if possible. Also, please check whether query folding is occurring within your model. Please reference the article below for more information on query folding.",
                href="https://docs.microsoft.com/power-query/power-query-folding",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.TABLE,
                Severity.WARNING,
                "Consider a star-schema instead of a snowflake architecture",
                lambda obj, tom, deps: obj.CalculationGroup is None
                and (
                    any(
                        r.FromTable.Name == obj.Name
                        for r in tom.used_in_relationships(obj)
                    )
                    and any(
                        r.ToTable.Name == obj.Name
                        for r in tom.used_in_relationships(obj)
                    )
                ),
                "Generally speaking, a star-schema is the optimal architecture for tabular models. That being the case, there are valid cases to use a snowflake approach. Please check your model and consider moving to a star-schema architecture.",
                href="https://docs.microsoft.com/power-bi/guidance/star-schema",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.MODEL,
                Severity.WARNING,
                "Avoid using views when using Direct Lake mode",
                lambda obj, tom, deps: tom.is_direct_lake_using_view,
                "In Direct Lake mode, views will always fall back to DirectQuery. Thus, in order to obtain the best performance use lakehouse tables instead of views.",
                href="https://learn.microsoft.com/fabric/get-started/direct-lake-overview#fallback",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "Avoid adding 0 to a measure",
                lambda obj, tom, deps: tom.get_dax_expression(obj).replace(" ", "").startswith("0+")
                or tom.get_dax_expression(obj).replace(" ", "").endswith("+0")
                or bool(re.search(
                    r"DIVIDE\s*\(\s*[^,]+,\s*[^,]+,\s*0\s*\)",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                ))
                or bool(re.search(
                    r"IFERROR\s*\(\s*[^,]+,\s*0\s*\)",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                )),
                "Adding 0 to a measure in order for it not to show a blank value may negatively impact performance.",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.TABLE,
                Severity.WARNING,
                "Reduce usage of calculated tables",
                lambda obj, tom, deps: not tom.is_field_parameter(table_name=obj.Name)
                and tom.is_calculated_table(table_name=obj.Name),
                "Migrate calculated table logic to your data warehouse. Reliance on calculated tables will lead to technical debt and potential misalignments if you have multiple models on your platform.",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.COLUMN,
                Severity.WARNING,
                "Reduce usage of calculated columns that use the RELATED function",
                lambda obj, tom, deps: obj.Type == TOM.ColumnType.Calculated
                and bool(re.search(r"related\s*\(", tom.get_dax_expression(obj), flags=re.IGNORECASE)),
                "Calculated columns do not compress as well as data columns and may cause longer processing times. As such, calculated columns should be avoided if possible. One scenario where they may be easier to avoid is if they use the RELATED function.",
                href="https://www.sqlbi.com/articles/storage-differences-between-calculated-columns-and-calculated-tables",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.MODEL,
                Severity.WARNING,
                "Avoid excessive bi-directional or many-to-many relationships",
                lambda obj, tom, deps: (
                    (
                        sum(
                            1
                            for r in obj.Relationships
                            if r.CrossFilteringBehavior
                            == TOM.CrossFilteringBehavior.BothDirections
                        )
                        + sum(
                            1
                            for r in obj.Relationships
                            if (
                                r.FromCardinality == TOM.RelationshipEndCardinality.Many
                            )
                            and (r.ToCardinality == TOM.RelationshipEndCardinality.Many)
                        )
                    )
                    / max(int(obj.Relationships.Count), 1)
                )
                > 0.3,
                "Limit use of b-di and many-to-many relationships. This rule flags the model if more than 30% of relationships are bi-di or many-to-many.",
                href="https://www.sqlbi.com/articles/bidirectional-relationships-and-ambiguity-in-dax",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.TABLE,
                Severity.WARNING,
                "Remove auto-date table",
                lambda obj, tom, deps: tom.is_calculated_table(table_name=obj.Name)
                and (
                    obj.Name.startswith("DateTableTemplate_")
                    or obj.Name.startswith("LocalDateTable_")
                ),
                "Avoid using auto-date tables. Make sure to turn off auto-date table in the settings in Power BI Desktop. This will save memory resources.",
                href="https://www.youtube.com/watch?v=xu3uDEHtCrg",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.TABLE,
                Severity.WARNING,
                "Date/calendar tables should be marked as a date table",
                lambda obj, tom, deps: (
                    bool(re.search(r"date", obj.Name, flags=re.IGNORECASE))
                    or bool(re.search(r"calendar", obj.Name, flags=re.IGNORECASE))
                )
                and str(obj.DataCategory) != "Time",
                "This rule looks for tables that contain the words 'date' or 'calendar' as they should likely be marked as a date table.",
                href="https://docs.microsoft.com/power-bi/transform-model/desktop-date-tables",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.TABLE,
                Severity.WARNING,
                "Large tables should be partitioned",
                lambda obj, tom, deps: not tom.is_direct_lake
                and int(obj.Partitions.Count) == 1
                and tom.get_row_count(obj) > 25000000,
                "Large tables should be partitioned in order to optimize processing. This is not relevant for semantic models in Direct Lake mode as they can only have one partition per table.",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.ROW_LEVEL_SECURITY,
                Severity.WARNING,
                "Limit row level security (RLS) logic",
                lambda obj, tom, deps: any(
                    re.search(p, obj.FilterExpression, flags=re.IGNORECASE)
                    for p in [
                        r"right\s*\(",
                        r"left\s*\(",
                        r"filter\s*\(",
                        r"upper\s*\(",
                        r"lower\s*\(",
                        r"find\s*\(",
                    ]
                ),
                "Try to simplify the DAX used for row level security. Usage of the functions within this rule can likely be offloaded to the upstream systems (data warehouse).",
            ),
            BestPracticeRule(
                Category.PERFORMANCE,
                Field.MODEL,
                Severity.WARNING,
                "Model should have a date table",
                lambda obj, tom, deps: not any(
                    (c.IsKey and c.DataType == TOM.DataType.DateTime)
                    and str(t.DataCategory) == "Time"
                    for t in obj.Tables
                    for c in t.Columns
                ),
                "Generally speaking, models should generally have a date table. Models that do not have a date table generally are not taking advantage of features such as time intelligence or may not have a properly structured architecture.",
            ),
            BestPracticeRule(
                Category.ERROR_PREVENTION,
                Field.CALCULATION_ITEM,
                Severity.ERROR,
                "Calculation items must have an expression",
                lambda obj, tom, deps: len(tom.get_dax_expression(obj)) == 0,
                "Calculation items must have an expression. Without an expression, they will not show any values.",
            ),
            BestPracticeRule(
                Category.ERROR_PREVENTION,
                Field.RELATIONSHIP,
                Severity.WARNING,
                "Relationship columns should be of the same data type",
                lambda obj, tom, deps: obj.FromColumn.DataType != obj.ToColumn.DataType,
                "Columns used in a relationship should be of the same data type. Ideally, they will be of integer data type (see the related rule '[Formatting] Relationship columns should be of integer data type'). Having columns within a relationship which are of different data types may lead to various issues.",
            ),
            BestPracticeRule(
                Category.ERROR_PREVENTION,
                Field.COLUMN,
                Severity.ERROR,
                "Data columns must have a source column",
                lambda obj, tom, deps: obj.Type == TOM.ColumnType.Data
                and len(obj.SourceColumn) == 0,
                "Data columns must have a source column. A data column without a source column will cause an error when processing the model.",
            ),
            BestPracticeRule(
                Category.ERROR_PREVENTION,
                Field.COLUMN,
                Severity.WARNING,
                "Set IsAvailableInMdx to true on necessary columns",
                lambda obj, tom, deps: not tom.is_direct_lake
                and not obj.IsAvailableInMDX
                and (
                    any(tom.used_in_sort_by(obj))
                    or any(tom.used_in_hierarchies(obj))
                    or obj.SortByColumn is not None
                ),
                "In order to avoid errors, ensure that attribute hierarchies are enabled if a column is used for sorting another column, used in a hierarchy, used in variations, or is sorted by another column. The IsAvailableInMdx property is not relevant for Direct Lake models.",
            ),
            BestPracticeRule(
                Category.ERROR_PREVENTION,
                Field.TABLE,
                Severity.ERROR,
                "Avoid the USERELATIONSHIP function and RLS against the same table",
                lambda obj, tom, deps: any(
                    re.search(
                        r"USERELATIONSHIP\s*\(\s*.+?(?=])\]\s*,\s*'*"
                        + re.escape(obj.Name)
                        + r"'*\[",
                        m.Expression,
                        flags=re.IGNORECASE,
                    )
                    for m in tom.all_measures
                )
                and any(r.Table.Name == obj.Name for r in tom.all_rls),
                "The USERELATIONSHIP function may not be used against a table which also leverages row-level security (RLS). This will generate an error when using the particular measure in a visual. This rule will highlight the table which is used in a measure's USERELATIONSHIP function as well as RLS.",
                href="https://blog.crossjoin.co.uk/2013/05/10/userelationship-and-tabular-row-security",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "Avoid using the IFERROR function",
                lambda obj, tom, deps: bool(re.search(
                    r"iferror\s*\(", tom.get_dax_expression(obj), flags=re.IGNORECASE
                )),
                "Avoid using the IFERROR function as it may cause performance degradation. If you are concerned about a divide-by-zero error, use the DIVIDE function as it naturally resolves such errors as blank (or you can customize what should be shown in case of such an error).",
                href="https://www.elegantbi.com/post/top10bestpractices",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "Use the TREATAS function instead of INTERSECT for virtual relationships",
                lambda obj, tom, deps: bool(re.search(
                    r"intersect\s*\(", tom.get_dax_expression(obj), flags=re.IGNORECASE
                )),
                "The TREATAS function is more efficient and provides better performance than the INTERSECT function when used in virutal relationships.",
                href="https://www.sqlbi.com/articles/propagate-filters-using-treatas-in-dax",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "The EVALUATEANDLOG function should not be used in production models",
                lambda obj, tom, deps: bool(re.search(
                    r"evaluateandlog\s*\(", tom.get_dax_expression(obj), flags=re.IGNORECASE
                )),
                "The EVALUATEANDLOG function is meant to be used only in development/test environments and should not be used in production models.",
                href="https://pbidax.wordpress.com/2022/08/16/introduce-the-dax-evaluateandlog-function",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                Field.MEASURE,
                Severity.WARNING,
                "Measures should not be direct references of other measures",
                lambda obj, tom, deps: any(
                    re.search(
                        r"^\s*('"
                        + re.escape(m.Parent.Name)
                        + r"|"
                        + f"'{re.escape(m.Parent.Name)}'"
                        + r")?\s*"
                        + re.escape(f"[{m.Name}]")
                        + r"\s*$",
                        tom.get_dax_expression(obj)
                    ) for m in tom.all_measures
                ),
                "This rule identifies measures which are simply a reference to another measure. As an example, consider a model with two measures: [MeasureA] and [MeasureB]. This rule would be triggered for MeasureB if MeasureB's DAX was MeasureB:=[MeasureA]. Such duplicative measures should be removed.",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                Field.MEASURE,
                Severity.WARNING,
                "No two measures should have the same definition",
                lambda obj, tom, deps: any(
                    re.sub(r"\s+", "", tom.get_dax_expression(obj))
                    == re.sub(r"\s+", "", m.Expression)
                    and obj.Name != m.Name
                    for m in tom.all_measures
                ),
                "Two measures with different names and defined by the same DAX expression should be avoided to reduce redundancy.",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "Avoid addition or subtraction of constant values to results of divisions",
                lambda obj, tom, deps: bool(re.search(
                    r"DIVIDE\s*\((\s*.*?)\)\s*[+-]\s*1|\/\s*.*(?=[-+]\s*1)",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                )),
                "Adding a constant value may lead to performance degradation.",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "Avoid using '1-(x/y)' syntax",
                lambda obj, tom, deps: bool(re.search(
                    r"[0-9]+\s*[-+]\s*[\(]*\s*SUM\s*\(\s*\'*[A-Za-z0-9 _]+\'*\s*\[[A-Za-z0-9 _]+\]\s*\)\s*/",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                ))
                or bool(re.search(
                    r"[0-9]+\s*[-+]\s*DIVIDE\s*\(",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                )),
                "Instead of using the '1-(x/y)' or '1+(x/y)' syntax to achieve a percentage calculation, use the basic DAX functions (as shown below). Using the improved syntax will generally improve the performance. The '1+/-...' syntax always returns a value whereas the solution without the '1+/-...' does not (as the value may be 'blank'). Therefore the '1+/-...' syntax may return more rows/columns which may result in a slower query speed.    Let's clarify with an example:    Avoid this: 1 - SUM ( 'Sales'[CostAmount] ) / SUM( 'Sales'[SalesAmount] )  Better: DIVIDE ( SUM ( 'Sales'[SalesAmount] ) - SUM ( 'Sales'[CostAmount] ), SUM ( 'Sales'[SalesAmount] ) )  Best: VAR x = SUM ( 'Sales'[SalesAmount] ) RETURN DIVIDE ( x - SUM ( 'Sales'[CostAmount] ), x )",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "Filter measure values by columns, not tables",
                lambda obj, tom, deps: bool(re.search(
                    r"CALCULATE\s*\(\s*[^,]+,\s*FILTER\s*\(\s*\'*[A-Za-z0-9 _]+\'*\s*,\s*\[[^\]]+\]",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                ))
                or bool(re.search(
                    r"CALCULATETABLE\s*\(\s*[^,]*,\s*FILTER\s*\(\s*\'*[A-Za-z0-9 _]+\'*\s*,\s*\[",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                )),
                "Instead of using this pattern FILTER('Table',[Measure]>Value) for the filter parameters of a CALCULATE or CALCULATETABLE function, use one of the options below (if possible). Filtering on a specific column will produce a smaller table for the engine to process, thereby enabling faster performance. Using the VALUES function or the ALL function depends on the desired measure result.\nOption 1: FILTER(VALUES('Table'[Column]),[Measure] > Value)\nOption 2: FILTER(ALL('Table'[Column]),[Measure] > Value)",
                href="https://docs.microsoft.com/power-bi/guidance/dax-avoid-avoid-filter-as-filter-argument",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "Filter column values with proper syntax",
                lambda obj, tom, deps: bool(re.search(
                    r"CALCULATE\s*\(\s*[^,]+,\s*FILTER\s*\(\s*'*[A-Za-z0-9 _]+'*\s*,\s*'*[A-Za-z0-9 _]+'*\[[A-Za-z0-9 _]+\]",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                ))
                or bool(re.search(
                    r"CALCULATETABLE\s*\([^,]*,\s*FILTER\s*\(\s*'*[A-Za-z0-9 _]+'*\s*,\s*'*[A-Za-z0-9 _]+'*\[[A-Za-z0-9 _]+\]",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE,
                )),
                "Instead of using this pattern FILTER('Table','Table'[Column]=\"Value\") for the filter parameters of a CALCULATE or CALCULATETABLE function, use one of the options below. As far as whether to use the KEEPFILTERS function, see the second reference link below.\nOption 1: KEEPFILTERS('Table'[Column]=\"Value\")\nOption 2: 'Table'[Column]=\"Value\"",
                href="https://docs.microsoft.com/power-bi/guidance/dax-avoid-avoid-filter-as-filter-argument  Reference: https://www.sqlbi.com/articles/using-keepfilters-in-dax",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.WARNING,
                "Use the DIVIDE function for division",
                lambda obj, tom, deps: bool(re.search(
                    r"\]\s*\/(?!\/)(?!\*)|\)\s*\/(?!\/)(?!\*)",
                    tom.get_dax_expression(obj),
                    flags=re.IGNORECASE
                )),
                'Use the DIVIDE  function instead of using "/". The DIVIDE function resolves divide-by-zero cases. As such, it is recommended to use to avoid errors.',
                href="https://docs.microsoft.com/power-bi/guidance/dax-divide-function-operator",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.ERROR,
                "Column references should be fully qualified",
                lambda obj, tom, deps: any(
                    deps.all_unqualified_column_dependencies(obj)
                ),
                "Using fully qualified column references makes it easier to distinguish between column and measure references, and also helps avoid certain errors. When referencing a column in DAX, first specify the table name, then specify the column name in square brackets.",
                href="https://www.elegantbi.com/post/top10bestpractices",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                [
                    Field.MEASURE,
                    Field.CALCULATED_COLUMN,
                    Field.CALCULATED_TABLE,
                    Field.CALCULATION_ITEM
                ],
                Severity.ERROR,
                "Measure references should be unqualified",
                lambda obj, tom, deps: any(
                    deps.all_fully_qualified_measure_dependencies(obj)
                ),
                "Using unqualified measure references makes it easier to distinguish between column and measure references, and also helps avoid certain errors. When referencing a measure using DAX, do not specify the table name. Use only the measure name in square brackets.",
                href="https://www.elegantbi.com/post/top10bestpractices",
            ),
            BestPracticeRule(
                Category.DAX_EXPRESSIONS,
                Field.RELATIONSHIP,
                Severity.WARNING,
                "Inactive relationships that are never activated",
                lambda obj, tom, deps: not obj.IsActive
                and not any(
                    re.search(
                        r"USERELATIONSHIP\s*\(\s*\'*"
                        + re.escape(obj.FromTable.Name)
                        + r"'*\["
                        + re.escape(obj.FromColumn.Name)
                        + r"\]\s*,\s*'*"
                        + re.escape(obj.ToTable.Name)
                        + r"'*\["
                        + re.escape(obj.ToColumn.Name)
                        + r"\]",
                        m.Expression,
                        flags=re.IGNORECASE,
                    )
                    for m in tom.all_measures
                ),
                "Inactive relationships are activated using the USERELATIONSHIP function. If an inactive relationship is not referenced in any measure via this function, the relationship will not be used. It should be determined whether the relationship is not necessary or to activate the relationship via this method.",
                href="https://dax.guide/userelationship",
            ),
            BestPracticeRule(
                Category.MAINTENANCE,
                Field.COLUMN,
                Severity.WARNING,
                "Remove unnecessary columns",
                lambda obj, tom, deps: (obj.IsHidden or obj.Parent.IsHidden)
                and not any(tom.used_in_relationships(obj))
                and not any(tom.used_in_hierarchies(obj))
                and not any(tom.used_in_sort_by(obj))
                and any(
                    itertools.chain(
                        deps.all_measure_references(obj),
                        deps.all_column_references(obj),
                        deps.all_table_references(obj)
                    )
                ),
                "Hidden columns that are not referenced by any DAX expressions, relationships, hierarchy levels or Sort By-properties should be removed.",
            ),
            BestPracticeRule(
                Category.MAINTENANCE,
                Field.MEASURE,
                Severity.WARNING,
                "Remove unnecessary measures",
                lambda obj, tom, deps: obj.IsHidden
                and not any(
                    itertools.chain(
                        deps.all_measure_references(obj),
                        deps.all_column_references(obj),
                        deps.all_table_references(obj)
                    )
                ),
                "Hidden measures that are not referenced by any DAX expressions should be removed for maintainability.",
            ),
            BestPracticeRule(
                Category.MAINTENANCE,
                Field.TABLE,
                Severity.WARNING,
                "Ensure tables have relationships",
                lambda obj, tom, deps: not any(tom.used_in_relationships(obj))
                and obj.CalculationGroup is None,
                "This rule highlights tables which are not connected to any other table in the model with a relationship.",
            ),
            BestPracticeRule(
                Category.MAINTENANCE,
                Field.TABLE,
                Severity.WARNING,
                "Calculation groups with no calculation items",
                lambda obj, tom, deps: obj.CalculationGroup is not None
                and not any(obj.CalculationGroup.CalculationItems),
                "Calculation groups have no function unless they have calculation items.",
            ),
            BestPracticeRule(
                Category.MAINTENANCE,
                [Field.COLUMN, Field.MEASURE, Field.TABLE],
                Severity.INFO,
                "Visible objects with no description",
                lambda obj, tom, deps: not obj.IsHidden and len(obj.Description) == 0,
                "Add descriptions to objects. These descriptions are shown on hover within the Field List in Power BI Desktop. Additionally, you can leverage these descriptions to create an automated data dictionary.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.COLUMN,
                Severity.WARNING,
                "Provide format string for 'Date' columns",
                lambda obj, tom, deps: bool(re.search(r"date", obj.Name, flags=re.IGNORECASE))
                and (obj.DataType == TOM.DataType.DateTime)
                and (obj.FormatString.lower() not in ['mm/dd/yyyy', 'mm-dd-yyyy', 'dd/mm/yyyy', 'dd-mm-yyyy', 'yyyy-mm-dd', 'yyyy/mm/dd']),
                'Columns of type "DateTime" that have "Date" in their names should be formatted.',
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.COLUMN,
                Severity.WARNING,
                "Do not summarize numeric columns",
                lambda obj, tom, deps: (
                    (obj.DataType == TOM.DataType.Int64)
                    or (obj.DataType == TOM.DataType.Decimal)
                    or (obj.DataType == TOM.DataType.Double)
                )
                and (str(obj.SummarizeBy) != "None")
                and not ((obj.IsHidden) or (obj.Parent.IsHidden)),
                'Numeric columns (integer, decimal, double) should have their SummarizeBy property set to "None" to avoid accidental summation in Power BI (create measures instead).',
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.MEASURE,
                Severity.INFO,
                "Provide format string for measures",
                lambda obj, tom, deps: not obj.IsHidden and len(obj.FormatString) == 0,
                "Visible measures should have their format string property assigned.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.COLUMN,
                Severity.INFO,
                "Add data category for columns",
                lambda obj, tom, deps: len(obj.DataCategory) == 0
                and any(
                    obj.Name.lower().startswith(item.lower())
                    for item in [
                        "country",
                        "city",
                        "continent",
                        "latitude",
                        "longitude",
                    ]
                ),
                "Add Data Category property for appropriate columns.",
                href="https://docs.microsoft.com/power-bi/transform-model/desktop-data-categorization",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.MEASURE,
                Severity.WARNING,
                "Percentages should be formatted with thousands separators and 1 decimal",
                lambda obj, tom, deps: "%" in obj.FormatString
                and obj.FormatString != "#,0.0%;-#,0.0%;#,0.0%",
                "For a better user experience, percengage measures should be formatted with a '%' sign.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.MEASURE,
                Severity.WARNING,
                "Whole numbers should be formatted with thousands separators and no decimals",
                lambda obj, tom, deps: "$" not in obj.FormatString
                and "%" not in obj.FormatString
                and obj.FormatString not in ["#,0", "#,0.0"],
                "For a better user experience, whole numbers should be formatted with commas.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.COLUMN,
                Severity.INFO,
                "Hide foreign keys",
                lambda obj, tom, deps: not obj.IsHidden
                and any(
                    r.FromColumn.Name == obj.Name
                    and r.FromCardinality == TOM.RelationshipEndCardinality.Many
                    for r in tom.used_in_relationships(obj)
                ),
                "Foreign keys should always be hidden as they should not be used by end users.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.COLUMN,
                Severity.INFO,
                "Mark primary keys",
                lambda obj, tom, deps: any(
                    r.ToTable.Name == obj.Table.Name
                    and r.ToColumn.Name == obj.Name
                    and r.ToCardinality == TOM.RelationshipEndCardinality.One
                    for r in tom.used_in_relationships(obj)
                )
                and not obj.IsKey
                and obj.Table.DataCategory != "Time",
                "Set the 'Key' property to 'True' for primary key columns within the column properties.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.COLUMN,
                Severity.INFO,
                "Month (as a string) must be sorted",
                lambda obj, tom, deps: bool(re.search(r"month", obj.Name, flags=re.IGNORECASE))
                and not bool(re.search(r"months", obj.Name, flags=re.IGNORECASE))
                and (obj.DataType == TOM.DataType.String)
                and len(str(obj.SortByColumn)) == 0,
                "This rule highlights month columns which are strings and are not sorted. If left unsorted, they will sort alphabetically (i.e. April, August...). Make sure to sort such columns so that they sort properly (January, February, March...).",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.RELATIONSHIP,
                Severity.WARNING,
                "Relationship columns should be of integer data type",
                lambda obj, tom, deps: obj.FromColumn.DataType != TOM.DataType.Int64
                or obj.ToColumn.DataType != TOM.DataType.Int64,
                "It is a best practice for relationship columns to be of integer data type. This applies not only to data warehousing but data modeling as well.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.COLUMN,
                Severity.WARNING,
                "Provide format string for 'Month' columns",
                lambda obj, tom, deps: bool(re.search(r"month", obj.Name, flags=re.IGNORECASE))
                and obj.DataType == TOM.DataType.DateTime
                and obj.FormatString != "MMMM yyyy",
                'Columns of type "DateTime" that have "Month" in their names should be formatted as "MMMM yyyy".',
            ),
            BestPracticeRule(
                Category.FORMATTING,
                Field.COLUMN,
                Severity.INFO,
                "Format flag columns as Yes/No value strings",
                lambda obj, tom, deps: obj.Name.lower().startswith("is")
                and obj.DataType == TOM.DataType.Int64
                and not (obj.IsHidden or obj.Parent.IsHidden)
                or obj.Name.lower().endswith(" flag")
                and obj.DataType != TOM.DataType.String
                and not (obj.IsHidden or obj.Parent.IsHidden),
                "Flags must be properly formatted as Yes/No as this is easier to read than using 0/1 integer values.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                [Field.TABLE, Field.COLUMN, Field.MEASURE, Field.PARTITION, Field.HIERARCHY],
                Severity.ERROR,
                "Objects should not start or end with a space",
                lambda obj, tom, deps: obj.Name[0] == " " or obj.Name[-1] == " ",
                "Objects should not start or end with a space. This usually happens by accident and is difficult to find.",
            ),
            BestPracticeRule(
                Category.FORMATTING,
                [Field.TABLE, Field.COLUMN, Field.MEASURE, Field.PARTITION, Field.HIERARCHY],
                Severity.INFO,
                "First letter of objects must be capitalized",
                lambda obj, tom, deps: obj.Name[0] != obj.Name[0].upper(),
                "The first letter of object names should be capitalized to maintain professional quality.",
            ),
            BestPracticeRule(
                Category.NAMING_CONVENTIONS,
                [Field.TABLE, Field.COLUMN, Field.MEASURE, Field.PARTITION, Field.HIERARCHY],
                Severity.WARNING,
                "Object names must not contain special characters",
                lambda obj, tom, deps: bool(re.search(r"[\t\r\n]", obj.Name)),
                "Object names should not include tabs, line breaks, etc.",
            ),
        ]

    @staticmethod
    def translate_rules(rules: List[BestPracticeRule], language: str) -> List[BestPracticeRule]:
        """
        Translates the rules to the specified language.

        Parameters
        ----------
        rules : list of BestPracticeRule
            The list of rules to translate.
        language : str, default=None
            Specifying a language name or code (i.e. 'it' for Italian) will
            auto-translate the Category, Rule Name and Description into the
            specified language. Please refer to
            `supported languages <https://api.cognitive.microsofttranslator.com/languages?api-version=3.0>`__
            for all supported languages and codes.

        Returns
        -------
        list of BestPracticeRule
            The translated list of rules.
        """
        from sempy.fabric._client._translations import _get_language_codes
        from sempy.fabric._client._cognitiveservice_rest_api import _CognitiveServiceAsyncRestAPI

        language = _get_language_codes(language)[0]

        texts: List[str] = []
        for rule in rules:
            texts.append(rule.name)
            texts.append(rule.description)
            texts.append(rule.category.value)

        df_translated = _CognitiveServiceAsyncRestAPI().translate_text(
            texts=texts, to_lang=[language]
        )

        for i, rule in enumerate(rules):
            rule.set_display_name(df_translated.iloc[i * 3][language])
            rule.set_display_description(df_translated.iloc[i * 3 + 1][language])
            rule.set_display_category(df_translated.iloc[i * 3 + 2][language])

        return rules

class BestPracticeRuleGroup:
    """
    A class to manage a group of Best Practice Analyzer rules.

    Parameters
    ----------
    field : Field
        The field to which the rules apply.
    retriever : Callable[[TOMWrapper], Iterable[Any]]
        A function that retrieves the TOM objects to which the rules apply.
    formatter : Callable[[Any], str]
        A function that formats the TOM object to a string.
    """
    def __init__(self, field: Field,
                 retriever: Callable[[TOMWrapper], Iterable[Any]],
                 formatter: Callable[[Any], str]):
        self._field = field
        self._retriever = retriever
        self._formatter = formatter
        self._rules: List[BestPracticeRule] = []

    def add_rule(self, rule: BestPracticeRule):
        self._rules.append(rule)

    def clear_rules(self):
        self._rules.clear()

    def retrieve(self, tom: TOMWrapper) -> Iterable[Any]:
        return self._retriever(tom)

    def format(self, tom_obj: Any) -> str:
        return self._formatter(tom_obj)

    @property
    def size(self) -> int:
        return len(self._rules)

    @property
    def field(self) -> Field:
        return self._field

    @property
    def rules(self) -> Iterable[BestPracticeRule]:
        yield from self._rules

    @staticmethod
    def get_default_rule_groups() -> List[BestPracticeRuleGroup]:
        """
        Returns a list of BestPracticeRuleGroup for the semantic model BPA used by the BestPracticeAnalyzer.

        Returns
        -------
        list of BestPracticeRuleGroup
            A list of BestPracticeRuleGroup objects
        """
        return [
            BestPracticeRuleGroup(
                Field.RELATIONSHIP,
                lambda tom: tom.model.Relationships,
                lambda obj: cast(str, _format_relationship_name(
                    obj.FromTable.Name,
                    obj.FromColumn.Name,
                    obj.ToTable.Name,
                    obj.ToColumn.Name,
                ))
            ),
            BestPracticeRuleGroup(
                Field.COLUMN,
                lambda tom: tom.all_columns,
                lambda obj: cast(str, _format_dax_object_name(obj.Parent.Name, obj.Name))
            ),
            BestPracticeRuleGroup(
                Field.MEASURE,
                lambda tom: tom.all_measures,
                lambda obj: obj.Name
            ),
            BestPracticeRuleGroup(
                Field.HIERARCHY,
                lambda tom: tom.all_hierarchies,
                lambda obj: cast(str, _format_dax_object_name(obj.Parent.Name, obj.Name))
            ),
            BestPracticeRuleGroup(
                Field.TABLE,
                lambda tom: tom.model.Tables,
                lambda obj: obj.Name
            ),
            BestPracticeRuleGroup(
                Field.ROLE,
                lambda tom: tom.model.Roles,
                lambda obj: obj.Name
            ),
            BestPracticeRuleGroup(
                Field.MODEL,
                lambda tom: [tom.model],
                lambda obj: obj.Model.Name
            ),
            BestPracticeRuleGroup(
                Field.CALCULATION_ITEM,
                lambda tom: tom.all_calculation_items,
                lambda obj: cast(str, _format_dax_object_name(obj.Parent.Table.Name, obj.Name))
            ),
            BestPracticeRuleGroup(
                Field.CALCULATED_COLUMN,
                lambda tom: tom.all_calculated_columns,
                lambda obj: cast(str, _format_dax_object_name(obj.Parent.Name, obj.Name))
            ),
            BestPracticeRuleGroup(
                Field.CALCULATED_TABLE,
                lambda tom: tom.all_calculated_tables,
                lambda obj: obj.Name
            ),
            BestPracticeRuleGroup(
                Field.ROW_LEVEL_SECURITY,
                lambda tom: tom.all_rls,
                lambda obj: cast(str, _format_dax_object_name(obj.Parent.Name, obj.Name))
            ),
            BestPracticeRuleGroup(
                Field.PARTITION,
                lambda tom: tom.all_partitions,
                lambda obj: cast(str, _format_dax_object_name(obj.Parent.Name, obj.Name))
            )
        ]
