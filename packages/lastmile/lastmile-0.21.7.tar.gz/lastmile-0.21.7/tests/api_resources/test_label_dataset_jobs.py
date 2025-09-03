# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lastmile import Lastmile, AsyncLastmile
from tests.utils import assert_matches_type
from lastmile.types import (
    LabelDatasetJobCreateResponse,
    LabelDatasetJobSubmitResponse,
    LabelDatasetJobGetStatusResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLabelDatasetJobs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Lastmile) -> None:
        label_dataset_job = client.label_dataset_jobs.create(
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        )
        assert_matches_type(LabelDatasetJobCreateResponse, label_dataset_job, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Lastmile) -> None:
        label_dataset_job = client.label_dataset_jobs.create(
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
                "active_labeled_dataset_id": "activeLabeledDatasetId",
                "description": "description",
                "few_shot_dataset_id": "fewShotDatasetId",
                "name": "name",
            },
        )
        assert_matches_type(LabelDatasetJobCreateResponse, label_dataset_job, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Lastmile) -> None:
        response = client.label_dataset_jobs.with_raw_response.create(
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        label_dataset_job = response.parse()
        assert_matches_type(LabelDatasetJobCreateResponse, label_dataset_job, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Lastmile) -> None:
        with client.label_dataset_jobs.with_streaming_response.create(
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            label_dataset_job = response.parse()
            assert_matches_type(LabelDatasetJobCreateResponse, label_dataset_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get_status(self, client: Lastmile) -> None:
        label_dataset_job = client.label_dataset_jobs.get_status(
            job_id="jobId",
        )
        assert_matches_type(LabelDatasetJobGetStatusResponse, label_dataset_job, path=["response"])

    @parametrize
    def test_raw_response_get_status(self, client: Lastmile) -> None:
        response = client.label_dataset_jobs.with_raw_response.get_status(
            job_id="jobId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        label_dataset_job = response.parse()
        assert_matches_type(LabelDatasetJobGetStatusResponse, label_dataset_job, path=["response"])

    @parametrize
    def test_streaming_response_get_status(self, client: Lastmile) -> None:
        with client.label_dataset_jobs.with_streaming_response.get_status(
            job_id="jobId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            label_dataset_job = response.parse()
            assert_matches_type(LabelDatasetJobGetStatusResponse, label_dataset_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_submit(self, client: Lastmile) -> None:
        label_dataset_job = client.label_dataset_jobs.submit(
            job_id="jobId",
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        )
        assert_matches_type(LabelDatasetJobSubmitResponse, label_dataset_job, path=["response"])

    @parametrize
    def test_method_submit_with_all_params(self, client: Lastmile) -> None:
        label_dataset_job = client.label_dataset_jobs.submit(
            job_id="jobId",
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
                "active_labeled_dataset_id": "activeLabeledDatasetId",
                "description": "description",
                "few_shot_dataset_id": "fewShotDatasetId",
                "name": "name",
            },
        )
        assert_matches_type(LabelDatasetJobSubmitResponse, label_dataset_job, path=["response"])

    @parametrize
    def test_raw_response_submit(self, client: Lastmile) -> None:
        response = client.label_dataset_jobs.with_raw_response.submit(
            job_id="jobId",
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        label_dataset_job = response.parse()
        assert_matches_type(LabelDatasetJobSubmitResponse, label_dataset_job, path=["response"])

    @parametrize
    def test_streaming_response_submit(self, client: Lastmile) -> None:
        with client.label_dataset_jobs.with_streaming_response.submit(
            job_id="jobId",
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            label_dataset_job = response.parse()
            assert_matches_type(LabelDatasetJobSubmitResponse, label_dataset_job, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncLabelDatasetJobs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncLastmile) -> None:
        label_dataset_job = await async_client.label_dataset_jobs.create(
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        )
        assert_matches_type(LabelDatasetJobCreateResponse, label_dataset_job, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncLastmile) -> None:
        label_dataset_job = await async_client.label_dataset_jobs.create(
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
                "active_labeled_dataset_id": "activeLabeledDatasetId",
                "description": "description",
                "few_shot_dataset_id": "fewShotDatasetId",
                "name": "name",
            },
        )
        assert_matches_type(LabelDatasetJobCreateResponse, label_dataset_job, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLastmile) -> None:
        response = await async_client.label_dataset_jobs.with_raw_response.create(
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        label_dataset_job = await response.parse()
        assert_matches_type(LabelDatasetJobCreateResponse, label_dataset_job, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLastmile) -> None:
        async with async_client.label_dataset_jobs.with_streaming_response.create(
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            label_dataset_job = await response.parse()
            assert_matches_type(LabelDatasetJobCreateResponse, label_dataset_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get_status(self, async_client: AsyncLastmile) -> None:
        label_dataset_job = await async_client.label_dataset_jobs.get_status(
            job_id="jobId",
        )
        assert_matches_type(LabelDatasetJobGetStatusResponse, label_dataset_job, path=["response"])

    @parametrize
    async def test_raw_response_get_status(self, async_client: AsyncLastmile) -> None:
        response = await async_client.label_dataset_jobs.with_raw_response.get_status(
            job_id="jobId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        label_dataset_job = await response.parse()
        assert_matches_type(LabelDatasetJobGetStatusResponse, label_dataset_job, path=["response"])

    @parametrize
    async def test_streaming_response_get_status(self, async_client: AsyncLastmile) -> None:
        async with async_client.label_dataset_jobs.with_streaming_response.get_status(
            job_id="jobId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            label_dataset_job = await response.parse()
            assert_matches_type(LabelDatasetJobGetStatusResponse, label_dataset_job, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_submit(self, async_client: AsyncLastmile) -> None:
        label_dataset_job = await async_client.label_dataset_jobs.submit(
            job_id="jobId",
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        )
        assert_matches_type(LabelDatasetJobSubmitResponse, label_dataset_job, path=["response"])

    @parametrize
    async def test_method_submit_with_all_params(self, async_client: AsyncLastmile) -> None:
        label_dataset_job = await async_client.label_dataset_jobs.submit(
            job_id="jobId",
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
                "active_labeled_dataset_id": "activeLabeledDatasetId",
                "description": "description",
                "few_shot_dataset_id": "fewShotDatasetId",
                "name": "name",
            },
        )
        assert_matches_type(LabelDatasetJobSubmitResponse, label_dataset_job, path=["response"])

    @parametrize
    async def test_raw_response_submit(self, async_client: AsyncLastmile) -> None:
        response = await async_client.label_dataset_jobs.with_raw_response.submit(
            job_id="jobId",
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        label_dataset_job = await response.parse()
        assert_matches_type(LabelDatasetJobSubmitResponse, label_dataset_job, path=["response"])

    @parametrize
    async def test_streaming_response_submit(self, async_client: AsyncLastmile) -> None:
        async with async_client.label_dataset_jobs.with_streaming_response.submit(
            job_id="jobId",
            pseudo_label_job_config={
                "base_evaluation_metric": "BASE_EVALUATION_METRIC_UNSPECIFIED",
                "dataset_id": "datasetId",
                "prompt_template": {
                    "id": "id",
                    "template": "template",
                },
                "selected_columns": ["string"],
                "skip_active_labeling": True,
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            label_dataset_job = await response.parse()
            assert_matches_type(LabelDatasetJobSubmitResponse, label_dataset_job, path=["response"])

        assert cast(Any, response.is_closed) is True
