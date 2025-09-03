# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hubmap_search_sdk import HubmapSearchSDK, AsyncHubmapSearchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestScrollSearch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: HubmapSearchSDK) -> None:
        scroll_search = client.scroll_search.create(
            index="index",
            body={
                "scroll_open_minutes": 5,
                "scroll_id": "abc123",
            },
        )
        assert scroll_search is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: HubmapSearchSDK) -> None:
        response = client.scroll_search.with_raw_response.create(
            index="index",
            body={
                "scroll_open_minutes": 5,
                "scroll_id": "abc123",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scroll_search = response.parse()
        assert scroll_search is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: HubmapSearchSDK) -> None:
        with client.scroll_search.with_streaming_response.create(
            index="index",
            body={
                "scroll_open_minutes": 5,
                "scroll_id": "abc123",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scroll_search = response.parse()
            assert scroll_search is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_create(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            client.scroll_search.with_raw_response.create(
                index="",
                body={
                    "scroll_open_minutes": 5,
                    "scroll_id": "abc123",
                },
            )


class TestAsyncScrollSearch:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncHubmapSearchSDK) -> None:
        scroll_search = await async_client.scroll_search.create(
            index="index",
            body={
                "scroll_open_minutes": 5,
                "scroll_id": "abc123",
            },
        )
        assert scroll_search is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.scroll_search.with_raw_response.create(
            index="index",
            body={
                "scroll_open_minutes": 5,
                "scroll_id": "abc123",
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        scroll_search = await response.parse()
        assert scroll_search is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.scroll_search.with_streaming_response.create(
            index="index",
            body={
                "scroll_open_minutes": 5,
                "scroll_id": "abc123",
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            scroll_search = await response.parse()
            assert scroll_search is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_create(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            await async_client.scroll_search.with_raw_response.create(
                index="",
                body={
                    "scroll_open_minutes": 5,
                    "scroll_id": "abc123",
                },
            )
