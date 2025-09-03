# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import search_execute_query_params, search_execute_index_query_params
from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["SearchResource", "AsyncSearchResource"]


class SearchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return SearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return SearchResourceWithStreamingResponse(self)

    def execute_index_query(
        self,
        index_name: str,
        *,
        body: object,
        produce_clt_manifest: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        To execute a query, the POST method must provide 1) a request body that
        specifies an
        [Elasticsearch Query DSL statement](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html) 2)
        a bearer token in the Authorization header supplied by HuBMAP. Results are
        limited to those authorized by the bearer token. Uses the
        <strong>entities</strong> index by default.

        Args:
          produce_clt_manifest: An optional parameter that, when set to "true", will make the endpoint return a
              text representation of a manifest file that corresponds with the datasets
              queried rather than the original response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index_name:
            raise ValueError(f"Expected a non-empty value for `index_name` but received {index_name!r}")
        return self._post(
            f"/{index_name}/search",
            body=maybe_transform(body, search_execute_index_query_params.SearchExecuteIndexQueryParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"produce_clt_manifest": produce_clt_manifest},
                    search_execute_index_query_params.SearchExecuteIndexQueryParams,
                ),
            ),
            cast_to=object,
        )

    def execute_query(
        self,
        *,
        body: object,
        produce_clt_manifest: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        To execute a query, the POST method must provide 1) a request body that
        specifies an
        [Elasticsearch Query DSL statement](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html) 2)
        a bearer token in the Authorization header supplied by HuBMAP. Results are
        limited to those authorized by the bearer token. Uses the
        <strong>entities</strong> index by default.

        Args:
          produce_clt_manifest: An optional parameter that, when set to "true", will make the endpoint return a
              text representation of a manifest file that corresponds with the datasets
              queried rather than the original response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/search",
            body=maybe_transform(body, search_execute_query_params.SearchExecuteQueryParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"produce_clt_manifest": produce_clt_manifest}, search_execute_query_params.SearchExecuteQueryParams
                ),
            ),
            cast_to=object,
        )


class AsyncSearchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AsyncSearchResourceWithStreamingResponse(self)

    async def execute_index_query(
        self,
        index_name: str,
        *,
        body: object,
        produce_clt_manifest: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        To execute a query, the POST method must provide 1) a request body that
        specifies an
        [Elasticsearch Query DSL statement](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html) 2)
        a bearer token in the Authorization header supplied by HuBMAP. Results are
        limited to those authorized by the bearer token. Uses the
        <strong>entities</strong> index by default.

        Args:
          produce_clt_manifest: An optional parameter that, when set to "true", will make the endpoint return a
              text representation of a manifest file that corresponds with the datasets
              queried rather than the original response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index_name:
            raise ValueError(f"Expected a non-empty value for `index_name` but received {index_name!r}")
        return await self._post(
            f"/{index_name}/search",
            body=await async_maybe_transform(body, search_execute_index_query_params.SearchExecuteIndexQueryParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"produce_clt_manifest": produce_clt_manifest},
                    search_execute_index_query_params.SearchExecuteIndexQueryParams,
                ),
            ),
            cast_to=object,
        )

    async def execute_query(
        self,
        *,
        body: object,
        produce_clt_manifest: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        To execute a query, the POST method must provide 1) a request body that
        specifies an
        [Elasticsearch Query DSL statement](https://www.elastic.co/guide/en/elasticsearch/reference/current/search-your-data.html) 2)
        a bearer token in the Authorization header supplied by HuBMAP. Results are
        limited to those authorized by the bearer token. Uses the
        <strong>entities</strong> index by default.

        Args:
          produce_clt_manifest: An optional parameter that, when set to "true", will make the endpoint return a
              text representation of a manifest file that corresponds with the datasets
              queried rather than the original response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/search",
            body=await async_maybe_transform(body, search_execute_query_params.SearchExecuteQueryParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"produce_clt_manifest": produce_clt_manifest}, search_execute_query_params.SearchExecuteQueryParams
                ),
            ),
            cast_to=object,
        )


class SearchResourceWithRawResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.execute_index_query = to_raw_response_wrapper(
            search.execute_index_query,
        )
        self.execute_query = to_raw_response_wrapper(
            search.execute_query,
        )


class AsyncSearchResourceWithRawResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.execute_index_query = async_to_raw_response_wrapper(
            search.execute_index_query,
        )
        self.execute_query = async_to_raw_response_wrapper(
            search.execute_query,
        )


class SearchResourceWithStreamingResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.execute_index_query = to_streamed_response_wrapper(
            search.execute_index_query,
        )
        self.execute_query = to_streamed_response_wrapper(
            search.execute_query,
        )


class AsyncSearchResourceWithStreamingResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.execute_index_query = async_to_streamed_response_wrapper(
            search.execute_index_query,
        )
        self.execute_query = async_to_streamed_response_wrapper(
            search.execute_query,
        )
