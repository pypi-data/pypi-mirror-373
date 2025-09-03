# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import mget_retrieve_multiple_params, mget_retrieve_multiple_by_index_params
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

__all__ = ["MgetResource", "AsyncMgetResource"]


class MgetResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MgetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return MgetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MgetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return MgetResourceWithStreamingResponse(self)

    def retrieve_multiple(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        To retrieve multiple documents by their IDs, the POST method must provide 1) a
        request body containing an array of document IDs in the \\__mget format, 2) a
        bearer token in the Authorization header supplied by HuBMAP. Results are limited
        to those authorized by the bearer token. Uses the <strong>entities</strong>
        index by default

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/mget",
            body=maybe_transform(body, mget_retrieve_multiple_params.MgetRetrieveMultipleParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def retrieve_multiple_by_index(
        self,
        index_name: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        To retrieve multiple documents by their IDs, the POST method must provide 1) a
        request body containing an array of document IDs in the \\__mget format, 2) a
        bearer token in the Authorization header supplied by HuBMAP. Results are limited
        to those authorized by the bearer token. Uses the <strong>entities</strong>
        index by default

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index_name:
            raise ValueError(f"Expected a non-empty value for `index_name` but received {index_name!r}")
        return self._post(
            f"/{index_name}/mget",
            body=maybe_transform(body, mget_retrieve_multiple_by_index_params.MgetRetrieveMultipleByIndexParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncMgetResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMgetResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMgetResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMgetResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AsyncMgetResourceWithStreamingResponse(self)

    async def retrieve_multiple(
        self,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        To retrieve multiple documents by their IDs, the POST method must provide 1) a
        request body containing an array of document IDs in the \\__mget format, 2) a
        bearer token in the Authorization header supplied by HuBMAP. Results are limited
        to those authorized by the bearer token. Uses the <strong>entities</strong>
        index by default

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/mget",
            body=await async_maybe_transform(body, mget_retrieve_multiple_params.MgetRetrieveMultipleParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def retrieve_multiple_by_index(
        self,
        index_name: str,
        *,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        To retrieve multiple documents by their IDs, the POST method must provide 1) a
        request body containing an array of document IDs in the \\__mget format, 2) a
        bearer token in the Authorization header supplied by HuBMAP. Results are limited
        to those authorized by the bearer token. Uses the <strong>entities</strong>
        index by default

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index_name:
            raise ValueError(f"Expected a non-empty value for `index_name` but received {index_name!r}")
        return await self._post(
            f"/{index_name}/mget",
            body=await async_maybe_transform(
                body, mget_retrieve_multiple_by_index_params.MgetRetrieveMultipleByIndexParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class MgetResourceWithRawResponse:
    def __init__(self, mget: MgetResource) -> None:
        self._mget = mget

        self.retrieve_multiple = to_raw_response_wrapper(
            mget.retrieve_multiple,
        )
        self.retrieve_multiple_by_index = to_raw_response_wrapper(
            mget.retrieve_multiple_by_index,
        )


class AsyncMgetResourceWithRawResponse:
    def __init__(self, mget: AsyncMgetResource) -> None:
        self._mget = mget

        self.retrieve_multiple = async_to_raw_response_wrapper(
            mget.retrieve_multiple,
        )
        self.retrieve_multiple_by_index = async_to_raw_response_wrapper(
            mget.retrieve_multiple_by_index,
        )


class MgetResourceWithStreamingResponse:
    def __init__(self, mget: MgetResource) -> None:
        self._mget = mget

        self.retrieve_multiple = to_streamed_response_wrapper(
            mget.retrieve_multiple,
        )
        self.retrieve_multiple_by_index = to_streamed_response_wrapper(
            mget.retrieve_multiple_by_index,
        )


class AsyncMgetResourceWithStreamingResponse:
    def __init__(self, mget: AsyncMgetResource) -> None:
        self._mget = mget

        self.retrieve_multiple = async_to_streamed_response_wrapper(
            mget.retrieve_multiple,
        )
        self.retrieve_multiple_by_index = async_to_streamed_response_wrapper(
            mget.retrieve_multiple_by_index,
        )
