# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from hubmap_search_sdk import HubmapSearchSDK, AsyncHubmapSearchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSearch:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_index_query(self, client: HubmapSearchSDK) -> None:
        search = client.search.execute_index_query(
            index_name="index_name",
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        )
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_index_query_with_all_params(self, client: HubmapSearchSDK) -> None:
        search = client.search.execute_index_query(
            index_name="index_name",
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
            produce_clt_manifest="produce-clt-manifest",
        )
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_index_query(self, client: HubmapSearchSDK) -> None:
        response = client.search.with_raw_response.execute_index_query(
            index_name="index_name",
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = response.parse()
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_index_query(self, client: HubmapSearchSDK) -> None:
        with client.search.with_streaming_response.execute_index_query(
            index_name="index_name",
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = response.parse()
            assert_matches_type(object, search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_execute_index_query(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index_name` but received ''"):
            client.search.with_raw_response.execute_index_query(
                index_name="",
                body={
                    "query": {
                        "bool": {
                            "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                            "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                        }
                    }
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_query(self, client: HubmapSearchSDK) -> None:
        search = client.search.execute_query(
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        )
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_execute_query_with_all_params(self, client: HubmapSearchSDK) -> None:
        search = client.search.execute_query(
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
            produce_clt_manifest="produce-clt-manifest",
        )
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_execute_query(self, client: HubmapSearchSDK) -> None:
        response = client.search.with_raw_response.execute_query(
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = response.parse()
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_execute_query(self, client: HubmapSearchSDK) -> None:
        with client.search.with_streaming_response.execute_query(
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = response.parse()
            assert_matches_type(object, search, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSearch:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_index_query(self, async_client: AsyncHubmapSearchSDK) -> None:
        search = await async_client.search.execute_index_query(
            index_name="index_name",
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        )
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_index_query_with_all_params(self, async_client: AsyncHubmapSearchSDK) -> None:
        search = await async_client.search.execute_index_query(
            index_name="index_name",
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
            produce_clt_manifest="produce-clt-manifest",
        )
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_index_query(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.search.with_raw_response.execute_index_query(
            index_name="index_name",
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = await response.parse()
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_index_query(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.search.with_streaming_response.execute_index_query(
            index_name="index_name",
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = await response.parse()
            assert_matches_type(object, search, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_execute_index_query(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index_name` but received ''"):
            await async_client.search.with_raw_response.execute_index_query(
                index_name="",
                body={
                    "query": {
                        "bool": {
                            "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                            "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                        }
                    }
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_query(self, async_client: AsyncHubmapSearchSDK) -> None:
        search = await async_client.search.execute_query(
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        )
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_execute_query_with_all_params(self, async_client: AsyncHubmapSearchSDK) -> None:
        search = await async_client.search.execute_query(
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
            produce_clt_manifest="produce-clt-manifest",
        )
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_execute_query(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.search.with_raw_response.execute_query(
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        search = await response.parse()
        assert_matches_type(object, search, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_execute_query(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.search.with_streaming_response.execute_query(
            body={
                "query": {
                    "bool": {
                        "must": [{"match_phrase": {"donor.group_name": "Vanderbilt TMC"}}],
                        "filter": [{"match": {"entity_type.keyword": "Sample"}}],
                    }
                }
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            search = await response.parse()
            assert_matches_type(object, search, path=["response"])

        assert cast(Any, response.is_closed) is True
