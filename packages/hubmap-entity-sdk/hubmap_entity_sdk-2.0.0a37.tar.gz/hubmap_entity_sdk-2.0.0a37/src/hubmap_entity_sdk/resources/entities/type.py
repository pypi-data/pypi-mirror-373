# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options

__all__ = ["TypeResource", "AsyncTypeResource"]


class TypeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TypeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return TypeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TypeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return TypeResourceWithStreamingResponse(self)

    def is_instance_of(
        self,
        type_b: str,
        *,
        type_a: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Determines if the Entity type type_a is an instance of type_b

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not type_a:
            raise ValueError(f"Expected a non-empty value for `type_a` but received {type_a!r}")
        if not type_b:
            raise ValueError(f"Expected a non-empty value for `type_b` but received {type_b!r}")
        return self._get(
            f"/entities/type/{type_a}/instanceof/{type_b}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncTypeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTypeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncTypeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTypeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/entity-python-sdk#with_streaming_response
        """
        return AsyncTypeResourceWithStreamingResponse(self)

    async def is_instance_of(
        self,
        type_b: str,
        *,
        type_a: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Determines if the Entity type type_a is an instance of type_b

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not type_a:
            raise ValueError(f"Expected a non-empty value for `type_a` but received {type_a!r}")
        if not type_b:
            raise ValueError(f"Expected a non-empty value for `type_b` but received {type_b!r}")
        return await self._get(
            f"/entities/type/{type_a}/instanceof/{type_b}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class TypeResourceWithRawResponse:
    def __init__(self, type: TypeResource) -> None:
        self._type = type

        self.is_instance_of = to_raw_response_wrapper(
            type.is_instance_of,
        )


class AsyncTypeResourceWithRawResponse:
    def __init__(self, type: AsyncTypeResource) -> None:
        self._type = type

        self.is_instance_of = async_to_raw_response_wrapper(
            type.is_instance_of,
        )


class TypeResourceWithStreamingResponse:
    def __init__(self, type: TypeResource) -> None:
        self._type = type

        self.is_instance_of = to_streamed_response_wrapper(
            type.is_instance_of,
        )


class AsyncTypeResourceWithStreamingResponse:
    def __init__(self, type: AsyncTypeResource) -> None:
        self._type = type

        self.is_instance_of = async_to_streamed_response_wrapper(
            type.is_instance_of,
        )
