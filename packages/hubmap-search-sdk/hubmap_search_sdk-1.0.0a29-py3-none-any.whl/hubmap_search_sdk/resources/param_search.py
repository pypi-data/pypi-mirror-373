# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import param_search_execute_params
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

__all__ = ["ParamSearchResource", "AsyncParamSearchResource"]


class ParamSearchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ParamSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return ParamSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ParamSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return ParamSearchResourceWithStreamingResponse(self)

    def execute(
        self,
        entity_type: str,
        *,
        produce_clt_manifest: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Searches datasets based on the given parameter entity-type ('donor', 'dataset',
        'sample', etc). GET method must provide a bearer token in the Authorization
        header supplied by HuBMAP. Results are limited to those authorized by the bearer
        token. For more detailed information on using this endpoint see
        [Detailed Param Search Docs](https://docs.hubmapconsortium.org/param-search)

        Args:
          produce_clt_manifest: An optional parameter that, when set to "true", will make the endpoint return a
              text representation of a manifest file that corresponds with the datasets
              queried rather than the original response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not entity_type:
            raise ValueError(f"Expected a non-empty value for `entity_type` but received {entity_type!r}")
        return self._get(
            f"/param-search/{entity_type}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"produce_clt_manifest": produce_clt_manifest}, param_search_execute_params.ParamSearchExecuteParams
                ),
            ),
            cast_to=object,
        )


class AsyncParamSearchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncParamSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncParamSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncParamSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/hubmapconsortium/search-python-sdk#with_streaming_response
        """
        return AsyncParamSearchResourceWithStreamingResponse(self)

    async def execute(
        self,
        entity_type: str,
        *,
        produce_clt_manifest: str | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Searches datasets based on the given parameter entity-type ('donor', 'dataset',
        'sample', etc). GET method must provide a bearer token in the Authorization
        header supplied by HuBMAP. Results are limited to those authorized by the bearer
        token. For more detailed information on using this endpoint see
        [Detailed Param Search Docs](https://docs.hubmapconsortium.org/param-search)

        Args:
          produce_clt_manifest: An optional parameter that, when set to "true", will make the endpoint return a
              text representation of a manifest file that corresponds with the datasets
              queried rather than the original response

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not entity_type:
            raise ValueError(f"Expected a non-empty value for `entity_type` but received {entity_type!r}")
        return await self._get(
            f"/param-search/{entity_type}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"produce_clt_manifest": produce_clt_manifest}, param_search_execute_params.ParamSearchExecuteParams
                ),
            ),
            cast_to=object,
        )


class ParamSearchResourceWithRawResponse:
    def __init__(self, param_search: ParamSearchResource) -> None:
        self._param_search = param_search

        self.execute = to_raw_response_wrapper(
            param_search.execute,
        )


class AsyncParamSearchResourceWithRawResponse:
    def __init__(self, param_search: AsyncParamSearchResource) -> None:
        self._param_search = param_search

        self.execute = async_to_raw_response_wrapper(
            param_search.execute,
        )


class ParamSearchResourceWithStreamingResponse:
    def __init__(self, param_search: ParamSearchResource) -> None:
        self._param_search = param_search

        self.execute = to_streamed_response_wrapper(
            param_search.execute,
        )


class AsyncParamSearchResourceWithStreamingResponse:
    def __init__(self, param_search: AsyncParamSearchResource) -> None:
        self._param_search = param_search

        self.execute = async_to_streamed_response_wrapper(
            param_search.execute,
        )
