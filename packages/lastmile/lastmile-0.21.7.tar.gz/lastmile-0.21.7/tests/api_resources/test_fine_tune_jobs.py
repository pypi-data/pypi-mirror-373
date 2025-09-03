# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lastmile import Lastmile, AsyncLastmile
from tests.utils import assert_matches_type
from lastmile.types import (
    FineTuneJobListResponse,
    FineTuneJobCreateResponse,
    FineTuneJobSubmitResponse,
    FineTuneJobGetStatusResponse,
    FineTuneJobListBaseModelsResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestFineTuneJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Lastmile) -> None:
        fine_tune_job = client.fine_tune_jobs.create(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
        )
        assert_matches_type(FineTuneJobCreateResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Lastmile) -> None:
        fine_tune_job = client.fine_tune_jobs.create(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
                "description": "description",
                "name": "name",
            },
        )
        assert_matches_type(FineTuneJobCreateResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Lastmile) -> None:
        response = client.fine_tune_jobs.with_raw_response.create(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = response.parse()
        assert_matches_type(FineTuneJobCreateResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Lastmile) -> None:
        with client.fine_tune_jobs.with_streaming_response.create(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = response.parse()
            assert_matches_type(FineTuneJobCreateResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Lastmile) -> None:
        fine_tune_job = client.fine_tune_jobs.list()
        assert_matches_type(FineTuneJobListResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Lastmile) -> None:
        fine_tune_job = client.fine_tune_jobs.list(
            filters={
                "query": "query",
                "status": "JOB_STATUS_UNSPECIFIED",
            },
        )
        assert_matches_type(FineTuneJobListResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Lastmile) -> None:
        response = client.fine_tune_jobs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = response.parse()
        assert_matches_type(FineTuneJobListResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Lastmile) -> None:
        with client.fine_tune_jobs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = response.parse()
            assert_matches_type(FineTuneJobListResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_status(self, client: Lastmile) -> None:
        fine_tune_job = client.fine_tune_jobs.get_status(
            job_id="jobId",
        )
        assert_matches_type(FineTuneJobGetStatusResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_raw_response_get_status(self, client: Lastmile) -> None:
        response = client.fine_tune_jobs.with_raw_response.get_status(
            job_id="jobId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = response.parse()
        assert_matches_type(FineTuneJobGetStatusResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_streaming_response_get_status(self, client: Lastmile) -> None:
        with client.fine_tune_jobs.with_streaming_response.get_status(
            job_id="jobId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = response.parse()
            assert_matches_type(FineTuneJobGetStatusResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list_base_models(self, client: Lastmile) -> None:
        fine_tune_job = client.fine_tune_jobs.list_base_models()
        assert_matches_type(FineTuneJobListBaseModelsResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_raw_response_list_base_models(self, client: Lastmile) -> None:
        response = client.fine_tune_jobs.with_raw_response.list_base_models()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = response.parse()
        assert_matches_type(FineTuneJobListBaseModelsResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_streaming_response_list_base_models(self, client: Lastmile) -> None:
        with client.fine_tune_jobs.with_streaming_response.list_base_models() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = response.parse()
            assert_matches_type(FineTuneJobListBaseModelsResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_submit(self, client: Lastmile) -> None:
        fine_tune_job = client.fine_tune_jobs.submit(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
            job_id="jobId",
        )
        assert_matches_type(FineTuneJobSubmitResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_method_submit_with_all_params(self, client: Lastmile) -> None:
        fine_tune_job = client.fine_tune_jobs.submit(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
                "description": "description",
                "name": "name",
            },
            job_id="jobId",
        )
        assert_matches_type(FineTuneJobSubmitResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_raw_response_submit(self, client: Lastmile) -> None:
        response = client.fine_tune_jobs.with_raw_response.submit(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
            job_id="jobId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = response.parse()
        assert_matches_type(FineTuneJobSubmitResponse, fine_tune_job, path=["response"])

    @parametrize
    def test_streaming_response_submit(self, client: Lastmile) -> None:
        with client.fine_tune_jobs.with_streaming_response.submit(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
            job_id="jobId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = response.parse()
            assert_matches_type(FineTuneJobSubmitResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncFineTuneJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncLastmile) -> None:
        fine_tune_job = await async_client.fine_tune_jobs.create(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
        )
        assert_matches_type(FineTuneJobCreateResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncLastmile) -> None:
        fine_tune_job = await async_client.fine_tune_jobs.create(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
                "description": "description",
                "name": "name",
            },
        )
        assert_matches_type(FineTuneJobCreateResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLastmile) -> None:
        response = await async_client.fine_tune_jobs.with_raw_response.create(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = await response.parse()
        assert_matches_type(FineTuneJobCreateResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLastmile) -> None:
        async with async_client.fine_tune_jobs.with_streaming_response.create(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = await response.parse()
            assert_matches_type(FineTuneJobCreateResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncLastmile) -> None:
        fine_tune_job = await async_client.fine_tune_jobs.list()
        assert_matches_type(FineTuneJobListResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLastmile) -> None:
        fine_tune_job = await async_client.fine_tune_jobs.list(
            filters={
                "query": "query",
                "status": "JOB_STATUS_UNSPECIFIED",
            },
        )
        assert_matches_type(FineTuneJobListResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLastmile) -> None:
        response = await async_client.fine_tune_jobs.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = await response.parse()
        assert_matches_type(FineTuneJobListResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLastmile) -> None:
        async with async_client.fine_tune_jobs.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = await response.parse()
            assert_matches_type(FineTuneJobListResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_status(self, async_client: AsyncLastmile) -> None:
        fine_tune_job = await async_client.fine_tune_jobs.get_status(
            job_id="jobId",
        )
        assert_matches_type(FineTuneJobGetStatusResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncLastmile) -> None:
        response = await async_client.fine_tune_jobs.with_raw_response.get_status(
            job_id="jobId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = await response.parse()
        assert_matches_type(FineTuneJobGetStatusResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncLastmile) -> None:
        async with async_client.fine_tune_jobs.with_streaming_response.get_status(
            job_id="jobId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = await response.parse()
            assert_matches_type(FineTuneJobGetStatusResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list_base_models(self, async_client: AsyncLastmile) -> None:
        fine_tune_job = await async_client.fine_tune_jobs.list_base_models()
        assert_matches_type(FineTuneJobListBaseModelsResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_raw_response_list_base_models(self, async_client: AsyncLastmile) -> None:
        response = await async_client.fine_tune_jobs.with_raw_response.list_base_models()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = await response.parse()
        assert_matches_type(FineTuneJobListBaseModelsResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_streaming_response_list_base_models(self, async_client: AsyncLastmile) -> None:
        async with async_client.fine_tune_jobs.with_streaming_response.list_base_models() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = await response.parse()
            assert_matches_type(FineTuneJobListBaseModelsResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_submit(self, async_client: AsyncLastmile) -> None:
        fine_tune_job = await async_client.fine_tune_jobs.submit(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
            job_id="jobId",
        )
        assert_matches_type(FineTuneJobSubmitResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncLastmile) -> None:
        fine_tune_job = await async_client.fine_tune_jobs.submit(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
                "description": "description",
                "name": "name",
            },
            job_id="jobId",
        )
        assert_matches_type(FineTuneJobSubmitResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncLastmile) -> None:
        response = await async_client.fine_tune_jobs.with_raw_response.submit(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
            job_id="jobId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        fine_tune_job = await response.parse()
        assert_matches_type(FineTuneJobSubmitResponse, fine_tune_job, path=["response"])

    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncLastmile) -> None:
        async with async_client.fine_tune_jobs.with_streaming_response.submit(
            fine_tune_job_config={
                "baseline_model_id": "baselineModelId",
                "selected_columns": ["string"],
                "test_dataset_id": "testDatasetId",
                "train_dataset_id": "trainDatasetId",
            },
            job_id="jobId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            fine_tune_job = await response.parse()
            assert_matches_type(FineTuneJobSubmitResponse, fine_tune_job, path=["response"])

        assert cast(Any, response.is_closed) is True
