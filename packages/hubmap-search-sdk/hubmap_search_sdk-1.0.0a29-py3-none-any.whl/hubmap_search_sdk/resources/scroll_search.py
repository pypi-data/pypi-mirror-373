# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import scroll_search_create_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
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

__all__ = ["ScrollSearchResource", "AsyncScrollSearchResource"]


class ScrollSearchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ScrollSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return ScrollSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ScrollSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return ScrollSearchResourceWithStreamingResponse(self)

    def create(
        self,
        index: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Use the OpenSearch scroll API
        (https://opensearch.org/docs/latest/api-reference/scroll/) to open a scroll
        which will be navigated in the specified time when scroll_id is not provided,
        retrieve more results when a scroll_id is provided, and close a scroll when zero
        is the specified time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/{index}/scroll-search",
            body=maybe_transform(body, scroll_search_create_params.ScrollSearchCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncScrollSearchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncScrollSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncScrollSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncScrollSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AsyncScrollSearchResourceWithStreamingResponse(self)

    async def create(
        self,
        index: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Use the OpenSearch scroll API
        (https://opensearch.org/docs/latest/api-reference/scroll/) to open a scroll
        which will be navigated in the specified time when scroll_id is not provided,
        retrieve more results when a scroll_id is provided, and close a scroll when zero
        is the specified time.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/{index}/scroll-search",
            body=await async_maybe_transform(body, scroll_search_create_params.ScrollSearchCreateParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ScrollSearchResourceWithRawResponse:
    def __init__(self, scroll_search: ScrollSearchResource) -> None:
        self._scroll_search = scroll_search

        self.create = to_raw_response_wrapper(
            scroll_search.create,
        )


class AsyncScrollSearchResourceWithRawResponse:
    def __init__(self, scroll_search: AsyncScrollSearchResource) -> None:
        self._scroll_search = scroll_search

        self.create = async_to_raw_response_wrapper(
            scroll_search.create,
        )


class ScrollSearchResourceWithStreamingResponse:
    def __init__(self, scroll_search: ScrollSearchResource) -> None:
        self._scroll_search = scroll_search

        self.create = to_streamed_response_wrapper(
            scroll_search.create,
        )


class AsyncScrollSearchResourceWithStreamingResponse:
    def __init__(self, scroll_search: AsyncScrollSearchResource) -> None:
        self._scroll_search = scroll_search

        self.create = async_to_streamed_response_wrapper(
            scroll_search.create,
        )
