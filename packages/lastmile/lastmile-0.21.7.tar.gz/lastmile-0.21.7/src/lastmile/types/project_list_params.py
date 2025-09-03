# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ProjectListParams", "Filters"]


class ProjectListParams(TypedDict, total=False):
    filters: Filters


class Filters(TypedDict, total=False):
    can_contribute: Annotated[bool, PropertyInfo(alias="canContribute")]
    """only return projects to which the viewer can contribute"""

    organization_id: Annotated[str, PropertyInfo(alias="organizationId")]
    """search only projects associated with specific organization"""

    query: str
    """search query substring match for name and description"""
