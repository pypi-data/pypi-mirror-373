from typing import Optional, TYPE_CHECKING
import uuid

from sempy.fabric._client._utils import refresh_tom_access_token

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential


class FabricAdomdException(Exception):
    def __init__(self, adomd_activity_id: str, root_cause_type: type,
                 root_cause_exc: Exception):
        super().__init__(
            f"An error occurred when running AdomdCommand. "
            f"AdomdCommandActivityId: '{adomd_activity_id}'\n"
            f"\nCaused by {root_cause_type.__qualname__}:\n{root_cause_exc}\n"
        )


class AdomdConnection:
    """
    Cached wrapper of Microsoft.AnalysisServices AdomdConnection object, designed to be used with python context manager.

    Parameters
    ----------
    dax_connection_string : str
        Adomd connection string.
    credential : TokenCredential, default=None
        The credential for token acquisition. Must be an instance of
        `azure.core.credentials.TokenCredential <https://learn.microsoft.com/en-us/azure/developer/python/sdk/authentication/overview>`_.
        If None, defaults to `fabric.analytics.environment.credentials.FabricAnalyticsTokenCredentials`.
    """

    def __init__(self, dax_connection_string: str, credential: Optional["TokenCredential"] = None):
        self.adomd_connection = None
        self.dax_connection_string = dax_connection_string
        self.credential = credential

        # state of context
        self._adomd_activity_id: str = str(uuid.UUID(int=0))
        self._inside_context: bool = False

    def _refresh_adomd_activity_id(self):
        """
        Create a new activity id for next call. This will be automatically executed at the beginning of each with-statement.
        """
        self._adomd_activity_id = str(uuid.uuid4())

    @property
    def adomd_activity_id(self) -> str:
        if not self._inside_context:
            raise ValueError("Read AdomdCommand activity ID out of the context "
                             "manager (with-statement) is not allowed")
        return self._adomd_activity_id

    @adomd_activity_id.setter
    def adomd_activity_id(self, value: str):
        raise ValueError("Cannot manually update the value of AdomdCommand "
                         "activity ID. Please use the context manager "
                         "(with-statement)")

    def __enter__(self):
        """
        Create a new Microsoft.AnalysisServices.AdomdClient.AdomdConnection object, or get from existing cache.
        """
        self._inside_context = True
        self._refresh_adomd_activity_id()
        return self.get_or_create_connection()

    def __exit__(self, exc_type, exc_value, exc_tb):
        """
        Handles clearing the cached connection only if an exception is thrown (exception will still be raised).
        """
        try:
            if exc_type is not None:
                self.close_and_dispose_connection()
                # Wrap the exception with the activity id for debugging.
                # Raise with the original traceback
                raise FabricAdomdException(self.adomd_activity_id, exc_type,
                                           exc_value) from exc_value
        finally:
            self._inside_context = False

    def get_or_create_connection(self):
        """
        If connection is not already created, creates a new Microsoft.AnalysisServices.AdomdClient.AdomdConnection object.
        Connection is opened and has token refresh callback.
        """
        if self.adomd_connection is None:
            from functools import partial
            import Microsoft.AnalysisServices
            from Microsoft.AnalysisServices.AdomdClient import AdomdConnection
            from System import Func

            self.adomd_connection = AdomdConnection(self.dax_connection_string)
            self.adomd_connection.AccessToken = refresh_tom_access_token(
                self.adomd_connection.AccessToken,
                self.credential
            )
            self.adomd_connection.OnAccessTokenExpired = Func[
                Microsoft.AnalysisServices.AccessToken,
                Microsoft.AnalysisServices.AccessToken
            ](partial(refresh_tom_access_token, creditial=self.credential))
            self.adomd_connection.Open()

        return self.adomd_connection

    def close_and_dispose_connection(self):
        """
        If a connection is cached, close and dispose of it and reset cache to None.
        """
        from System import NotSupportedException
        if self.adomd_connection is not None:
            try:
                # for some unknown reason, closing the connection throws an exception for larger datasets
                self.adomd_connection.Close()
                self.adomd_connection.Dispose()
            except NotSupportedException:
                # ignore for now, open issue we investigate
                pass

            self.adomd_connection = None
