# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ExperimentListParams", "Filters"]


class ExperimentListParams(TypedDict, total=False):
    filters: Filters

    page_index: Annotated[int, PropertyInfo(alias="pageIndex")]

    page_size: Annotated[int, PropertyInfo(alias="pageSize")]


class Filters(TypedDict, total=False):
    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """search only experiments associated with specific project"""

    query: str
    """search query substring match for name and description"""
