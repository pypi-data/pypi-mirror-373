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
from ..types.descendant_retrieve_response import DescendantRetrieveResponse

__all__ = ["DescendantsResource", "AsyncDescendantsResource"]


class DescendantsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DescendantsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return DescendantsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DescendantsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return DescendantsResourceWithStreamingResponse(self)

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
    ) -> DescendantRetrieveResponse:
        """Get the descendant list for an Entity.

        The descendants are the nodes
        "downstream" from the current node. This list traverses all the levels in the
        graph. Returns all descendants as an array of Entities.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return self._get(
            f"/descendants/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescendantRetrieveResponse,
        )


class AsyncDescendantsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDescendantsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDescendantsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDescendantsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return AsyncDescendantsResourceWithStreamingResponse(self)

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
    ) -> DescendantRetrieveResponse:
        """Get the descendant list for an Entity.

        The descendants are the nodes
        "downstream" from the current node. This list traverses all the levels in the
        graph. Returns all descendants as an array of Entities.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not id:
            raise ValueError(f"Expected a non-empty value for `id` but received {id!r}")
        return await self._get(
            f"/descendants/{id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DescendantRetrieveResponse,
        )


class DescendantsResourceWithRawResponse:
    def __init__(self, descendants: DescendantsResource) -> None:
        self._descendants = descendants

        self.retrieve = to_raw_response_wrapper(
            descendants.retrieve,
        )


class AsyncDescendantsResourceWithRawResponse:
    def __init__(self, descendants: AsyncDescendantsResource) -> None:
        self._descendants = descendants

        self.retrieve = async_to_raw_response_wrapper(
            descendants.retrieve,
        )


class DescendantsResourceWithStreamingResponse:
    def __init__(self, descendants: DescendantsResource) -> None:
        self._descendants = descendants

        self.retrieve = to_streamed_response_wrapper(
            descendants.retrieve,
        )


class AsyncDescendantsResourceWithStreamingResponse:
    def __init__(self, descendants: AsyncDescendantsResource) -> None:
        self._descendants = descendants

        self.retrieve = async_to_streamed_response_wrapper(
            descendants.retrieve,
        )
