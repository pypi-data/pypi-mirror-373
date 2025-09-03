# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["EvaluationEvaluateResponse", "Metric"]


class Metric(BaseModel):
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


class EvaluationEvaluateResponse(BaseModel):
    metric: Metric

    scores: List[float]
