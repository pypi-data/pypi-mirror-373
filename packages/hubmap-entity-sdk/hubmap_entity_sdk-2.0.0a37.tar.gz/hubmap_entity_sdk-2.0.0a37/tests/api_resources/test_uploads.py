# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from hubmap_entity_sdk import HubmapEntitySDK, AsyncHubmapEntitySDK
from hubmap_entity_sdk.types import UploadUpdateBulkResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUploads:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_bulk(self, client: HubmapEntitySDK) -> None:
        upload = client.uploads.update_bulk(
            body={},
        )
        assert_matches_type(UploadUpdateBulkResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_bulk(self, client: HubmapEntitySDK) -> None:
        response = client.uploads.with_raw_response.update_bulk(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = response.parse()
        assert_matches_type(UploadUpdateBulkResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_bulk(self, client: HubmapEntitySDK) -> None:
        with client.uploads.with_streaming_response.update_bulk(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = response.parse()
            assert_matches_type(UploadUpdateBulkResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUploads:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_bulk(self, async_client: AsyncHubmapEntitySDK) -> None:
        upload = await async_client.uploads.update_bulk(
            body={},
        )
        assert_matches_type(UploadUpdateBulkResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_bulk(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.uploads.with_raw_response.update_bulk(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        upload = await response.parse()
        assert_matches_type(UploadUpdateBulkResponse, upload, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_bulk(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.uploads.with_streaming_response.update_bulk(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            upload = await response.parse()
            assert_matches_type(UploadUpdateBulkResponse, upload, path=["response"])

        assert cast(Any, response.is_closed) is True
