# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    label_dataset_job_create_params,
    label_dataset_job_submit_params,
    label_dataset_job_get_status_params,
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
from ..types.label_dataset_job_create_response import LabelDatasetJobCreateResponse
from ..types.label_dataset_job_submit_response import LabelDatasetJobSubmitResponse
from ..types.label_dataset_job_get_status_response import LabelDatasetJobGetStatusResponse

__all__ = ["LabelDatasetJobsResource", "AsyncLabelDatasetJobsResource"]


class LabelDatasetJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> LabelDatasetJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#accessing-raw-response-data-eg-headers
        """
        return LabelDatasetJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> LabelDatasetJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#with_streaming_response
        """
        return LabelDatasetJobsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        pseudo_label_job_config: label_dataset_job_create_params.PseudoLabelJobConfig,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LabelDatasetJobCreateResponse:
        """
        Step 1 of 2: Create a new job configuration for LLM Judge labeling, to be
        subsequently submitted by calling SubmitPseudoLabelJob.

        Args:
          pseudo_label_job_config: Partial configuration containing updates via its non-null fields.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/pseudo_label_job/create",
            body=maybe_transform(
                {"pseudo_label_job_config": pseudo_label_job_config},
                label_dataset_job_create_params.LabelDatasetJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LabelDatasetJobCreateResponse,
        )

    def get_status(
        self,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LabelDatasetJobGetStatusResponse:
        """
        Get the status of an existing job, including any results.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/pseudo_label_job/get_status",
            body=maybe_transform(
                {"job_id": job_id}, label_dataset_job_get_status_params.LabelDatasetJobGetStatusParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LabelDatasetJobGetStatusResponse,
        )

    def submit(
        self,
        *,
        job_id: str,
        pseudo_label_job_config: label_dataset_job_submit_params.PseudoLabelJobConfig,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LabelDatasetJobSubmitResponse:
        """
        Step 2 of 2: Submit the job configuration created by CreatePseudoLabelJob to
        initiate an LLM Judge labeling job.

        Args:
          pseudo_label_job_config: The pseudo-labeling job configuration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/pseudo_label_job/submit",
            body=maybe_transform(
                {
                    "job_id": job_id,
                    "pseudo_label_job_config": pseudo_label_job_config,
                },
                label_dataset_job_submit_params.LabelDatasetJobSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LabelDatasetJobSubmitResponse,
        )


class AsyncLabelDatasetJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncLabelDatasetJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#accessing-raw-response-data-eg-headers
        """
        return AsyncLabelDatasetJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncLabelDatasetJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#with_streaming_response
        """
        return AsyncLabelDatasetJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        pseudo_label_job_config: label_dataset_job_create_params.PseudoLabelJobConfig,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LabelDatasetJobCreateResponse:
        """
        Step 1 of 2: Create a new job configuration for LLM Judge labeling, to be
        subsequently submitted by calling SubmitPseudoLabelJob.

        Args:
          pseudo_label_job_config: Partial configuration containing updates via its non-null fields.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/pseudo_label_job/create",
            body=await async_maybe_transform(
                {"pseudo_label_job_config": pseudo_label_job_config},
                label_dataset_job_create_params.LabelDatasetJobCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LabelDatasetJobCreateResponse,
        )

    async def get_status(
        self,
        *,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LabelDatasetJobGetStatusResponse:
        """
        Get the status of an existing job, including any results.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/pseudo_label_job/get_status",
            body=await async_maybe_transform(
                {"job_id": job_id}, label_dataset_job_get_status_params.LabelDatasetJobGetStatusParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LabelDatasetJobGetStatusResponse,
        )

    async def submit(
        self,
        *,
        job_id: str,
        pseudo_label_job_config: label_dataset_job_submit_params.PseudoLabelJobConfig,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> LabelDatasetJobSubmitResponse:
        """
        Step 2 of 2: Submit the job configuration created by CreatePseudoLabelJob to
        initiate an LLM Judge labeling job.

        Args:
          pseudo_label_job_config: The pseudo-labeling job configuration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/pseudo_label_job/submit",
            body=await async_maybe_transform(
                {
                    "job_id": job_id,
                    "pseudo_label_job_config": pseudo_label_job_config,
                },
                label_dataset_job_submit_params.LabelDatasetJobSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=LabelDatasetJobSubmitResponse,
        )


class LabelDatasetJobsResourceWithRawResponse:
    def __init__(self, label_dataset_jobs: LabelDatasetJobsResource) -> None:
        self._label_dataset_jobs = label_dataset_jobs

        self.create = to_raw_response_wrapper(
            label_dataset_jobs.create,
        )
        self.get_status = to_raw_response_wrapper(
            label_dataset_jobs.get_status,
        )
        self.submit = to_raw_response_wrapper(
            label_dataset_jobs.submit,
        )


class AsyncLabelDatasetJobsResourceWithRawResponse:
    def __init__(self, label_dataset_jobs: AsyncLabelDatasetJobsResource) -> None:
        self._label_dataset_jobs = label_dataset_jobs

        self.create = async_to_raw_response_wrapper(
            label_dataset_jobs.create,
        )
        self.get_status = async_to_raw_response_wrapper(
            label_dataset_jobs.get_status,
        )
        self.submit = async_to_raw_response_wrapper(
            label_dataset_jobs.submit,
        )


class LabelDatasetJobsResourceWithStreamingResponse:
    def __init__(self, label_dataset_jobs: LabelDatasetJobsResource) -> None:
        self._label_dataset_jobs = label_dataset_jobs

        self.create = to_streamed_response_wrapper(
            label_dataset_jobs.create,
        )
        self.get_status = to_streamed_response_wrapper(
            label_dataset_jobs.get_status,
        )
        self.submit = to_streamed_response_wrapper(
            label_dataset_jobs.submit,
        )


class AsyncLabelDatasetJobsResourceWithStreamingResponse:
    def __init__(self, label_dataset_jobs: AsyncLabelDatasetJobsResource) -> None:
        self._label_dataset_jobs = label_dataset_jobs

        self.create = async_to_streamed_response_wrapper(
            label_dataset_jobs.create,
        )
        self.get_status = async_to_streamed_response_wrapper(
            label_dataset_jobs.get_status,
        )
        self.submit = async_to_streamed_response_wrapper(
            label_dataset_jobs.submit,
        )
