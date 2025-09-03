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
from .resources import add, mget, search, update, indices, mapping, reindex, clear_docs, param_search, scroll_search
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

__all__ = [
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "HubmapSearchSDK",
    "AsyncHubmapSearchSDK",
    "Client",
    "AsyncClient",
]


class HubmapSearchSDK(SyncAPIClient):
    indices: indices.IndicesResource
    search: search.SearchResource
    param_search: param_search.ParamSearchResource
    reindex: reindex.ReindexResource
    mget: mget.MgetResource
    mapping: mapping.MappingResource
    update: update.UpdateResource
    add: add.AddResource
    clear_docs: clear_docs.ClearDocsResource
    scroll_search: scroll_search.ScrollSearchResource
    with_raw_response: HubmapSearchSDKWithRawResponse
    with_streaming_response: HubmapSearchSDKWithStreamedResponse

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
        """Construct a new synchronous HubmapSearchSDK client instance."""
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("HUBMAP_SEARCH_SDK_BASE_URL")
        if base_url is None:
            base_url = f"https://search.api.hubmapconsortium.org/v3/"

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

        self.indices = indices.IndicesResource(self)
        self.search = search.SearchResource(self)
        self.param_search = param_search.ParamSearchResource(self)
        self.reindex = reindex.ReindexResource(self)
        self.mget = mget.MgetResource(self)
        self.mapping = mapping.MappingResource(self)
        self.update = update.UpdateResource(self)
        self.add = add.AddResource(self)
        self.clear_docs = clear_docs.ClearDocsResource(self)
        self.scroll_search = scroll_search.ScrollSearchResource(self)
        self.with_raw_response = HubmapSearchSDKWithRawResponse(self)
        self.with_streaming_response = HubmapSearchSDKWithStreamedResponse(self)

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


class AsyncHubmapSearchSDK(AsyncAPIClient):
    indices: indices.AsyncIndicesResource
    search: search.AsyncSearchResource
    param_search: param_search.AsyncParamSearchResource
    reindex: reindex.AsyncReindexResource
    mget: mget.AsyncMgetResource
    mapping: mapping.AsyncMappingResource
    update: update.AsyncUpdateResource
    add: add.AsyncAddResource
    clear_docs: clear_docs.AsyncClearDocsResource
    scroll_search: scroll_search.AsyncScrollSearchResource
    with_raw_response: AsyncHubmapSearchSDKWithRawResponse
    with_streaming_response: AsyncHubmapSearchSDKWithStreamedResponse

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
        """Construct a new async AsyncHubmapSearchSDK client instance."""
        self.bearer_token = bearer_token

        if base_url is None:
            base_url = os.environ.get("HUBMAP_SEARCH_SDK_BASE_URL")
        if base_url is None:
            base_url = f"https://search.api.hubmapconsortium.org/v3/"

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

        self.indices = indices.AsyncIndicesResource(self)
        self.search = search.AsyncSearchResource(self)
        self.param_search = param_search.AsyncParamSearchResource(self)
        self.reindex = reindex.AsyncReindexResource(self)
        self.mget = mget.AsyncMgetResource(self)
        self.mapping = mapping.AsyncMappingResource(self)
        self.update = update.AsyncUpdateResource(self)
        self.add = add.AsyncAddResource(self)
        self.clear_docs = clear_docs.AsyncClearDocsResource(self)
        self.scroll_search = scroll_search.AsyncScrollSearchResource(self)
        self.with_raw_response = AsyncHubmapSearchSDKWithRawResponse(self)
        self.with_streaming_response = AsyncHubmapSearchSDKWithStreamedResponse(self)

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


class HubmapSearchSDKWithRawResponse:
    def __init__(self, client: HubmapSearchSDK) -> None:
        self.indices = indices.IndicesResourceWithRawResponse(client.indices)
        self.search = search.SearchResourceWithRawResponse(client.search)
        self.param_search = param_search.ParamSearchResourceWithRawResponse(client.param_search)
        self.reindex = reindex.ReindexResourceWithRawResponse(client.reindex)
        self.mget = mget.MgetResourceWithRawResponse(client.mget)
        self.mapping = mapping.MappingResourceWithRawResponse(client.mapping)
        self.update = update.UpdateResourceWithRawResponse(client.update)
        self.add = add.AddResourceWithRawResponse(client.add)
        self.clear_docs = clear_docs.ClearDocsResourceWithRawResponse(client.clear_docs)
        self.scroll_search = scroll_search.ScrollSearchResourceWithRawResponse(client.scroll_search)


class AsyncHubmapSearchSDKWithRawResponse:
    def __init__(self, client: AsyncHubmapSearchSDK) -> None:
        self.indices = indices.AsyncIndicesResourceWithRawResponse(client.indices)
        self.search = search.AsyncSearchResourceWithRawResponse(client.search)
        self.param_search = param_search.AsyncParamSearchResourceWithRawResponse(client.param_search)
        self.reindex = reindex.AsyncReindexResourceWithRawResponse(client.reindex)
        self.mget = mget.AsyncMgetResourceWithRawResponse(client.mget)
        self.mapping = mapping.AsyncMappingResourceWithRawResponse(client.mapping)
        self.update = update.AsyncUpdateResourceWithRawResponse(client.update)
        self.add = add.AsyncAddResourceWithRawResponse(client.add)
        self.clear_docs = clear_docs.AsyncClearDocsResourceWithRawResponse(client.clear_docs)
        self.scroll_search = scroll_search.AsyncScrollSearchResourceWithRawResponse(client.scroll_search)


class HubmapSearchSDKWithStreamedResponse:
    def __init__(self, client: HubmapSearchSDK) -> None:
        self.indices = indices.IndicesResourceWithStreamingResponse(client.indices)
        self.search = search.SearchResourceWithStreamingResponse(client.search)
        self.param_search = param_search.ParamSearchResourceWithStreamingResponse(client.param_search)
        self.reindex = reindex.ReindexResourceWithStreamingResponse(client.reindex)
        self.mget = mget.MgetResourceWithStreamingResponse(client.mget)
        self.mapping = mapping.MappingResourceWithStreamingResponse(client.mapping)
        self.update = update.UpdateResourceWithStreamingResponse(client.update)
        self.add = add.AddResourceWithStreamingResponse(client.add)
        self.clear_docs = clear_docs.ClearDocsResourceWithStreamingResponse(client.clear_docs)
        self.scroll_search = scroll_search.ScrollSearchResourceWithStreamingResponse(client.scroll_search)


class AsyncHubmapSearchSDKWithStreamedResponse:
    def __init__(self, client: AsyncHubmapSearchSDK) -> None:
        self.indices = indices.AsyncIndicesResourceWithStreamingResponse(client.indices)
        self.search = search.AsyncSearchResourceWithStreamingResponse(client.search)
        self.param_search = param_search.AsyncParamSearchResourceWithStreamingResponse(client.param_search)
        self.reindex = reindex.AsyncReindexResourceWithStreamingResponse(client.reindex)
        self.mget = mget.AsyncMgetResourceWithStreamingResponse(client.mget)
        self.mapping = mapping.AsyncMappingResourceWithStreamingResponse(client.mapping)
        self.update = update.AsyncUpdateResourceWithStreamingResponse(client.update)
        self.add = add.AsyncAddResourceWithStreamingResponse(client.add)
        self.clear_docs = clear_docs.AsyncClearDocsResourceWithStreamingResponse(client.clear_docs)
        self.scroll_search = scroll_search.AsyncScrollSearchResourceWithStreamingResponse(client.scroll_search)


Client = HubmapSearchSDK

AsyncClient = AsyncHubmapSearchSDK
