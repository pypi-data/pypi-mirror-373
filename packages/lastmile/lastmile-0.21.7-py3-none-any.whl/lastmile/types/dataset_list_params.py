# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DatasetListParams", "Filters"]


class DatasetListParams(TypedDict, total=False):
    filters: Filters
    """Filter listed datasets by ALL filters specified"""


class Filters(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """filter datasets associated with the project"""

    query: str
    """search query substring match for name and description"""
