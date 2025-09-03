# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["FineTuneJobSubmitParams", "FineTuneJobConfig"]


class FineTuneJobSubmitParams(TypedDict, total=False):
    fine_tune_job_config: Required[Annotated[FineTuneJobConfig, PropertyInfo(alias="fineTuneJobConfig")]]
    """The fine-tune job configuration."""

    job_id: Required[Annotated[str, PropertyInfo(alias="jobId")]]


class FineTuneJobConfig(TypedDict, total=False):
    baseline_model_id: Required[Annotated[str, PropertyInfo(alias="baselineModelId")]]
    """The ID for the model used as the starting point for training."""

    selected_columns: Required[Annotated[List[str], PropertyInfo(alias="selectedColumns")]]

    test_dataset_id: Required[Annotated[str, PropertyInfo(alias="testDatasetId")]]
    """The dataset to use for an unbiased evaluation of the model"""

    train_dataset_id: Required[Annotated[str, PropertyInfo(alias="trainDatasetId")]]
    """
    The dataset to use for training, with splits baked in or to be derived
    dynamically
    """

    description: str
    """Optional description for the job."""

    name: str
    """Optional name for the job."""
