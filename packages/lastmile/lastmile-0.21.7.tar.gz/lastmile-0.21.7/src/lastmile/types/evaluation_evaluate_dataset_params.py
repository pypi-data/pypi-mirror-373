# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, Iterable
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluationEvaluateDatasetParams", "Metric", "Metadata"]


class EvaluationEvaluateDatasetParams(TypedDict, total=False):
    dataset_id: Required[Annotated[str, PropertyInfo(alias="datasetId")]]
    """The dataset to evaluate"""

    metrics: Required[Iterable[Metric]]

    experiment_id: Annotated[str, PropertyInfo(alias="experimentId")]
    """If specified, the evaluation run will be associated with this experiment"""

    metadata: Metadata
    """
    Common metadata relevant to the application configuration from which all request
    inputs were derived. E.g. 'llm_model', 'chunk_size'
    """

    metric: Metric
    """The metric to compute for the dataset.

    Use if only a single metric is required. For multiple metrics, use 'metrics'.
    """

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """The project where the evaluation run will be persisted"""


class Metric(TypedDict, total=False):
    id: str

    deployment_status: Annotated[
        Literal[
            "MODEL_DEPLOYMENT_STATUS_UNSPECIFIED",
            "MODEL_DEPLOYMENT_STATUS_PENDING",
            "MODEL_DEPLOYMENT_STATUS_ONLINE",
            "MODEL_DEPLOYMENT_STATUS_OFFLINE",
            "MODEL_DEPLOYMENT_STATUS_PAUSED",
        ],
        PropertyInfo(alias="deploymentStatus"),
    ]

    description: str

    name: str


class Metadata(TypedDict, total=False):
    fields: Required[Dict[str, Dict[str, object]]]
