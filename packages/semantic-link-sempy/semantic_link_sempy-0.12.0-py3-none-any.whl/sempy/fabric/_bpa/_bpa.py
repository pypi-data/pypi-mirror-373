from functools import reduce
from typing import TYPE_CHECKING, Any, cast, Dict, List, Literal, Optional, Union
from uuid import UUID

import pandas as pd
from IPython.display import display, HTML

import sempy._utils._icons as icons
from sempy.fabric._bpa._rules import (
    BestPracticeRule,
    BestPracticeRuleGroup,
)
from sempy.fabric._bpa._types import Field
from sempy.fabric._client._tom._dependencies import (
    get_model_calc_dependencies,
    ModelCalcDependencies,
    TOMWrapper
)
from sempy.fabric._client._tom import connect_semantic_model
from sempy.fabric._credentials import with_credential
from sempy._utils._log import log

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class BestPracticeRecord:
    """
    A class to represent a Best Practice Analyzer record i.e. TOM object that
    violates the rule.

    Parameters
    ----------
    obj : Any
        The TOM object that violates the rule.
    rule : BestPracticeRule
        The rule that is violated.
    group : BestPracticeRuleGroup
        The group of rules that the rule belongs to.
    """
    def __init__(self, obj: Any, rule: BestPracticeRule,
                 group: BestPracticeRuleGroup):
        self._obj = obj
        self._rule = rule
        self._group = group

    def to_dict(self) -> Dict[str, Optional[str]]:
        """
        Convert the record to a dictionary that can be used to create a
        pandas.DataFrame.

        Returns
        -------
        Dict[str, Optional[str]]
            A dictionary containing the record information.
        """
        return {
            "Category": self._rule.display_category,
            "Rule Name": self._rule.display_name,
            "Severity": self._rule.severity.value,
            "Object Type": self._group.field.value,
            "Object Name": self._group.format(self._obj),
            "Description": self._rule.display_description,
            "URL": self._rule.href
        }


class BestPracticeAnalyzer:
    """
    A class to analyze a semantic model using the VertiPaq Analyzer.

    Parameters
    ----------
    dataset : str or uuid.UUID, default=None
        Name or ID of the semantic model.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    """

    def __init__(self, use_default_rules=True) -> None:
        self._rules: List[BestPracticeRule] = []
        self._groups: Dict[Field, BestPracticeRuleGroup] = dict()

        for group in BestPracticeRuleGroup.get_default_rule_groups():
            self._groups[group.field] = group

        if use_default_rules:
            for rule in BestPracticeRule.get_default_rules():
                self.register_rule(rule)

    def register_rule(self, rule: BestPracticeRule):
        for field in rule.fields:
            if field not in self._groups:
                raise ValueError(f"Invalid field '{field.value}' for rule '{rule.name}'.")
            self._groups[field].add_rule(rule)
        self._rules.append(rule)

    def analyze(self, tom: TOMWrapper, deps: ModelCalcDependencies,
                language: Optional[str] = None) -> pd.DataFrame:
        rule_records: Dict[BestPracticeRule, List[BestPracticeRecord]] = dict()

        # tranlsate rule name, description, and category
        if language is not None:
            self._rules = BestPracticeRule.translate_rules(self._rules, language=language)

        # analyze with rule groups to avoid redundant traversals
        for group in self._groups.values():
            if group.size == 0:
                continue
            for obj in group.retrieve(tom):
                for rule in group.rules:
                    if not rule(obj, tom, deps):
                        continue
                    rule_records.setdefault(rule, []) \
                        .append(BestPracticeRecord(obj, rule, group))

        # return the result with the original rule order
        return pd.DataFrame(reduce(
            lambda records, rule: records + [
                r.to_dict() for r in rule_records.get(rule, [])
            ],
            self._rules,
            cast(List[Dict[str, Optional[str]]], []),
        ))


@log
@with_credential
def run_model_bpa(
    dataset: Union[str, UUID],
    workspace: Optional[Union[str, UUID]] = None,
    export: Literal["html", "table", "zip", "none"] = "html",
    return_dataframe: bool = False,
    language: Optional[str] = None,
    credential: Optional["TokenCredential"] = None
) -> Optional[pd.DataFrame]:
    """
    Run Best Practice Analyzer scan for a semantic model, and display an HTML visualization, or return a pandas dataframe.

    ⚠️ This function leverages the `Tabular Object Model (TOM) <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.server?view=analysisservices-dotnet>`_
    to interact with the target semantic model. You must have at least **ReadWrite** permissions on the model to use this function.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or ID of the semantic model.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    export : {"html", "table", "zip", "none"}, default="html"
        The export format for the analysis data.
        - "html": Displays the analysis data as an HTML table. (default)
        - "table": Exports the analysis data to delta tables (appended) in your lakehouse.
        - "zip": Exports the analysis data to a zip file in your lakehouse.
        - "none": Does not export the analysis data, usually run with `return_dataframe=True` to return the data as a pandas DataFrame.
    return_dataframe : bool, default=False
        Whether to return the analysis data as a DataFrame.
    language : str, default=None
        Specifying a language name or code (i.e. 'it' for Italian) will auto-translate the Category, Rule Name and Description into the specified language.
        Defaults to None which resolves to English. Please refer to `supported languages <https://api.cognitive.microsofttranslator.com/languages?api-version=3.0>`__
        for all supported languages and codes.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.

    Returns
    -------
    pandas.DataFrame or None
        The analysis data as a DataFrame if `return_dataframe` is True.
    """
    if export not in ["html", "table", "zip", "none"]:
        raise ValueError(f"Invalid export format '{export}'. Choose from "
                         "'html', 'table', 'zip', or 'none'.")

    if export in ["table", "zip"]:
        raise NotImplementedError("Exporting to delta tables or zip files is not yet supported.")

    df_bpa = get_bpa_dataframe(dataset, workspace=workspace, language=language)

    if export == "html" and not df_bpa.empty:
        visualize_bpa(df_bpa)

    if return_dataframe:
        return df_bpa

    return None


