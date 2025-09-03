# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime

import httpx

from ..types import search_search_params
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
from ..types.search_response import SearchResponse

__all__ = ["SearchResource", "AsyncSearchResource"]


class SearchResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return SearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return SearchResourceWithStreamingResponse(self)

    def search(
        self,
        *,
        captured_after: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        captured_before: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        person_ids: List[str] | NotGiven = NOT_GIVEN,
        query: Optional[str] | NotGiven = NOT_GIVEN,
        threshold: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchResponse:
        """Searches for assets using semantic similarity and/or metadata filters.

        Results
        include asset metadata, faces, and people. At least one search criterion must be
        provided.

        Args:
          captured_after: Filter to only include assets captured after this date (ISO format).

          captured_before: Filter to only include assets captured before this date (ISO format).

          library_id: Library to search assets from (optional)

          limit: Number of results per page

          page: Page number

          person_ids: Filter to only include assets containing ALL of these person IDs. Can be
              comma-delimited string (e.g. 'person_123,person_abc') or multiple query
              parameters.

          query: The text query to search for. If you want to search for a specific person or set
              of people, use the person_ids parameter instead.If you want to search for a
              photos taken during a specific date range, use the captured_before and
              captured_after parameters instead.

          threshold: Similarity threshold (lower means more similar)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/api/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "captured_after": captured_after,
                        "captured_before": captured_before,
                        "library_id": library_id,
                        "limit": limit,
                        "page": page,
                        "person_ids": person_ids,
                        "query": query,
                        "threshold": threshold,
                    },
                    search_search_params.SearchSearchParams,
                ),
            ),
            cast_to=SearchResponse,
        )


class AsyncSearchResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSearchResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSearchResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSearchResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return AsyncSearchResourceWithStreamingResponse(self)

    async def search(
        self,
        *,
        captured_after: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        captured_before: Union[str, datetime, None] | NotGiven = NOT_GIVEN,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        page: int | NotGiven = NOT_GIVEN,
        person_ids: List[str] | NotGiven = NOT_GIVEN,
        query: Optional[str] | NotGiven = NOT_GIVEN,
        threshold: float | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SearchResponse:
        """Searches for assets using semantic similarity and/or metadata filters.

        Results
        include asset metadata, faces, and people. At least one search criterion must be
        provided.

        Args:
          captured_after: Filter to only include assets captured after this date (ISO format).

          captured_before: Filter to only include assets captured before this date (ISO format).

          library_id: Library to search assets from (optional)

          limit: Number of results per page

          page: Page number

          person_ids: Filter to only include assets containing ALL of these person IDs. Can be
              comma-delimited string (e.g. 'person_123,person_abc') or multiple query
              parameters.

          query: The text query to search for. If you want to search for a specific person or set
              of people, use the person_ids parameter instead.If you want to search for a
              photos taken during a specific date range, use the captured_before and
              captured_after parameters instead.

          threshold: Similarity threshold (lower means more similar)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/api/search",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "captured_after": captured_after,
                        "captured_before": captured_before,
                        "library_id": library_id,
                        "limit": limit,
                        "page": page,
                        "person_ids": person_ids,
                        "query": query,
                        "threshold": threshold,
                    },
                    search_search_params.SearchSearchParams,
                ),
            ),
            cast_to=SearchResponse,
        )


class SearchResourceWithRawResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.search = to_raw_response_wrapper(
            search.search,
        )


class AsyncSearchResourceWithRawResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.search = async_to_raw_response_wrapper(
            search.search,
        )


class SearchResourceWithStreamingResponse:
    def __init__(self, search: SearchResource) -> None:
        self._search = search

        self.search = to_streamed_response_wrapper(
            search.search,
        )


class AsyncSearchResourceWithStreamingResponse:
    def __init__(self, search: AsyncSearchResource) -> None:
        self._search = search

        self.search = async_to_streamed_response_wrapper(
            search.search,
        )
