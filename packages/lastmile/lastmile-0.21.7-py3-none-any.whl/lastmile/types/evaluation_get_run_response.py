# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional
from datetime import datetime
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = [
    "EvaluationGetRunResponse",
    "EvaluationRun",
    "EvaluationRunAggregateMetric",
    "EvaluationRunAggregateMetricMetric",
    "EvaluationRunMetadata",
]


class EvaluationRunAggregateMetricMetric(BaseModel):
    id: Optional[str] = None

    deployment_status: Optional[
        Literal[
            "MODEL_DEPLOYMENT_STATUS_UNSPECIFIED",
            "MODEL_DEPLOYMENT_STATUS_PENDING",
            "MODEL_DEPLOYMENT_STATUS_ONLINE",
            "MODEL_DEPLOYMENT_STATUS_OFFLINE",
            "MODEL_DEPLOYMENT_STATUS_PAUSED",
        ]
    ] = FieldInfo(alias="deploymentStatus", default=None)

    description: Optional[str] = None

    name: Optional[str] = None


class EvaluationRunAggregateMetric(BaseModel):
    aggregate_method: Literal[
        "METRIC_AGGREGATE_METHOD_UNSPECIFIED", "METRIC_AGGREGATE_METHOD_SUM", "METRIC_AGGREGATE_METHOD_AVG"
    ] = FieldInfo(alias="aggregateMethod")

    metric: EvaluationRunAggregateMetricMetric

    score: float


class EvaluationRunMetadata(BaseModel):
    fields: Dict[str, Dict[str, object]]


class EvaluationRun(BaseModel):
    id: str

    aggregate_metrics: List[EvaluationRunAggregateMetric] = FieldInfo(alias="aggregateMetrics")

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    name: str

    num_rows: int = FieldInfo(alias="numRows")

    project_id: str = FieldInfo(alias="projectId")

    run_type: Literal[
        "EVALUATION_RUN_TYPE_UNSPECIFIED", "EVALUATION_RUN_TYPE_ADHOC", "EVALUATION_RUN_TYPE_EXPERIMENT"
    ] = FieldInfo(alias="runType")

    creator_id: Optional[str] = FieldInfo(alias="creatorId", default=None)

    experiment_id: Optional[str] = FieldInfo(alias="experimentId", default=None)

    experiment_name: Optional[str] = FieldInfo(alias="experimentName", default=None)

    metadata: Optional[EvaluationRunMetadata] = None

    result_dataset_id: Optional[str] = FieldInfo(alias="resultDatasetId", default=None)

    source_dataset_id: Optional[str] = FieldInfo(alias="sourceDatasetId", default=None)


class EvaluationGetRunResponse(BaseModel):
    evaluation_run: EvaluationRun = FieldInfo(alias="evaluationRun")
