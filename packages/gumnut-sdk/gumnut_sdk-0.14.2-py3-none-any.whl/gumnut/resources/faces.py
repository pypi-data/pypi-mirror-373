# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..types import face_list_params, face_delete_params, face_update_params, face_retrieve_params
from .._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from .._utils import maybe_transform, async_maybe_transform
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
from ..types.face_response import FaceResponse

__all__ = ["FacesResource", "AsyncFacesResource"]


class FacesResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> FacesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return FacesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> FacesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return FacesResourceWithStreamingResponse(self)

    def retrieve(
        self,
        face_id: str,
        *,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaceResponse:
        """
        Retrieves details for a specific face.

        Args:
          library_id: Library ID (required if user has multiple libraries)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not face_id:
            raise ValueError(f"Expected a non-empty value for `face_id` but received {face_id!r}")
        return self._get(
            f"/api/faces/{face_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"library_id": library_id}, face_retrieve_params.FaceRetrieveParams),
            ),
            cast_to=FaceResponse,
        )

    def update(
        self,
        face_id: str,
        *,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        person_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaceResponse:
        """
        Updates the details of a specific face, currently only supporting
        associating/disassociating with a person.

        Args:
          library_id: Library ID (required if user has multiple libraries)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not face_id:
            raise ValueError(f"Expected a non-empty value for `face_id` but received {face_id!r}")
        return self._patch(
            f"/api/faces/{face_id}",
            body=maybe_transform({"person_id": person_id}, face_update_params.FaceUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"library_id": library_id}, face_update_params.FaceUpdateParams),
            ),
            cast_to=FaceResponse,
        )

    def list(
        self,
        *,
        asset_id: Optional[str] | NotGiven = NOT_GIVEN,
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
    ) -> SyncCursorPage[FaceResponse]:
        """
        Retrieves a paginated list of faces, optionally filtered by asset or person,
        ordered by creation time, descending.

        Args:
          asset_id: Filter by faces in a specific asset

          library_id: Library ID (required if user has multiple libraries)

          person_id: Filter by faces associated with a specific person

          starting_after_id: Face ID to start listing faces after

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/faces",
            page=SyncCursorPage[FaceResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "asset_id": asset_id,
                        "library_id": library_id,
                        "limit": limit,
                        "person_id": person_id,
                        "starting_after_id": starting_after_id,
                    },
                    face_list_params.FaceListParams,
                ),
            ),
            model=FaceResponse,
        )

    def delete(
        self,
        face_id: str,
        *,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Deletes a specific face entry.

        This does not delete the associated asset or
        person.

        Args:
          library_id: Library ID (required if user has multiple libraries)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not face_id:
            raise ValueError(f"Expected a non-empty value for `face_id` but received {face_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/api/faces/{face_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform({"library_id": library_id}, face_delete_params.FaceDeleteParams),
            ),
            cast_to=NoneType,
        )

    def download_thumbnail(
        self,
        face_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> BinaryAPIResponse:
        """
        Retrieves a thumbnail for a specific face.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not face_id:
            raise ValueError(f"Expected a non-empty value for `face_id` but received {face_id!r}")
        extra_headers = {"Accept": "image/*", **(extra_headers or {})}
        return self._get(
            f"/api/faces/{face_id}/thumbnail",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=BinaryAPIResponse,
        )


class AsyncFacesResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncFacesResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncFacesResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncFacesResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/gumnut-ai/photos-sdk-python#with_streaming_response
        """
        return AsyncFacesResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        face_id: str,
        *,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaceResponse:
        """
        Retrieves details for a specific face.

        Args:
          library_id: Library ID (required if user has multiple libraries)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not face_id:
            raise ValueError(f"Expected a non-empty value for `face_id` but received {face_id!r}")
        return await self._get(
            f"/api/faces/{face_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"library_id": library_id}, face_retrieve_params.FaceRetrieveParams),
            ),
            cast_to=FaceResponse,
        )

    async def update(
        self,
        face_id: str,
        *,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        person_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> FaceResponse:
        """
        Updates the details of a specific face, currently only supporting
        associating/disassociating with a person.

        Args:
          library_id: Library ID (required if user has multiple libraries)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not face_id:
            raise ValueError(f"Expected a non-empty value for `face_id` but received {face_id!r}")
        return await self._patch(
            f"/api/faces/{face_id}",
            body=await async_maybe_transform({"person_id": person_id}, face_update_params.FaceUpdateParams),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"library_id": library_id}, face_update_params.FaceUpdateParams),
            ),
            cast_to=FaceResponse,
        )

    def list(
        self,
        *,
        asset_id: Optional[str] | NotGiven = NOT_GIVEN,
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
    ) -> AsyncPaginator[FaceResponse, AsyncCursorPage[FaceResponse]]:
        """
        Retrieves a paginated list of faces, optionally filtered by asset or person,
        ordered by creation time, descending.

        Args:
          asset_id: Filter by faces in a specific asset

          library_id: Library ID (required if user has multiple libraries)

          person_id: Filter by faces associated with a specific person

          starting_after_id: Face ID to start listing faces after

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/api/faces",
            page=AsyncCursorPage[FaceResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "asset_id": asset_id,
                        "library_id": library_id,
                        "limit": limit,
                        "person_id": person_id,
                        "starting_after_id": starting_after_id,
                    },
                    face_list_params.FaceListParams,
                ),
            ),
            model=FaceResponse,
        )

    async def delete(
        self,
        face_id: str,
        *,
        library_id: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """Deletes a specific face entry.

        This does not delete the associated asset or
        person.

        Args:
          library_id: Library ID (required if user has multiple libraries)

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not face_id:
            raise ValueError(f"Expected a non-empty value for `face_id` but received {face_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/api/faces/{face_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform({"library_id": library_id}, face_delete_params.FaceDeleteParams),
            ),
            cast_to=NoneType,
        )

    async def download_thumbnail(
        self,
        face_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncBinaryAPIResponse:
        """
        Retrieves a thumbnail for a specific face.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not face_id:
            raise ValueError(f"Expected a non-empty value for `face_id` but received {face_id!r}")
        extra_headers = {"Accept": "image/*", **(extra_headers or {})}
        return await self._get(
            f"/api/faces/{face_id}/thumbnail",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AsyncBinaryAPIResponse,
        )


class FacesResourceWithRawResponse:
    def __init__(self, faces: FacesResource) -> None:
        self._faces = faces

        self.retrieve = to_raw_response_wrapper(
            faces.retrieve,
        )
        self.update = to_raw_response_wrapper(
            faces.update,
        )
        self.list = to_raw_response_wrapper(
            faces.list,
        )
        self.delete = to_raw_response_wrapper(
            faces.delete,
        )
        self.download_thumbnail = to_custom_raw_response_wrapper(
            faces.download_thumbnail,
            BinaryAPIResponse,
        )


class AsyncFacesResourceWithRawResponse:
    def __init__(self, faces: AsyncFacesResource) -> None:
        self._faces = faces

        self.retrieve = async_to_raw_response_wrapper(
            faces.retrieve,
        )
        self.update = async_to_raw_response_wrapper(
            faces.update,
        )
        self.list = async_to_raw_response_wrapper(
            faces.list,
        )
        self.delete = async_to_raw_response_wrapper(
            faces.delete,
        )
        self.download_thumbnail = async_to_custom_raw_response_wrapper(
            faces.download_thumbnail,
            AsyncBinaryAPIResponse,
        )


class FacesResourceWithStreamingResponse:
    def __init__(self, faces: FacesResource) -> None:
        self._faces = faces

        self.retrieve = to_streamed_response_wrapper(
            faces.retrieve,
        )
        self.update = to_streamed_response_wrapper(
            faces.update,
        )
        self.list = to_streamed_response_wrapper(
            faces.list,
        )
        self.delete = to_streamed_response_wrapper(
            faces.delete,
        )
        self.download_thumbnail = to_custom_streamed_response_wrapper(
            faces.download_thumbnail,
            StreamedBinaryAPIResponse,
        )


class AsyncFacesResourceWithStreamingResponse:
    def __init__(self, faces: AsyncFacesResource) -> None:
        self._faces = faces

        self.retrieve = async_to_streamed_response_wrapper(
            faces.retrieve,
        )
        self.update = async_to_streamed_response_wrapper(
            faces.update,
        )
        self.list = async_to_streamed_response_wrapper(
            faces.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            faces.delete,
        )
        self.download_thumbnail = async_to_custom_streamed_response_wrapper(
            faces.download_thumbnail,
            AsyncStreamedBinaryAPIResponse,
        )
