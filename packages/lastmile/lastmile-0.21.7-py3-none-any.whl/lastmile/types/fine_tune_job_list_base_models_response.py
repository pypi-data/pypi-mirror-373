# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "FineTuneJobListBaseModelsResponse",
    "Model",
    "ModelMetricBaseModel",
    "ModelModelCard",
    "ModelModelCardTrainingProgress",
]


class ModelMetricBaseModel(BaseModel):
    id: str

    base_model_architecture: Literal[
        "BASE_MODEL_ARCHITECTURE_UNSPECIFIED",
        "BASE_MODEL_ARCHITECTURE_ALBERTA_XS",
        "BASE_MODEL_ARCHITECTURE_ALBERTA_LC",
        "BASE_MODEL_ARCHITECTURE_DEBERTA_V3",
        "BASE_MODEL_ARCHITECTURE_ST_SIMILARITY",
        "BASE_MODEL_ARCHITECTURE_MODERNBERT_BASE",
        "BASE_MODEL_ARCHITECTURE_MODERNBERT_LARGE",
        "BASE_MODEL_ARCHITECTURE_MODERNBERT_LARGE_GNN",
    ] = FieldInfo(alias="baseModelArchitecture")
    """Keep in sync with www/prisma/schema.prisma:AEBaseModelArchitecture"""

    model_id: str = FieldInfo(alias="modelId")

    base_evaluation_metric: Optional[
        Literal[
            "BASE_EVALUATION_METRIC_UNSPECIFIED",
            "BASE_EVALUATION_METRIC_FAITHFULNESS",
            "BASE_EVALUATION_METRIC_RELEVANCE",
            "BASE_EVALUATION_METRIC_TOXICITY",
            "BASE_EVALUATION_METRIC_QA",
            "BASE_EVALUATION_METRIC_SUMMARIZATION",
        ]
    ] = FieldInfo(alias="baseEvaluationMetric", default=None)
    """Keep in sync with www/prisma/schema.prisma:AEBaseEvaluationMetric"""


class ModelModelCardTrainingProgress(BaseModel):
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


class ModelModelCard(BaseModel):
    base_model_architecture: Literal[
        "BASE_MODEL_ARCHITECTURE_UNSPECIFIED",
        "BASE_MODEL_ARCHITECTURE_ALBERTA_XS",
        "BASE_MODEL_ARCHITECTURE_ALBERTA_LC",
        "BASE_MODEL_ARCHITECTURE_DEBERTA_V3",
        "BASE_MODEL_ARCHITECTURE_ST_SIMILARITY",
        "BASE_MODEL_ARCHITECTURE_MODERNBERT_BASE",
        "BASE_MODEL_ARCHITECTURE_MODERNBERT_LARGE",
        "BASE_MODEL_ARCHITECTURE_MODERNBERT_LARGE_GNN",
    ] = FieldInfo(alias="baseModelArchitecture")
    """Keep in sync with www/prisma/schema.prisma:AEBaseModelArchitecture"""

    columns: List[str]

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    deployment_status: Literal[
        "MODEL_DEPLOYMENT_STATUS_UNSPECIFIED",
        "MODEL_DEPLOYMENT_STATUS_PENDING",
        "MODEL_DEPLOYMENT_STATUS_ONLINE",
        "MODEL_DEPLOYMENT_STATUS_OFFLINE",
        "MODEL_DEPLOYMENT_STATUS_PAUSED",
    ] = FieldInfo(alias="deploymentStatus")

    description: str

    model_id: str = FieldInfo(alias="modelId")

    model_size: int = FieldInfo(alias="modelSize")

    name: str

    purpose: str

    tags: List[str]

    training_progress: ModelModelCardTrainingProgress = FieldInfo(alias="trainingProgress")
    """Progress metrics from model training."""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    values: Dict[str, str]

    base_evaluation_metric: Optional[
        Literal[
            "BASE_EVALUATION_METRIC_UNSPECIFIED",
            "BASE_EVALUATION_METRIC_FAITHFULNESS",
            "BASE_EVALUATION_METRIC_RELEVANCE",
            "BASE_EVALUATION_METRIC_TOXICITY",
            "BASE_EVALUATION_METRIC_QA",
            "BASE_EVALUATION_METRIC_SUMMARIZATION",
        ]
    ] = FieldInfo(alias="baseEvaluationMetric", default=None)
    """Keep in sync with www/prisma/schema.prisma:AEBaseEvaluationMetric"""


class Model(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    metric_base_model: ModelMetricBaseModel = FieldInfo(alias="metricBaseModel")
    """Information about a base model corresponding to a metric"""

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    model_card: Optional[ModelModelCard] = FieldInfo(alias="modelCard", default=None)

    user_id: Optional[str] = FieldInfo(alias="userId", default=None)


class FineTuneJobListBaseModelsResponse(BaseModel):
    models: List[Model]
