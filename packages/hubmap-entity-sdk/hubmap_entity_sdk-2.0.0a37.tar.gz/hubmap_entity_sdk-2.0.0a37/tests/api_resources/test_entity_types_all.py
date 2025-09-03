# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from hubmap_entity_sdk import HubmapEntitySDK, AsyncHubmapEntitySDK
from hubmap_entity_sdk.types import EntityTypesAllListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEntityTypesAll:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: HubmapEntitySDK) -> None:
        entity_types_all = client.entity_types_all.list()
        assert_matches_type(EntityTypesAllListResponse, entity_types_all, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: HubmapEntitySDK) -> None:
        response = client.entity_types_all.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity_types_all = response.parse()
        assert_matches_type(EntityTypesAllListResponse, entity_types_all, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: HubmapEntitySDK) -> None:
        with client.entity_types_all.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity_types_all = response.parse()
            assert_matches_type(EntityTypesAllListResponse, entity_types_all, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEntityTypesAll:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity_types_all = await async_client.entity_types_all.list()
        assert_matches_type(EntityTypesAllListResponse, entity_types_all, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entity_types_all.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity_types_all = await response.parse()
        assert_matches_type(EntityTypesAllListResponse, entity_types_all, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entity_types_all.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity_types_all = await response.parse()
            assert_matches_type(EntityTypesAllListResponse, entity_types_all, path=["response"])

        assert cast(Any, response.is_closed) is True
