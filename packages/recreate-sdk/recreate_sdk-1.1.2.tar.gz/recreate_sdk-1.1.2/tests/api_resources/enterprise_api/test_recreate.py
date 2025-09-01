# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from recreate_sdk import RecreateSDK, AsyncRecreateSDK
from recreate_sdk.types.enterprise_api import (
    EnterpriseAPIResponse,
    RecreateGetJsonResponse,
)

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestRecreate:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: RecreateSDK) -> None:
        recreate = client.enterprise_api.recreate.create(
            file=b"raw file contents",
            selected_pages="selected_pages",
        )
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: RecreateSDK) -> None:
        recreate = client.enterprise_api.recreate.create(
            file=b"raw file contents",
            selected_pages="selected_pages",
            is_ppt_process_enabled="is_ppt_process_enabled",
            is_xls_process_charts_enabled="is_xls_process_charts_enabled",
            is_xls_process_tables_enabled="is_xls_process_tables_enabled",
            selected_table_format="selected_table_format",
        )
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: RecreateSDK) -> None:
        response = client.enterprise_api.recreate.with_raw_response.create(
            file=b"raw file contents",
            selected_pages="selected_pages",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recreate = response.parse()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: RecreateSDK) -> None:
        with client.enterprise_api.recreate.with_streaming_response.create(
            file=b"raw file contents",
            selected_pages="selected_pages",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recreate = response.parse()
            assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_get_json(self, client: RecreateSDK) -> None:
        recreate = client.enterprise_api.recreate.get_json(
            "recreate_id",
        )
        assert_matches_type(RecreateGetJsonResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_get_json(self, client: RecreateSDK) -> None:
        response = client.enterprise_api.recreate.with_raw_response.get_json(
            "recreate_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recreate = response.parse()
        assert_matches_type(RecreateGetJsonResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_get_json(self, client: RecreateSDK) -> None:
        with client.enterprise_api.recreate.with_streaming_response.get_json(
            "recreate_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recreate = response.parse()
            assert_matches_type(RecreateGetJsonResponse, recreate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_get_json(self, client: RecreateSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `recreate_id` but received ''"):
            client.enterprise_api.recreate.with_raw_response.get_json(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_hide(self, client: RecreateSDK) -> None:
        recreate = client.enterprise_api.recreate.hide()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_hide(self, client: RecreateSDK) -> None:
        response = client.enterprise_api.recreate.with_raw_response.hide()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recreate = response.parse()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_hide(self, client: RecreateSDK) -> None:
        with client.enterprise_api.recreate.with_streaming_response.hide() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recreate = response.parse()
            assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_status(self, client: RecreateSDK) -> None:
        recreate = client.enterprise_api.recreate.retrieve_status()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve_status_with_all_params(self, client: RecreateSDK) -> None:
        recreate = client.enterprise_api.recreate.retrieve_status(
            recreate_id="recreate_id",
        )
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve_status(self, client: RecreateSDK) -> None:
        response = client.enterprise_api.recreate.with_raw_response.retrieve_status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recreate = response.parse()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve_status(self, client: RecreateSDK) -> None:
        with client.enterprise_api.recreate.with_streaming_response.retrieve_status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recreate = response.parse()
            assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncRecreate:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncRecreateSDK) -> None:
        recreate = await async_client.enterprise_api.recreate.create(
            file=b"raw file contents",
            selected_pages="selected_pages",
        )
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncRecreateSDK) -> None:
        recreate = await async_client.enterprise_api.recreate.create(
            file=b"raw file contents",
            selected_pages="selected_pages",
            is_ppt_process_enabled="is_ppt_process_enabled",
            is_xls_process_charts_enabled="is_xls_process_charts_enabled",
            is_xls_process_tables_enabled="is_xls_process_tables_enabled",
            selected_table_format="selected_table_format",
        )
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncRecreateSDK) -> None:
        response = await async_client.enterprise_api.recreate.with_raw_response.create(
            file=b"raw file contents",
            selected_pages="selected_pages",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recreate = await response.parse()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncRecreateSDK) -> None:
        async with async_client.enterprise_api.recreate.with_streaming_response.create(
            file=b"raw file contents",
            selected_pages="selected_pages",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recreate = await response.parse()
            assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_get_json(self, async_client: AsyncRecreateSDK) -> None:
        recreate = await async_client.enterprise_api.recreate.get_json(
            "recreate_id",
        )
        assert_matches_type(RecreateGetJsonResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_get_json(self, async_client: AsyncRecreateSDK) -> None:
        response = await async_client.enterprise_api.recreate.with_raw_response.get_json(
            "recreate_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recreate = await response.parse()
        assert_matches_type(RecreateGetJsonResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_get_json(self, async_client: AsyncRecreateSDK) -> None:
        async with async_client.enterprise_api.recreate.with_streaming_response.get_json(
            "recreate_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recreate = await response.parse()
            assert_matches_type(RecreateGetJsonResponse, recreate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_get_json(self, async_client: AsyncRecreateSDK) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `recreate_id` but received ''"):
            await async_client.enterprise_api.recreate.with_raw_response.get_json(
                "",
            )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_hide(self, async_client: AsyncRecreateSDK) -> None:
        recreate = await async_client.enterprise_api.recreate.hide()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_hide(self, async_client: AsyncRecreateSDK) -> None:
        response = await async_client.enterprise_api.recreate.with_raw_response.hide()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recreate = await response.parse()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_hide(self, async_client: AsyncRecreateSDK) -> None:
        async with async_client.enterprise_api.recreate.with_streaming_response.hide() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recreate = await response.parse()
            assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_status(self, async_client: AsyncRecreateSDK) -> None:
        recreate = await async_client.enterprise_api.recreate.retrieve_status()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve_status_with_all_params(self, async_client: AsyncRecreateSDK) -> None:
        recreate = await async_client.enterprise_api.recreate.retrieve_status(
            recreate_id="recreate_id",
        )
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve_status(self, async_client: AsyncRecreateSDK) -> None:
        response = await async_client.enterprise_api.recreate.with_raw_response.retrieve_status()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        recreate = await response.parse()
        assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve_status(self, async_client: AsyncRecreateSDK) -> None:
        async with async_client.enterprise_api.recreate.with_streaming_response.retrieve_status() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            recreate = await response.parse()
            assert_matches_type(EnterpriseAPIResponse, recreate, path=["response"])

        assert cast(Any, response.is_closed) is True
