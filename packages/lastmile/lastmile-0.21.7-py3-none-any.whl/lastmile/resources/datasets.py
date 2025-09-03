# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable

import httpx

from ..types import (
    dataset_get_params,
    dataset_copy_params,
    dataset_list_params,
    dataset_create_params,
    dataset_delete_params,
    dataset_get_view_params,
    dataset_upload_file_params,
    dataset_get_download_url_params,
    dataset_finalize_file_upload_params,
)
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.dataset_get_response import DatasetGetResponse
from ..types.dataset_copy_response import DatasetCopyResponse
from ..types.dataset_list_response import DatasetListResponse
from ..types.dataset_create_response import DatasetCreateResponse
from ..types.dataset_delete_response import DatasetDeleteResponse
from ..types.dataset_get_view_response import DatasetGetViewResponse
from ..types.dataset_upload_file_response import DatasetUploadFileResponse
from ..types.dataset_get_download_url_response import DatasetGetDownloadURLResponse
from ..types.dataset_finalize_file_upload_response import DatasetFinalizeFileUploadResponse

__all__ = ["DatasetsResource", "AsyncDatasetsResource"]


class DatasetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DatasetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#accessing-raw-response-data-eg-headers
        """
        return DatasetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DatasetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#with_streaming_response
        """
        return DatasetsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        description: str | NotGiven = NOT_GIVEN,
        is_active_labels: bool | NotGiven = NOT_GIVEN,
        is_few_shot_examples: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetCreateResponse:
        """Create a new Dataset.

        Use UploadDatasetFile to upload files to the dataset.

        Args:
          description: Human-readable description of the dataset, if one exists.

          is_few_shot_examples: PseudoLabel job fields.

          name: Human-readable name for the dataset, if one exists.

          project_id: The project to add the new dataset to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/create",
            body=maybe_transform(
                {
                    "description": description,
                    "is_active_labels": is_active_labels,
                    "is_few_shot_examples": is_few_shot_examples,
                    "name": name,
                    "project_id": project_id,
                },
                dataset_create_params.DatasetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetCreateResponse,
        )

    def list(
        self,
        *,
        filters: dataset_list_params.Filters | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetListResponse:
        """
        List Datasets.

        Args:
          filters: Filter listed datasets by ALL filters specified

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/list",
            body=maybe_transform({"filters": filters}, dataset_list_params.DatasetListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetListResponse,
        )

    def delete(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetDeleteResponse:
        """
        Archive a dataset

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/archive",
            body=maybe_transform({"id": id}, dataset_delete_params.DatasetDeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetDeleteResponse,
        )

    def copy(
        self,
        *,
        dataset_id: str,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetCopyResponse:
        """
        Clone a dataset into a new dataset containing the latest file contents

        Args:
          dataset_id: Dataset to clone

          description: Human-readable description of the dataset. If not provided, will use the name of
              the dataset being cloned

          name: New dataset name. If not provided, will use the name of the dataset being cloned

          project_id: The project to add the new dataset to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/clone",
            body=maybe_transform(
                {
                    "dataset_id": dataset_id,
                    "description": description,
                    "name": name,
                    "project_id": project_id,
                },
                dataset_copy_params.DatasetCopyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetCopyResponse,
        )

    def finalize_file_upload(
        self,
        *,
        dataset_id: str,
        s3_presigned_post: dataset_finalize_file_upload_params.S3PresignedPost,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetFinalizeFileUploadResponse:
        """Finalize a Dataset file upload.

        This call should be made after the file has been
        uploaded to the S3 URL returned from UploadDatasetFile.

        Args:
          dataset_id: The ID of the dataset corresponding to the file

          s3_presigned_post: The pre-signed S3 URL where the file was uploadeded

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/finalize_single_file_upload",
            body=maybe_transform(
                {
                    "dataset_id": dataset_id,
                    "s3_presigned_post": s3_presigned_post,
                },
                dataset_finalize_file_upload_params.DatasetFinalizeFileUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetFinalizeFileUploadResponse,
        )

    def get(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetGetResponse:
        """
        Get a Dataset.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/get",
            body=maybe_transform({"id": id}, dataset_get_params.DatasetGetParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetGetResponse,
        )

    def get_download_url(
        self,
        *,
        dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetGetDownloadURLResponse:
        """
        Get a download url for a Dataset.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/get_download_url",
            body=maybe_transform(
                {"dataset_id": dataset_id}, dataset_get_download_url_params.DatasetGetDownloadURLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetGetDownloadURLResponse,
        )

    def get_view(
        self,
        *,
        dataset_file_id: str,
        dataset_id: str,
        filters: Iterable[dataset_get_view_params.Filter],
        after: int | NotGiven = NOT_GIVEN,
        get_last_page: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        next_page_cursor: str | NotGiven = NOT_GIVEN,
        order_by: str | NotGiven = NOT_GIVEN,
        order_direction: str | NotGiven = NOT_GIVEN,
        previous_page_cursor: str | NotGiven = NOT_GIVEN,
        use_datasets_service: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetGetViewResponse:
        """
        Get a paginated view of the data within a Dataset.

        Args:
          dataset_file_id: The ID of the (pinned) dataset file from which to retrieve content. Requests
              iterating over pages of results are recommended to use this pinned identifier
              after the first page in order to prevent any effects from a dataset changing
              between the queries.

          dataset_id: The ID of the dataset from which to retrieve content. When specified, gets data
              from the current file in the dataset.

          after: Pagination: The index, by row-order, after which to query results.

          limit: Pagination: The maximum number of results to return on this page.

          next_page_cursor: A cursor for the next page in the pagination, if one exists.

          order_by: Column to order results by

          order_direction: Direction to order results ("asc" or "desc")

          previous_page_cursor: A cursor for the previous page in the pagination, if one exists.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/get_view",
            body=maybe_transform(
                {
                    "dataset_file_id": dataset_file_id,
                    "dataset_id": dataset_id,
                    "filters": filters,
                    "after": after,
                    "get_last_page": get_last_page,
                    "limit": limit,
                    "next_page_cursor": next_page_cursor,
                    "order_by": order_by,
                    "order_direction": order_direction,
                    "previous_page_cursor": previous_page_cursor,
                    "use_datasets_service": use_datasets_service,
                },
                dataset_get_view_params.DatasetGetViewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetGetViewResponse,
        )

    def upload_file(
        self,
        *,
        dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetUploadFileResponse:
        """Initiate a file upload to a Dataset.

        Call FinalizeSingleDatasetFileUpload to
        complete the upload with the presigned URL returned from this call.

        Args:
          dataset_id: The ID of the dataset corresponding to the file.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/dataset/upload_file",
            body=maybe_transform({"dataset_id": dataset_id}, dataset_upload_file_params.DatasetUploadFileParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetUploadFileResponse,
        )


class AsyncDatasetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDatasetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#accessing-raw-response-data-eg-headers
        """
        return AsyncDatasetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDatasetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#with_streaming_response
        """
        return AsyncDatasetsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        description: str | NotGiven = NOT_GIVEN,
        is_active_labels: bool | NotGiven = NOT_GIVEN,
        is_few_shot_examples: bool | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetCreateResponse:
        """Create a new Dataset.

        Use UploadDatasetFile to upload files to the dataset.

        Args:
          description: Human-readable description of the dataset, if one exists.

          is_few_shot_examples: PseudoLabel job fields.

          name: Human-readable name for the dataset, if one exists.

          project_id: The project to add the new dataset to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/create",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "is_active_labels": is_active_labels,
                    "is_few_shot_examples": is_few_shot_examples,
                    "name": name,
                    "project_id": project_id,
                },
                dataset_create_params.DatasetCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetCreateResponse,
        )

    async def list(
        self,
        *,
        filters: dataset_list_params.Filters | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetListResponse:
        """
        List Datasets.

        Args:
          filters: Filter listed datasets by ALL filters specified

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/list",
            body=await async_maybe_transform({"filters": filters}, dataset_list_params.DatasetListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetListResponse,
        )

    async def delete(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetDeleteResponse:
        """
        Archive a dataset

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/archive",
            body=await async_maybe_transform({"id": id}, dataset_delete_params.DatasetDeleteParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetDeleteResponse,
        )

    async def copy(
        self,
        *,
        dataset_id: str,
        description: str | NotGiven = NOT_GIVEN,
        name: str | NotGiven = NOT_GIVEN,
        project_id: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetCopyResponse:
        """
        Clone a dataset into a new dataset containing the latest file contents

        Args:
          dataset_id: Dataset to clone

          description: Human-readable description of the dataset. If not provided, will use the name of
              the dataset being cloned

          name: New dataset name. If not provided, will use the name of the dataset being cloned

          project_id: The project to add the new dataset to

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/clone",
            body=await async_maybe_transform(
                {
                    "dataset_id": dataset_id,
                    "description": description,
                    "name": name,
                    "project_id": project_id,
                },
                dataset_copy_params.DatasetCopyParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetCopyResponse,
        )

    async def finalize_file_upload(
        self,
        *,
        dataset_id: str,
        s3_presigned_post: dataset_finalize_file_upload_params.S3PresignedPost,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetFinalizeFileUploadResponse:
        """Finalize a Dataset file upload.

        This call should be made after the file has been
        uploaded to the S3 URL returned from UploadDatasetFile.

        Args:
          dataset_id: The ID of the dataset corresponding to the file

          s3_presigned_post: The pre-signed S3 URL where the file was uploadeded

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/finalize_single_file_upload",
            body=await async_maybe_transform(
                {
                    "dataset_id": dataset_id,
                    "s3_presigned_post": s3_presigned_post,
                },
                dataset_finalize_file_upload_params.DatasetFinalizeFileUploadParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetFinalizeFileUploadResponse,
        )

    async def get(
        self,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetGetResponse:
        """
        Get a Dataset.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/get",
            body=await async_maybe_transform({"id": id}, dataset_get_params.DatasetGetParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetGetResponse,
        )

    async def get_download_url(
        self,
        *,
        dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetGetDownloadURLResponse:
        """
        Get a download url for a Dataset.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/get_download_url",
            body=await async_maybe_transform(
                {"dataset_id": dataset_id}, dataset_get_download_url_params.DatasetGetDownloadURLParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetGetDownloadURLResponse,
        )

    async def get_view(
        self,
        *,
        dataset_file_id: str,
        dataset_id: str,
        filters: Iterable[dataset_get_view_params.Filter],
        after: int | NotGiven = NOT_GIVEN,
        get_last_page: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        next_page_cursor: str | NotGiven = NOT_GIVEN,
        order_by: str | NotGiven = NOT_GIVEN,
        order_direction: str | NotGiven = NOT_GIVEN,
        previous_page_cursor: str | NotGiven = NOT_GIVEN,
        use_datasets_service: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetGetViewResponse:
        """
        Get a paginated view of the data within a Dataset.

        Args:
          dataset_file_id: The ID of the (pinned) dataset file from which to retrieve content. Requests
              iterating over pages of results are recommended to use this pinned identifier
              after the first page in order to prevent any effects from a dataset changing
              between the queries.

          dataset_id: The ID of the dataset from which to retrieve content. When specified, gets data
              from the current file in the dataset.

          after: Pagination: The index, by row-order, after which to query results.

          limit: Pagination: The maximum number of results to return on this page.

          next_page_cursor: A cursor for the next page in the pagination, if one exists.

          order_by: Column to order results by

          order_direction: Direction to order results ("asc" or "desc")

          previous_page_cursor: A cursor for the previous page in the pagination, if one exists.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/get_view",
            body=await async_maybe_transform(
                {
                    "dataset_file_id": dataset_file_id,
                    "dataset_id": dataset_id,
                    "filters": filters,
                    "after": after,
                    "get_last_page": get_last_page,
                    "limit": limit,
                    "next_page_cursor": next_page_cursor,
                    "order_by": order_by,
                    "order_direction": order_direction,
                    "previous_page_cursor": previous_page_cursor,
                    "use_datasets_service": use_datasets_service,
                },
                dataset_get_view_params.DatasetGetViewParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetGetViewResponse,
        )

    async def upload_file(
        self,
        *,
        dataset_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DatasetUploadFileResponse:
        """Initiate a file upload to a Dataset.

        Call FinalizeSingleDatasetFileUpload to
        complete the upload with the presigned URL returned from this call.

        Args:
          dataset_id: The ID of the dataset corresponding to the file.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/dataset/upload_file",
            body=await async_maybe_transform(
                {"dataset_id": dataset_id}, dataset_upload_file_params.DatasetUploadFileParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DatasetUploadFileResponse,
        )


class DatasetsResourceWithRawResponse:
    def __init__(self, datasets: DatasetsResource) -> None:
        self._datasets = datasets

        self.create = to_raw_response_wrapper(
            datasets.create,
        )
        self.list = to_raw_response_wrapper(
            datasets.list,
        )
        self.delete = to_raw_response_wrapper(
            datasets.delete,
        )
        self.copy = to_raw_response_wrapper(
            datasets.copy,
        )
        self.finalize_file_upload = to_raw_response_wrapper(
            datasets.finalize_file_upload,
        )
        self.get = to_raw_response_wrapper(
            datasets.get,
        )
        self.get_download_url = to_raw_response_wrapper(
            datasets.get_download_url,
        )
        self.get_view = to_raw_response_wrapper(
            datasets.get_view,
        )
        self.upload_file = to_raw_response_wrapper(
            datasets.upload_file,
        )


class AsyncDatasetsResourceWithRawResponse:
    def __init__(self, datasets: AsyncDatasetsResource) -> None:
        self._datasets = datasets

        self.create = async_to_raw_response_wrapper(
            datasets.create,
        )
        self.list = async_to_raw_response_wrapper(
            datasets.list,
        )
        self.delete = async_to_raw_response_wrapper(
            datasets.delete,
        )
        self.copy = async_to_raw_response_wrapper(
            datasets.copy,
        )
        self.finalize_file_upload = async_to_raw_response_wrapper(
            datasets.finalize_file_upload,
        )
        self.get = async_to_raw_response_wrapper(
            datasets.get,
        )
        self.get_download_url = async_to_raw_response_wrapper(
            datasets.get_download_url,
        )
        self.get_view = async_to_raw_response_wrapper(
            datasets.get_view,
        )
        self.upload_file = async_to_raw_response_wrapper(
            datasets.upload_file,
        )


class DatasetsResourceWithStreamingResponse:
    def __init__(self, datasets: DatasetsResource) -> None:
        self._datasets = datasets

        self.create = to_streamed_response_wrapper(
            datasets.create,
        )
        self.list = to_streamed_response_wrapper(
            datasets.list,
        )
        self.delete = to_streamed_response_wrapper(
            datasets.delete,
        )
        self.copy = to_streamed_response_wrapper(
            datasets.copy,
        )
        self.finalize_file_upload = to_streamed_response_wrapper(
            datasets.finalize_file_upload,
        )
        self.get = to_streamed_response_wrapper(
            datasets.get,
        )
        self.get_download_url = to_streamed_response_wrapper(
            datasets.get_download_url,
        )
        self.get_view = to_streamed_response_wrapper(
            datasets.get_view,
        )
        self.upload_file = to_streamed_response_wrapper(
            datasets.upload_file,
        )


class AsyncDatasetsResourceWithStreamingResponse:
    def __init__(self, datasets: AsyncDatasetsResource) -> None:
        self._datasets = datasets

        self.create = async_to_streamed_response_wrapper(
            datasets.create,
        )
        self.list = async_to_streamed_response_wrapper(
            datasets.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            datasets.delete,
        )
        self.copy = async_to_streamed_response_wrapper(
            datasets.copy,
        )
        self.finalize_file_upload = async_to_streamed_response_wrapper(
            datasets.finalize_file_upload,
        )
        self.get = async_to_streamed_response_wrapper(
            datasets.get,
        )
        self.get_download_url = async_to_streamed_response_wrapper(
            datasets.get_download_url,
        )
        self.get_view = async_to_streamed_response_wrapper(
            datasets.get_view,
        )
        self.upload_file = async_to_streamed_response_wrapper(
            datasets.upload_file,
        )
