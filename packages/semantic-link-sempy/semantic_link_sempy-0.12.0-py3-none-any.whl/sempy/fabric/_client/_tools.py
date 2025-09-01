import os
from azure.core.credentials import AccessToken
from azure.storage.blob import BlobServiceClient
from azure.storage.filedatalake import DataLakeServiceClient
from typing import List, Optional, Union
from uuid import UUID
import tqdm

from sempy.fabric._client._pbi_rest_api import _PBIRestAPI
from sempy._utils._log import log
import sempy.fabric as fabric


def _download_pbix(dataset,
                   storage_account="https://mmlspark.blob.core.windows.net/",
                   container="publicwasb") -> bytes:
    service = BlobServiceClient(account_url=storage_account, credential=None)

    # download azure blob using blob service client in service
    blob_client = service.get_blob_client(container, blob=f"SemPy/pbi_data/{dataset}.pbix")
    return blob_client.download_blob().readall()


@log
def import_pbix_sample(datasets: Union[str, List[str]],
                       workspace: Optional[Union[str, UUID]] = None,
                       overwrite: Optional[bool] = False,
                       skip_report: Optional[bool] = True):
    """
    Import .pbix file to the workspace.

    Parameters
    ----------
    datasets : str or list of str
        Name(s) of the dataset(s).
    workspace_id : str
        PowerBI Workspace Name or UUID object containing the workspace ID.
    overwrite : bool, default=False
        Whether to overwrite existing dataset.
    skip_report : bool, default=True
        Whether to skip report import.
    """
    if isinstance(datasets, str):
        datasets = [datasets]

    workspace_id = fabric.resolve_workspace_id(workspace)
    workspace_name = fabric.resolve_workspace_name(workspace)

    rest = _PBIRestAPI()
    existing_datasets = rest.get_workspace_datasets(workspace_name, workspace_id)
    existing_dataset_names = [row["name"] for row in existing_datasets]

    for dataset_name in (pbar := tqdm.tqdm(datasets)):
        # check if dataset w/o extension is already exists
        if overwrite or dataset_name not in existing_dataset_names:
            pbar.set_description(f"Uploading Power BI semantic model '{dataset_name}'")
            rest.upload_pbix(dataset_name, _download_pbix(dataset_name), workspace_id, workspace, skip_report)
        else:
            pbar.set_description(f"Power BI semantic model '{dataset_name}' already exists, skipping")


def create_lakehouse_if_not_exists(workspace_id, lakehouse_name, folder_id: Optional[str] = None) -> str:
    df = fabric.list_items("Lakehouse", workspace_id, root_folder=folder_id)
    ids = df[df["Display Name"] == lakehouse_name]["Id"].values

    if len(ids) == 0:
        print(f"Creating lakehouse {lakehouse_name}")
        from sempy.fabric._cache import _get_or_create_workspace_client
        return _get_or_create_workspace_client(workspace_id) \
            .create_lakehouse(lakehouse_name, folder_id=folder_id)
    else:
        return ids[0]


def upload_to_lakehouse(dir_or_file, workspace_id, lakehouse_id, onelake_url, bearer_token, date=""):

    class AADCredential:
        def __init__(self, token, **kwargs):
            self.token = token

        def get_token(self, *scopes, **kwargs):
            return self.token

    t = AccessToken(token=bearer_token, expires_on=1684934721)
    service = DataLakeServiceClient(account_url=f"https://{onelake_url}", credential=AADCredential(token=t))

    # Get file system client (workspace)
    file_system_client = service.get_file_system_client(workspace_id)

    def upload_file_dfs(file_path, date):
        with open(file_path, "rb") as data:
            file_content = data.read()
            file_name = f'{lakehouse_id}/Files/{date}/{file_path}' if date else f'{lakehouse_id}/Files/{file_path}'
            file_client = file_system_client.get_file_client(file_name)

            if len(file_content) == 0:
                # For empty files, create the file directly
                file_client.create_file()
            else:
                # For non-empty files, upload the data
                file_client.upload_data(file_content, overwrite=True)

    if os.path.isfile(dir_or_file):
        upload_file_dfs(dir_or_file, date)
    else:
        for path, _, files in os.walk(dir_or_file):
            # Process all files, including empty ones
            for file in files:
                file_path = os.path.join(path, file)
                upload_file_dfs(file_path, date)
