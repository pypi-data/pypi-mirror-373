from abc import ABC, abstractmethod
from typing import Any, Type

from sempy._metadata._mseries import MSeries

import pandas as pd
import datetime
import numpy as np


class SeriesMatcher(ABC):
    """
    Define a column-level matcher for a semantic function.
    """

    @abstractmethod
    def matches(self, series: MSeries) -> bool:
        """
        Return true if the matcher is met.

        Parameters
        ----------
        series : sempy.fabric.FabricSeries
            The column the matcher is being tested against.

        Returns
        -------
        bool
            True if the matcher is met.
        """
        pass


class AlwaysTrueMatcher(SeriesMatcher):
    """
    Match any column.
    """
    def matches(self, series: MSeries) -> bool:
        """
        Match any column.

        Parameters
        ----------
        series : sempy.fabric.FabricSeries
            The series the matcher is being tested against.

        Returns
        -------
        bool
            True for all columns.
        """
        return True


class TypeMatcher(SeriesMatcher):
    """
    A column matcher that checks the data type of the column matches.

    Parameters
    ----------
    dtype : type
        The data type required in the column.
        Date/Time types like :class:`~pandas.Timestamp` and :class:`~numpy.datetime64` are normalized into datetime.datetime.
    """
    def __init__(self, dtype: Type):
        self.dtype = self._normalize(dtype)

    def _normalize(self, _type: Type) -> Type:
        if _type == pd.Timestamp:
            return datetime.datetime

        if isinstance(_type, np.dtype):
            if np.issubdtype(_type, np.datetime64):
                return datetime.datetime

        if isinstance(_type, pd.StringDtype):
            return str

        return _type

    def __repr__(self) -> str:
        return f"TypeMatcher({self.dtype})"

    def matches(self, series: MSeries) -> bool:
        """
        Check if the column has the expected data type.

        Parameters
        ----------
        series : sempy.fabric.FabricSeries
            The series the matcher is being tested against.

        Returns
        -------
        bool
            True if the matcher is met.
        """

        # need to be a bit careful w/ object as it matches with everything
        if series.dtype == np.dtype('object'):
            return self.dtype == Any or self.dtype == any or self.dtype == str

        return self._normalize(series.dtype) == self.dtype  # type: ignore


class NameMatcher(SeriesMatcher):
    """
    A column matcher that checks the name of the column matches.

    Parameters
    ----------
    name : str
        The name of the column.
    """
    def __init__(self, name: str):
        self.name = name

    def __repr__(self) -> str:
        return f"NameMatcher({self.name})"

    def matches(self, series: MSeries) -> bool:
        """
        Check if the column has the expected name.

        Parameters
        ----------
        series : sempy.fabric.FabricSeries
            The series the matcher is being tested against.

        Returns
        -------
        bool
            True if the matcher is met.
        """
        return series.name == self.name


class AndMatcher(SeriesMatcher):
    """
    A column matcher that checks if a list of matchers are all met.

    Parameters
    ----------
    *matchers : list[sempy.functions.matcher.SeriesMatcher]
        The list of matchers to check.
    """
    def __init__(self, *matchers: SeriesMatcher):
        self.matchers = matchers

    def __repr__(self) -> str:
        return f"AndMatcher({self.matchers})"

    def matches(self, series: MSeries) -> bool:
        """
        Check if the column has the expected name.

        Parameters
        ----------
        series : sempy.fabric.FabricSeries
            The series the matcher is being tested against.

        Returns
        -------
        bool
            True if the matcher is met.
        """
        return all([m.matches(series) for m in self.matchers])


class OrMatcher(SeriesMatcher):
    """
    A column matcher that checks if at least one of a list of matchers is met.

    Parameters
    ----------
    *matchers : list[SeriesMatcher]
        The list of matchers to check.
    """
    def __init__(self, *matchers: SeriesMatcher):
        self.matchers = matchers

    def __repr__(self) -> str:
        return f"OrMatcher({self.matchers})"

    def matches(self, series: MSeries) -> bool:
        """
        Check if the column has the expected name.

        Parameters
        ----------
        series : sempy.fabric.FabricSeries
            The series the matcher is being tested against.

        Returns
        -------
        bool
            True if the matcher is met.
        """
        return any([m.matches(series) for m in self.matchers])


class NameTypeMatcher(SeriesMatcher):
    """
    A column matcher that checks if the column has the expected name and data type.

    Parameters
    ----------
    name : str
        The name of the column.
    dtype : Type
        The data type required in the column.
        Date/Time types like pd.TimeStamp and np.datetime64 are normalized into datetime.datetime.
    """
    def __init__(self, name: str, dtype: Type):
        self.matcher = AndMatcher(NameMatcher(name), TypeMatcher(dtype))

    def __repr__(self) -> str:
        return f"NameTypeMatcher({self.matcher})"

    def matches(self, series: MSeries) -> bool:
        """
        Check if the column has the expected name and data type.

        Parameters
        ----------
        series : sempy.fabric.FabricSeries
            The series the matcher is being tested against.

        Returns
        -------
        bool
            True if the matcher is met.
        """
        return self.matcher.matches(series)
