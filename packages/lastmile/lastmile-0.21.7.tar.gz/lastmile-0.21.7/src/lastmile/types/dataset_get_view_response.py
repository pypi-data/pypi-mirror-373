# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DatasetGetViewResponse", "DatasetView", "DatasetViewColumn", "DatasetViewData"]


class DatasetViewColumn(BaseModel):
    id: str
    """The ID of the dataset file."""

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    index: int
    """Index of the column within the dataset file."""

    literal_name: str = FieldInfo(alias="literalName")
    """The literal name for the column."""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    dtype: Optional[
        Literal[
            "DATASET_COLUMN_D_TYPE_UNSPECIFIED",
            "DATASET_COLUMN_D_TYPE_INT32",
            "DATASET_COLUMN_D_TYPE_INT64",
            "DATASET_COLUMN_D_TYPE_FLOAT32",
            "DATASET_COLUMN_D_TYPE_FLOAT64",
            "DATASET_COLUMN_D_TYPE_STRING",
            "DATASET_COLUMN_D_TYPE_BYTES",
            "DATASET_COLUMN_D_TYPE_ANY",
            "DATASET_COLUMN_D_TYPE_LIST_OF_STRINGS",
            "DATASET_COLUMN_D_TYPE_BOOLEAN",
        ]
    ] = None
    """Datatypes for a column in a dataset file.

    We likely don't need everything here, but it's good to be explicit, for example
    to avoid unknowingly coercing int64 values into int32. Encoding for text is
    UTF_8 unless indicated otherwise.
    """


class DatasetViewData(BaseModel):
    id: str

    row_values: List[Dict[str, object]] = FieldInfo(alias="rowValues")


class DatasetView(BaseModel):
    columns: List[DatasetViewColumn]

    data: List[DatasetViewData]

    num_cols: int = FieldInfo(alias="numCols")

    num_rows: int = FieldInfo(alias="numRows")


class DatasetGetViewResponse(BaseModel):
    dataset_file_id: str = FieldInfo(alias="datasetFileId")

    dataset_id: str = FieldInfo(alias="datasetId")

    dataset_version_key: str = FieldInfo(alias="datasetVersionKey")
    """dataset version key"""

    dataset_view: DatasetView = FieldInfo(alias="datasetView")

    next_page_cursor: Optional[str] = FieldInfo(alias="nextPageCursor", default=None)
    """A cursor for the next page in the pagination, if one exists."""

    previous_page_cursor: Optional[str] = FieldInfo(alias="previousPageCursor", default=None)
    """A cursor for the previous page in the pagination, if one exists."""
