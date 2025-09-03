# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import (
    add_create_document_params,
    add_create_document_with_index_params,
    add_update_document_with_scope_params,
)
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

__all__ = ["AddResource", "AsyncAddResource"]


class AddResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AddResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AddResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AddResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AddResourceWithStreamingResponse(self)

    def create_document(
        self,
        uuid: str,
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
        Add a specific document with the passed in UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/add/{uuid}",
            body=maybe_transform(body, add_create_document_params.AddCreateDocumentParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def create_document_with_index(
        self,
        index: str,
        *,
        uuid: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a specific document with the passed in UUID and index

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/add/{uuid}/{index}",
            body=maybe_transform(body, add_create_document_with_index_params.AddCreateDocumentWithIndexParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def update_document_with_scope(
        self,
        scope: str,
        *,
        uuid: str,
        index: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Update a specific document with the passed in UUID, Index, and Scope

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        if not scope:
            raise ValueError(f"Expected a non-empty value for `scope` but received {scope!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._post(
            f"/add/{uuid}/{index}/{scope}",
            body=maybe_transform(body, add_update_document_with_scope_params.AddUpdateDocumentWithScopeParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncAddResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAddResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncAddResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAddResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AsyncAddResourceWithStreamingResponse(self)

    async def create_document(
        self,
        uuid: str,
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
        Add a specific document with the passed in UUID

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/add/{uuid}",
            body=await async_maybe_transform(body, add_create_document_params.AddCreateDocumentParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def create_document_with_index(
        self,
        index: str,
        *,
        uuid: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Create a specific document with the passed in UUID and index

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/add/{uuid}/{index}",
            body=await async_maybe_transform(
                body, add_create_document_with_index_params.AddCreateDocumentWithIndexParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def update_document_with_scope(
        self,
        scope: str,
        *,
        uuid: str,
        index: str,
        body: object,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Update a specific document with the passed in UUID, Index, and Scope

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not uuid:
            raise ValueError(f"Expected a non-empty value for `uuid` but received {uuid!r}")
        if not index:
            raise ValueError(f"Expected a non-empty value for `index` but received {index!r}")
        if not scope:
            raise ValueError(f"Expected a non-empty value for `scope` but received {scope!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._post(
            f"/add/{uuid}/{index}/{scope}",
            body=await async_maybe_transform(
                body, add_update_document_with_scope_params.AddUpdateDocumentWithScopeParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AddResourceWithRawResponse:
    def __init__(self, add: AddResource) -> None:
        self._add = add

        self.create_document = to_raw_response_wrapper(
            add.create_document,
        )
        self.create_document_with_index = to_raw_response_wrapper(
            add.create_document_with_index,
        )
        self.update_document_with_scope = to_raw_response_wrapper(
            add.update_document_with_scope,
        )


class AsyncAddResourceWithRawResponse:
    def __init__(self, add: AsyncAddResource) -> None:
        self._add = add

        self.create_document = async_to_raw_response_wrapper(
            add.create_document,
        )
        self.create_document_with_index = async_to_raw_response_wrapper(
            add.create_document_with_index,
        )
        self.update_document_with_scope = async_to_raw_response_wrapper(
            add.update_document_with_scope,
        )


class AddResourceWithStreamingResponse:
    def __init__(self, add: AddResource) -> None:
        self._add = add

        self.create_document = to_streamed_response_wrapper(
            add.create_document,
        )
        self.create_document_with_index = to_streamed_response_wrapper(
            add.create_document_with_index,
        )
        self.update_document_with_scope = to_streamed_response_wrapper(
            add.update_document_with_scope,
        )


class AsyncAddResourceWithStreamingResponse:
    def __init__(self, add: AsyncAddResource) -> None:
        self._add = add

        self.create_document = async_to_streamed_response_wrapper(
            add.create_document,
        )
        self.create_document_with_index = async_to_streamed_response_wrapper(
            add.create_document_with_index,
        )
        self.update_document_with_scope = async_to_streamed_response_wrapper(
            add.update_document_with_scope,
        )
