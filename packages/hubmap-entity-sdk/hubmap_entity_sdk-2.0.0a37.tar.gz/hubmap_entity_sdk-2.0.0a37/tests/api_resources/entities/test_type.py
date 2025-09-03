# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from hubmap_entity_sdk import HubmapEntitySDK, AsyncHubmapEntitySDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestType:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_is_instance_of(self, client: HubmapEntitySDK) -> None:
        type = client.entities.type.is_instance_of(
            type_b="type_b",
            type_a="type_a",
        )
        assert_matches_type(object, type, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_is_instance_of(self, client: HubmapEntitySDK) -> None:
        response = client.entities.type.with_raw_response.is_instance_of(
            type_b="type_b",
            type_a="type_a",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        type = response.parse()
        assert_matches_type(object, type, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_is_instance_of(self, client: HubmapEntitySDK) -> None:
        with client.entities.type.with_streaming_response.is_instance_of(
            type_b="type_b",
            type_a="type_a",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            type = response.parse()
            assert_matches_type(object, type, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_is_instance_of(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `type_a` but received ''"):
            client.entities.type.with_raw_response.is_instance_of(
                type_b="type_b",
                type_a="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `type_b` but received ''"):
            client.entities.type.with_raw_response.is_instance_of(
                type_b="",
                type_a="type_a",
            )


class TestAsyncType:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_is_instance_of(self, async_client: AsyncHubmapEntitySDK) -> None:
        type = await async_client.entities.type.is_instance_of(
            type_b="type_b",
            type_a="type_a",
        )
        assert_matches_type(object, type, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_is_instance_of(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.type.with_raw_response.is_instance_of(
            type_b="type_b",
            type_a="type_a",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        type = await response.parse()
        assert_matches_type(object, type, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_is_instance_of(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.type.with_streaming_response.is_instance_of(
            type_b="type_b",
            type_a="type_a",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            type = await response.parse()
            assert_matches_type(object, type, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_is_instance_of(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `type_a` but received ''"):
            await async_client.entities.type.with_raw_response.is_instance_of(
                type_b="type_b",
                type_a="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `type_b` but received ''"):
            await async_client.entities.type.with_raw_response.is_instance_of(
                type_b="",
                type_a="type_a",
            )
