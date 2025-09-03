# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options

__all__ = ["ClearDocsResource", "AsyncClearDocsResource"]


class ClearDocsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ClearDocsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return ClearDocsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ClearDocsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return ClearDocsResourceWithStreamingResponse(self)

    def clear_all(
        self,
        index: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Clear all docs for the given index

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
            f"/clear-docs/{index}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def clear_by_uuid(
        self,
        uuid: str,
        *,
        index: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Clear all docs for the given uuid within the index

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/clear-docs/{index}/{uuid}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def clear_by_uuid_and_scope(
        self,
        scope: str,
        *,
        index: str,
        uuid: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Clear all docs for the given uuid within the index and scope

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        if not scope:
            raise ValueError(f"Expected a non-empty value for `scope` but received {scope!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/clear-docs/{index}/{uuid}/{scope}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncClearDocsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncClearDocsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncClearDocsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncClearDocsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AsyncClearDocsResourceWithStreamingResponse(self)

    async def clear_all(
        self,
        index: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Clear all docs for the given index

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
            f"/clear-docs/{index}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def clear_by_uuid(
        self,
        uuid: str,
        *,
        index: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Clear all docs for the given uuid within the index

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/clear-docs/{index}/{uuid}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def clear_by_uuid_and_scope(
        self,
        scope: str,
        *,
        index: str,
        uuid: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Clear all docs for the given uuid within the index and scope

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        if not scope:
            raise ValueError(f"Expected a non-empty value for `scope` but received {scope!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/clear-docs/{index}/{uuid}/{scope}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class ClearDocsResourceWithRawResponse:
    def __init__(self, clear_docs: ClearDocsResource) -> None:
        self._clear_docs = clear_docs

        self.clear_all = to_raw_response_wrapper(
            clear_docs.clear_all,
        )
        self.clear_by_uuid = to_raw_response_wrapper(
            clear_docs.clear_by_uuid,
        )
        self.clear_by_uuid_and_scope = to_raw_response_wrapper(
            clear_docs.clear_by_uuid_and_scope,
        )


class AsyncClearDocsResourceWithRawResponse:
    def __init__(self, clear_docs: AsyncClearDocsResource) -> None:
        self._clear_docs = clear_docs

        self.clear_all = async_to_raw_response_wrapper(
            clear_docs.clear_all,
        )
        self.clear_by_uuid = async_to_raw_response_wrapper(
            clear_docs.clear_by_uuid,
        )
        self.clear_by_uuid_and_scope = async_to_raw_response_wrapper(
            clear_docs.clear_by_uuid_and_scope,
        )


class ClearDocsResourceWithStreamingResponse:
    def __init__(self, clear_docs: ClearDocsResource) -> None:
        self._clear_docs = clear_docs

        self.clear_all = to_streamed_response_wrapper(
            clear_docs.clear_all,
        )
        self.clear_by_uuid = to_streamed_response_wrapper(
            clear_docs.clear_by_uuid,
        )
        self.clear_by_uuid_and_scope = to_streamed_response_wrapper(
            clear_docs.clear_by_uuid_and_scope,
        )


class AsyncClearDocsResourceWithStreamingResponse:
    def __init__(self, clear_docs: AsyncClearDocsResource) -> None:
        self._clear_docs = clear_docs

        self.clear_all = async_to_streamed_response_wrapper(
            clear_docs.clear_all,
        )
        self.clear_by_uuid = async_to_streamed_response_wrapper(
            clear_docs.clear_by_uuid,
        )
        self.clear_by_uuid_and_scope = async_to_streamed_response_wrapper(
            clear_docs.clear_by_uuid_and_scope,
        )
