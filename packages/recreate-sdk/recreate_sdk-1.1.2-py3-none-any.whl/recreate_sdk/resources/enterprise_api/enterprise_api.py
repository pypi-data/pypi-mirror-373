# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Mapping, cast

import httpx

from ...types import enterprise_api_unprotect_pdf_params, enterprise_api_validate_token_params
from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven, FileTypes
from ..._utils import extract_files, maybe_transform, deepcopy_minimal, async_maybe_transform
from .recreate import (
    RecreateResource,
    AsyncRecreateResource,
    RecreateResourceWithRawResponse,
    AsyncRecreateResourceWithRawResponse,
    RecreateResourceWithStreamingResponse,
    AsyncRecreateResourceWithStreamingResponse,
)
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ..._base_client import make_request_options
from ...types.enterprise_api.enterprise_api_response import EnterpriseAPIResponse
from ...types.enterprise_api_validate_token_response import EnterpriseAPIValidateTokenResponse

__all__ = ["EnterpriseAPIResource", "AsyncEnterpriseAPIResource"]


class EnterpriseAPIResource(SyncAPIResource):
    @cached_property
    def recreate(self) -> RecreateResource:
        return RecreateResource(self._client)

    @cached_property
    def with_raw_response(self) -> EnterpriseAPIResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/prosights/recreate-sdk-python#accessing-raw-response-data-eg-headers
        """
        return EnterpriseAPIResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> EnterpriseAPIResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/prosights/recreate-sdk-python#with_streaming_response
        """
        return EnterpriseAPIResourceWithStreamingResponse(self)

    def list_formats(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIResponse:
        """Enterprise Get Formats"""
        return self._get(
            "/enterprise-api/formats/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnterpriseAPIResponse,
        )

    def unprotect_pdf(
        self,
        *,
        file: FileTypes,
        password: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Enterprise Unprotect Pdf

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "password": password,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return self._post(
            "/enterprise-api/unprotect-pdf/",
            body=maybe_transform(body, enterprise_api_unprotect_pdf_params.EnterpriseAPIUnprotectPdfParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    def validate_token(
        self,
        *,
        token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIValidateTokenResponse:
        """
        Validate JWT token

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/enterprise-api/validate-token",
            body=maybe_transform(
                {"token": token}, enterprise_api_validate_token_params.EnterpriseAPIValidateTokenParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnterpriseAPIValidateTokenResponse,
        )


class AsyncEnterpriseAPIResource(AsyncAPIResource):
    @cached_property
    def recreate(self) -> AsyncRecreateResource:
        return AsyncRecreateResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncEnterpriseAPIResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/prosights/recreate-sdk-python#accessing-raw-response-data-eg-headers
        """
        return AsyncEnterpriseAPIResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncEnterpriseAPIResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/prosights/recreate-sdk-python#with_streaming_response
        """
        return AsyncEnterpriseAPIResourceWithStreamingResponse(self)

    async def list_formats(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIResponse:
        """Enterprise Get Formats"""
        return await self._get(
            "/enterprise-api/formats/",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnterpriseAPIResponse,
        )

    async def unprotect_pdf(
        self,
        *,
        file: FileTypes,
        password: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> object:
        """
        Enterprise Unprotect Pdf

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        body = deepcopy_minimal(
            {
                "file": file,
                "password": password,
            }
        )
        files = extract_files(cast(Mapping[str, object], body), paths=[["file"]])
        # It should be noted that the actual Content-Type header that will be
        # sent to the server will contain a `boundary` parameter, e.g.
        # multipart/form-data; boundary=---abc--
        extra_headers = {"Content-Type": "multipart/form-data", **(extra_headers or {})}
        return await self._post(
            "/enterprise-api/unprotect-pdf/",
            body=await async_maybe_transform(body, enterprise_api_unprotect_pdf_params.EnterpriseAPIUnprotectPdfParams),
            files=files,
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=object,
        )

    async def validate_token(
        self,
        *,
        token: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> EnterpriseAPIValidateTokenResponse:
        """
        Validate JWT token

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/enterprise-api/validate-token",
            body=await async_maybe_transform(
                {"token": token}, enterprise_api_validate_token_params.EnterpriseAPIValidateTokenParams
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=EnterpriseAPIValidateTokenResponse,
        )


class EnterpriseAPIResourceWithRawResponse:
    def __init__(self, enterprise_api: EnterpriseAPIResource) -> None:
        self._enterprise_api = enterprise_api

        self.list_formats = to_raw_response_wrapper(
            enterprise_api.list_formats,
        )
        self.unprotect_pdf = to_raw_response_wrapper(
            enterprise_api.unprotect_pdf,
        )
        self.validate_token = to_raw_response_wrapper(
            enterprise_api.validate_token,
        )

    @cached_property
    def recreate(self) -> RecreateResourceWithRawResponse:
        return RecreateResourceWithRawResponse(self._enterprise_api.recreate)


class AsyncEnterpriseAPIResourceWithRawResponse:
    def __init__(self, enterprise_api: AsyncEnterpriseAPIResource) -> None:
        self._enterprise_api = enterprise_api

        self.list_formats = async_to_raw_response_wrapper(
            enterprise_api.list_formats,
        )
        self.unprotect_pdf = async_to_raw_response_wrapper(
            enterprise_api.unprotect_pdf,
        )
        self.validate_token = async_to_raw_response_wrapper(
            enterprise_api.validate_token,
        )

    @cached_property
    def recreate(self) -> AsyncRecreateResourceWithRawResponse:
        return AsyncRecreateResourceWithRawResponse(self._enterprise_api.recreate)


class EnterpriseAPIResourceWithStreamingResponse:
    def __init__(self, enterprise_api: EnterpriseAPIResource) -> None:
        self._enterprise_api = enterprise_api

        self.list_formats = to_streamed_response_wrapper(
            enterprise_api.list_formats,
        )
        self.unprotect_pdf = to_streamed_response_wrapper(
            enterprise_api.unprotect_pdf,
        )
        self.validate_token = to_streamed_response_wrapper(
            enterprise_api.validate_token,
        )

    @cached_property
    def recreate(self) -> RecreateResourceWithStreamingResponse:
        return RecreateResourceWithStreamingResponse(self._enterprise_api.recreate)


class AsyncEnterpriseAPIResourceWithStreamingResponse:
    def __init__(self, enterprise_api: AsyncEnterpriseAPIResource) -> None:
        self._enterprise_api = enterprise_api

        self.list_formats = async_to_streamed_response_wrapper(
            enterprise_api.list_formats,
        )
        self.unprotect_pdf = async_to_streamed_response_wrapper(
            enterprise_api.unprotect_pdf,
        )
        self.validate_token = async_to_streamed_response_wrapper(
            enterprise_api.validate_token,
        )

    @cached_property
    def recreate(self) -> AsyncRecreateResourceWithStreamingResponse:
        return AsyncRecreateResourceWithStreamingResponse(self._enterprise_api.recreate)