def get_bpa_dataframe(
    dataset: Union[str, UUID],
    workspace: Optional[Union[str, UUID]] = None,
    language: Optional[str] = None
) -> pd.DataFrame:
    """
    Generate a Best Practice Analyzer violations DataFrame for a semantic model.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or ID of the semantic model.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    language : str, default=None
        Specifying a language name or code (i.e. 'it' for Italian) will auto-translate the Category, Rule Name and Description into the specified language.
        Defaults to None which resolves to English. Please refer to `supported languages <https://api.cognitive.microsofttranslator.com/languages?api-version=3.0>`__
        for all supported languages and codes.

    Returns
    -------
    pandas.DataFrame
        A pandas DataFrame containing the Best Practice Analyzer violations.
    """
    with connect_semantic_model(
        dataset, workspace=workspace, readonly=True
    ) as tom:

        # Do not run BPA for models with no tables
        if tom.model.Tables.Count == 0:
            icons.Logger.warn(
                f"The '{dataset}' semantic model within the "
                f"'{workspace}' workspace has no tables and therefore there "
                "are no valid BPA violations."
            )

            return pd.DataFrame(
                columns=[
                    "Category",
                    "Rule Name",
                    "Severity",
                    "Object Type",
                    "Object Name",
                    "Description",
                    "URL",
                ]
            )

        with get_model_calc_dependencies(
            dataset, workspace=workspace
        ) as deps:
            return BestPracticeAnalyzer().analyze(tom, deps, language=language)


def visualize_bpa(df: pd.DataFrame):
    """
    Visualize the Best Practice Analyzer violations in an HTML format.

    Parameters
    ----------
    df : pandas.DataFrame
        A pandas dataframe containing the Best Practice Analyzer violations.
    """

    df = (
        df[
            [
                "Category",
                "Rule Name",
                "Object Type",
                "Object Name",
                "Severity",
                "Description",
                "URL",
            ]
        ]
        .sort_values(["Category", "Rule Name", "Object Type", "Object Name"])
        .set_index(["Category", "Rule Name"])
    )

    bpa2 = df.reset_index()
    bpa_dict = {
        cat: bpa2[bpa2["Category"] == cat].drop("Category", axis=1)
        for cat in bpa2["Category"].drop_duplicates().values
    }

    styles = """
    <style>
        .tab { overflow: hidden; border: 1px solid #ccc; background-color: #f1f1f1; }
        .tab button { background-color: inherit; float: left; border: none; outline: none; cursor: pointer; padding: 14px 16px; transition: 0.3s; }
        .tab button:hover { background-color: #ddd; }
        .tab button.active { background-color: #ccc; }
        .tabcontent { display: none; padding: 6px 12px; border: 1px solid #ccc; border-top: none; }
        .tabcontent.active { display: block; }
        .tooltip { position: relative; display: inline-block; }
        .tooltip .tooltiptext { visibility: hidden; width: 300px; background-color: #555; color: #fff; text-align: center; border-radius: 6px; padding: 5px; position: absolute; z-index: 1; bottom: 125%; left: 50%; margin-left: -110px; opacity: 0; transition: opacity 0.3s; }
        .tooltip:hover .tooltiptext { visibility: visible; opacity: 1; }
    </style>
    """  # noqa: E501

    # JavaScript for tab functionality
    script = """
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

    # HTML for tabs
    tab_html = '<div class="tab">'
    content_html = ""
    for i, (title, df) in enumerate(bpa_dict.items()):
        if df.shape[0] == 0:
            continue

        tab_id = f"tab{i}"
        active_class = ""
        if i == 0:
            active_class = "active"

        summary = " + ".join(
            [f"{idx} ({v})" for idx, v in df["Severity"].value_counts().items()]
        )
        tab_html += f'<button class="tablinks {active_class}" onclick="openTab(event, \'{tab_id}\')"><b>{title}</b><br/>{summary}</button>'
        content_html += f'<div id="{tab_id}" class="tabcontent {active_class}">'

        # Adding tooltip for Rule Name using Description column
        content_html += '<table border="1">'
        content_html += "<tr><th>Rule Name</th><th>Object Type</th><th>Object Name</th><th>Severity</th></tr>"
        for _, row in df.iterrows():
            content_html += "<tr>"
            if pd.notnull(row["URL"]):
                content_html += f'<td class="tooltip" onmouseover="adjustTooltipPosition(event)"><a href="{row["URL"]}">{row["Rule Name"]}</a><span class="tooltiptext">{row["Description"]}</span></td>'  # noqa: E501
            elif pd.notnull(row["Description"]):
                content_html += f'<td class="tooltip" onmouseover="adjustTooltipPosition(event)">{row["Rule Name"]}<span class="tooltiptext">{row["Description"]}</span></td>'
            else:
                content_html += f'<td>{row["Rule Name"]}</td>'
            content_html += f'<td>{row["Object Type"]}</td>'
            content_html += f'<td>{row["Object Name"]}</td>'
            content_html += f'<td style="text-align: center;">{row["Severity"]}</td>'
            # content_html += f'<td>{row["Severity"]}</td>'
            content_html += "</tr>"
        content_html += "</table>"

        content_html += "</div>"
    tab_html += "</div>"

    with pd.option_context("display.max_colwidth", 100):
        # Display the tabs, tab contents, and run the script
        return display(HTML(styles + tab_html + content_html + script))
