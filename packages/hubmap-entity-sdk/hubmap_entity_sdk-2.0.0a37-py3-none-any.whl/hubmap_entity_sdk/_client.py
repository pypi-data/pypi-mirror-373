# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, Union, Mapping
from typing_extensions import Self, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    NOT_GIVEN,
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
)
from ._utils import is_given, get_async_library
from ._version import __version__
from .resources import doi, parents, uploads, children, datasets, ancestors, descendants, entity_types_all
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)
from .resources.entities import entities

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "HubmapEntitySDK",
    "AsyncHubmapEntitySDK",
    "Client",
    "AsyncClient",
]


class HubmapEntitySDK(SyncAPIClient):
    entities: entities.EntitiesResource
    entity_types_all: entity_types_all.EntityTypesAllResource
    ancestors: ancestors.AncestorsResource
    descendants: descendants.DescendantsResource
    parents: parents.ParentsResource
    children: children.ChildrenResource
    doi: doi.DoiResource
    datasets: datasets.DatasetsResource
    uploads: uploads.UploadsResource
    with_raw_response: HubmapEntitySDKWithRawResponse
    with_streaming_response: HubmapEntitySDKWithStreamedResponse

    # client options
    bearer_token: str | None

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous HubmapEntitySDK client instance.

        This automatically infers the `bearer_token` argument from the `HUBMAP_ENTITY_SDK_BEARER_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("HUBMAP_ENTITY_SDK_BEARER_TOKEN")
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("HUBMAP_ENTITY_SDK_BASE_URL")
        if base_url is None:
            base_url = f"https://entity.api.hubmapconsortium.org"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.entities = entities.EntitiesResource(self)
        self.entity_types_all = entity_types_all.EntityTypesAllResource(self)
        self.ancestors = ancestors.AncestorsResource(self)
        self.descendants = descendants.DescendantsResource(self)
        self.parents = parents.ParentsResource(self)
        self.children = children.ChildrenResource(self)
        self.doi = doi.DoiResource(self)
        self.datasets = datasets.DatasetsResource(self)
        self.uploads = uploads.UploadsResource(self)
        self.with_raw_response = HubmapEntitySDKWithRawResponse(self)
        self.with_streaming_response = HubmapEntitySDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        if bearer_token is None:
            return {}
        return {"Authorization": bearer_token}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncHubmapEntitySDK(AsyncAPIClient):
    entities: entities.AsyncEntitiesResource
    entity_types_all: entity_types_all.AsyncEntityTypesAllResource
    ancestors: ancestors.AsyncAncestorsResource
    descendants: descendants.AsyncDescendantsResource
    parents: parents.AsyncParentsResource
    children: children.AsyncChildrenResource
    doi: doi.AsyncDoiResource
    datasets: datasets.AsyncDatasetsResource
    uploads: uploads.AsyncUploadsResource
    with_raw_response: AsyncHubmapEntitySDKWithRawResponse
    with_streaming_response: AsyncHubmapEntitySDKWithStreamedResponse

    # client options
    bearer_token: str | None

    def __init__(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: Union[float, Timeout, None, NotGiven] = NOT_GIVEN,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncHubmapEntitySDK client instance.

        This automatically infers the `bearer_token` argument from the `HUBMAP_ENTITY_SDK_BEARER_TOKEN` environment variable if it is not provided.
        """
        if bearer_token is None:
            bearer_token = os.environ.get("HUBMAP_ENTITY_SDK_BEARER_TOKEN")
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("HUBMAP_ENTITY_SDK_BASE_URL")
        if base_url is None:
            base_url = f"https://entity.api.hubmapconsortium.org"

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

        self.entities = entities.AsyncEntitiesResource(self)
        self.entity_types_all = entity_types_all.AsyncEntityTypesAllResource(self)
        self.ancestors = ancestors.AsyncAncestorsResource(self)
        self.descendants = descendants.AsyncDescendantsResource(self)
        self.parents = parents.AsyncParentsResource(self)
        self.children = children.AsyncChildrenResource(self)
        self.doi = doi.AsyncDoiResource(self)
        self.datasets = datasets.AsyncDatasetsResource(self)
        self.uploads = uploads.AsyncUploadsResource(self)
        self.with_raw_response = AsyncHubmapEntitySDKWithRawResponse(self)
        self.with_streaming_response = AsyncHubmapEntitySDKWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def auth_headers(self) -> dict[str, str]:
        bearer_token = self.bearer_token
        if bearer_token is None:
            return {}
        return {"Authorization": bearer_token}

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        bearer_token: str | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = NOT_GIVEN,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = NOT_GIVEN,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            bearer_token=bearer_token or self.bearer_token,
            base_url=base_url or self.base_url,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class HubmapEntitySDKWithRawResponse:
    def __init__(self, client: HubmapEntitySDK) -> None:
        self.entities = entities.EntitiesResourceWithRawResponse(client.entities)
        self.entity_types_all = entity_types_all.EntityTypesAllResourceWithRawResponse(client.entity_types_all)
        self.ancestors = ancestors.AncestorsResourceWithRawResponse(client.ancestors)
        self.descendants = descendants.DescendantsResourceWithRawResponse(client.descendants)
        self.parents = parents.ParentsResourceWithRawResponse(client.parents)
        self.children = children.ChildrenResourceWithRawResponse(client.children)
        self.doi = doi.DoiResourceWithRawResponse(client.doi)
        self.datasets = datasets.DatasetsResourceWithRawResponse(client.datasets)
        self.uploads = uploads.UploadsResourceWithRawResponse(client.uploads)


class AsyncHubmapEntitySDKWithRawResponse:
    def __init__(self, client: AsyncHubmapEntitySDK) -> None:
        self.entities = entities.AsyncEntitiesResourceWithRawResponse(client.entities)
        self.entity_types_all = entity_types_all.AsyncEntityTypesAllResourceWithRawResponse(client.entity_types_all)
        self.ancestors = ancestors.AsyncAncestorsResourceWithRawResponse(client.ancestors)
        self.descendants = descendants.AsyncDescendantsResourceWithRawResponse(client.descendants)
        self.parents = parents.AsyncParentsResourceWithRawResponse(client.parents)
        self.children = children.AsyncChildrenResourceWithRawResponse(client.children)
        self.doi = doi.AsyncDoiResourceWithRawResponse(client.doi)
        self.datasets = datasets.AsyncDatasetsResourceWithRawResponse(client.datasets)
        self.uploads = uploads.AsyncUploadsResourceWithRawResponse(client.uploads)


class HubmapEntitySDKWithStreamedResponse:
    def __init__(self, client: HubmapEntitySDK) -> None:
        self.entities = entities.EntitiesResourceWithStreamingResponse(client.entities)
        self.entity_types_all = entity_types_all.EntityTypesAllResourceWithStreamingResponse(client.entity_types_all)
        self.ancestors = ancestors.AncestorsResourceWithStreamingResponse(client.ancestors)
        self.descendants = descendants.DescendantsResourceWithStreamingResponse(client.descendants)
        self.parents = parents.ParentsResourceWithStreamingResponse(client.parents)
        self.children = children.ChildrenResourceWithStreamingResponse(client.children)
        self.doi = doi.DoiResourceWithStreamingResponse(client.doi)
        self.datasets = datasets.DatasetsResourceWithStreamingResponse(client.datasets)
        self.uploads = uploads.UploadsResourceWithStreamingResponse(client.uploads)


class AsyncHubmapEntitySDKWithStreamedResponse:
    def __init__(self, client: AsyncHubmapEntitySDK) -> None:
        self.entities = entities.AsyncEntitiesResourceWithStreamingResponse(client.entities)
        self.entity_types_all = entity_types_all.AsyncEntityTypesAllResourceWithStreamingResponse(
            client.entity_types_all
        )
        self.ancestors = ancestors.AsyncAncestorsResourceWithStreamingResponse(client.ancestors)
        self.descendants = descendants.AsyncDescendantsResourceWithStreamingResponse(client.descendants)
        self.parents = parents.AsyncParentsResourceWithStreamingResponse(client.parents)
        self.children = children.AsyncChildrenResourceWithStreamingResponse(client.children)
        self.doi = doi.AsyncDoiResourceWithStreamingResponse(client.doi)
        self.datasets = datasets.AsyncDatasetsResourceWithStreamingResponse(client.datasets)
        self.uploads = uploads.AsyncUploadsResourceWithStreamingResponse(client.uploads)


Client = HubmapEntitySDK

AsyncClient = AsyncHubmapEntitySDK
