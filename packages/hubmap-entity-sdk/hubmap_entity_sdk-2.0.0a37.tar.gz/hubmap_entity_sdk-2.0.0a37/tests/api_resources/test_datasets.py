# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from hubmap_entity_sdk import HubmapEntitySDK, AsyncHubmapEntitySDK
from hubmap_entity_sdk.types import (
    DatasetBulkUpdateResponse,
    DatasetListDonorsResponse,
    DatasetListOrgansResponse,
    DatasetListSamplesResponse,
    DatasetCreateComponentsResponse,
    DatasetRetrieveRevisionResponse,
    DatasetRetrievePairedDatasetResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestDatasets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_bulk_update(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.bulk_update(
            body=[{}],
        )
        assert_matches_type(DatasetBulkUpdateResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_bulk_update(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.bulk_update(
            body=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetBulkUpdateResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_bulk_update(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.bulk_update(
            body=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetBulkUpdateResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_components(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.create_components(
            body={},
        )
        assert_matches_type(DatasetCreateComponentsResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create_components(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.create_components(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetCreateComponentsResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create_components(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.create_components(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetCreateComponentsResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_donors(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.list_donors(
            "id",
        )
        assert_matches_type(DatasetListDonorsResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_donors(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.list_donors(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetListDonorsResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_donors(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.list_donors(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetListDonorsResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_donors(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.list_donors(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_organs(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.list_organs(
            "id",
        )
        assert_matches_type(DatasetListOrgansResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_organs(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.list_organs(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetListOrgansResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_organs(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.list_organs(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetListOrgansResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_organs(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.list_organs(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_revisions(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.list_revisions(
            id="id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_revisions_with_all_params(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.list_revisions(
            id="id",
            include_dataset="true",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_revisions(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.list_revisions(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_revisions(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.list_revisions(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_revisions(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.list_revisions(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_samples(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.list_samples(
            "id",
        )
        assert_matches_type(DatasetListSamplesResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_samples(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.list_samples(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetListSamplesResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_samples(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.list_samples(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetListSamplesResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_list_samples(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.list_samples(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_unpublished(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.list_unpublished()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_unpublished_with_all_params(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.list_unpublished(
            format="format",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_unpublished(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.list_unpublished()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_unpublished(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.list_unpublished() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retract(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retract(
            id="id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retract_with_all_params(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retract(
            id="id",
            retraction_reason="retraction_reason",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retract(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.retract(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retract(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.retract(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retract(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.retract(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_latest_revision(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retrieve_latest_revision(
            "id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_latest_revision(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.retrieve_latest_revision(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_latest_revision(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.retrieve_latest_revision(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_latest_revision(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.retrieve_latest_revision(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_paired_dataset(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retrieve_paired_dataset(
            id="id",
            data_type="data_type",
        )
        assert_matches_type(DatasetRetrievePairedDatasetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_paired_dataset_with_all_params(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retrieve_paired_dataset(
            id="id",
            data_type="data_type",
            search_depth=0,
        )
        assert_matches_type(DatasetRetrievePairedDatasetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_paired_dataset(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.retrieve_paired_dataset(
            id="id",
            data_type="data_type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetRetrievePairedDatasetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_paired_dataset(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.retrieve_paired_dataset(
            id="id",
            data_type="data_type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetRetrievePairedDatasetResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_paired_dataset(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.retrieve_paired_dataset(
                id="",
                data_type="data_type",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_prov_info(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retrieve_prov_info(
            id="id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_prov_info_with_all_params(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retrieve_prov_info(
            id="id",
            format="json",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_prov_info(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.retrieve_prov_info(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_prov_info(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.retrieve_prov_info(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_prov_info(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.retrieve_prov_info(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_prov_metadata(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retrieve_prov_metadata(
            "id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_prov_metadata(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.retrieve_prov_metadata(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_prov_metadata(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.retrieve_prov_metadata(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_prov_metadata(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.retrieve_prov_metadata(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_revision(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retrieve_revision(
            "id",
        )
        assert_matches_type(DatasetRetrieveRevisionResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_revision(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.retrieve_revision(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(DatasetRetrieveRevisionResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_revision(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.retrieve_revision(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(DatasetRetrieveRevisionResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_revision(self, client: HubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            client.datasets.with_raw_response.retrieve_revision(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_sankey_data(self, client: HubmapEntitySDK) -> None:
        dataset = client.datasets.retrieve_sankey_data()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_sankey_data(self, client: HubmapEntitySDK) -> None:
        response = client.datasets.with_raw_response.retrieve_sankey_data()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_sankey_data(self, client: HubmapEntitySDK) -> None:
        with client.datasets.with_streaming_response.retrieve_sankey_data() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncDatasets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_bulk_update(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.bulk_update(
            body=[{}],
        )
        assert_matches_type(DatasetBulkUpdateResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_bulk_update(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.bulk_update(
            body=[{}],
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetBulkUpdateResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_bulk_update(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.bulk_update(
            body=[{}],
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetBulkUpdateResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_components(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.create_components(
            body={},
        )
        assert_matches_type(DatasetCreateComponentsResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create_components(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.create_components(
            body={},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetCreateComponentsResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create_components(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.create_components(
            body={},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetCreateComponentsResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_donors(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.list_donors(
            "id",
        )
        assert_matches_type(DatasetListDonorsResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_donors(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.list_donors(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetListDonorsResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_donors(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.list_donors(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetListDonorsResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_donors(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.list_donors(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_organs(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.list_organs(
            "id",
        )
        assert_matches_type(DatasetListOrgansResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_organs(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.list_organs(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetListOrgansResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_organs(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.list_organs(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetListOrgansResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_organs(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.list_organs(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_revisions(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.list_revisions(
            id="id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_revisions_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.list_revisions(
            id="id",
            include_dataset="true",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_revisions(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.list_revisions(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_revisions(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.list_revisions(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_revisions(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.list_revisions(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_samples(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.list_samples(
            "id",
        )
        assert_matches_type(DatasetListSamplesResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_samples(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.list_samples(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetListSamplesResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_samples(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.list_samples(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetListSamplesResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_list_samples(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.list_samples(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_unpublished(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.list_unpublished()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_unpublished_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.list_unpublished(
            format="format",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_unpublished(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.list_unpublished()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_unpublished(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.list_unpublished() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retract(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retract(
            id="id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retract_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retract(
            id="id",
            retraction_reason="retraction_reason",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retract(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.retract(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retract(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.retract(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retract(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.retract(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_latest_revision(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retrieve_latest_revision(
            "id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_latest_revision(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.retrieve_latest_revision(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_latest_revision(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.retrieve_latest_revision(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_latest_revision(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.retrieve_latest_revision(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_paired_dataset(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retrieve_paired_dataset(
            id="id",
            data_type="data_type",
        )
        assert_matches_type(DatasetRetrievePairedDatasetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_paired_dataset_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retrieve_paired_dataset(
            id="id",
            data_type="data_type",
            search_depth=0,
        )
        assert_matches_type(DatasetRetrievePairedDatasetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_paired_dataset(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.retrieve_paired_dataset(
            id="id",
            data_type="data_type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetRetrievePairedDatasetResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_paired_dataset(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.retrieve_paired_dataset(
            id="id",
            data_type="data_type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetRetrievePairedDatasetResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_paired_dataset(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.retrieve_paired_dataset(
                id="",
                data_type="data_type",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_prov_info(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retrieve_prov_info(
            id="id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_prov_info_with_all_params(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retrieve_prov_info(
            id="id",
            format="json",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_prov_info(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.retrieve_prov_info(
            id="id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_prov_info(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.retrieve_prov_info(
            id="id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_prov_info(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.retrieve_prov_info(
                id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_prov_metadata(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retrieve_prov_metadata(
            "id",
        )
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_prov_metadata(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.retrieve_prov_metadata(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_prov_metadata(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.retrieve_prov_metadata(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_prov_metadata(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.retrieve_prov_metadata(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_revision(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retrieve_revision(
            "id",
        )
        assert_matches_type(DatasetRetrieveRevisionResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_revision(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.retrieve_revision(
            "id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(DatasetRetrieveRevisionResponse, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_revision(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.retrieve_revision(
            "id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(DatasetRetrieveRevisionResponse, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_revision(self, async_client: AsyncHubmapEntitySDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `id` but received ''"):
            await async_client.datasets.with_raw_response.retrieve_revision(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_sankey_data(self, async_client: AsyncHubmapEntitySDK) -> None:
        dataset = await async_client.datasets.retrieve_sankey_data()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_sankey_data(self, async_client: AsyncHubmapEntitySDK) -> None:
        response = await async_client.datasets.with_raw_response.retrieve_sankey_data()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        dataset = await response.parse()
        assert_matches_type(object, dataset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_sankey_data(self, async_client: AsyncHubmapEntitySDK) -> None:
        async with async_client.datasets.with_streaming_response.retrieve_sankey_data() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            dataset = await response.parse()
            assert_matches_type(object, dataset, path=["response"])

        assert cast(Any, response.is_closed) is True
