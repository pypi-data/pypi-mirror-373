# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from gumnut import Gumnut, AsyncGumnut
from tests.utils import assert_matches_type
from gumnut.types import SearchResponse
from gumnut._utils import parse_datetime

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSearch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search(self, client: Gumnut) -> None:
        search = client.search.search()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_search_with_all_params(self, client: Gumnut) -> None:
        search = client.search.search(
            captured_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            captured_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            library_id="library_id",
            limit=1,
            page=1,
            person_ids=["string"],
            query="query",
            threshold=0,
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_search(self, client: Gumnut) -> None:
        response = client.search.with_raw_response.search()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = response.parse()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_search(self, client: Gumnut) -> None:
        with client.search.with_streaming_response.search() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = response.parse()
            assert_matches_type(SearchResponse, search, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSearch:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search(self, async_client: AsyncGumnut) -> None:
        search = await async_client.search.search()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_search_with_all_params(self, async_client: AsyncGumnut) -> None:
        search = await async_client.search.search(
            captured_after=parse_datetime("2019-12-27T18:11:19.117Z"),
            captured_before=parse_datetime("2019-12-27T18:11:19.117Z"),
            library_id="library_id",
            limit=1,
            page=1,
            person_ids=["string"],
            query="query",
            threshold=0,
        )
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_search(self, async_client: AsyncGumnut) -> None:
        response = await async_client.search.with_raw_response.search()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = await response.parse()
        assert_matches_type(SearchResponse, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_search(self, async_client: AsyncGumnut) -> None:
        async with async_client.search.with_streaming_response.search() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = await response.parse()
            assert_matches_type(SearchResponse, search, path=["response"])

        assert cast(Any, response.is_closed) is True
