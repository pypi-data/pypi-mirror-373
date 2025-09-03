# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from datetime import datetime

from pydantic import Field as FieldInfo

from .._models import BaseModel

__all__ = ["ProjectGetResponse", "Project"]


class Project(BaseModel):
    id: str

    created_at: datetime = FieldInfo(alias="createdAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    name: str

    updated_at: datetime = FieldInfo(alias="updatedAt")
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    creator_id: Optional[str] = FieldInfo(alias="creatorId", default=None)

    deleted_at: Optional[datetime] = FieldInfo(alias="deletedAt", default=None)
    """
    A summary is retrieved for a time range from start_time to end_time If no
    end_time is provided, current time is used
    """

    description: Optional[str] = None

    organization_id: Optional[str] = FieldInfo(alias="organizationId", default=None)

    organization_name: Optional[str] = FieldInfo(alias="organizationName", default=None)


class ProjectGetResponse(BaseModel):
    project: Project
