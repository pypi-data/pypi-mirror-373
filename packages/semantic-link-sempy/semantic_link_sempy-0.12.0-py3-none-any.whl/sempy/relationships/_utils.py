import pandas as pd
import inspect
import warnings

from typing import Dict, List, Optional, Set, Tuple, Union


def _to_dataframe_dict(
    tables: Union[Dict[str, pd.DataFrame], List[pd.DataFrame]],
) -> Dict[str, pd.DataFrame]:

    if isinstance(tables, (tuple, list)):
        result = {}
        for i in range(len(tables)):
            # Try to find the name of the element in the session or use the index as name
            # if a match cannot be found
            var_name = _find_variable_name_up_the_stack(tables[i])
            if var_name:
                result[var_name] = tables[i]
            else:
                result[f"[{i}]"] = tables[i]
    elif isinstance(tables, dict):
        result = tables
    else:
        raise TypeError(f"Unexpected type {type(tables)} for \"tables\": not a dictionary of dataframes by name or a list of dataframes")

    if not all(isinstance(e, pd.DataFrame) for e in result.values()):
        raise TypeError("All \"tables\" elements must be pandas dataframes or derived")

    return result


def _find_variable_name_up_the_stack(obj):
    frame = inspect.currentframe().f_back
    while frame is not None:
        for name, value in frame.f_locals.items():
            if value is obj:
                return name
        frame = frame.f_back
    return None


def _to_exclude_tuples(
    exclude: Optional[Union[List[Tuple[str]], pd.DataFrame]]
) -> Optional[Set[Tuple[str]]]:
    msg = "not a list of tuples(from_table, from_column, to_table, to_column)"
    if exclude is None:
        result = None
    elif isinstance(exclude, list):
        for t in exclude:
            if not isinstance(t, tuple):
                raise TypeError(f"Invalid type {type(t)} of an element of \"exclude\": {msg}")
            if len(t) != 4:
                raise ValueError(f"Invalid len {len(t)} of an element of \"exclude\": {msg}")
        result = set(exclude)
    elif isinstance(exclude, pd.DataFrame):
        df_sub = exclude[["From Table", "From Column", "To Table", "To Column"]]
        result = set(df_sub.itertuples(index=False, name=None))   # type: ignore
    else:
        raise TypeError(f"Unexpected type {type(exclude)} for \"exclude\": {msg}")
    return result


def _is_key_missing(rel, table_columns, action):

    from_table, from_column, to_table, to_column = (
        rel["From Table"],
        rel["From Column"],
        rel["To Table"],
        rel["To Column"]
    )

    def _execute_action(msg: str):
        if action == 'raise':
            raise ValueError(f"{msg}. To suppress this exception use \"missing_key_errors\" of ['warn', 'ignore']")
        elif action == 'warn':
            warnings.warn(msg)
        return True

    if from_table not in table_columns:
        return _execute_action(f"Table '{from_table}' not in \"tables\"")
    if to_table not in table_columns:
        return _execute_action(f"Table '{to_table}' not in \"tables\"")
    if from_column not in table_columns[from_table]:
        return _execute_action(f"Column '{from_column}' not in table '{from_table}'")
    if to_column not in table_columns[to_table]:
        return _execute_action(f"Column '{to_column}' not in table '{to_table}'")
    return False
