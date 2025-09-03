# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hubmap_entity_sdk import HubmapEntitySDK, AsyncHubmapEntitySDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDoi:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_method_redirect(self, client: HubmapEntitySDK) -> None:
        doi = client.doi.redirect(
            "id",
        )
        assert doi is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_raw_response_redirect(self, client: HubmapEntitySDK) -> None:
        response = client.doi.with_raw_response.redirect(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doi = response.parse()
        assert doi is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_streaming_response_redirect(self, client: HubmapEntitySDK) -> None:
        with client.doi.with_streaming_response.redirect(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doi = response.parse()
            assert doi is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    def test_path_params_redirect(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.doi.with_raw_response.redirect(
                "",
            )


class TestAsyncDoi:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_method_redirect(self, async_client: AsyncHubmapEntitySDK) -> None:
        doi = await async_client.doi.redirect(
            "id",
        )
        assert doi is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_raw_response_redirect(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.doi.with_raw_response.redirect(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        doi = await response.parse()
        assert doi is None

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_streaming_response_redirect(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.doi.with_streaming_response.redirect(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            doi = await response.parse()
            assert doi is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism doesn't properly handle redirects")
    @parametrize
    async def test_path_params_redirect(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.doi.with_raw_response.redirect(
                "",
            )
