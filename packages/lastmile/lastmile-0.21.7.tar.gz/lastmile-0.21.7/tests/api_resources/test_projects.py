# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from lastmile import Lastmile, AsyncLastmile
from tests.utils import assert_matches_type
from lastmile.types import (
    ProjectGetResponse,
    ProjectListResponse,
    ProjectCreateResponse,
    ProjectDefaultResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProjects:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @parametrize
    def test_method_create(self, client: Lastmile) -> None:
        project = client.projects.create(
            name="name",
        )
        assert_matches_type(ProjectCreateResponse, project, path=["response"])

    @parametrize
    def test_method_create_with_all_params(self, client: Lastmile) -> None:
        project = client.projects.create(
            name="name",
            description="description",
            organization_id="organizationId",
        )
        assert_matches_type(ProjectCreateResponse, project, path=["response"])

    @parametrize
    def test_raw_response_create(self, client: Lastmile) -> None:
        response = client.projects.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert_matches_type(ProjectCreateResponse, project, path=["response"])

    @parametrize
    def test_streaming_response_create(self, client: Lastmile) -> None:
        with client.projects.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert_matches_type(ProjectCreateResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_list(self, client: Lastmile) -> None:
        project = client.projects.list()
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @parametrize
    def test_method_list_with_all_params(self, client: Lastmile) -> None:
        project = client.projects.list(
            filters={
                "can_contribute": True,
                "organization_id": "organizationId",
                "query": "query",
            },
        )
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @parametrize
    def test_raw_response_list(self, client: Lastmile) -> None:
        response = client.projects.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @parametrize
    def test_streaming_response_list(self, client: Lastmile) -> None:
        with client.projects.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert_matches_type(ProjectListResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_default(self, client: Lastmile) -> None:
        project = client.projects.default()
        assert_matches_type(ProjectDefaultResponse, project, path=["response"])

    @parametrize
    def test_method_default_with_all_params(self, client: Lastmile) -> None:
        project = client.projects.default(
            organization_id="organizationId",
        )
        assert_matches_type(ProjectDefaultResponse, project, path=["response"])

    @parametrize
    def test_raw_response_default(self, client: Lastmile) -> None:
        response = client.projects.with_raw_response.default()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert_matches_type(ProjectDefaultResponse, project, path=["response"])

    @parametrize
    def test_streaming_response_default(self, client: Lastmile) -> None:
        with client.projects.with_streaming_response.default() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert_matches_type(ProjectDefaultResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    def test_method_get(self, client: Lastmile) -> None:
        project = client.projects.get(
            id="id",
        )
        assert_matches_type(ProjectGetResponse, project, path=["response"])

    @parametrize
    def test_raw_response_get(self, client: Lastmile) -> None:
        response = client.projects.with_raw_response.get(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = response.parse()
        assert_matches_type(ProjectGetResponse, project, path=["response"])

    @parametrize
    def test_streaming_response_get(self, client: Lastmile) -> None:
        with client.projects.with_streaming_response.get(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = response.parse()
            assert_matches_type(ProjectGetResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncProjects:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @parametrize
    async def test_method_create(self, async_client: AsyncLastmile) -> None:
        project = await async_client.projects.create(
            name="name",
        )
        assert_matches_type(ProjectCreateResponse, project, path=["response"])

    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncLastmile) -> None:
        project = await async_client.projects.create(
            name="name",
            description="description",
            organization_id="organizationId",
        )
        assert_matches_type(ProjectCreateResponse, project, path=["response"])

    @parametrize
    async def test_raw_response_create(self, async_client: AsyncLastmile) -> None:
        response = await async_client.projects.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert_matches_type(ProjectCreateResponse, project, path=["response"])

    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncLastmile) -> None:
        async with async_client.projects.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert_matches_type(ProjectCreateResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_list(self, async_client: AsyncLastmile) -> None:
        project = await async_client.projects.list()
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncLastmile) -> None:
        project = await async_client.projects.list(
            filters={
                "can_contribute": True,
                "organization_id": "organizationId",
                "query": "query",
            },
        )
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @parametrize
    async def test_raw_response_list(self, async_client: AsyncLastmile) -> None:
        response = await async_client.projects.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert_matches_type(ProjectListResponse, project, path=["response"])

    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncLastmile) -> None:
        async with async_client.projects.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert_matches_type(ProjectListResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_default(self, async_client: AsyncLastmile) -> None:
        project = await async_client.projects.default()
        assert_matches_type(ProjectDefaultResponse, project, path=["response"])

    @parametrize
    async def test_method_default_with_all_params(self, async_client: AsyncLastmile) -> None:
        project = await async_client.projects.default(
            organization_id="organizationId",
        )
        assert_matches_type(ProjectDefaultResponse, project, path=["response"])

    @parametrize
    async def test_raw_response_default(self, async_client: AsyncLastmile) -> None:
        response = await async_client.projects.with_raw_response.default()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert_matches_type(ProjectDefaultResponse, project, path=["response"])

    @parametrize
    async def test_streaming_response_default(self, async_client: AsyncLastmile) -> None:
        async with async_client.projects.with_streaming_response.default() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert_matches_type(ProjectDefaultResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True

    @parametrize
    async def test_method_get(self, async_client: AsyncLastmile) -> None:
        project = await async_client.projects.get(
            id="id",
        )
        assert_matches_type(ProjectGetResponse, project, path=["response"])

    @parametrize
    async def test_raw_response_get(self, async_client: AsyncLastmile) -> None:
        response = await async_client.projects.with_raw_response.get(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        project = await response.parse()
        assert_matches_type(ProjectGetResponse, project, path=["response"])

    @parametrize
    async def test_streaming_response_get(self, async_client: AsyncLastmile) -> None:
        async with async_client.projects.with_streaming_response.get(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            project = await response.parse()
            assert_matches_type(ProjectGetResponse, project, path=["response"])

        assert cast(Any, response.is_closed) is True
