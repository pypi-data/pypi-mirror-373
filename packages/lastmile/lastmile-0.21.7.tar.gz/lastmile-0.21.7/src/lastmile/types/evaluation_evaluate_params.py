# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict, List
from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluationEvaluateParams", "Metric", "Metadata"]


class EvaluationEvaluateParams(TypedDict, total=False):
    ground_truth: Required[Annotated[List[str], PropertyInfo(alias="groundTruth")]]

    input: Required[List[str]]

    metric: Required[Metric]

    output: Required[List[str]]

    metadata: Metadata
    """
    Common metadata relevant to the application configuration from which all request
    inputs were derived. E.g. 'llm_model', 'chunk_size'
    """

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """The project where evaluation inference logs will be stored"""


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
