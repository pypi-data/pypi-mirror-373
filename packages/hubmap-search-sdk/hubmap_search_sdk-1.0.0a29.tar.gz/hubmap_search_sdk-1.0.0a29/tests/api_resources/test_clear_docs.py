# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hubmap_search_sdk import HubmapSearchSDK, AsyncHubmapSearchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestClearDocs:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear_all(self, client: HubmapSearchSDK) -> None:
        clear_doc = client.clear_docs.clear_all(
            "index",
        )
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear_all(self, client: HubmapSearchSDK) -> None:
        response = client.clear_docs.with_raw_response.clear_all(
            "index",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clear_doc = response.parse()
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear_all(self, client: HubmapSearchSDK) -> None:
        with client.clear_docs.with_streaming_response.clear_all(
            "index",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clear_doc = response.parse()
            assert clear_doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clear_all(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            client.clear_docs.with_raw_response.clear_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear_by_uuid(self, client: HubmapSearchSDK) -> None:
        clear_doc = client.clear_docs.clear_by_uuid(
            uuid="uuid",
            index="index",
        )
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear_by_uuid(self, client: HubmapSearchSDK) -> None:
        response = client.clear_docs.with_raw_response.clear_by_uuid(
            uuid="uuid",
            index="index",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clear_doc = response.parse()
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear_by_uuid(self, client: HubmapSearchSDK) -> None:
        with client.clear_docs.with_streaming_response.clear_by_uuid(
            uuid="uuid",
            index="index",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clear_doc = response.parse()
            assert clear_doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clear_by_uuid(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            client.clear_docs.with_raw_response.clear_by_uuid(
                uuid="uuid",
                index="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            client.clear_docs.with_raw_response.clear_by_uuid(
                uuid="",
                index="index",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_clear_by_uuid_and_scope(self, client: HubmapSearchSDK) -> None:
        clear_doc = client.clear_docs.clear_by_uuid_and_scope(
            scope="scope",
            index="index",
            uuid="uuid",
        )
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_clear_by_uuid_and_scope(self, client: HubmapSearchSDK) -> None:
        response = client.clear_docs.with_raw_response.clear_by_uuid_and_scope(
            scope="scope",
            index="index",
            uuid="uuid",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clear_doc = response.parse()
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_clear_by_uuid_and_scope(self, client: HubmapSearchSDK) -> None:
        with client.clear_docs.with_streaming_response.clear_by_uuid_and_scope(
            scope="scope",
            index="index",
            uuid="uuid",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clear_doc = response.parse()
            assert clear_doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_clear_by_uuid_and_scope(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            client.clear_docs.with_raw_response.clear_by_uuid_and_scope(
                scope="scope",
                index="",
                uuid="uuid",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            client.clear_docs.with_raw_response.clear_by_uuid_and_scope(
                scope="scope",
                index="index",
                uuid="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `scope` but received ''"):
            client.clear_docs.with_raw_response.clear_by_uuid_and_scope(
                scope="",
                index="index",
                uuid="uuid",
            )


class TestAsyncClearDocs:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear_all(self, async_client: AsyncHubmapSearchSDK) -> None:
        clear_doc = await async_client.clear_docs.clear_all(
            "index",
        )
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear_all(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.clear_docs.with_raw_response.clear_all(
            "index",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clear_doc = await response.parse()
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear_all(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.clear_docs.with_streaming_response.clear_all(
            "index",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clear_doc = await response.parse()
            assert clear_doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clear_all(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            await async_client.clear_docs.with_raw_response.clear_all(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear_by_uuid(self, async_client: AsyncHubmapSearchSDK) -> None:
        clear_doc = await async_client.clear_docs.clear_by_uuid(
            uuid="uuid",
            index="index",
        )
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear_by_uuid(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.clear_docs.with_raw_response.clear_by_uuid(
            uuid="uuid",
            index="index",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clear_doc = await response.parse()
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear_by_uuid(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.clear_docs.with_streaming_response.clear_by_uuid(
            uuid="uuid",
            index="index",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clear_doc = await response.parse()
            assert clear_doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clear_by_uuid(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            await async_client.clear_docs.with_raw_response.clear_by_uuid(
                uuid="uuid",
                index="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            await async_client.clear_docs.with_raw_response.clear_by_uuid(
                uuid="",
                index="index",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_clear_by_uuid_and_scope(self, async_client: AsyncHubmapSearchSDK) -> None:
        clear_doc = await async_client.clear_docs.clear_by_uuid_and_scope(
            scope="scope",
            index="index",
            uuid="uuid",
        )
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_clear_by_uuid_and_scope(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.clear_docs.with_raw_response.clear_by_uuid_and_scope(
            scope="scope",
            index="index",
            uuid="uuid",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        clear_doc = await response.parse()
        assert clear_doc is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_clear_by_uuid_and_scope(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.clear_docs.with_streaming_response.clear_by_uuid_and_scope(
            scope="scope",
            index="index",
            uuid="uuid",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            clear_doc = await response.parse()
            assert clear_doc is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_clear_by_uuid_and_scope(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            await async_client.clear_docs.with_raw_response.clear_by_uuid_and_scope(
                scope="scope",
                index="",
                uuid="uuid",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            await async_client.clear_docs.with_raw_response.clear_by_uuid_and_scope(
                scope="scope",
                index="index",
                uuid="",
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `scope` but received ''"):
            await async_client.clear_docs.with_raw_response.clear_by_uuid_and_scope(
                scope="",
                index="index",
                uuid="uuid",
            )
