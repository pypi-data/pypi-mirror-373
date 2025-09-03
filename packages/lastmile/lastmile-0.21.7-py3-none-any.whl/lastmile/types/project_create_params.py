# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ProjectCreateParams"]


class ProjectCreateParams(TypedDict, total=False):
    name: Required[str]
    """Human-readable name for the project, if one exists."""

    description: str
    """Human-readable description of the project, if one exists."""

    organization_id: Annotated[str, PropertyInfo(alias="organizationId")]
    """Organization to associate the project with, if applicable"""
