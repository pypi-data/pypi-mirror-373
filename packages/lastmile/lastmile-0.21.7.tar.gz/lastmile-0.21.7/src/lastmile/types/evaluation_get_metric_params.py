# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["EvaluationGetMetricParams", "Metric"]


class EvaluationGetMetricParams(TypedDict, total=False):
    metric: Required[Metric]


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
