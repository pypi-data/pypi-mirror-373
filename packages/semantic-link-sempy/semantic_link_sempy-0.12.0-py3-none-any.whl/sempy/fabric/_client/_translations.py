import pandas as pd
from uuid import UUID
from typing import TYPE_CHECKING, List, Optional, Union
from sempy._utils import _icons as icons
from sempy.fabric._client._utils import _init_analysis_services
from sempy.fabric._client._languages import ISO_LANGUAGE_MAP, API_LANGUAGE_MAP
import sempy.fabric as fabric
from sempy.fabric._utils import is_valid_uuid

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


def _clean_text(text, exclude_chars):
    """
    Replace chars in exclude_chars with space.

    Parameters
    ----------
    text : str
    exclude_chars : str
        Characters to exclude from translation. For example, "," "!".
    """
    if exclude_chars:
        for char in exclude_chars:
            text = text.replace(char, " ")
    return text


def _get_language_map():
    """
    Get language codes from language names.

    """
    from sempy.fabric._client._cognitiveservice_rest_api import _CognitiveServiceRestAPI
    results = _CognitiveServiceRestAPI().fetch_language_map()
    if isinstance(results, dict) and "translation" in results:
        full_language_map = results["translation"]
        # use lower case for indexing and keep original code for API call
        language_map = {
            key.lower(): {
                "code": key,
                "name": value["name"].lower()
            } for key, value in full_language_map.items()
        }
        reverted_language_map = {}
        for key, info in language_map.items():
            value = info["name"]
            if value not in reverted_language_map:
                reverted_language_map[value] = key
            else:
                if isinstance(reverted_language_map[value], str):
                    reverted_language_map[value] = [reverted_language_map[value]]
                    reverted_language_map[value].append(key)
        return language_map, reverted_language_map
    else:
        raise ValueError(f"Failed to fetch language map {results}")


def _get_language_codes(languages: str | List[str]):
    """
    Get language codes from language names and check language codes when used directly.

    Parameters
    ----------
    languages : str or List[str]
        Language names or language codes.
    """
    if isinstance(languages, str):
        languages = [languages]

    language_map, reverted_language_map = _get_language_map()

    for i, lang in enumerate(languages):
        input_lang = lang
        # normalize to lowercase for looking up in language maps
        lang = lang.lower()
        if lang not in language_map:
            if lang in ISO_LANGUAGE_MAP:
                languages[i] = ISO_LANGUAGE_MAP[lang]
            elif lang in reverted_language_map:
                language_codes = reverted_language_map[lang]
                if isinstance(language_codes, list):
                    codes = ", ".join(map(lambda c: language_map[c]["code"], language_codes))
                    raise ValueError(f"Multiple language codes found: {codes} for language name: {input_lang}. "
                                     "Please use the language code instead")
                else:
                    languages[i] = reverted_language_map[lang]
            else:
                raise ValueError(f"Language name/code error: {input_lang}, please refer to translation in "
                                 "https://api.cognitive.microsofttranslator.com/languages?api-version=3.0 for supported languages")

    # convert lowercased code back to original language code for API call
    languages = list(map(lambda k: language_map[k.lower()]["code"], languages))

    return languages


def _create_data_entry(
    obj: Union[
        "TOM.Table", "TOM.Column", "TOM.Measure", "TOM.Hierarchy", "TOM.Level"
    ],
    object_type: str,
    exclude_characters: str
) -> dict:
    """
    Generate a row of data for the translation DataFrame.

    Parameters
    ----------
    obj : TOM Object
        An object (i.e. table/column/measure) within a semantic model.
    object_type : str
        Type of the object.
    exclude_characters : str
        Characters to exclude from translation.
    """
    obj_name = getattr(obj, 'Name', None)
    obj_description = getattr(obj, 'Description', None)
    obj_display_folder = getattr(obj, 'DisplayFolder', None)
    obj_name_cleaned = _clean_text(obj_name, exclude_characters) if obj_name else obj_name
    obj_description_cleaned = _clean_text(obj_description, exclude_characters) if obj_description else obj_description
    obj_display_folder_cleaned = _clean_text(obj_display_folder, exclude_characters) if obj_display_folder else obj_display_folder
    return {
        "Object Type": object_type,
        "Name": obj_name,
        "TName": obj_name_cleaned,
        "Description": obj_description,
        "TDescription": obj_description_cleaned,
        "Display Folder": obj_display_folder,
        "TDisplay Folder": obj_display_folder_cleaned,
    }


def _prepare_translation_dataframe(dataset, exclude_characters, workspace=None):
    """
    Prepare the translation pandas dataframe.

    Parameters
    ----------
    dataset : str
        Name of the dataset.
    exclude_characters : str
        Characters to exclude from translation.
    workspace : str, optional
        Name of the workspace, by default None.
    """
    from sempy.fabric._client._tom._model import connect_semantic_model

    df_prep = pd.DataFrame(columns=["Object Type", "Name", "TName", "Description", "TDescription", "Display Folder", "TDisplay Folder"])

    with connect_semantic_model(dataset=dataset, readonly=True, workspace=workspace) as tom:
        for obj_type, tom_objects in [
            ("Table", tom.all_tables),
            ("Column", tom.all_columns),
            ("Measure", tom.all_measures),
            ("Hierarchy", tom.all_hierarchies),
            ("Level", tom.all_levels)
        ]:
            for tom_object in tom_objects:
                new_data = _create_data_entry(tom_object, obj_type, exclude_characters)
                df_prep = pd.concat([df_prep, pd.DataFrame(new_data, index=[0])], ignore_index=True)
    return df_prep


