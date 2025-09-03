# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["ProjectDefaultParams"]


class ProjectDefaultParams(TypedDict, total=False):
    organization_id: Annotated[str, PropertyInfo(alias="organizationId")]
    """
    If provided, will get the default project for the organization Otherwise, will
    retrieve the default project for the user or organization associated with the
    api key used
    """
