# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gumnut import Gumnut, AsyncGumnut
from tests.utils import assert_matches_type
from gumnut.types import LibraryResponse, LibraryListResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestLibraries:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Gumnut) -> None:
        library = client.libraries.create(
            name="name",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Gumnut) -> None:
        library = client.libraries.create(
            name="name",
            description="description",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Gumnut) -> None:
        response = client.libraries.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = response.parse()
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Gumnut) -> None:
        with client.libraries.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = response.parse()
            assert_matches_type(LibraryResponse, library, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Gumnut) -> None:
        library = client.libraries.retrieve(
            "library_id",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Gumnut) -> None:
        response = client.libraries.with_raw_response.retrieve(
            "library_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = response.parse()
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Gumnut) -> None:
        with client.libraries.with_streaming_response.retrieve(
            "library_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = response.parse()
            assert_matches_type(LibraryResponse, library, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `library_id` but received ''"):
            client.libraries.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Gumnut) -> None:
        library = client.libraries.update(
            library_id="library_id",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Gumnut) -> None:
        library = client.libraries.update(
            library_id="library_id",
            description="description",
            name="name",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Gumnut) -> None:
        response = client.libraries.with_raw_response.update(
            library_id="library_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = response.parse()
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Gumnut) -> None:
        with client.libraries.with_streaming_response.update(
            library_id="library_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = response.parse()
            assert_matches_type(LibraryResponse, library, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `library_id` but received ''"):
            client.libraries.with_raw_response.update(
                library_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Gumnut) -> None:
        library = client.libraries.list()
        assert_matches_type(LibraryListResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Gumnut) -> None:
        response = client.libraries.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = response.parse()
        assert_matches_type(LibraryListResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Gumnut) -> None:
        with client.libraries.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = response.parse()
            assert_matches_type(LibraryListResponse, library, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Gumnut) -> None:
        library = client.libraries.delete(
            "library_id",
        )
        assert library is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Gumnut) -> None:
        response = client.libraries.with_raw_response.delete(
            "library_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = response.parse()
        assert library is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Gumnut) -> None:
        with client.libraries.with_streaming_response.delete(
            "library_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = response.parse()
            assert library is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `library_id` but received ''"):
            client.libraries.with_raw_response.delete(
                "",
            )


class TestAsyncLibraries:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncGumnut) -> None:
        library = await async_client.libraries.create(
            name="name",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGumnut) -> None:
        library = await async_client.libraries.create(
            name="name",
            description="description",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGumnut) -> None:
        response = await async_client.libraries.with_raw_response.create(
            name="name",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = await response.parse()
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGumnut) -> None:
        async with async_client.libraries.with_streaming_response.create(
            name="name",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = await response.parse()
            assert_matches_type(LibraryResponse, library, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGumnut) -> None:
        library = await async_client.libraries.retrieve(
            "library_id",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGumnut) -> None:
        response = await async_client.libraries.with_raw_response.retrieve(
            "library_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = await response.parse()
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGumnut) -> None:
        async with async_client.libraries.with_streaming_response.retrieve(
            "library_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = await response.parse()
            assert_matches_type(LibraryResponse, library, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `library_id` but received ''"):
            await async_client.libraries.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncGumnut) -> None:
        library = await async_client.libraries.update(
            library_id="library_id",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncGumnut) -> None:
        library = await async_client.libraries.update(
            library_id="library_id",
            description="description",
            name="name",
        )
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncGumnut) -> None:
        response = await async_client.libraries.with_raw_response.update(
            library_id="library_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = await response.parse()
        assert_matches_type(LibraryResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncGumnut) -> None:
        async with async_client.libraries.with_streaming_response.update(
            library_id="library_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = await response.parse()
            assert_matches_type(LibraryResponse, library, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `library_id` but received ''"):
            await async_client.libraries.with_raw_response.update(
                library_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncGumnut) -> None:
        library = await async_client.libraries.list()
        assert_matches_type(LibraryListResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGumnut) -> None:
        response = await async_client.libraries.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = await response.parse()
        assert_matches_type(LibraryListResponse, library, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGumnut) -> None:
        async with async_client.libraries.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = await response.parse()
            assert_matches_type(LibraryListResponse, library, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncGumnut) -> None:
        library = await async_client.libraries.delete(
            "library_id",
        )
        assert library is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncGumnut) -> None:
        response = await async_client.libraries.with_raw_response.delete(
            "library_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        library = await response.parse()
        assert library is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncGumnut) -> None:
        async with async_client.libraries.with_streaming_response.delete(
            "library_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            library = await response.parse()
            assert library is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `library_id` but received ''"):
            await async_client.libraries.with_raw_response.delete(
                "",
            )