def _translate_columns(df_prep, languages):
    """
    Translate the DataFrame to specific languages.

    Parameters
    ----------
    df_prep : pd.DataFrame
        DataFrame to be translated.
    languages : str or List[str]
        Target languages for translation.
    """
    from sempy.fabric._client._cognitiveservice_rest_api import _CognitiveServiceAsyncRestAPI

    columns = ["Name", "Description", "Display Folder"]
    columns_to_translate = []
    for clm in columns:
        column_name = f"T{clm}"
        column_after_dedup = df_prep[column_name].drop_duplicates().astype(str).to_list()
        columns_to_translate.extend(column_after_dedup)
    cognitive_service_client = _CognitiveServiceAsyncRestAPI()
    return cognitive_service_client.translate_text(
        texts=columns_to_translate, to_lang=[languages] if isinstance(languages, str) else languages
    )


def _set_translation_if_exists(obj, language, language_index, columns_translated, tom, exclude_characters, verbose):
    """
    Set translation in tom if the target translation exists.

    Parameters
    ----------
    obj : object
        Object to be translated.
    language : str
        Target language for translation.
    language_index : int
        Index of the target language.
    columns_translated : pd.DataFrame
        DataFrame containing the translated columns.
    tom : object
        TOM object.
    exclude_characters : str
        Characters to exclude from translation.
    verbose : int
        If verbose is set to bigger than 0, a message will be printed to the console.
    """
    for prop in ["Name", "Description", "Display Folder"]:
        trans = getattr(obj, prop, None)
        if trans:
            trans = _clean_text(trans, exclude_characters)
            df_filt = columns_translated[columns_translated.iloc[:, 0] == trans].iloc[:, language_index + 1]
            if not df_filt.empty:
                translation_value = df_filt.iloc[0]
                tom.set_translation(object=obj, language=language, property=prop, value=translation_value, verbose=verbose)


def _apply_translations(columns_translated, languages, workspace, dataset, exclude_characters, model_readonly=False, verbose=0):
    """
    Apply translations to the semantic model.

    Parameters
    ----------
    columns_translated : pd.DataFrame
        DataFrame containing the translated columns.
    languages : str or List[str]
        Target languages for translation.
    workspace : str
        Name of the workspace.
    dataset : str
        Name of the dataset.
    exclude_characters : str
        Characters to exclude from translation.
    verbose : int
        If verbose is set to bigger than 0, a message will be printed to the console.
    model_readonly : bool, optional
        If True, the model will be opened in read-only mode, by default False.
    """
    from sempy.fabric._client._tom._model import connect_semantic_model

    with connect_semantic_model(dataset=dataset, readonly=model_readonly, workspace=workspace, verbose=verbose) as tom:
        tom.sll_tags.append("TranslateSemanticModel")
        iso_languages = []
        for lang in languages:
            if lang in API_LANGUAGE_MAP:
                if API_LANGUAGE_MAP[lang]:
                    iso_languages.append(API_LANGUAGE_MAP[lang])
                else:
                    iso_languages.append(lang)
                    print(f"The target language {lang} may not be supported in Power BI.")
            else:
                raise ValueError(f"Language code error: {lang}.")
        for iso_language in iso_languages:
            tom.add_translation(language=iso_language, verbose=verbose)
            language_ind = iso_languages.index(iso_language)
            if verbose > 0:
                print(
                    f"{icons.in_progress} Translating into the '{iso_language}' language..."
                )
            for objects in [
                (tom.all_tables),
                (tom.all_columns),
                (tom.all_measures),
                (tom.all_hierarchies),
                (tom.all_levels)
            ]:
                for o in objects:
                    _set_translation_if_exists(o, iso_language, language_ind, columns_translated, tom, exclude_characters, verbose)


