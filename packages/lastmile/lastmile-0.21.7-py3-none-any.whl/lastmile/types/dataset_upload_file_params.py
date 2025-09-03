# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, Annotated, TypedDict

from .._utils import PropertyInfo

__all__ = ["DatasetUploadFileParams"]


class DatasetUploadFileParams(TypedDict, total=False):
    dataset_id: Required[Annotated[str, PropertyInfo(alias="datasetId")]]
    """The ID of the dataset corresponding to the file."""
