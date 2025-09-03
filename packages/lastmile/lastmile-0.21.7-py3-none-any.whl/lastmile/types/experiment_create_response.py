# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ExperimentCreateResponse", "Experiment", "ExperimentMetadata"]


class ExperimentMetadata(BaseModel):
    fields: Dict[str, Dict[str, object]]


class Experiment(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    name: str

    project_id: str = FieldInfo(alias="projectId")

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    creator_id: Optional[str] = FieldInfo(alias="creatorId", default=None)

    description: Optional[str] = None

    metadata: Optional[ExperimentMetadata] = None


class ExperimentCreateResponse(BaseModel):
    experiment: Experiment
