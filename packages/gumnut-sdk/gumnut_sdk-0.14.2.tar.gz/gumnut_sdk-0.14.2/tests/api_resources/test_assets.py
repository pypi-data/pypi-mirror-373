# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import httpx
import pytest
from respx import MockRouter

from gumnut import Gumnut, AsyncGumnut
from tests.utils import assert_matches_type
from gumnut.types import AssetResponse
from gumnut._utils import parse_datetime
from gumnut._response import (
    BinaryAPIResponse,
    AsyncBinaryAPIResponse,
    StreamedBinaryAPIResponse,
    AsyncStreamedBinaryAPIResponse,
)
from gumnut.pagination import SyncCursorPage, AsyncCursorPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestAssets:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Gumnut) -> None:
        asset = client.assets.create(
            asset_data=b"raw file contents",
            device_asset_id="device_asset_id",
            device_id="device_id",
            file_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            file_modified_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Gumnut) -> None:
        asset = client.assets.create(
            asset_data=b"raw file contents",
            device_asset_id="device_asset_id",
            device_id="device_id",
            file_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            file_modified_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            library_id="library_id",
        )
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Gumnut) -> None:
        response = client.assets.with_raw_response.create(
            asset_data=b"raw file contents",
            device_asset_id="device_asset_id",
            device_id="device_id",
            file_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            file_modified_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Gumnut) -> None:
        with client.assets.with_streaming_response.create(
            asset_data=b"raw file contents",
            device_asset_id="device_asset_id",
            device_id="device_id",
            file_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            file_modified_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(AssetResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Gumnut) -> None:
        asset = client.assets.retrieve(
            "asset_id",
        )
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Gumnut) -> None:
        response = client.assets.with_raw_response.retrieve(
            "asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Gumnut) -> None:
        with client.assets.with_streaming_response.retrieve(
            "asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(AssetResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            client.assets.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Gumnut) -> None:
        asset = client.assets.list()
        assert_matches_type(SyncCursorPage[AssetResponse], asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Gumnut) -> None:
        asset = client.assets.list(
            album_id="album_id",
            library_id="library_id",
            limit=1,
            person_id="person_id",
            starting_after_id="starting_after_id",
        )
        assert_matches_type(SyncCursorPage[AssetResponse], asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Gumnut) -> None:
        response = client.assets.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert_matches_type(SyncCursorPage[AssetResponse], asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Gumnut) -> None:
        with client.assets.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert_matches_type(SyncCursorPage[AssetResponse], asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Gumnut) -> None:
        asset = client.assets.delete(
            "asset_id",
        )
        assert asset is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Gumnut) -> None:
        response = client.assets.with_raw_response.delete(
            "asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = response.parse()
        assert asset is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Gumnut) -> None:
        with client.assets.with_streaming_response.delete(
            "asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = response.parse()
            assert asset is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            client.assets.with_raw_response.delete(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download(self, client: Gumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        asset = client.assets.download(
            "asset_id",
        )
        assert asset.is_closed
        assert asset.json() == {"foo": "bar"}
        assert cast(Any, asset.is_closed) is True
        assert isinstance(asset, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download(self, client: Gumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        asset = client.assets.with_raw_response.download(
            "asset_id",
        )

        assert asset.is_closed is True
        assert asset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert asset.json() == {"foo": "bar"}
        assert isinstance(asset, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download(self, client: Gumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.assets.with_streaming_response.download(
            "asset_id",
        ) as asset:
            assert not asset.is_closed
            assert asset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert asset.json() == {"foo": "bar"}
            assert cast(Any, asset.is_closed) is True
            assert isinstance(asset, StreamedBinaryAPIResponse)

        assert cast(Any, asset.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            client.assets.with_raw_response.download(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download_thumbnail(self, client: Gumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/thumbnail").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        asset = client.assets.download_thumbnail(
            asset_id="asset_id",
        )
        assert asset.is_closed
        assert asset.json() == {"foo": "bar"}
        assert cast(Any, asset.is_closed) is True
        assert isinstance(asset, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_method_download_thumbnail_with_all_params(self, client: Gumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/thumbnail").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        asset = client.assets.download_thumbnail(
            asset_id="asset_id",
            size="size",
        )
        assert asset.is_closed
        assert asset.json() == {"foo": "bar"}
        assert cast(Any, asset.is_closed) is True
        assert isinstance(asset, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_raw_response_download_thumbnail(self, client: Gumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/thumbnail").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        asset = client.assets.with_raw_response.download_thumbnail(
            asset_id="asset_id",
        )

        assert asset.is_closed is True
        assert asset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert asset.json() == {"foo": "bar"}
        assert isinstance(asset, BinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_streaming_response_download_thumbnail(self, client: Gumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/thumbnail").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        with client.assets.with_streaming_response.download_thumbnail(
            asset_id="asset_id",
        ) as asset:
            assert not asset.is_closed
            assert asset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert asset.json() == {"foo": "bar"}
            assert cast(Any, asset.is_closed) is True
            assert isinstance(asset, StreamedBinaryAPIResponse)

        assert cast(Any, asset.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    def test_path_params_download_thumbnail(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            client.assets.with_raw_response.download_thumbnail(
                asset_id="",
            )


class TestAsyncAssets:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncGumnut) -> None:
        asset = await async_client.assets.create(
            asset_data=b"raw file contents",
            device_asset_id="device_asset_id",
            device_id="device_id",
            file_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            file_modified_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGumnut) -> None:
        asset = await async_client.assets.create(
            asset_data=b"raw file contents",
            device_asset_id="device_asset_id",
            device_id="device_id",
            file_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            file_modified_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            library_id="library_id",
        )
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGumnut) -> None:
        response = await async_client.assets.with_raw_response.create(
            asset_data=b"raw file contents",
            device_asset_id="device_asset_id",
            device_id="device_id",
            file_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            file_modified_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGumnut) -> None:
        async with async_client.assets.with_streaming_response.create(
            asset_data=b"raw file contents",
            device_asset_id="device_asset_id",
            device_id="device_id",
            file_created_at=parse_datetime("2019-12-27T18:11:19.117Z"),
            file_modified_at=parse_datetime("2019-12-27T18:11:19.117Z"),
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(AssetResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGumnut) -> None:
        asset = await async_client.assets.retrieve(
            "asset_id",
        )
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGumnut) -> None:
        response = await async_client.assets.with_raw_response.retrieve(
            "asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(AssetResponse, asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGumnut) -> None:
        async with async_client.assets.with_streaming_response.retrieve(
            "asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(AssetResponse, asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            await async_client.assets.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncGumnut) -> None:
        asset = await async_client.assets.list()
        assert_matches_type(AsyncCursorPage[AssetResponse], asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGumnut) -> None:
        asset = await async_client.assets.list(
            album_id="album_id",
            library_id="library_id",
            limit=1,
            person_id="person_id",
            starting_after_id="starting_after_id",
        )
        assert_matches_type(AsyncCursorPage[AssetResponse], asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGumnut) -> None:
        response = await async_client.assets.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert_matches_type(AsyncCursorPage[AssetResponse], asset, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGumnut) -> None:
        async with async_client.assets.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert_matches_type(AsyncCursorPage[AssetResponse], asset, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncGumnut) -> None:
        asset = await async_client.assets.delete(
            "asset_id",
        )
        assert asset is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncGumnut) -> None:
        response = await async_client.assets.with_raw_response.delete(
            "asset_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        asset = await response.parse()
        assert asset is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncGumnut) -> None:
        async with async_client.assets.with_streaming_response.delete(
            "asset_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            asset = await response.parse()
            assert asset is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            await async_client.assets.with_raw_response.delete(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download(self, async_client: AsyncGumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        asset = await async_client.assets.download(
            "asset_id",
        )
        assert asset.is_closed
        assert await asset.json() == {"foo": "bar"}
        assert cast(Any, asset.is_closed) is True
        assert isinstance(asset, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download(self, async_client: AsyncGumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        asset = await async_client.assets.with_raw_response.download(
            "asset_id",
        )

        assert asset.is_closed is True
        assert asset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await asset.json() == {"foo": "bar"}
        assert isinstance(asset, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download(self, async_client: AsyncGumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/download").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.assets.with_streaming_response.download(
            "asset_id",
        ) as asset:
            assert not asset.is_closed
            assert asset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await asset.json() == {"foo": "bar"}
            assert cast(Any, asset.is_closed) is True
            assert isinstance(asset, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, asset.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            await async_client.assets.with_raw_response.download(
                "",
            )

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download_thumbnail(self, async_client: AsyncGumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/thumbnail").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        asset = await async_client.assets.download_thumbnail(
            asset_id="asset_id",
        )
        assert asset.is_closed
        assert await asset.json() == {"foo": "bar"}
        assert cast(Any, asset.is_closed) is True
        assert isinstance(asset, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_method_download_thumbnail_with_all_params(
        self, async_client: AsyncGumnut, respx_mock: MockRouter
    ) -> None:
        respx_mock.get("/api/assets/asset_id/thumbnail").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        asset = await async_client.assets.download_thumbnail(
            asset_id="asset_id",
            size="size",
        )
        assert asset.is_closed
        assert await asset.json() == {"foo": "bar"}
        assert cast(Any, asset.is_closed) is True
        assert isinstance(asset, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_raw_response_download_thumbnail(self, async_client: AsyncGumnut, respx_mock: MockRouter) -> None:
        respx_mock.get("/api/assets/asset_id/thumbnail").mock(return_value=httpx.Response(200, json={"foo": "bar"}))

        asset = await async_client.assets.with_raw_response.download_thumbnail(
            asset_id="asset_id",
        )

        assert asset.is_closed is True
        assert asset.http_request.headers.get("X-Stainless-Lang") == "python"
        assert await asset.json() == {"foo": "bar"}
        assert isinstance(asset, AsyncBinaryAPIResponse)

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_streaming_response_download_thumbnail(
        self, async_client: AsyncGumnut, respx_mock: MockRouter
    ) -> None:
        respx_mock.get("/api/assets/asset_id/thumbnail").mock(return_value=httpx.Response(200, json={"foo": "bar"}))
        async with async_client.assets.with_streaming_response.download_thumbnail(
            asset_id="asset_id",
        ) as asset:
            assert not asset.is_closed
            assert asset.http_request.headers.get("X-Stainless-Lang") == "python"

            assert await asset.json() == {"foo": "bar"}
            assert cast(Any, asset.is_closed) is True
            assert isinstance(asset, AsyncStreamedBinaryAPIResponse)

        assert cast(Any, asset.is_closed) is True

    @parametrize
    @pytest.mark.respx(base_url=base_url)
    async def test_path_params_download_thumbnail(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `asset_id` but received ''"):
            await async_client.assets.with_raw_response.download_thumbnail(
                asset_id="",
            )
