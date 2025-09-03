# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.entity_types_all_list_response import EntityTypesAllListResponse

__all__ = ["EntityTypesAllResource", "AsyncEntityTypesAllResource"]


class EntityTypesAllResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> EntityTypesAllResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return EntityTypesAllResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EntityTypesAllResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return EntityTypesAllResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityTypesAllListResponse:
        """Get a list of all the available entity types defined in the schema yaml"""
        return self._get(
            "/entity-types",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityTypesAllListResponse,
        )


class AsyncEntityTypesAllResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncEntityTypesAllResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncEntityTypesAllResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEntityTypesAllResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return AsyncEntityTypesAllResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EntityTypesAllListResponse:
        """Get a list of all the available entity types defined in the schema yaml"""
        return await self._get(
            "/entity-types",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EntityTypesAllListResponse,
        )


class EntityTypesAllResourceWithRawResponse:
    def __init__(self, entity_types_all: EntityTypesAllResource) -> None:
        self._entity_types_all = entity_types_all

        self.list = to_raw_response_wrapper(
            entity_types_all.list,
        )


class AsyncEntityTypesAllResourceWithRawResponse:
    def __init__(self, entity_types_all: AsyncEntityTypesAllResource) -> None:
        self._entity_types_all = entity_types_all

        self.list = async_to_raw_response_wrapper(
            entity_types_all.list,
        )


class EntityTypesAllResourceWithStreamingResponse:
    def __init__(self, entity_types_all: EntityTypesAllResource) -> None:
        self._entity_types_all = entity_types_all

        self.list = to_streamed_response_wrapper(
            entity_types_all.list,
        )


class AsyncEntityTypesAllResourceWithStreamingResponse:
    def __init__(self, entity_types_all: AsyncEntityTypesAllResource) -> None:
        self._entity_types_all = entity_types_all

        self.list = async_to_streamed_response_wrapper(
            entity_types_all.list,
        )
