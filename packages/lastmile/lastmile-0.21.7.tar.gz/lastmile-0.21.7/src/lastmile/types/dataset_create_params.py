# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DatasetCreateParams"]


class DatasetCreateParams(TypedDict, total=False):
    description: str
    """Human-readable description of the dataset, if one exists."""

    is_active_labels: Annotated[bool, PropertyInfo(alias="isActiveLabels")]

    is_few_shot_examples: Annotated[bool, PropertyInfo(alias="isFewShotExamples")]
    """PseudoLabel job fields."""

    name: str
    """Human-readable name for the dataset, if one exists."""

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """The project to add the new dataset to"""
