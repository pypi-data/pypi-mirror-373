# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gumnut import Gumnut, AsyncGumnut
from tests.utils import assert_matches_type
from gumnut.types import PersonResponse
from gumnut._utils import parse_date
from gumnut.pagination import SyncCursorPage, AsyncCursorPage

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestPeople:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: Gumnut) -> None:
        person = client.people.create()
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: Gumnut) -> None:
        person = client.people.create(
            birth_date=parse_date("2019-12-27"),
            is_favorite=True,
            is_hidden=True,
            library_id="library_id",
            name="name",
            thumbnail_face_id="thumbnail_face_id",
        )
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: Gumnut) -> None:
        response = client.people.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = response.parse()
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: Gumnut) -> None:
        with client.people.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = response.parse()
            assert_matches_type(PersonResponse, person, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Gumnut) -> None:
        person = client.people.retrieve(
            "person_id",
        )
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Gumnut) -> None:
        response = client.people.with_raw_response.retrieve(
            "person_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = response.parse()
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Gumnut) -> None:
        with client.people.with_streaming_response.retrieve(
            "person_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = response.parse()
            assert_matches_type(PersonResponse, person, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `person_id` but received ''"):
            client.people.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update(self, client: Gumnut) -> None:
        person = client.people.update(
            person_id="person_id",
        )
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_with_all_params(self, client: Gumnut) -> None:
        person = client.people.update(
            person_id="person_id",
            birth_date=parse_date("2019-12-27"),
            is_favorite=True,
            is_hidden=True,
            name="name",
            thumbnail_face_id="thumbnail_face_id",
        )
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update(self, client: Gumnut) -> None:
        response = client.people.with_raw_response.update(
            person_id="person_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = response.parse()
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update(self, client: Gumnut) -> None:
        with client.people.with_streaming_response.update(
            person_id="person_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = response.parse()
            assert_matches_type(PersonResponse, person, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `person_id` but received ''"):
            client.people.with_raw_response.update(
                person_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list(self, client: Gumnut) -> None:
        person = client.people.list()
        assert_matches_type(SyncCursorPage[PersonResponse], person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_with_all_params(self, client: Gumnut) -> None:
        person = client.people.list(
            album_id="album_id",
            asset_id="asset_id",
            library_id="library_id",
            limit=1,
            starting_after_id="starting_after_id",
        )
        assert_matches_type(SyncCursorPage[PersonResponse], person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list(self, client: Gumnut) -> None:
        response = client.people.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = response.parse()
        assert_matches_type(SyncCursorPage[PersonResponse], person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list(self, client: Gumnut) -> None:
        with client.people.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = response.parse()
            assert_matches_type(SyncCursorPage[PersonResponse], person, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_delete(self, client: Gumnut) -> None:
        person = client.people.delete(
            "person_id",
        )
        assert person is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_delete(self, client: Gumnut) -> None:
        response = client.people.with_raw_response.delete(
            "person_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = response.parse()
        assert person is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_delete(self, client: Gumnut) -> None:
        with client.people.with_streaming_response.delete(
            "person_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = response.parse()
            assert person is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_delete(self, client: Gumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `person_id` but received ''"):
            client.people.with_raw_response.delete(
                "",
            )


class TestAsyncPeople:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncGumnut) -> None:
        person = await async_client.people.create()
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncGumnut) -> None:
        person = await async_client.people.create(
            birth_date=parse_date("2019-12-27"),
            is_favorite=True,
            is_hidden=True,
            library_id="library_id",
            name="name",
            thumbnail_face_id="thumbnail_face_id",
        )
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncGumnut) -> None:
        response = await async_client.people.with_raw_response.create()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = await response.parse()
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncGumnut) -> None:
        async with async_client.people.with_streaming_response.create() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = await response.parse()
            assert_matches_type(PersonResponse, person, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncGumnut) -> None:
        person = await async_client.people.retrieve(
            "person_id",
        )
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncGumnut) -> None:
        response = await async_client.people.with_raw_response.retrieve(
            "person_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = await response.parse()
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncGumnut) -> None:
        async with async_client.people.with_streaming_response.retrieve(
            "person_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = await response.parse()
            assert_matches_type(PersonResponse, person, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `person_id` but received ''"):
            await async_client.people.with_raw_response.retrieve(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update(self, async_client: AsyncGumnut) -> None:
        person = await async_client.people.update(
            person_id="person_id",
        )
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_with_all_params(self, async_client: AsyncGumnut) -> None:
        person = await async_client.people.update(
            person_id="person_id",
            birth_date=parse_date("2019-12-27"),
            is_favorite=True,
            is_hidden=True,
            name="name",
            thumbnail_face_id="thumbnail_face_id",
        )
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update(self, async_client: AsyncGumnut) -> None:
        response = await async_client.people.with_raw_response.update(
            person_id="person_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = await response.parse()
        assert_matches_type(PersonResponse, person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update(self, async_client: AsyncGumnut) -> None:
        async with async_client.people.with_streaming_response.update(
            person_id="person_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = await response.parse()
            assert_matches_type(PersonResponse, person, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `person_id` but received ''"):
            await async_client.people.with_raw_response.update(
                person_id="",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list(self, async_client: AsyncGumnut) -> None:
        person = await async_client.people.list()
        assert_matches_type(AsyncCursorPage[PersonResponse], person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_with_all_params(self, async_client: AsyncGumnut) -> None:
        person = await async_client.people.list(
            album_id="album_id",
            asset_id="asset_id",
            library_id="library_id",
            limit=1,
            starting_after_id="starting_after_id",
        )
        assert_matches_type(AsyncCursorPage[PersonResponse], person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list(self, async_client: AsyncGumnut) -> None:
        response = await async_client.people.with_raw_response.list()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = await response.parse()
        assert_matches_type(AsyncCursorPage[PersonResponse], person, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list(self, async_client: AsyncGumnut) -> None:
        async with async_client.people.with_streaming_response.list() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = await response.parse()
            assert_matches_type(AsyncCursorPage[PersonResponse], person, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_delete(self, async_client: AsyncGumnut) -> None:
        person = await async_client.people.delete(
            "person_id",
        )
        assert person is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_delete(self, async_client: AsyncGumnut) -> None:
        response = await async_client.people.with_raw_response.delete(
            "person_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        person = await response.parse()
        assert person is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_delete(self, async_client: AsyncGumnut) -> None:
        async with async_client.people.with_streaming_response.delete(
            "person_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            person = await response.parse()
            assert person is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_delete(self, async_client: AsyncGumnut) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `person_id` but received ''"):
            await async_client.people.with_raw_response.delete(
                "",
            )
