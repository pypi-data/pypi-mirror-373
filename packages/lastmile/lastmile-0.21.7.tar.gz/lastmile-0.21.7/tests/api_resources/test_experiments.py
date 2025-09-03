# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lastmile import Lastmile, AsyncLastmile
from tests.utils import assert_matches_type
from lastmile.types import (
    ExperimentGetResponse,
    ExperimentListResponse,
    ExperimentCreateResponse,
    ExperimentDeleteResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestExperiments:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Lastmile) -> None:
        experiment = client.experiments.create(
            name="name",
            project_id="projectId",
        )
        assert_matches_type(ExperimentCreateResponse, experiment, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Lastmile) -> None:
        experiment = client.experiments.create(
            name="name",
            project_id="projectId",
            description="description",
            metadata={"fields": {"foo": {"foo": "bar"}}},
        )
        assert_matches_type(ExperimentCreateResponse, experiment, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Lastmile) -> None:
        response = client.experiments.with_raw_response.create(
            name="name",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        experiment = response.parse()
        assert_matches_type(ExperimentCreateResponse, experiment, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Lastmile) -> None:
        with client.experiments.with_streaming_response.create(
            name="name",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            experiment = response.parse()
            assert_matches_type(ExperimentCreateResponse, experiment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Lastmile) -> None:
        experiment = client.experiments.list()
        assert_matches_type(ExperimentListResponse, experiment, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Lastmile) -> None:
        experiment = client.experiments.list(
            filters={
                "project_id": "projectId",
                "query": "query",
            },
            page_index=0,
            page_size=0,
        )
        assert_matches_type(ExperimentListResponse, experiment, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Lastmile) -> None:
        response = client.experiments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        experiment = response.parse()
        assert_matches_type(ExperimentListResponse, experiment, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Lastmile) -> None:
        with client.experiments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            experiment = response.parse()
            assert_matches_type(ExperimentListResponse, experiment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_delete(self, client: Lastmile) -> None:
        experiment = client.experiments.delete(
            id="id",
        )
        assert_matches_type(ExperimentDeleteResponse, experiment, path=["response"])

    @parametrize
    def test_raw_response_delete(self, client: Lastmile) -> None:
        response = client.experiments.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        experiment = response.parse()
        assert_matches_type(ExperimentDeleteResponse, experiment, path=["response"])

    @parametrize
    def test_streaming_response_delete(self, client: Lastmile) -> None:
        with client.experiments.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            experiment = response.parse()
            assert_matches_type(ExperimentDeleteResponse, experiment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Lastmile) -> None:
        experiment = client.experiments.get(
            id="id",
        )
        assert_matches_type(ExperimentGetResponse, experiment, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Lastmile) -> None:
        response = client.experiments.with_raw_response.get(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        experiment = response.parse()
        assert_matches_type(ExperimentGetResponse, experiment, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Lastmile) -> None:
        with client.experiments.with_streaming_response.get(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            experiment = response.parse()
            assert_matches_type(ExperimentGetResponse, experiment, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncExperiments:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncLastmile) -> None:
        experiment = await async_client.experiments.create(
            name="name",
            project_id="projectId",
        )
        assert_matches_type(ExperimentCreateResponse, experiment, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncLastmile) -> None:
        experiment = await async_client.experiments.create(
            name="name",
            project_id="projectId",
            description="description",
            metadata={"fields": {"foo": {"foo": "bar"}}},
        )
        assert_matches_type(ExperimentCreateResponse, experiment, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLastmile) -> None:
        response = await async_client.experiments.with_raw_response.create(
            name="name",
            project_id="projectId",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        experiment = await response.parse()
        assert_matches_type(ExperimentCreateResponse, experiment, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLastmile) -> None:
        async with async_client.experiments.with_streaming_response.create(
            name="name",
            project_id="projectId",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            experiment = await response.parse()
            assert_matches_type(ExperimentCreateResponse, experiment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncLastmile) -> None:
        experiment = await async_client.experiments.list()
        assert_matches_type(ExperimentListResponse, experiment, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLastmile) -> None:
        experiment = await async_client.experiments.list(
            filters={
                "project_id": "projectId",
                "query": "query",
            },
            page_index=0,
            page_size=0,
        )
        assert_matches_type(ExperimentListResponse, experiment, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLastmile) -> None:
        response = await async_client.experiments.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        experiment = await response.parse()
        assert_matches_type(ExperimentListResponse, experiment, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLastmile) -> None:
        async with async_client.experiments.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            experiment = await response.parse()
            assert_matches_type(ExperimentListResponse, experiment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_delete(self, async_client: AsyncLastmile) -> None:
        experiment = await async_client.experiments.delete(
            id="id",
        )
        assert_matches_type(ExperimentDeleteResponse, experiment, path=["response"])

    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncLastmile) -> None:
        response = await async_client.experiments.with_raw_response.delete(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        experiment = await response.parse()
        assert_matches_type(ExperimentDeleteResponse, experiment, path=["response"])

    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncLastmile) -> None:
        async with async_client.experiments.with_streaming_response.delete(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            experiment = await response.parse()
            assert_matches_type(ExperimentDeleteResponse, experiment, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncLastmile) -> None:
        experiment = await async_client.experiments.get(
            id="id",
        )
        assert_matches_type(ExperimentGetResponse, experiment, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncLastmile) -> None:
        response = await async_client.experiments.with_raw_response.get(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        experiment = await response.parse()
        assert_matches_type(ExperimentGetResponse, experiment, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncLastmile) -> None:
        async with async_client.experiments.with_streaming_response.get(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            experiment = await response.parse()
            assert_matches_type(ExperimentGetResponse, experiment, path=["response"])

        assert cast(Any, response.is_closed) is True