def get_model_translations(workspace, dataset, verbose: int = 0):
    """
    Get the translated semantic model.

    Parameters
    ----------
    workspace : str
        Name of the workspace.
    dataset : str
        Name of the dataset.
    verbose : int
        If verbose is set to bigger than 0, a message will be printed to the console
    """
    from sempy.fabric._client._tom._model import connect_semantic_model

    result = pd.DataFrame(
        columns=[
            "Language", "Object Type", "Table Name", "Object Name", "Translated Object Name",
            "Description", "Translated Description", "Display Folder", "Translated Display Folder"
        ]
    )
    with connect_semantic_model(dataset=dataset, readonly=True, workspace=workspace, verbose=verbose) as tom:
        from sempy.fabric._client._utils import _init_analysis_services
        _init_analysis_services()
        import Microsoft.AnalysisServices.Tabular as TOM

        for culture in tom.model.Cultures:
            for trans in culture.ObjectTranslations:
                object_type = str(trans.Object.ObjectType)
                object_name = trans.Object.Name
                trans_value = trans.Value
                trans_prop = str(trans.Property)

                if trans.Object.ObjectType == TOM.ObjectType.Table:
                    desc = tom.model.Tables[object_name].Description
                    new_data = {
                        "Language": culture.Name,
                        "Table Name": object_name,
                        "Object Name": object_name,
                        "Object Type": object_type,
                        "Description": desc,
                    }
                elif trans.Object.ObjectType == TOM.ObjectType.Level:
                    hierarchy_name = trans.Object.Parent.Name
                    table_name = trans.Object.Parent.Parent.Name
                    level_name = "'" + hierarchy_name + "'[" + object_name + "]"
                    desc = (
                        tom.model.Tables[table_name]
                        .Hierarchies[hierarchy_name]
                        .Levels[object_name]
                        .Description
                    )
                    new_data = {
                        "Language": culture.Name,
                        "Table Name": table_name,
                        "Object Name": level_name,
                        "Object Type": object_type,
                        "Description": desc,
                    }
                elif trans.Object.ObjectType == TOM.ObjectType.Column:
                    table_name = trans.Object.Table.Name
                    desc = tom.model.Tables[table_name].Columns[object_name].Description
                    display_folder = (
                        tom.model.Tables[table_name].Columns[object_name].DisplayFolder
                    )
                    new_data = {
                        "Language": culture.Name,
                        "Table Name": table_name,
                        "Object Name": object_name,
                        "Object Type": object_type,
                        "Description": desc,
                        "Display Folder": display_folder,
                    }
                elif trans.Object.ObjectType == TOM.ObjectType.Measure:
                    table_name = trans.Object.Table.Name
                    desc = tom.model.Tables[table_name].Measures[object_name].Description
                    display_folder = (
                        tom.model.Tables[table_name].Measures[object_name].DisplayFolder
                    )
                    new_data = {
                        "Language": culture.Name,
                        "Table Name": table_name,
                        "Object Name": object_name,
                        "Object Type": object_type,
                        "Description": desc,
                        "Display Folder": display_folder,
                    }
                elif trans.Object.ObjectType == TOM.ObjectType.Hierarchy:
                    table_name = trans.Object.Table.Name
                    desc = tom.model.Tables[table_name].Hierarchies[object_name].Description
                    display_folder = (
                        tom.model.Tables[table_name].Hierarchies[object_name].DisplayFolder
                    )
                    new_data = {
                        "Language": culture.Name,
                        "Table Name": table_name,
                        "Object Name": object_name,
                        "Object Type": object_type,
                        "Description": desc,
                        "Display Folder": display_folder,
                    }

                result = pd.concat(
                        [result, pd.DataFrame(new_data, index=[0])], ignore_index=True
                    )

                if trans_prop == "Caption":
                    result.loc[result.index[-1], "Translated Object Name"] = trans_value
                elif trans_prop == "Description":
                    result.loc[result.index[-1], "Translated Description"] = trans_value
                elif trans_prop == "DisplayFolder":
                    result.loc[result.index[-1], "Translated Display Folder"] = trans_value
                else:
                    raise ValueError(f"Wrong property name {trans_prop}")
        result.fillna("", inplace=True)
    return result


def translate_semantic_model(
    dataset: Union[str, UUID],
    languages: Union[str, List[str]],
    exclude_characters: Optional[str] = None,
    workspace: Optional[Union[str, UUID]] = None,
    model_readonly: bool = False,
    verbose: int = 0
) -> pd.DataFrame:
    """
    Translate names, descriptions, display folders for all objects in a semantic model.

    Parameters
    ----------
    dataset : str or uuid.UUID
        Name or UUID of the dataset.
    languages : str or list of str
        The target languages for translation.
    exclude_characters : str, default=None
        Characters to exclude from translation, by default None.
    workspace : str or uuid.UUID, default=None
        The Fabric workspace name or UUID object containing the workspace ID.
        Defaults to None which resolves to the workspace of the attached lakehouse
        or if no lakehouse attached, resolves to the workspace of the notebook.
    model_readonly : bool, default=False
        If True, the model will be opened in read-only mode.
    verbose : int, default=0
        If verbose is set to bigger than 0, a message will be printed to the console.

    Returns
    -------
    pandas.DataFrame
        A DataFrame containing the translated semantic model.
    """
    if workspace is None or is_valid_uuid(str(workspace)):
        workspace = fabric.resolve_workspace_name(workspace)

    if is_valid_uuid(str(dataset)):
        dataset = fabric.resolve_dataset_name(dataset, workspace)
    languages = _get_language_codes(languages)
    df_prep = _prepare_translation_dataframe(dataset, exclude_characters, workspace)
    columns_translated = _translate_columns(df_prep, languages)
    _apply_translations(columns_translated, languages, workspace, dataset, exclude_characters, model_readonly, verbose)
    return get_model_translations(workspace, dataset)
