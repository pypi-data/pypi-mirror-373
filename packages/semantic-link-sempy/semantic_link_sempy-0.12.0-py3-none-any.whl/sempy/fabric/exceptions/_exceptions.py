import requests


class SemPyException(Exception):
    """
    Base class for other exceptions.
    """
    pass


class FabricHTTPException(SemPyException, requests.HTTPError):
    """
    Raised when an API call to any Fabric REST API fails with status code >= 400.

    Parameters
    ----------
    response : requests.Response
        Response object returned from API call (see `requests.Response <https://requests.readthedocs.io/en/latest/api/#requests.Response>`_).
    """
    def __init__(self, response: requests.Response):
        self.error_reason: str
        # The following section is copied from response.raise_for_status()
        # ----------------------------------------------------------------
        if isinstance(response.reason, bytes):
            # We attempt to decode utf-8 first because some servers
            # choose to localize their reason strings. If the string
            # isn't utf-8, we fall back to iso-8859-1 for all other
            # encodings. (See PR #3538)
            try:
                self.error_reason = response.reason.decode("utf-8")
            except UnicodeDecodeError:
                self.error_reason = response.reason.decode("iso-8859-1")
        else:
            self.error_reason = response.reason
        # -----------------------------------------------------------------

        self.error_text = f"\nError: {response.text}" if response.text else ""
        self.status_code = response.status_code

        if response.headers:
            self.error_text += f"\nHeaders: {response.headers}"

        # Surface important details from the response into the message text:
        msg = f"{self.status_code} {self.error_reason} for url: {response.url}{self.error_text}"

        requests.HTTPError.__init__(self, msg, response=response)  # type: ignore


class DatasetNotFoundException(SemPyException):
    """
    Raised when specified dataset (name or UUID) is not found in workspace.

    Parameters
    ----------
    dataset : str
        Dataset name or id.
    workspace_name : str
        Workspace name.
    """
    def __init__(self, dataset: str, workspace_name: str):
        self.dataset = dataset
        self.workspace_name = workspace_name
        msg = f"Dataset '{dataset}' not found in workspace '{workspace_name}'"
        super().__init__(msg)


class WorkspaceNotFoundException(SemPyException):
    """
    Raised when specified workspace (name or UUID) is not found.

    Parameters
    ----------
    workspace : str
        Workspace name or id.
    """
    def __init__(self, workspace: str):
        self.workspace = workspace
        msg = f"Workspace '{workspace}' not found"
        super().__init__(msg)


class FolderNotFoundException(SemPyException, OSError):
    """
    Raised when specified folder (name or UUID) is not found.

    Parameters
    ----------
    folder : str
        Folder name or id.
    workspace : str
        Workspace name or id.
    """
    def __init__(self, folder: str, workspace: str):
        self.folder = folder
        msg = f"Folder path or ID '{folder}' not found in workspace: '{workspace}'"
        super().__init__(msg)
