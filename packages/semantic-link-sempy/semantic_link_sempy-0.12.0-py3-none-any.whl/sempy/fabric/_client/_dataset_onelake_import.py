import pandas as pd
from uuid import UUID

from sempy.fabric._credentials import get_access_token, set_default_credential
from sempy.fabric._client._base_dataset_client import BaseDatasetClient
from sempy.fabric._environment import _get_onelake_abfss_path
from sempy.fabric._utils import SparkConfigTemporarily

from typing import Optional, Union, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from azure.core.credentials import TokenCredential
    from sempy.fabric._client import WorkspaceClient


def _convert_pandas_datetime64_unit(df, unit: str = "ns"):
    for col in df.select_dtypes(include=["datetime64"]).columns:
        df[col] = df[col].astype(f"datetime64[{unit}]")
    return df


class DatasetOneLakeImportClient(BaseDatasetClient):
    """
    Import exported semantic models from onelake.

    See `onelake integration <https://learn.microsoft.com/en-us/power-bi/enterprise/onelake-integration-overview>`_
    """
    def __init__(
            self,
            workspace: Union[str, "WorkspaceClient"],
            dataset: Union[str, UUID],
            credential: Optional["TokenCredential"] = None
    ):
        BaseDatasetClient.__init__(self, workspace, dataset, credential)

        self._import_method: Literal["spark", "pandas"] = "spark"

    def _set_import_method(self, method: Literal["spark", "pandas"] = "spark"):
        self._import_method = method

    def _get_pandas_table(self, table_name, num_rows, verbose):
        if self._import_method not in ["spark", "pandas"]:
            raise ValueError(f"Unsupported import method '{self._import_method}'")

        workspace_id = self.resolver.workspace_id
        dataset_id = self.resolver.dataset_id

        url = f"{_get_onelake_abfss_path(workspace_id=workspace_id, dataset_id=dataset_id)}/Tables/{table_name}"
        if self._import_method == "pandas":
            df = self._get_pandas_table_delta(url, num_rows)
        else:
            df = self._get_pandas_table_spark(url, num_rows)

        # convert all datetime64 columns to [ns] to ensure compatibility with PowerBI's native reading behavior.
        return _convert_pandas_datetime64_unit(df, unit="ns")

    def _get_pandas_table_spark(self, url, num_rows) -> pd.DataFrame:
        from pyspark.sql import SparkSession

        spark = SparkSession.builder.getOrCreate()

        # the Spark config is only relevant at toPandas(), but to be avoid any future mistakes, let's wrap the whole.
        with SparkConfigTemporarily(spark, {
            "spark.sql.parquet.datetimeRebaseModeInRead": "CORRECTED"
        }):
            df = spark.read.format("delta").load(url)

            if num_rows is not None:
                df = df.limit(num_rows)

            # PowerBI datasets frequently have old dates.
            return df.toPandas()

    def _get_pandas_table_delta(self, url, num_rows) -> pd.DataFrame:
        # Currently pandas cannot resolve the metadata of exported onelake
        # table correctly, we may need to populate the dataframe with correct
        # column names
        table_name = url.split("/")[-1]
        database = self.resolver.workspace_client.get_dataset(self.resolver.dataset_name)
        for table in database.Model.Tables:
            if table.Name != table_name:
                continue

            # Get column names from TOM server metadata, and remove the column
            # of row number
            col_names = [col.Name for col in table.Columns][1:]

            with set_default_credential(self.credential):
                from fabric.analytics.environment.constant import STORAGE_SCOPE
                df = pd.read_parquet(url, storage_options={
                    "sas_token": get_access_token(STORAGE_SCOPE)
                })

            # Remapping column names
            df = df.rename(columns={
                k: v for k, v in zip(df.columns, col_names)
            }, errors="raise")

            if num_rows is not None:
                # Partial loading using `num_rows` is not fully supported with
                # pandas API.
                #
                # There's an issue https://github.com/pandas-dev/pandas/issues/51830.
                # tracking this and it may get resolved in the future.
                #
                # For now, we just return the first `num_rows` rows to the user
                # to maintain the consistency with other modes
                df = df.head(num_rows)

            return df

        raise ValueError(f"Cannot find table {table_name} from PowerBI")
