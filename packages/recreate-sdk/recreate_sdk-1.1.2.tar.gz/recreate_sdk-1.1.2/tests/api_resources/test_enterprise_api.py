# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tests.utils import assert_matches_type
from recreate_sdk import RecreateSDK, AsyncRecreateSDK
from recreate_sdk.types import (
    EnterpriseAPIValidateTokenResponse,
)
from recreate_sdk.types.enterprise_api import EnterpriseAPIResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestEnterpriseAPI:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_list_formats(self, client: RecreateSDK) -> None:
        enterprise_api = client.enterprise_api.list_formats()
        assert_matches_type(EnterpriseAPIResponse, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_list_formats(self, client: RecreateSDK) -> None:
        response = client.enterprise_api.with_raw_response.list_formats()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        enterprise_api = response.parse()
        assert_matches_type(EnterpriseAPIResponse, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_list_formats(self, client: RecreateSDK) -> None:
        with client.enterprise_api.with_streaming_response.list_formats() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            enterprise_api = response.parse()
            assert_matches_type(EnterpriseAPIResponse, enterprise_api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_unprotect_pdf(self, client: RecreateSDK) -> None:
        enterprise_api = client.enterprise_api.unprotect_pdf(
            file=b"raw file contents",
            password="password",
        )
        assert_matches_type(object, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_unprotect_pdf(self, client: RecreateSDK) -> None:
        response = client.enterprise_api.with_raw_response.unprotect_pdf(
            file=b"raw file contents",
            password="password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        enterprise_api = response.parse()
        assert_matches_type(object, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_unprotect_pdf(self, client: RecreateSDK) -> None:
        with client.enterprise_api.with_streaming_response.unprotect_pdf(
            file=b"raw file contents",
            password="password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            enterprise_api = response.parse()
            assert_matches_type(object, enterprise_api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_validate_token(self, client: RecreateSDK) -> None:
        enterprise_api = client.enterprise_api.validate_token(
            token="token",
        )
        assert_matches_type(EnterpriseAPIValidateTokenResponse, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_validate_token(self, client: RecreateSDK) -> None:
        response = client.enterprise_api.with_raw_response.validate_token(
            token="token",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        enterprise_api = response.parse()
        assert_matches_type(EnterpriseAPIValidateTokenResponse, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_validate_token(self, client: RecreateSDK) -> None:
        with client.enterprise_api.with_streaming_response.validate_token(
            token="token",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            enterprise_api = response.parse()
            assert_matches_type(EnterpriseAPIValidateTokenResponse, enterprise_api, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncEnterpriseAPI:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_list_formats(self, async_client: AsyncRecreateSDK) -> None:
        enterprise_api = await async_client.enterprise_api.list_formats()
        assert_matches_type(EnterpriseAPIResponse, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_list_formats(self, async_client: AsyncRecreateSDK) -> None:
        response = await async_client.enterprise_api.with_raw_response.list_formats()

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        enterprise_api = await response.parse()
        assert_matches_type(EnterpriseAPIResponse, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_list_formats(self, async_client: AsyncRecreateSDK) -> None:
        async with async_client.enterprise_api.with_streaming_response.list_formats() as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            enterprise_api = await response.parse()
            assert_matches_type(EnterpriseAPIResponse, enterprise_api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_unprotect_pdf(self, async_client: AsyncRecreateSDK) -> None:
        enterprise_api = await async_client.enterprise_api.unprotect_pdf(
            file=b"raw file contents",
            password="password",
        )
        assert_matches_type(object, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_unprotect_pdf(self, async_client: AsyncRecreateSDK) -> None:
        response = await async_client.enterprise_api.with_raw_response.unprotect_pdf(
            file=b"raw file contents",
            password="password",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        enterprise_api = await response.parse()
        assert_matches_type(object, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_unprotect_pdf(self, async_client: AsyncRecreateSDK) -> None:
        async with async_client.enterprise_api.with_streaming_response.unprotect_pdf(
            file=b"raw file contents",
            password="password",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            enterprise_api = await response.parse()
            assert_matches_type(object, enterprise_api, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_validate_token(self, async_client: AsyncRecreateSDK) -> None:
        enterprise_api = await async_client.enterprise_api.validate_token(
            token="token",
        )
        assert_matches_type(EnterpriseAPIValidateTokenResponse, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_validate_token(self, async_client: AsyncRecreateSDK) -> None:
        response = await async_client.enterprise_api.with_raw_response.validate_token(
            token="token",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        enterprise_api = await response.parse()
        assert_matches_type(EnterpriseAPIValidateTokenResponse, enterprise_api, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_validate_token(self, async_client: AsyncRecreateSDK) -> None:
        async with async_client.enterprise_api.with_streaming_response.validate_token(
            token="token",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            enterprise_api = await response.parse()
            assert_matches_type(EnterpriseAPIValidateTokenResponse, enterprise_api, path=["response"])

        assert cast(Any, response.is_closed) is True
