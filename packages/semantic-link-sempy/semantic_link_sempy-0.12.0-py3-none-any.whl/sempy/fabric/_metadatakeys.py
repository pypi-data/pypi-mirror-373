
class MetadataKeys:
    """
    Keys for column metadata in :class:`~sempy.fabric.FabricDataFrame`.

    Column properties can be found `here <https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.column?view=analysisservices-dotnet#properties>`_.
    """

    ALIGNMENT = "alignment"

    COLUMN = "column"

    # https://learn.microsoft.com/en-us/dotnet/api/microsoft.analysisservices.tabular.annotation?view=analysisservices-dotnet
    COLUMN_ANNOTATIONS = "column_annotations"

    DATA_CATEGORY = "data_category"

    DATASET = "dataset"

    DATA_TYPE = "data_type"

    DESCRIPTION = "description"

    ERROR_MESSAGE = "error_message"

    FORMAT_STRING = "format_string"

    IS_HIDDEN = "is_hidden"

    IS_KEY = "is_key"

    IS_NULLABLE = "is_nullable"

    IS_REMOVED = "is_removed"

    IS_UNIQUE = "is_unique"

    LINEAGE_TAG = "lineage_tag"

    MODIFIED_TIME = "modified_time"

    REFRESHED_TIME = "refreshed_time"

    RELATIONSHIP = "relationship"

    SORT_BY_COLUMN = "sort_by_column"

    SOURCE_LINEAGE_TAG = "source_lineage_tag"

    SUMMARIZE_BY = "summarize_by"

    TABLE = "table"

    TABLE_ANNOTATIONS = "table_annotations"

    WORKSPACE_ID = "workspace_id"

    WORKSPACE_NAME = "workspace_name"
