from typing import TYPE_CHECKING, Protocol

from sempy.fabric._client._utils import _init_analysis_services

if TYPE_CHECKING:
    _init_analysis_services()

    import Microsoft.AnalysisServices.Tabular as TOM


class TOMWrapperProtocol(Protocol):
    """
    Protocol for the TOMWrapper class.
    This is used to type hint the properties of the TOMWrapper class in the Mixin classes.
    """

    @property
    def model(self) -> "TOM.Model":
        ...

    @property
    def dataset(self) -> str:
        ...

    @property
    def workspace(self) -> str:
        ...
