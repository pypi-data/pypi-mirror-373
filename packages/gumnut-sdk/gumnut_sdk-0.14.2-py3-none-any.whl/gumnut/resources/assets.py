# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Union, Mapping, Optional, cast
from datetime import datetime

import httpx

from ..types import asset_list_params, asset_create_params, asset_download_thumbnail_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven, FileTypes
from .._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    to_custom_raw_response_wrapper,
    async_to_streamed_response_wrapper,
    to_custom_streamed_response_wrapper,
    async_to_custom_raw_response_wrapper,
    async_to_custom_streamed_response_wrapper,
)
from ..pagination import SyncCursorPage, AsyncCursorPage
from .._base_client import AsyncPaginator, make_request_options
from ..types.asset_response import AssetResponse

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

    def create(
        self,
        *,
        asset_data: FileTypes,
        device_asset_id: str,
        device_id: str,
        file_created_at: Union[str, datetime],
        file_modified_at: Union[str, datetime],
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetResponse:
        """
        Uploads a new asset file (image or video) along with its metadata to the
        specified library. If no library_id is provided and the user only has one
        library, uses that library. If the user has multiple libraries, library_id is
        required.

        Args:
          library_id: Library to upload asset to (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "asset_data": asset_data,
                "device_asset_id": device_asset_id,
                "device_id": device_id,
                "file_created_at": file_created_at,
                "file_modified_at": file_modified_at,
                "library_id": library_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["asset_data"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/api/assets",
            body=maybe_transform(body, asset_create_params.AssetCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetResponse,
        )

    def retrieve(
        self,
        asset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetResponse:
        """
        Retrieves detailed metadata for a specific asset, including EXIF information,
        asset metrics, faces, and people.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        return self._get(
            f"/api/assets/{asset_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetResponse,
        )

    def list(
        self,
        *,
        album_id: Optional[str] | NotGiven = NOT_GIVEN,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        person_id: Optional[str] | NotGiven = NOT_GIVEN,
        starting_after_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncCursorPage[AssetResponse]:
        """
        Retrieves a paginated list of assets from the specified library, optionally
        filtered by album or person. Asset data includes metrics, EXIF data, faces, and
        people. Assets are ordered by local creation time, descending.

        Args:
          album_id: Filter by assets in a specific album

          library_id: Library to list assets from (optional)

          person_id: Filter by assets associated with a specific person ID

          starting_after_id: Asset ID to start listing assets after

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/assets",
            page=SyncCursorPage[AssetResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "album_id": album_id,
                        "library_id": library_id,
                        "limit": limit,
                        "person_id": person_id,
                        "starting_after_id": starting_after_id,
                    },
                    asset_list_params.AssetListParams,
                ),
            ),
            model=AssetResponse,
        )

    def delete(
        self,
        asset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Deletes a specific asset and its associated data (including the file from
        storage).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/assets/{asset_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    def download(
        self,
        asset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Downloads the original file for a specific asset.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        extra_headers = {"Accept": "image/*", **(extra_headers or {})}
        return self._get(
            f"/api/assets/{asset_id}/download",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )

    def download_thumbnail(
        self,
        asset_id: str,
        *,
        size: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """Downloads a thumbnail for a specific asset.

        The exact thumbnail returned depends
        on availability and the optional `size` parameter.

        Args:
          size: Desired thumbnail size (e.g., thumbnail, preview)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        extra_headers = {"Accept": "image/*", **(extra_headers or {})}
        return self._get(
            f"/api/assets/{asset_id}/thumbnail",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"size": size}, asset_download_thumbnail_params.AssetDownloadThumbnailParams),
            ),
            cast_to=BinaryAPIResponse,
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

    async def create(
        self,
        *,
        asset_data: FileTypes,
        device_asset_id: str,
        device_id: str,
        file_created_at: Union[str, datetime],
        file_modified_at: Union[str, datetime],
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetResponse:
        """
        Uploads a new asset file (image or video) along with its metadata to the
        specified library. If no library_id is provided and the user only has one
        library, uses that library. If the user has multiple libraries, library_id is
        required.

        Args:
          library_id: Library to upload asset to (optional)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "asset_data": asset_data,
                "device_asset_id": device_asset_id,
                "device_id": device_id,
                "file_created_at": file_created_at,
                "file_modified_at": file_modified_at,
                "library_id": library_id,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["asset_data"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/api/assets",
            body=await async_maybe_transform(body, asset_create_params.AssetCreateParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetResponse,
        )

    async def retrieve(
        self,
        asset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AssetResponse:
        """
        Retrieves detailed metadata for a specific asset, including EXIF information,
        asset metrics, faces, and people.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        return await self._get(
            f"/api/assets/{asset_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AssetResponse,
        )

    def list(
        self,
        *,
        album_id: Optional[str] | NotGiven = NOT_GIVEN,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        person_id: Optional[str] | NotGiven = NOT_GIVEN,
        starting_after_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[AssetResponse, AsyncCursorPage[AssetResponse]]:
        """
        Retrieves a paginated list of assets from the specified library, optionally
        filtered by album or person. Asset data includes metrics, EXIF data, faces, and
        people. Assets are ordered by local creation time, descending.

        Args:
          album_id: Filter by assets in a specific album

          library_id: Library to list assets from (optional)

          person_id: Filter by assets associated with a specific person ID

          starting_after_id: Asset ID to start listing assets after

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/assets",
            page=AsyncCursorPage[AssetResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "album_id": album_id,
                        "library_id": library_id,
                        "limit": limit,
                        "person_id": person_id,
                        "starting_after_id": starting_after_id,
                    },
                    asset_list_params.AssetListParams,
                ),
            ),
            model=AssetResponse,
        )

    async def delete(
        self,
        asset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Deletes a specific asset and its associated data (including the file from
        storage).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/assets/{asset_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
        )

    async def download(
        self,
        asset_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Downloads the original file for a specific asset.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        extra_headers = {"Accept": "image/*", **(extra_headers or {})}
        return await self._get(
            f"/api/assets/{asset_id}/download",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )

    async def download_thumbnail(
        self,
        asset_id: str,
        *,
        size: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """Downloads a thumbnail for a specific asset.

        The exact thumbnail returned depends
        on availability and the optional `size` parameter.

        Args:
          size: Desired thumbnail size (e.g., thumbnail, preview)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not asset_id:
            raise ValueError(f"Expected a non-empty value for `asset_id` but received {asset_id!r}")
        extra_headers = {"Accept": "image/*", **(extra_headers or {})}
        return await self._get(
            f"/api/assets/{asset_id}/thumbnail",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"size": size}, asset_download_thumbnail_params.AssetDownloadThumbnailParams
                ),
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class AssetsResourceWithRawResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.create = to_raw_response_wrapper(
            assets.create,
        )
        self.retrieve = to_raw_response_wrapper(
            assets.retrieve,
        )
        self.list = to_raw_response_wrapper(
            assets.list,
        )
        self.delete = to_raw_response_wrapper(
            assets.delete,
        )
        self.download = to_custom_raw_response_wrapper(
            assets.download,
            BinaryAPIResponse,
        )
        self.download_thumbnail = to_custom_raw_response_wrapper(
            assets.download_thumbnail,
            BinaryAPIResponse,
        )


class AsyncAssetsResourceWithRawResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.create = async_to_raw_response_wrapper(
            assets.create,
        )
        self.retrieve = async_to_raw_response_wrapper(
            assets.retrieve,
        )
        self.list = async_to_raw_response_wrapper(
            assets.list,
        )
        self.delete = async_to_raw_response_wrapper(
            assets.delete,
        )
        self.download = async_to_custom_raw_response_wrapper(
            assets.download,
            AsyncBinaryAPIResponse,
        )
        self.download_thumbnail = async_to_custom_raw_response_wrapper(
            assets.download_thumbnail,
            AsyncBinaryAPIResponse,
        )


class AssetsResourceWithStreamingResponse:
    def __init__(self, assets: AssetsResource) -> None:
        self._assets = assets

        self.create = to_streamed_response_wrapper(
            assets.create,
        )
        self.retrieve = to_streamed_response_wrapper(
            assets.retrieve,
        )
        self.list = to_streamed_response_wrapper(
            assets.list,
        )
        self.delete = to_streamed_response_wrapper(
            assets.delete,
        )
        self.download = to_custom_streamed_response_wrapper(
            assets.download,
            StreamedBinaryAPIResponse,
        )
        self.download_thumbnail = to_custom_streamed_response_wrapper(
            assets.download_thumbnail,
            StreamedBinaryAPIResponse,
        )


class AsyncAssetsResourceWithStreamingResponse:
    def __init__(self, assets: AsyncAssetsResource) -> None:
        self._assets = assets

        self.create = async_to_streamed_response_wrapper(
            assets.create,
        )
        self.retrieve = async_to_streamed_response_wrapper(
            assets.retrieve,
        )
        self.list = async_to_streamed_response_wrapper(
            assets.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            assets.delete,
        )
        self.download = async_to_custom_streamed_response_wrapper(
            assets.download,
            AsyncStreamedBinaryAPIResponse,
        )
        self.download_thumbnail = async_to_custom_streamed_response_wrapper(
            assets.download_thumbnail,
            AsyncStreamedBinaryAPIResponse,
        )
