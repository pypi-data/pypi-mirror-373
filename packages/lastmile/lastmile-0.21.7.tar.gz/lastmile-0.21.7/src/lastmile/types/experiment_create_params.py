# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Dict
from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ExperimentCreateParams", "Metadata"]


class ExperimentCreateParams(TypedDict, total=False):
    name: Required[str]
    """Human-readable name for the experiment"""

    project_id: Required[Annotated[str, PropertyInfo(alias="projectId")]]
    """Project the experiment is associated with"""

    description: str
    """Succint description of the experiment, if one exists."""

    metadata: Metadata
    """
    Metadata relevant to the application configuration from which all experiment
    evaluation runs are derived. E.g. 'llm_model', 'chunk_size'
    """


class Metadata(TypedDict, total=False):
    fields: Required[Dict[str, Dict[str, object]]]
