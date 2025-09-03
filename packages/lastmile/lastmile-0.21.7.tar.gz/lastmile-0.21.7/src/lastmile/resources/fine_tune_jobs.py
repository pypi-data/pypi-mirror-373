# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    fine_tune_job_list_params,
    fine_tune_job_create_params,
    fine_tune_job_submit_params,
    fine_tune_job_get_status_params,
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
from ..types.fine_tune_job_list_response import FineTuneJobListResponse
from ..types.fine_tune_job_create_response import FineTuneJobCreateResponse
from ..types.fine_tune_job_submit_response import FineTuneJobSubmitResponse
from ..types.fine_tune_job_get_status_response import FineTuneJobGetStatusResponse
from ..types.fine_tune_job_list_base_models_response import FineTuneJobListBaseModelsResponse

__all__ = ["FineTuneJobsResource", "AsyncFineTuneJobsResource"]


class FineTuneJobsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FineTuneJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#accessing-raw-response-data-eg-headers
        """
        return FineTuneJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FineTuneJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#with_streaming_response
        """
        return FineTuneJobsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        fine_tune_job_config: fine_tune_job_create_params.FineTuneJobConfig,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneJobCreateResponse:
        """
        Step 1 of 2: Create a new job configuration for fine-tuning, to be subsequently
        submitted by calling SubmitFineTuneJob.

        Args:
          fine_tune_job_config: Partial configuration with parameters for the fine-tune job.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/fine_tune_job/create",
            body=maybe_transform(
                {"fine_tune_job_config": fine_tune_job_config}, fine_tune_job_create_params.FineTuneJobCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobCreateResponse,
        )

    def list(
        self,
        *,
        filters: fine_tune_job_list_params.Filters | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneJobListResponse:
        """
        List all fine-tune jobs with optional filters.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/fine_tune_job/list",
            body=maybe_transform({"filters": filters}, fine_tune_job_list_params.FineTuneJobListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobListResponse,
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
    ) -> FineTuneJobGetStatusResponse:
        """
        Get the status of an existing job, including any results.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/fine_tune_job/get_status",
            body=maybe_transform({"job_id": job_id}, fine_tune_job_get_status_params.FineTuneJobGetStatusParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobGetStatusResponse,
        )

    def list_base_models(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneJobListBaseModelsResponse:
        """List all base models available for fine-tuning."""
        return self._post(
            "/api/2/auto_eval/fine_tune_job/list_base_models",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobListBaseModelsResponse,
        )

    def submit(
        self,
        *,
        fine_tune_job_config: fine_tune_job_submit_params.FineTuneJobConfig,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneJobSubmitResponse:
        """
        Step 2 of 2: Submit the job configuration created by CreateFineTuneJob to
        initiate a job.

        Args:
          fine_tune_job_config: The fine-tune job configuration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/2/auto_eval/fine_tune_job/submit",
            body=maybe_transform(
                {
                    "fine_tune_job_config": fine_tune_job_config,
                    "job_id": job_id,
                },
                fine_tune_job_submit_params.FineTuneJobSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobSubmitResponse,
        )


class AsyncFineTuneJobsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFineTuneJobsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFineTuneJobsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFineTuneJobsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lastmile-ai/lastmile-python#with_streaming_response
        """
        return AsyncFineTuneJobsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        fine_tune_job_config: fine_tune_job_create_params.FineTuneJobConfig,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneJobCreateResponse:
        """
        Step 1 of 2: Create a new job configuration for fine-tuning, to be subsequently
        submitted by calling SubmitFineTuneJob.

        Args:
          fine_tune_job_config: Partial configuration with parameters for the fine-tune job.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/fine_tune_job/create",
            body=await async_maybe_transform(
                {"fine_tune_job_config": fine_tune_job_config}, fine_tune_job_create_params.FineTuneJobCreateParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobCreateResponse,
        )

    async def list(
        self,
        *,
        filters: fine_tune_job_list_params.Filters | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneJobListResponse:
        """
        List all fine-tune jobs with optional filters.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/fine_tune_job/list",
            body=await async_maybe_transform({"filters": filters}, fine_tune_job_list_params.FineTuneJobListParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobListResponse,
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
    ) -> FineTuneJobGetStatusResponse:
        """
        Get the status of an existing job, including any results.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/fine_tune_job/get_status",
            body=await async_maybe_transform(
                {"job_id": job_id}, fine_tune_job_get_status_params.FineTuneJobGetStatusParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobGetStatusResponse,
        )

    async def list_base_models(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneJobListBaseModelsResponse:
        """List all base models available for fine-tuning."""
        return await self._post(
            "/api/2/auto_eval/fine_tune_job/list_base_models",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobListBaseModelsResponse,
        )

    async def submit(
        self,
        *,
        fine_tune_job_config: fine_tune_job_submit_params.FineTuneJobConfig,
        job_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FineTuneJobSubmitResponse:
        """
        Step 2 of 2: Submit the job configuration created by CreateFineTuneJob to
        initiate a job.

        Args:
          fine_tune_job_config: The fine-tune job configuration.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/2/auto_eval/fine_tune_job/submit",
            body=await async_maybe_transform(
                {
                    "fine_tune_job_config": fine_tune_job_config,
                    "job_id": job_id,
                },
                fine_tune_job_submit_params.FineTuneJobSubmitParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=FineTuneJobSubmitResponse,
        )


class FineTuneJobsResourceWithRawResponse:
    def __init__(self, fine_tune_jobs: FineTuneJobsResource) -> None:
        self._fine_tune_jobs = fine_tune_jobs

        self.create = to_raw_response_wrapper(
            fine_tune_jobs.create,
        )
        self.list = to_raw_response_wrapper(
            fine_tune_jobs.list,
        )
        self.get_status = to_raw_response_wrapper(
            fine_tune_jobs.get_status,
        )
        self.list_base_models = to_raw_response_wrapper(
            fine_tune_jobs.list_base_models,
        )
        self.submit = to_raw_response_wrapper(
            fine_tune_jobs.submit,
        )


class AsyncFineTuneJobsResourceWithRawResponse:
    def __init__(self, fine_tune_jobs: AsyncFineTuneJobsResource) -> None:
        self._fine_tune_jobs = fine_tune_jobs

        self.create = async_to_raw_response_wrapper(
            fine_tune_jobs.create,
        )
        self.list = async_to_raw_response_wrapper(
            fine_tune_jobs.list,
        )
        self.get_status = async_to_raw_response_wrapper(
            fine_tune_jobs.get_status,
        )
        self.list_base_models = async_to_raw_response_wrapper(
            fine_tune_jobs.list_base_models,
        )
        self.submit = async_to_raw_response_wrapper(
            fine_tune_jobs.submit,
        )


class FineTuneJobsResourceWithStreamingResponse:
    def __init__(self, fine_tune_jobs: FineTuneJobsResource) -> None:
        self._fine_tune_jobs = fine_tune_jobs

        self.create = to_streamed_response_wrapper(
            fine_tune_jobs.create,
        )
        self.list = to_streamed_response_wrapper(
            fine_tune_jobs.list,
        )
        self.get_status = to_streamed_response_wrapper(
            fine_tune_jobs.get_status,
        )
        self.list_base_models = to_streamed_response_wrapper(
            fine_tune_jobs.list_base_models,
        )
        self.submit = to_streamed_response_wrapper(
            fine_tune_jobs.submit,
        )


class AsyncFineTuneJobsResourceWithStreamingResponse:
    def __init__(self, fine_tune_jobs: AsyncFineTuneJobsResource) -> None:
        self._fine_tune_jobs = fine_tune_jobs

        self.create = async_to_streamed_response_wrapper(
            fine_tune_jobs.create,
        )
        self.list = async_to_streamed_response_wrapper(
            fine_tune_jobs.list,
        )
        self.get_status = async_to_streamed_response_wrapper(
            fine_tune_jobs.get_status,
        )
        self.list_base_models = async_to_streamed_response_wrapper(
            fine_tune_jobs.list_base_models,
        )
        self.submit = async_to_streamed_response_wrapper(
            fine_tune_jobs.submit,
        )
