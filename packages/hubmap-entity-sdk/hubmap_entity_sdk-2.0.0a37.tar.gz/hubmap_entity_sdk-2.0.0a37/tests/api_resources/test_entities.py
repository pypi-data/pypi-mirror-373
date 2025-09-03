# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from hubmap_entity_sdk import HubmapEntitySDK, AsyncHubmapEntitySDK
from hubmap_entity_sdk.types import (
    EntityListTupletsResponse,
    EntityListUploadsResponse,
    EntityListSiblingsResponse,
    EntityListCollectionsResponse,
    EntityListAncestorOrgansResponse,
    EntityCreateMultipleSamplesResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEntities:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.retrieve(
            "id",
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(object, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.update(
            id="id",
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.update(
            id="id",
            body={},
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(object, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_multiple_samples(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.create_multiple_samples(
            "count",
        )
        assert_matches_type(EntityCreateMultipleSamplesResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_multiple_samples(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.create_multiple_samples(
            "count",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityCreateMultipleSamplesResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_multiple_samples(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.create_multiple_samples(
            "count",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityCreateMultipleSamplesResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create_multiple_samples(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `count` but received ''"):
            client.entities.with_raw_response.create_multiple_samples(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_flush_cache(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.flush_cache(
            "id",
        )
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_flush_cache(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.flush_cache(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_flush_cache(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.flush_cache(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert entity is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_flush_cache(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.flush_cache(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_is_instance_of(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.is_instance_of(
            type="type",
            id="id",
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_is_instance_of(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.is_instance_of(
            type="type",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_is_instance_of(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.is_instance_of(
            type="type",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(object, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_is_instance_of(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.is_instance_of(
                type="type",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `type` but received ''"):
            client.entities.with_raw_response.is_instance_of(
                type="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_ancestor_organs(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_ancestor_organs(
            "id",
        )
        assert_matches_type(EntityListAncestorOrgansResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_ancestor_organs(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.list_ancestor_organs(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityListAncestorOrgansResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_ancestor_organs(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.list_ancestor_organs(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityListAncestorOrgansResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_ancestor_organs(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.list_ancestor_organs(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_collections(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_collections(
            id="id",
        )
        assert_matches_type(EntityListCollectionsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_collections_with_all_params(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_collections(
            id="id",
            property="uuid",
        )
        assert_matches_type(EntityListCollectionsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_collections(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.list_collections(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityListCollectionsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_collections(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.list_collections(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityListCollectionsResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_collections(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.list_collections(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_siblings(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_siblings(
            id="id",
        )
        assert_matches_type(EntityListSiblingsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_siblings_with_all_params(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_siblings(
            id="id",
            include_old_revisions="true",
            property_key="uuid",
            status="New",
        )
        assert_matches_type(EntityListSiblingsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_siblings(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.list_siblings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityListSiblingsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_siblings(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.list_siblings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityListSiblingsResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_siblings(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.list_siblings(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_tuplets(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_tuplets(
            id="id",
        )
        assert_matches_type(EntityListTupletsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_tuplets_with_all_params(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_tuplets(
            id="id",
            property_key="uuid",
            status="New",
        )
        assert_matches_type(EntityListTupletsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_tuplets(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.list_tuplets(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityListTupletsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_tuplets(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.list_tuplets(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityListTupletsResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_tuplets(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.list_tuplets(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_uploads(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_uploads(
            id="id",
        )
        assert_matches_type(EntityListUploadsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_uploads_with_all_params(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.list_uploads(
            id="id",
            property="uuid",
        )
        assert_matches_type(EntityListUploadsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_uploads(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.list_uploads(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(EntityListUploadsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_uploads(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.list_uploads(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(EntityListUploadsResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_uploads(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.list_uploads(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_globus_url(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.retrieve_globus_url(
            "id",
        )
        assert_matches_type(str, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_globus_url(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.retrieve_globus_url(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(str, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_globus_url(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.retrieve_globus_url(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(str, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_globus_url(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.retrieve_globus_url(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_provenance(self, client: HubmapEntitySDK) -> None:
        entity = client.entities.retrieve_provenance(
            "id",
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_provenance(self, client: HubmapEntitySDK) -> None:
        response = client.entities.with_raw_response.retrieve_provenance(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = response.parse()
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_provenance(self, client: HubmapEntitySDK) -> None:
        with client.entities.with_streaming_response.retrieve_provenance(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = response.parse()
            assert_matches_type(object, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_provenance(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.entities.with_raw_response.retrieve_provenance(
                "",
            )


class TestAsyncEntities:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.retrieve(
            "id",
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.retrieve(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.retrieve(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(object, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.update(
            id="id",
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.update(
            id="id",
            body={},
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.update(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.update(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(object, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.update(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_multiple_samples(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.create_multiple_samples(
            "count",
        )
        assert_matches_type(EntityCreateMultipleSamplesResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_multiple_samples(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.create_multiple_samples(
            "count",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityCreateMultipleSamplesResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_multiple_samples(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.create_multiple_samples(
            "count",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityCreateMultipleSamplesResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create_multiple_samples(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `count` but received ''"):
            await async_client.entities.with_raw_response.create_multiple_samples(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_flush_cache(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.flush_cache(
            "id",
        )
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_flush_cache(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.flush_cache(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert entity is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_flush_cache(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.flush_cache(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert entity is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_flush_cache(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.flush_cache(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_is_instance_of(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.is_instance_of(
            type="type",
            id="id",
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_is_instance_of(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.is_instance_of(
            type="type",
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_is_instance_of(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.is_instance_of(
            type="type",
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(object, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_is_instance_of(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.is_instance_of(
                type="type",
                id="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `type` but received ''"):
            await async_client.entities.with_raw_response.is_instance_of(
                type="",
                id="id",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_ancestor_organs(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_ancestor_organs(
            "id",
        )
        assert_matches_type(EntityListAncestorOrgansResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_ancestor_organs(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.list_ancestor_organs(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityListAncestorOrgansResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_ancestor_organs(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.list_ancestor_organs(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityListAncestorOrgansResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_ancestor_organs(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.list_ancestor_organs(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_collections(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_collections(
            id="id",
        )
        assert_matches_type(EntityListCollectionsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_collections_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_collections(
            id="id",
            property="uuid",
        )
        assert_matches_type(EntityListCollectionsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_collections(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.list_collections(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityListCollectionsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_collections(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.list_collections(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityListCollectionsResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_collections(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.list_collections(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_siblings(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_siblings(
            id="id",
        )
        assert_matches_type(EntityListSiblingsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_siblings_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_siblings(
            id="id",
            include_old_revisions="true",
            property_key="uuid",
            status="New",
        )
        assert_matches_type(EntityListSiblingsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_siblings(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.list_siblings(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityListSiblingsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_siblings(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.list_siblings(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityListSiblingsResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_siblings(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.list_siblings(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_tuplets(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_tuplets(
            id="id",
        )
        assert_matches_type(EntityListTupletsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_tuplets_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_tuplets(
            id="id",
            property_key="uuid",
            status="New",
        )
        assert_matches_type(EntityListTupletsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_tuplets(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.list_tuplets(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityListTupletsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_tuplets(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.list_tuplets(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityListTupletsResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_tuplets(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.list_tuplets(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_uploads(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_uploads(
            id="id",
        )
        assert_matches_type(EntityListUploadsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_uploads_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.list_uploads(
            id="id",
            property="uuid",
        )
        assert_matches_type(EntityListUploadsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_uploads(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.list_uploads(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(EntityListUploadsResponse, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_uploads(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.list_uploads(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(EntityListUploadsResponse, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_uploads(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.list_uploads(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_globus_url(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.retrieve_globus_url(
            "id",
        )
        assert_matches_type(str, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_globus_url(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.retrieve_globus_url(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(str, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_globus_url(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.retrieve_globus_url(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(str, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_globus_url(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.retrieve_globus_url(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_provenance(self, async_client: AsyncHubmapEntitySDK) -> None:
        entity = await async_client.entities.retrieve_provenance(
            "id",
        )
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_provenance(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.entities.with_raw_response.retrieve_provenance(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        entity = await response.parse()
        assert_matches_type(object, entity, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_provenance(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.entities.with_streaming_response.retrieve_provenance(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            entity = await response.parse()
            assert_matches_type(object, entity, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_provenance(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.entities.with_raw_response.retrieve_provenance(
                "",
            )
