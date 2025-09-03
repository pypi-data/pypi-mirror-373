# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from .type import (
    TypeResource,
    AsyncTypeResource,
    TypeResourceWithRawResponse,
    AsyncTypeResourceWithRawResponse,
    TypeResourceWithStreamingResponse,
    AsyncTypeResourceWithStreamingResponse,
)
from ...types import (
    entity_update_params,
    entity_list_tuplets_params,
    entity_list_uploads_params,
    entity_list_siblings_params,
    entity_list_collections_params,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.entity_list_tuplets_response import EntityListTupletsResponse
from ...types.entity_list_uploads_response import EntityListUploadsResponse
from ...types.entity_list_siblings_response import EntityListSiblingsResponse
from ...types.entity_list_collections_response import EntityListCollectionsResponse
from ...types.entity_list_ancestor_organs_response import EntityListAncestorOrgansResponse
from ...types.entity_create_multiple_samples_response import EntityCreateMultipleSamplesResponse

__all__ = ["EntitiesResource", "AsyncEntitiesResource"]


class EntitiesResource(SyncAPIResource):
    @cached_property
    def type(self) -> TypeResource:
        return TypeResource(self._client)

    @cached_property
    def with_raw_response(self) -> EntitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return EntitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EntitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return EntitiesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Retrieve a provenance entity by id.

        Entity types of Donor, Sample and Datasets.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/entities/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def update(
        self,
        id: str,
        *,
        body: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Update the properties of a given Donor, Sample, Dataset or Upload

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._put(
            f"/entities/{id}",
            body=maybe_transform(body, entity_update_params.EntityUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def create_multiple_samples(
        self,
        count: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityCreateMultipleSamplesResponse:
        """Create multiple samples from the same source entity.

        'count' samples will be
        generated each with individual uuids, hubmap_ids and submission_ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not count:
            raise ValueError(f"Expected a non-empty value for `count` but received {count!r}")
        return self._post(
            f"/entities/multiple-samples/{count}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityCreateMultipleSamplesResponse,
        )

    def flush_cache(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete the cached data from Memcached for a given entity, HuBMAP-Read access is
        required in AWS API Gateway

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/entities/{id}/flush-cache",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def is_instance_of(
        self,
        type: str,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Determines if the Entity with id is an instance of type

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not type:
            raise ValueError(f"Expected a non-empty value for `type` but received {type!r}")
        return self._get(
            f"/entities/{id}/instanceof/{type}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def list_ancestor_organs(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListAncestorOrgansResponse:
        """
        Retrievea list of ancestor organ(s) of a given uuid

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/entities/{id}/ancestor-organs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityListAncestorOrgansResponse,
        )

    def list_collections(
        self,
        id: str,
        *,
        property: Literal["uuid"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListCollectionsResponse:
        """
        Get the list of all collections the Entity belongs to.

        Args:
          property: A case insensitive string. Any value besides 'uuid' will raise an error. If
              property=uuid is provided, rather than entire dictionary representations of each
              node, only the list of matching uuid's will be returned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/entities/{id}/collections",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"property": property}, entity_list_collections_params.EntityListCollectionsParams
                ),
            ),
            cast_to=EntityListCollectionsResponse,
        )

    def list_siblings(
        self,
        id: str,
        *,
        include_old_revisions: Literal["true", "false"] | NotGiven = NOT_GIVEN,
        property_key: Literal["uuid"] | NotGiven = NOT_GIVEN,
        status: Literal["New", "QA", "Published"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListSiblingsResponse:
        """Get the siblings list for an Entity.

        The siblings have the same direct ancestor.
        This list does not include all nodes whom have common ancestors, only the direct
        ancestor.

        Args:
          include_old_revisions: A case insensitive string. Any value besides true will have no effect. If the
              string is 'true', datasets that are have newer revisions will be included,
              otherwise by default they are not included.

          property_key: A case insensitive string. Any value besides 'uuid' will raise an error. If
              property_key=uuid is provided, rather than entire dictionary representations of
              each node, only the list of matching uuid's will be returned

          status: A case insensitive string. Any value besides 'New', 'Qa', and 'Published' will
              raise an error. If a valid status is provided, only results matching that status
              (if they are datasets) will be returned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/entities/{id}/siblings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "include_old_revisions": include_old_revisions,
                        "property_key": property_key,
                        "status": status,
                    },
                    entity_list_siblings_params.EntityListSiblingsParams,
                ),
            ),
            cast_to=EntityListSiblingsResponse,
        )

    def list_tuplets(
        self,
        id: str,
        *,
        property_key: Literal["uuid"] | NotGiven = NOT_GIVEN,
        status: Literal["New", "QA", "Published"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListTupletsResponse:
        """Get the tuplets list for an Entity.

        The tuplets have the same parent activity
        node.

        Args:
          property_key: A case insensitive string. Any value besides 'uuid' will raise an error. If
              property_key=uuid is provided, rather than entire dictionary representations of
              each node, only the list of matching uuid's will be returned

          status: A case insensitive string. Any value besides 'New', 'Qa', and 'Published' will
              raise an error. If a valid status is provided, only results matching that status
              (if they are datasets) will be returned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/entities/{id}/tuplets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "property_key": property_key,
                        "status": status,
                    },
                    entity_list_tuplets_params.EntityListTupletsParams,
                ),
            ),
            cast_to=EntityListTupletsResponse,
        )

    def list_uploads(
        self,
        id: str,
        *,
        property: Literal["uuid"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListUploadsResponse:
        """
        Get the list of all uploads the Entity belongs to.

        Args:
          property: A case insensitive string. Any value besides 'uuid' will raise an error. If
              property=uuid is provided, rather than entire dictionary representations of each
              node, only the list of matching uuid's will be returned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/entities/{id}/uploads",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"property": property}, entity_list_uploads_params.EntityListUploadsParams),
            ),
            cast_to=EntityListUploadsResponse,
        )

    def retrieve_globus_url(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get the Globus URL to the given Dataset or Upload entity

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return self._get(
            f"/entities/{id}/globus-url",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    def retrieve_provenance(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Get Provenance Data for Entity.

        This returns a PROV JSON compliant
        representation of the entity's provenance. Refer to this document for more
        information regarding
        [PROV JSON format](https://www.w3.org/Submission/2013/SUBM-prov-json-20130424/)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/entities/{id}/provenance",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncEntitiesResource(AsyncAPIResource):
    @cached_property
    def type(self) -> AsyncTypeResource:
        return AsyncTypeResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEntitiesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncEntitiesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEntitiesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return AsyncEntitiesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Retrieve a provenance entity by id.

        Entity types of Donor, Sample and Datasets.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/entities/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def update(
        self,
        id: str,
        *,
        body: object | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Update the properties of a given Donor, Sample, Dataset or Upload

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._put(
            f"/entities/{id}",
            body=await async_maybe_transform(body, entity_update_params.EntityUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def create_multiple_samples(
        self,
        count: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityCreateMultipleSamplesResponse:
        """Create multiple samples from the same source entity.

        'count' samples will be
        generated each with individual uuids, hubmap_ids and submission_ids.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not count:
            raise ValueError(f"Expected a non-empty value for `count` but received {count!r}")
        return await self._post(
            f"/entities/multiple-samples/{count}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityCreateMultipleSamplesResponse,
        )

    async def flush_cache(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Delete the cached data from Memcached for a given entity, HuBMAP-Read access is
        required in AWS API Gateway

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/entities/{id}/flush-cache",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def is_instance_of(
        self,
        type: str,
        *,
        id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Determines if the Entity with id is an instance of type

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        if not type:
            raise ValueError(f"Expected a non-empty value for `type` but received {type!r}")
        return await self._get(
            f"/entities/{id}/instanceof/{type}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def list_ancestor_organs(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListAncestorOrgansResponse:
        """
        Retrievea list of ancestor organ(s) of a given uuid

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/entities/{id}/ancestor-organs",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityListAncestorOrgansResponse,
        )

    async def list_collections(
        self,
        id: str,
        *,
        property: Literal["uuid"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListCollectionsResponse:
        """
        Get the list of all collections the Entity belongs to.

        Args:
          property: A case insensitive string. Any value besides 'uuid' will raise an error. If
              property=uuid is provided, rather than entire dictionary representations of each
              node, only the list of matching uuid's will be returned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/entities/{id}/collections",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"property": property}, entity_list_collections_params.EntityListCollectionsParams
                ),
            ),
            cast_to=EntityListCollectionsResponse,
        )

    async def list_siblings(
        self,
        id: str,
        *,
        include_old_revisions: Literal["true", "false"] | NotGiven = NOT_GIVEN,
        property_key: Literal["uuid"] | NotGiven = NOT_GIVEN,
        status: Literal["New", "QA", "Published"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListSiblingsResponse:
        """Get the siblings list for an Entity.

        The siblings have the same direct ancestor.
        This list does not include all nodes whom have common ancestors, only the direct
        ancestor.

        Args:
          include_old_revisions: A case insensitive string. Any value besides true will have no effect. If the
              string is 'true', datasets that are have newer revisions will be included,
              otherwise by default they are not included.

          property_key: A case insensitive string. Any value besides 'uuid' will raise an error. If
              property_key=uuid is provided, rather than entire dictionary representations of
              each node, only the list of matching uuid's will be returned

          status: A case insensitive string. Any value besides 'New', 'Qa', and 'Published' will
              raise an error. If a valid status is provided, only results matching that status
              (if they are datasets) will be returned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/entities/{id}/siblings",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "include_old_revisions": include_old_revisions,
                        "property_key": property_key,
                        "status": status,
                    },
                    entity_list_siblings_params.EntityListSiblingsParams,
                ),
            ),
            cast_to=EntityListSiblingsResponse,
        )

    async def list_tuplets(
        self,
        id: str,
        *,
        property_key: Literal["uuid"] | NotGiven = NOT_GIVEN,
        status: Literal["New", "QA", "Published"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListTupletsResponse:
        """Get the tuplets list for an Entity.

        The tuplets have the same parent activity
        node.

        Args:
          property_key: A case insensitive string. Any value besides 'uuid' will raise an error. If
              property_key=uuid is provided, rather than entire dictionary representations of
              each node, only the list of matching uuid's will be returned

          status: A case insensitive string. Any value besides 'New', 'Qa', and 'Published' will
              raise an error. If a valid status is provided, only results matching that status
              (if they are datasets) will be returned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/entities/{id}/tuplets",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "property_key": property_key,
                        "status": status,
                    },
                    entity_list_tuplets_params.EntityListTupletsParams,
                ),
            ),
            cast_to=EntityListTupletsResponse,
        )

    async def list_uploads(
        self,
        id: str,
        *,
        property: Literal["uuid"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityListUploadsResponse:
        """
        Get the list of all uploads the Entity belongs to.

        Args:
          property: A case insensitive string. Any value besides 'uuid' will raise an error. If
              property=uuid is provided, rather than entire dictionary representations of each
              node, only the list of matching uuid's will be returned

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/entities/{id}/uploads",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"property": property}, entity_list_uploads_params.EntityListUploadsParams
                ),
            ),
            cast_to=EntityListUploadsResponse,
        )

    async def retrieve_globus_url(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> str:
        """
        Get the Globus URL to the given Dataset or Upload entity

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        extra_headers = {"Accept": "text/plain", **(extra_headers or {})}
        return await self._get(
            f"/entities/{id}/globus-url",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=str,
        )

    async def retrieve_provenance(
        self,
        id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Get Provenance Data for Entity.

        This returns a PROV JSON compliant
        representation of the entity's provenance. Refer to this document for more
        information regarding
        [PROV JSON format](https://www.w3.org/Submission/2013/SUBM-prov-json-20130424/)

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/entities/{id}/provenance",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class EntitiesResourceWithRawResponse:
    def __init__(self, entities: EntitiesResource) -> None:
        self._entities = entities

        self.retrieve = to_raw_response_wrapper(
            entities.retrieve,
        )
        self.update = to_raw_response_wrapper(
            entities.update,
        )
        self.create_multiple_samples = to_raw_response_wrapper(
            entities.create_multiple_samples,
        )
        self.flush_cache = to_raw_response_wrapper(
            entities.flush_cache,
        )
        self.is_instance_of = to_raw_response_wrapper(
            entities.is_instance_of,
        )
        self.list_ancestor_organs = to_raw_response_wrapper(
            entities.list_ancestor_organs,
        )
        self.list_collections = to_raw_response_wrapper(
            entities.list_collections,
        )
        self.list_siblings = to_raw_response_wrapper(
            entities.list_siblings,
        )
        self.list_tuplets = to_raw_response_wrapper(
            entities.list_tuplets,
        )
        self.list_uploads = to_raw_response_wrapper(
            entities.list_uploads,
        )
        self.retrieve_globus_url = to_raw_response_wrapper(
            entities.retrieve_globus_url,
        )
        self.retrieve_provenance = to_raw_response_wrapper(
            entities.retrieve_provenance,
        )

    @cached_property
    def type(self) -> TypeResourceWithRawResponse:
        return TypeResourceWithRawResponse(self._entities.type)


class AsyncEntitiesResourceWithRawResponse:
    def __init__(self, entities: AsyncEntitiesResource) -> None:
        self._entities = entities

        self.retrieve = async_to_raw_response_wrapper(
            entities.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            entities.update,
        )
        self.create_multiple_samples = async_to_raw_response_wrapper(
            entities.create_multiple_samples,
        )
        self.flush_cache = async_to_raw_response_wrapper(
            entities.flush_cache,
        )
        self.is_instance_of = async_to_raw_response_wrapper(
            entities.is_instance_of,
        )
        self.list_ancestor_organs = async_to_raw_response_wrapper(
            entities.list_ancestor_organs,
        )
        self.list_collections = async_to_raw_response_wrapper(
            entities.list_collections,
        )
        self.list_siblings = async_to_raw_response_wrapper(
            entities.list_siblings,
        )
        self.list_tuplets = async_to_raw_response_wrapper(
            entities.list_tuplets,
        )
        self.list_uploads = async_to_raw_response_wrapper(
            entities.list_uploads,
        )
        self.retrieve_globus_url = async_to_raw_response_wrapper(
            entities.retrieve_globus_url,
        )
        self.retrieve_provenance = async_to_raw_response_wrapper(
            entities.retrieve_provenance,
        )

    @cached_property
    def type(self) -> AsyncTypeResourceWithRawResponse:
        return AsyncTypeResourceWithRawResponse(self._entities.type)


class EntitiesResourceWithStreamingResponse:
    def __init__(self, entities: EntitiesResource) -> None:
        self._entities = entities

        self.retrieve = to_streamed_response_wrapper(
            entities.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            entities.update,
        )
        self.create_multiple_samples = to_streamed_response_wrapper(
            entities.create_multiple_samples,
        )
        self.flush_cache = to_streamed_response_wrapper(
            entities.flush_cache,
        )
        self.is_instance_of = to_streamed_response_wrapper(
            entities.is_instance_of,
        )
        self.list_ancestor_organs = to_streamed_response_wrapper(
            entities.list_ancestor_organs,
        )
        self.list_collections = to_streamed_response_wrapper(
            entities.list_collections,
        )
        self.list_siblings = to_streamed_response_wrapper(
            entities.list_siblings,
        )
        self.list_tuplets = to_streamed_response_wrapper(
            entities.list_tuplets,
        )
        self.list_uploads = to_streamed_response_wrapper(
            entities.list_uploads,
        )
        self.retrieve_globus_url = to_streamed_response_wrapper(
            entities.retrieve_globus_url,
        )
        self.retrieve_provenance = to_streamed_response_wrapper(
            entities.retrieve_provenance,
        )

    @cached_property
    def type(self) -> TypeResourceWithStreamingResponse:
        return TypeResourceWithStreamingResponse(self._entities.type)


class AsyncEntitiesResourceWithStreamingResponse:
    def __init__(self, entities: AsyncEntitiesResource) -> None:
        self._entities = entities

        self.retrieve = async_to_streamed_response_wrapper(
            entities.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            entities.update,
        )
        self.create_multiple_samples = async_to_streamed_response_wrapper(
            entities.create_multiple_samples,
        )
        self.flush_cache = async_to_streamed_response_wrapper(
            entities.flush_cache,
        )
        self.is_instance_of = async_to_streamed_response_wrapper(
            entities.is_instance_of,
        )
        self.list_ancestor_organs = async_to_streamed_response_wrapper(
            entities.list_ancestor_organs,
        )
        self.list_collections = async_to_streamed_response_wrapper(
            entities.list_collections,
        )
        self.list_siblings = async_to_streamed_response_wrapper(
            entities.list_siblings,
        )
        self.list_tuplets = async_to_streamed_response_wrapper(
            entities.list_tuplets,
        )
        self.list_uploads = async_to_streamed_response_wrapper(
            entities.list_uploads,
        )
        self.retrieve_globus_url = async_to_streamed_response_wrapper(
            entities.retrieve_globus_url,
        )
        self.retrieve_provenance = async_to_streamed_response_wrapper(
            entities.retrieve_provenance,
        )

    @cached_property
    def type(self) -> AsyncTypeResourceWithStreamingResponse:
        return AsyncTypeResourceWithStreamingResponse(self._entities.type)
