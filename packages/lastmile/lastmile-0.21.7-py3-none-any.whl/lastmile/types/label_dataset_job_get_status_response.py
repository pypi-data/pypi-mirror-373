# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["LabelDatasetJobGetStatusResponse", "PseudoLabelJobResult", "PseudoLabelJobResultPromptTemplate"]


class PseudoLabelJobResultPromptTemplate(BaseModel):
    id: str

    template: str
    """The template string that defines the prompt"""


class PseudoLabelJobResult(BaseModel):
    base_evaluation_metric: Literal[
        "BASE_EVALUATION_METRIC_UNSPECIFIED",
        "BASE_EVALUATION_METRIC_FAITHFULNESS",
        "BASE_EVALUATION_METRIC_RELEVANCE",
        "BASE_EVALUATION_METRIC_TOXICITY",
        "BASE_EVALUATION_METRIC_QA",
        "BASE_EVALUATION_METRIC_SUMMARIZATION",
    ] = FieldInfo(alias="baseEvaluationMetric")
    """Reserved field. Do not use at the moment."""

    dataset_id: str = FieldInfo(alias="datasetId")
    """ID of the main dataset to be pseudo-labeled"""

    prompt_template: PseudoLabelJobResultPromptTemplate = FieldInfo(alias="promptTemplate")

    selected_columns: List[str] = FieldInfo(alias="selectedColumns")

    skip_active_labeling: bool = FieldInfo(alias="skipActiveLabeling")
    """
    If true, skip active labeling, which involves an intermediate Dataset created
    for human labeling.
    """

    active_labeled_dataset_id: Optional[str] = FieldInfo(alias="activeLabeledDatasetId", default=None)
    """ID of the actively labeled dataset.

    Optional. If null, this job is for active learning.
    """

    description: Optional[str] = None
    """Optional description for the job."""

    few_shot_dataset_id: Optional[str] = FieldInfo(alias="fewShotDatasetId", default=None)
    """ID of the dataset containing few-shot examples. Optional."""

    name: Optional[str] = None
    """Optional name for the job."""


class LabelDatasetJobGetStatusResponse(BaseModel):
    pseudo_label_job_result: PseudoLabelJobResult = FieldInfo(alias="pseudoLabelJobResult")
    """Configuration for LLM Judge labeling job."""

    status: Literal[
        "JOB_STATUS_UNSPECIFIED",
        "JOB_STATUS_QUEUED",
        "JOB_STATUS_RUNNING",
        "JOB_STATUS_COMPLETED",
        "JOB_STATUS_CANCELLED",
        "JOB_STATUS_FAILED",
    ]
