# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DatasetCopyParams"]


class DatasetCopyParams(TypedDict, total=False):
    dataset_id: Required[Annotated[str, PropertyInfo(alias="datasetId")]]
    """Dataset to clone"""

    description: str
    """
    Human-readable description of the dataset. If not provided, will use the name of
    the dataset being cloned
    """

    name: str
    """New dataset name.

    If not provided, will use the name of the dataset being cloned
    """

    project_id: Annotated[str, PropertyInfo(alias="projectId")]
    """The project to add the new dataset to"""
