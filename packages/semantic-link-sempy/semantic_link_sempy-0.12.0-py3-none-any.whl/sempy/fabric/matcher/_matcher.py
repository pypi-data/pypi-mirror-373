from sempy.functions.matcher import TypeMatcher
from typing import Type
from sempy._metadata._mseries import MSeries
from sempy.fabric import DataCategory


class DataCategoryMatcher(TypeMatcher):
    def __init__(self, data_category: str, dtype: Type) -> None:
        """
        Base class for PowerBI data category matchers.

        Parameters
        ----------
        data_category : str
            The Power BI data category to match.
        dtype : type
            The data type required in the column.
        """
        super().__init__(dtype)

        self.data_category = data_category

    def matches(self, series: MSeries) -> bool:
        """
        Match the data category with metadata in the series.

        Parameters
        ----------
        series : MSeries
            The series that is checked.

        Returns
        -------
        bool
            Returns true if data category matches the data category of the series.
        """

        # print(f"{type(self)}.matches({series.name}) against {self.data_category}")

        # check data type
        if not super().matches(series):
            return False

        # check data category
        col_metadata = series.column_metadata
        if col_metadata is None:
            return False

        col_metadata = col_metadata.get(series.name, None)
        if col_metadata is None:
            return False

        # print(f"{type(self)}.matches({series.name}) against {self.data_category}: {col_metadata.get('data_category', None)} out of {col_metadata}")
        return col_metadata.get("data_category", None) == self.data_category

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self.data_category}, {self.dtype})"


class LatitudeMatcher(DataCategoryMatcher):
    """
    Match a column containing latitude values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.LATITUDE, float)


class LongitudeMatcher(DataCategoryMatcher):
    """
    Match a column containing longitude values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.LONGITUDE, float)


class AddressMatcher(DataCategoryMatcher):
    """
    Match a column containing address values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.ADDRESS, str)


class BarcodeMatcher(DataCategoryMatcher):
    """
    Match a column containing barcode values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.BARCODE, str)


class CityMatcher(DataCategoryMatcher):
    """
    Match a column containing city values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.CITY, str)


class ContinentMatcher(DataCategoryMatcher):
    """
    Match a column containing continent values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.CONTINENT, str)


class CountryMatcher(DataCategoryMatcher):
    """
    Match a column containing country values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.COUNTRY, str)


class PlaceMatcher(DataCategoryMatcher):
    """
    Match a column containing place values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.PLACE, str)


class PostalCodeMatcher(DataCategoryMatcher):
    """
    Match a column containing postal code values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.POSTAL_CODE, str)


class StateOrProvinceMatcher(DataCategoryMatcher):
    """
    Match a column containing state or province values.
    """

    def __init__(self) -> None:
        super().__init__(DataCategory.STATE_OR_PROVINCE, str)
