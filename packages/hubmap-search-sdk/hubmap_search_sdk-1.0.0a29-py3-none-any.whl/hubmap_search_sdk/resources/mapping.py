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

__all__ = ["MappingResource", "AsyncMappingResource"]


class MappingResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> MappingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return MappingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> MappingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return MappingResourceWithStreamingResponse(self)

    def retrieve_default(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Retrieve mapping information for the defeault index, which is consortium." """
        return self._get(
            "/mapping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def retrieve_index(
        self,
        index_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Retrieve mapping information for the specified index

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index_name:
            raise ValueError(f"Expected a non-empty value for `index_name` but received {index_name!r}")
        return self._get(
            f"/{index_name}/mapping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class AsyncMappingResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncMappingResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncMappingResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncMappingResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AsyncMappingResourceWithStreamingResponse(self)

    async def retrieve_default(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """Retrieve mapping information for the defeault index, which is consortium." """
        return await self._get(
            "/mapping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def retrieve_index(
        self,
        index_name: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Retrieve mapping information for the specified index

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index_name:
            raise ValueError(f"Expected a non-empty value for `index_name` but received {index_name!r}")
        return await self._get(
            f"/{index_name}/mapping",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )


class MappingResourceWithRawResponse:
    def __init__(self, mapping: MappingResource) -> None:
        self._mapping = mapping

        self.retrieve_default = to_raw_response_wrapper(
            mapping.retrieve_default,
        )
        self.retrieve_index = to_raw_response_wrapper(
            mapping.retrieve_index,
        )


class AsyncMappingResourceWithRawResponse:
    def __init__(self, mapping: AsyncMappingResource) -> None:
        self._mapping = mapping

        self.retrieve_default = async_to_raw_response_wrapper(
            mapping.retrieve_default,
        )
        self.retrieve_index = async_to_raw_response_wrapper(
            mapping.retrieve_index,
        )


class MappingResourceWithStreamingResponse:
    def __init__(self, mapping: MappingResource) -> None:
        self._mapping = mapping

        self.retrieve_default = to_streamed_response_wrapper(
            mapping.retrieve_default,
        )
        self.retrieve_index = to_streamed_response_wrapper(
            mapping.retrieve_index,
        )


class AsyncMappingResourceWithStreamingResponse:
    def __init__(self, mapping: AsyncMappingResource) -> None:
        self._mapping = mapping

        self.retrieve_default = async_to_streamed_response_wrapper(
            mapping.retrieve_default,
        )
        self.retrieve_index = async_to_streamed_response_wrapper(
            mapping.retrieve_index,
        )
