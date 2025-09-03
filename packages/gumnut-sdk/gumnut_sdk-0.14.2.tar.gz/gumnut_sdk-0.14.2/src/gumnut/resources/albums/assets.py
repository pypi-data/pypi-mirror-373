# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List

import httpx

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
from ..._base_client import make_request_options
from ...types.albums import asset_add_params, asset_remove_params
from ...types.albums.asset_add_response import AssetAddResponse
from ...types.albums.asset_list_response import AssetListResponse

__all__ = ["AssetsResource", "AsyncAssetsResource"]


class AssetsResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AssetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AssetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AssetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return AssetsResourceWithStreamingResponse(self)

    def list(
        self,
        album_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetListResponse:
        """
        Retrieves a list of all assets contained within a specific album, along with
        their associated metrics, EXIF data, faces, and people.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        return self._get(
            f"/api/albums/{album_id}/assets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetListResponse,
        )

    def add(
        self,
        album_id: str,
        *,
        asset_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetAddResponse:
        """Adds one or more existing assets to a specific album.

        Assets must be in the same
        library as the album. Duplicate assets are ignored.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        return self._post(
            f"/api/albums/{album_id}/assets",
            body=maybe_transform({"asset_ids": asset_ids}, asset_add_params.AssetAddParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetAddResponse,
        )

    def remove(
        self,
        album_id: str,
        *,
        asset_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Removes one or more assets from a specific album.

        Note: This does not delete the
        assets themselves.

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
            f"/api/albums/{album_id}/assets",
            body=maybe_transform({"asset_ids": asset_ids}, asset_remove_params.AssetRemoveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AsyncAssetsResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAssetsResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAssetsResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAssetsResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return AsyncAssetsResourceWithStreamingResponse(self)

    async def list(
        self,
        album_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetListResponse:
        """
        Retrieves a list of all assets contained within a specific album, along with
        their associated metrics, EXIF data, faces, and people.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        return await self._get(
            f"/api/albums/{album_id}/assets",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetListResponse,
        )

    async def add(
        self,
        album_id: str,
        *,
        asset_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetAddResponse:
        """Adds one or more existing assets to a specific album.

        Assets must be in the same
        library as the album. Duplicate assets are ignored.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not album_id:
            raise ValueError(f"Expected a non-empty value for `album_id` but received {album_id!r}")
        return await self._post(
            f"/api/albums/{album_id}/assets",
            body=await async_maybe_transform({"asset_ids": asset_ids}, asset_add_params.AssetAddParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetAddResponse,
        )

    async def remove(
        self,
        album_id: str,
        *,
        asset_ids: List[str],
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Removes one or more assets from a specific album.

        Note: This does not delete the
        assets themselves.

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
            f"/api/albums/{album_id}/assets",
            body=await async_maybe_transform({"asset_ids": asset_ids}, asset_remove_params.AssetRemoveParams),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )


class AssetsResourceWithRawResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.list = to_raw_response_wrapper(
            assets.list,
        )
        self.add = to_raw_response_wrapper(
            assets.add,
        )
        self.remove = to_raw_response_wrapper(
            assets.remove,
        )


class AsyncAssetsResourceWithRawResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.list = async_to_raw_response_wrapper(
            assets.list,
        )
        self.add = async_to_raw_response_wrapper(
            assets.add,
        )
        self.remove = async_to_raw_response_wrapper(
            assets.remove,
        )


class AssetsResourceWithStreamingResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.list = to_streamed_response_wrapper(
            assets.list,
        )
        self.add = to_streamed_response_wrapper(
            assets.add,
        )
        self.remove = to_streamed_response_wrapper(
            assets.remove,
        )


class AsyncAssetsResourceWithStreamingResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.list = async_to_streamed_response_wrapper(
            assets.list,
        )
        self.add = async_to_streamed_response_wrapper(
            assets.add,
        )
        self.remove = async_to_streamed_response_wrapper(
            assets.remove,
        )
