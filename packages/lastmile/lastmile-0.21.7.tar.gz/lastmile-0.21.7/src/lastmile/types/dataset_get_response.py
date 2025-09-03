# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["DatasetGetResponse", "Dataset", "DatasetColumn", "DatasetLabelState"]


class DatasetColumn(BaseModel):
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


class DatasetLabelState(BaseModel):
    labeling_status: Literal[
        "JOB_STATUS_UNSPECIFIED",
        "JOB_STATUS_QUEUED",
        "JOB_STATUS_RUNNING",
        "JOB_STATUS_COMPLETED",
        "JOB_STATUS_CANCELLED",
        "JOB_STATUS_FAILED",
    ] = FieldInfo(alias="labelingStatus")
    """The status of the latest general pseudo-labeling job for the dataset"""

    prompt_template: str = FieldInfo(alias="promptTemplate")
    """aka user general instructions"""

    error: Optional[str] = None
    """if the labeling status is error, this field may contain an error message"""


class Dataset(BaseModel):
    id: str
    """The ID of the dataset."""

    columns: List[DatasetColumn]

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    initialization_status: Literal[
        "JOB_STATUS_UNSPECIFIED",
        "JOB_STATUS_QUEUED",
        "JOB_STATUS_RUNNING",
        "JOB_STATUS_COMPLETED",
        "JOB_STATUS_CANCELLED",
        "JOB_STATUS_FAILED",
    ] = FieldInfo(alias="initializationStatus")

    num_cols: int = FieldInfo(alias="numCols")

    num_rows: int = FieldInfo(alias="numRows")

    owner_user_id: str = FieldInfo(alias="ownerUserId")
    """The ID of the user who owns the dataset."""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    description: Optional[str] = None
    """Human-readable description of the dataset, if one exists."""

    initialization_error: Optional[str] = FieldInfo(alias="initializationError", default=None)

    label_state: Optional[DatasetLabelState] = FieldInfo(alias="labelState", default=None)
    """The state of the latest labeling job for the dataset"""

    name: Optional[str] = None
    """Human-readable name for the dataset, if one exists."""


class DatasetGetResponse(BaseModel):
    dataset: Dataset
    """
    A Dataset in the most basic sense: metadata and ownership, but nothing tied to
    its data.
    """
