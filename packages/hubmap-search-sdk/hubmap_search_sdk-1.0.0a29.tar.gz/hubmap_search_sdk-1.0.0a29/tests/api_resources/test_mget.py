# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from hubmap_search_sdk import HubmapSearchSDK, AsyncHubmapSearchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestMget:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_multiple(self, client: HubmapSearchSDK) -> None:
        mget = client.mget.retrieve_multiple(
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        )
        assert_matches_type(object, mget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_multiple(self, client: HubmapSearchSDK) -> None:
        response = client.mget.with_raw_response.retrieve_multiple(
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mget = response.parse()
        assert_matches_type(object, mget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_multiple(self, client: HubmapSearchSDK) -> None:
        with client.mget.with_streaming_response.retrieve_multiple(
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mget = response.parse()
            assert_matches_type(object, mget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_multiple_by_index(self, client: HubmapSearchSDK) -> None:
        mget = client.mget.retrieve_multiple_by_index(
            index_name="index_name",
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        )
        assert_matches_type(object, mget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_multiple_by_index(self, client: HubmapSearchSDK) -> None:
        response = client.mget.with_raw_response.retrieve_multiple_by_index(
            index_name="index_name",
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mget = response.parse()
        assert_matches_type(object, mget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_multiple_by_index(self, client: HubmapSearchSDK) -> None:
        with client.mget.with_streaming_response.retrieve_multiple_by_index(
            index_name="index_name",
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mget = response.parse()
            assert_matches_type(object, mget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve_multiple_by_index(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index_name` but received ''"):
            client.mget.with_raw_response.retrieve_multiple_by_index(
                index_name="",
                body={
                    "docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]
                },
            )


class TestAsyncMget:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_multiple(self, async_client: AsyncHubmapSearchSDK) -> None:
        mget = await async_client.mget.retrieve_multiple(
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        )
        assert_matches_type(object, mget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_multiple(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.mget.with_raw_response.retrieve_multiple(
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mget = await response.parse()
        assert_matches_type(object, mget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_multiple(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.mget.with_streaming_response.retrieve_multiple(
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mget = await response.parse()
            assert_matches_type(object, mget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_multiple_by_index(self, async_client: AsyncHubmapSearchSDK) -> None:
        mget = await async_client.mget.retrieve_multiple_by_index(
            index_name="index_name",
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        )
        assert_matches_type(object, mget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_multiple_by_index(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.mget.with_raw_response.retrieve_multiple_by_index(
            index_name="index_name",
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        mget = await response.parse()
        assert_matches_type(object, mget, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_multiple_by_index(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.mget.with_streaming_response.retrieve_multiple_by_index(
            index_name="index_name",
            body={"docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]},
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            mget = await response.parse()
            assert_matches_type(object, mget, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve_multiple_by_index(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index_name` but received ''"):
            await async_client.mget.with_raw_response.retrieve_multiple_by_index(
                index_name="",
                body={
                    "docs": [{"_id": "abcd1234ef56gh78ij90klmnop123456"}, {"_id": "abcd1234ef56gh78ij90klmnop123456"}]
                },
            )
