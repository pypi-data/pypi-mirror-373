from sempy._utils import _icons as icons
from typing import TYPE_CHECKING, Union
from sempy.fabric._client._utils import _init_analysis_services
from sempy.fabric._client._tom import TOMWrapperProtocol
from sempy.fabric._client._tom import ListAllMixin

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class TranslationMixin(ListAllMixin, TOMWrapperProtocol):

    def add_translation(self, language: str, verbose: int = 0):
        """
        Add a `translation language <https://learn.microsoft.com/dotnet/api/microsoft.analysisservices.tabular.culture?view=analysisservices-dotnet>`_ (culture) to a semantic model.

        Parameters
        ----------
        language : str
            The language code (i.e. 'it-IT' for Italian).
        verbose : int, optional
            If verbose is set to bigger than 0, a message will be printed to the console.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        if not self.model.Cultures.Contains(language):
            cul = TOM.Culture()
            cul.Name = language
            lm = TOM.LinguisticMetadata()
            lm.ContentType = TOM.ContentType.Json
            lm.Content = f'{{"Version": "1.0.0", "Language": "{language}"}}'
            cul.LinguisticMetadata = lm
            self.model.Cultures.Add(cul)
            if verbose > 0:
                print(
                    f"{icons.in_progress} Adding '{language}' language into the model's cultures..."
                )
        else:
            if verbose > 0:
                print(
                    f"{icons.red_dot} The '{language}' translation language already exists."
                )

    def remove_translation(
        self,
        object: Union[
            "TOM.Table", "TOM.Column", "TOM.Measure", "TOM.Hierarchy", "TOM.Level"
        ],
        language: str,
        verbose: int = 0
    ):
        """
        Remove an object's `translation <https://learn.microsoft.com/dotnet/api/microsoft.analysisservices.tabular.culture?view=analysisservices-dotnet>`_ value.

        Parameters
        ----------
        object : TOM Object
            An object (i.e. table/column/measure) within a semantic model.
        language : str
            The language code.
        verbose : int, optional
            If verbose is set to bigger than 0, a message will be printed to the console.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        o = object.Model.Cultures[language].ObjectTranslations[
            object, TOM.TranslatedProperty.Caption
        ]
        if object.Model.Cultures[language].ObjectTranslations.Contains(o):
            object.Model.Cultures[language].ObjectTranslations.Remove(o)
        else:
            if verbose > 0:
                print(
                    f"{icons.red_dot} The '{language}' translation language does not exist for the object."
                )

    def set_translation(
        self,
        object: Union[
            "TOM.Table", "TOM.Column", "TOM.Measure", "TOM.Hierarchy", "TOM.Level"
        ],
        language: str,
        property: str,
        value: str,
        verbose: int = 0
    ):
        """
        Set a `translation <https://learn.microsoft.com/dotnet/api/microsoft.analysisservices.tabular.culture?view=analysisservices-dotnet>`_ value for an object's property.

        Parameters
        ----------
        object : TOM Object
            An object (i.e. table/column/measure) within a semantic model.
        language : str
            The language code.
        property : str
            The property to set. Options: 'Name', 'Description', 'Display Folder'.
        value : str
            The transation value.
        verbose : int, optional
            If verbose is set to bigger than 0, a message will be printed to the console.
        """
        import Microsoft.AnalysisServices.Tabular as TOM

        if not self.model.Cultures.Contains(language):
            self.add_translation(language=language)

        validObjects = [
            TOM.ObjectType.Table,
            TOM.ObjectType.Column,
            TOM.ObjectType.Measure,
            TOM.ObjectType.Hierarchy,
            TOM.ObjectType.Level,
        ]

        if object.ObjectType not in validObjects:
            raise ValueError(
                f"{icons.red_dot} Translations can only be set to {validObjects}."
            )

        mapping = {
            "Name": TOM.TranslatedProperty.Caption,
            "Description": TOM.TranslatedProperty.Description,
            "Display Folder": TOM.TranslatedProperty.DisplayFolder,
        }

        prop = mapping.get(property)
        if prop is None:
            raise ValueError(
                f"{icons.red_dot} Invalid property value. Please choose from the following: {list(mapping.keys())}."
            )

        object.Model.Cultures[language].ObjectTranslations.SetTranslation(
            object, prop, value
        )

        if verbose > 0:
            if object.ObjectType in [TOM.ObjectType.Table, TOM.ObjectType.Measure]:
                print(
                    f"{icons.green_dot} The {property} property for the '{object.Name}' {str(object.ObjectType).lower()} has been translated into '{language}' as '{value}'."
                )
            elif object.ObjectType in [
                TOM.ObjectType.Column,
                TOM.ObjectType.Hierarchy,
                TOM.ObjectType.Level,
            ]:
                print(
                    f"{icons.green_dot} The {property} property for the '{object.Parent.Name}'[{object.Name}] {str(object.ObjectType).lower()} has been translated into '{language}' as '{value}'."
                )
