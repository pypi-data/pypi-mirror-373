# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from hubmap_search_sdk import HubmapSearchSDK, AsyncHubmapSearchSDK

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUpdate:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_document(self, client: HubmapSearchSDK) -> None:
        update = client.update.update_document(
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_document(self, client: HubmapSearchSDK) -> None:
        response = client.update.with_raw_response.update_document(
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        update = response.parse()
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_document(self, client: HubmapSearchSDK) -> None:
        with client.update.with_streaming_response.update_document(
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            update = response.parse()
            assert update is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_document(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            client.update.with_raw_response.update_document(
                uuid="",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_document_at_index(self, client: HubmapSearchSDK) -> None:
        update = client.update.update_document_at_index(
            index="index",
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_document_at_index(self, client: HubmapSearchSDK) -> None:
        response = client.update.with_raw_response.update_document_at_index(
            index="index",
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        update = response.parse()
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_document_at_index(self, client: HubmapSearchSDK) -> None:
        with client.update.with_streaming_response.update_document_at_index(
            index="index",
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            update = response.parse()
            assert update is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_document_at_index(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            client.update.with_raw_response.update_document_at_index(
                index="index",
                uuid="",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            client.update.with_raw_response.update_document_at_index(
                index="",
                uuid="uuid",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_update_document_with_scope(self, client: HubmapSearchSDK) -> None:
        update = client.update.update_document_with_scope(
            scope="scope",
            uuid="uuid",
            index="index",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_update_document_with_scope(self, client: HubmapSearchSDK) -> None:
        response = client.update.with_raw_response.update_document_with_scope(
            scope="scope",
            uuid="uuid",
            index="index",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        update = response.parse()
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_update_document_with_scope(self, client: HubmapSearchSDK) -> None:
        with client.update.with_streaming_response.update_document_with_scope(
            scope="scope",
            uuid="uuid",
            index="index",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            update = response.parse()
            assert update is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_update_document_with_scope(self, client: HubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            client.update.with_raw_response.update_document_with_scope(
                scope="scope",
                uuid="",
                index="index",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            client.update.with_raw_response.update_document_with_scope(
                scope="scope",
                uuid="uuid",
                index="",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `scope` but received ''"):
            client.update.with_raw_response.update_document_with_scope(
                scope="",
                uuid="uuid",
                index="index",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )


class TestAsyncUpdate:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_document(self, async_client: AsyncHubmapSearchSDK) -> None:
        update = await async_client.update.update_document(
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_document(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.update.with_raw_response.update_document(
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        update = await response.parse()
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_document(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.update.with_streaming_response.update_document(
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            update = await response.parse()
            assert update is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_document(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            await async_client.update.with_raw_response.update_document(
                uuid="",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_document_at_index(self, async_client: AsyncHubmapSearchSDK) -> None:
        update = await async_client.update.update_document_at_index(
            index="index",
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_document_at_index(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.update.with_raw_response.update_document_at_index(
            index="index",
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        update = await response.parse()
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_document_at_index(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.update.with_streaming_response.update_document_at_index(
            index="index",
            uuid="uuid",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            update = await response.parse()
            assert update is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_document_at_index(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            await async_client.update.with_raw_response.update_document_at_index(
                index="index",
                uuid="",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            await async_client.update.with_raw_response.update_document_at_index(
                index="",
                uuid="uuid",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_update_document_with_scope(self, async_client: AsyncHubmapSearchSDK) -> None:
        update = await async_client.update.update_document_with_scope(
            scope="scope",
            uuid="uuid",
            index="index",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_update_document_with_scope(self, async_client: AsyncHubmapSearchSDK) -> None:
        response = await async_client.update.with_raw_response.update_document_with_scope(
            scope="scope",
            uuid="uuid",
            index="index",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        update = await response.parse()
        assert update is None

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_update_document_with_scope(self, async_client: AsyncHubmapSearchSDK) -> None:
        async with async_client.update.with_streaming_response.update_document_with_scope(
            scope="scope",
            uuid="uuid",
            index="index",
            body={
                "uuid": "abcd1234ef56gh78ij90klmnop123456",
                "entity_type": "Sample",
                "sample_category": "organ",
                "organ": "heart",
                "donor": {
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Donor",
                },
                "ancestors": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
                "descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "immediate_ancestors": [
                    {
                        "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                        "entity_type": "Sample",
                    }
                ],
                "immediate_descendants": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Dataset",
                    }
                ],
                "origin_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                        "organ": "heart",
                    }
                ],
                "source_samples": [
                    {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Sample",
                    }
                ],
            },
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            update = await response.parse()
            assert update is None

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_update_document_with_scope(self, async_client: AsyncHubmapSearchSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `uuid` but received ''"):
            await async_client.update.with_raw_response.update_document_with_scope(
                scope="scope",
                uuid="",
                index="index",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `index` but received ''"):
            await async_client.update.with_raw_response.update_document_with_scope(
                scope="scope",
                uuid="uuid",
                index="",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )

        with pytest.raises(ValueError, match=r"Expected a non-empty value for `scope` but received ''"):
            await async_client.update.with_raw_response.update_document_with_scope(
                scope="",
                uuid="uuid",
                index="index",
                body={
                    "uuid": "abcd1234ef56gh78ij90klmnop123456",
                    "entity_type": "Sample",
                    "sample_category": "organ",
                    "organ": "heart",
                    "donor": {
                        "uuid": "abcd1234ef56gh78ij90klmnop123456",
                        "entity_type": "Donor",
                    },
                    "ancestors": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                    "descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "immediate_ancestors": [
                        {
                            "uuid": "xyz9876-5432-10dc-ba98-76543210fedc",
                            "entity_type": "Sample",
                        }
                    ],
                    "immediate_descendants": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Dataset",
                        }
                    ],
                    "origin_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                            "organ": "heart",
                        }
                    ],
                    "source_samples": [
                        {
                            "uuid": "abcd1234ef56gh78ij90klmnop123456",
                            "entity_type": "Sample",
                        }
                    ],
                },
            )
