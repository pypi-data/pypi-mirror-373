# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from .assets import (
    AssetsResource,
    AsyncAssetsResource,
    AssetsResourceWithRawResponse,
    AsyncAssetsResourceWithRawResponse,
    AssetsResourceWithStreamingResponse,
    AsyncAssetsResourceWithStreamingResponse,
)
from ...types import album_list_params, album_create_params, album_update_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncCursorPage, AsyncCursorPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.album_response import AlbumResponse

__all__ = ["AlbumsResource", "AsyncAlbumsResource"]


class AlbumsResource(SyncAPIResource):
    @cached_property
    def assets(self) -> AssetsResource:
        return AssetsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AlbumsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AlbumsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AlbumsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return AlbumsResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AlbumResponse:
        """
        Creates a new, empty album with optional name and description in the specified
        library.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/api/albums",
            body=maybe_transform(
                {
                    "description": description,
                    "library_id": library_id,
                    "name": name,
                },
                album_create_params.AlbumCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AlbumResponse,
        )

    def retrieve(
        self,
        album_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AlbumResponse:
        """
        Retrieves details for a specific album.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        return self._get(
            f"/api/albums/{album_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AlbumResponse,
        )

    def update(
        self,
        album_id: str,
        *,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AlbumResponse:
        """
        Updates the name and/or description of a specific album.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        return self._patch(
            f"/api/albums/{album_id}",
            body=maybe_transform(
                {
                    "description": description,
                    "name": name,
                },
                album_update_params.AlbumUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AlbumResponse,
        )

    def list(
        self,
        *,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        starting_after_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[AlbumResponse]:
        """
        Retrieves a paginated list of albums from the specified library, ordered by
        creation time, descending.

        Args:
          library_id: Library to list albums from (optional)

          starting_after_id: Album ID to start listing albums after

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/albums",
            page=SyncCursorPage[AlbumResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "library_id": library_id,
                        "limit": limit,
                        "starting_after_id": starting_after_id,
                    },
                    album_list_params.AlbumListParams,
                ),
            ),
            model=AlbumResponse,
        )

    def delete(
        self,
        album_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Deletes a specific album.

        Note: This does not delete the assets within the
        album.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/albums/{album_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncAlbumsResource(AsyncAPIResource):
    @cached_property
    def assets(self) -> AsyncAssetsResource:
        return AsyncAssetsResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncAlbumsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAlbumsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAlbumsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return AsyncAlbumsResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AlbumResponse:
        """
        Creates a new, empty album with optional name and description in the specified
        library.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/api/albums",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "library_id": library_id,
                    "name": name,
                },
                album_create_params.AlbumCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AlbumResponse,
        )

    async def retrieve(
        self,
        album_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AlbumResponse:
        """
        Retrieves details for a specific album.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        return await self._get(
            f"/api/albums/{album_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AlbumResponse,
        )

    async def update(
        self,
        album_id: str,
        *,
        description: Optional[str] | NotGiven = NOT_GIVEN,
        name: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AlbumResponse:
        """
        Updates the name and/or description of a specific album.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        return await self._patch(
            f"/api/albums/{album_id}",
            body=await async_maybe_transform(
                {
                    "description": description,
                    "name": name,
                },
                album_update_params.AlbumUpdateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AlbumResponse,
        )

    def list(
        self,
        *,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        starting_after_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[AlbumResponse, AsyncCursorPage[AlbumResponse]]:
        """
        Retrieves a paginated list of albums from the specified library, ordered by
        creation time, descending.

        Args:
          library_id: Library to list albums from (optional)

          starting_after_id: Album ID to start listing albums after

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/albums",
            page=AsyncCursorPage[AlbumResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "library_id": library_id,
                        "limit": limit,
                        "starting_after_id": starting_after_id,
                    },
                    album_list_params.AlbumListParams,
                ),
            ),
            model=AlbumResponse,
        )

    async def delete(
        self,
        album_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Deletes a specific album.

        Note: This does not delete the assets within the
        album.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/albums/{album_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AlbumsResourceWithRawResponse:
    def __init__(self, albums: AlbumsResource) -> None:
        self._albums = albums

        self.create = to_raw_response_wrapper(
            albums.create,
        )
        self.retrieve = to_raw_response_wrapper(
            albums.retrieve,
        )
        self.update = to_raw_response_wrapper(
            albums.update,
        )
        self.list = to_raw_response_wrapper(
            albums.list,
        )
        self.delete = to_raw_response_wrapper(
            albums.delete,
        )

    @cached_property
    def assets(self) -> AssetsResourceWithRawResponse:
        return AssetsResourceWithRawResponse(self._albums.assets)


class AsyncAlbumsResourceWithRawResponse:
    def __init__(self, albums: AsyncAlbumsResource) -> None:
        self._albums = albums

        self.create = async_to_raw_response_wrapper(
            albums.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            albums.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            albums.update,
        )
        self.list = async_to_raw_response_wrapper(
            albums.list,
        )
        self.delete = async_to_raw_response_wrapper(
            albums.delete,
        )

    @cached_property
    def assets(self) -> AsyncAssetsResourceWithRawResponse:
        return AsyncAssetsResourceWithRawResponse(self._albums.assets)


class AlbumsResourceWithStreamingResponse:
    def __init__(self, albums: AlbumsResource) -> None:
        self._albums = albums

        self.create = to_streamed_response_wrapper(
            albums.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            albums.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            albums.update,
        )
        self.list = to_streamed_response_wrapper(
            albums.list,
        )
        self.delete = to_streamed_response_wrapper(
            albums.delete,
        )

    @cached_property
    def assets(self) -> AssetsResourceWithStreamingResponse:
        return AssetsResourceWithStreamingResponse(self._albums.assets)


class AsyncAlbumsResourceWithStreamingResponse:
    def __init__(self, albums: AsyncAlbumsResource) -> None:
        self._albums = albums

        self.create = async_to_streamed_response_wrapper(
            albums.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            albums.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            albums.update,
        )
        self.list = async_to_streamed_response_wrapper(
            albums.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            albums.delete,
        )

    @cached_property
    def assets(self) -> AsyncAssetsResourceWithStreamingResponse:
        return AsyncAssetsResourceWithStreamingResponse(self._albums.assets)
