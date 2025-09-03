# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from hubmap_search_sdk import HubmapSearchSDK, AsyncHubmapSearchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestParamSearch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute(self, client: HubmapSearchSDK) -> None:
        param_search = client.param_search.execute(
            entity_type="entity_type",
        )
        assert_matches_type(object, param_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_with_all_params(self, client: HubmapSearchSDK) -> None:
        param_search = client.param_search.execute(
            entity_type="entity_type",
            produce_clt_manifest="produce-clt-manifest",
        )
        assert_matches_type(object, param_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute(self, client: HubmapSearchSDK) -> None:
        response = client.param_search.with_raw_response.execute(
            entity_type="entity_type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        param_search = response.parse()
        assert_matches_type(object, param_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute(self, client: HubmapSearchSDK) -> None:
        with client.param_search.with_streaming_response.execute(
            entity_type="entity_type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            param_search = response.parse()
            assert_matches_type(object, param_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_execute(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_type` but received ''"):
            client.param_search.with_raw_response.execute(
                entity_type="",
            )


class TestAsyncParamSearch:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute(self, async_client: AsyncHubmapSearchSDK) -> None:
        param_search = await async_client.param_search.execute(
            entity_type="entity_type",
        )
        assert_matches_type(object, param_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_with_all_params(self, async_client: AsyncHubmapSearchSDK) -> None:
        param_search = await async_client.param_search.execute(
            entity_type="entity_type",
            produce_clt_manifest="produce-clt-manifest",
        )
        assert_matches_type(object, param_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.param_search.with_raw_response.execute(
            entity_type="entity_type",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        param_search = await response.parse()
        assert_matches_type(object, param_search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.param_search.with_streaming_response.execute(
            entity_type="entity_type",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            param_search = await response.parse()
            assert_matches_type(object, param_search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_execute(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `entity_type` but received ''"):
            await async_client.param_search.with_raw_response.execute(
                entity_type="",
            )
