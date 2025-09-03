# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["FineTuneJobListResponse", "Job", "JobConfig", "JobResult", "JobResultProgress", "JobResultTrainedModelFile"]


class JobConfig(BaseModel):
    baseline_model_id: str = FieldInfo(alias="baselineModelId")
    """The ID for the model used as the starting point for training."""

    selected_columns: List[str] = FieldInfo(alias="selectedColumns")

    test_dataset_id: str = FieldInfo(alias="testDatasetId")
    """The dataset to use for an unbiased evaluation of the model"""

    train_dataset_id: str = FieldInfo(alias="trainDatasetId")
    """
    The dataset to use for training, with splits baked in or to be derived
    dynamically
    """

    description: Optional[str] = None
    """Optional description for the job."""

    name: Optional[str] = None
    """Optional name for the job."""


class JobResultProgress(BaseModel):
    accuracy: float

    epoch: int

    job_id: str = FieldInfo(alias="jobId")

    loss: float

    progress: float

    timestamp: datetime
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """


class JobResultTrainedModelFile(BaseModel):
    id: str

    content_md5_hash: str = FieldInfo(alias="contentMd5Hash")

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    file_size_bytes: int = FieldInfo(alias="fileSizeBytes")

    model_id: str = FieldInfo(alias="modelId")

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """


class JobResult(BaseModel):
    progress: List[JobResultProgress]

    result_url: Optional[str] = FieldInfo(alias="resultUrl", default=None)
    """Url to view the full results and progress (e.g. external W&B url)"""

    trained_model_file: Optional[JobResultTrainedModelFile] = FieldInfo(alias="trainedModelFile", default=None)
    """The trained model, if it was created successfully."""


class Job(BaseModel):
    id: str
    """The ID of the fine tune job."""

    config: JobConfig

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    result: JobResult
    """Result of a Fine-Tuning Job."""

    status: Literal[
        "JOB_STATUS_UNSPECIFIED",
        "JOB_STATUS_QUEUED",
        "JOB_STATUS_RUNNING",
        "JOB_STATUS_COMPLETED",
        "JOB_STATUS_CANCELLED",
        "JOB_STATUS_FAILED",
    ]

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    description: Optional[str] = None

    name: Optional[str] = None
    """Name corresponding to the fine tuned model derived from this job"""


class FineTuneJobListResponse(BaseModel):
    jobs: List[Job]

    total_count: int = FieldInfo(alias="totalCount")
    """
    Total count of fine tune jobs which can be listed with applicable filters,
    regardless of page size
    """
