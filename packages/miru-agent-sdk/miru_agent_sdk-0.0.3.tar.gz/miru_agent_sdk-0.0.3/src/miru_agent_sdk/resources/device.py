# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.device_sync_response import DeviceSyncResponse
from ..types.device_retrieve_response import DeviceRetrieveResponse

__all__ = ["DeviceResource", "AsyncDeviceResource"]


class DeviceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> DeviceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/miruml/python-agent-sdk#accessing-raw-response-data-eg-headers
        """
        return DeviceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> DeviceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/miruml/python-agent-sdk#with_streaming_response
        """
        return DeviceResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeviceRetrieveResponse:
        """Get the device"""
        return self._get(
            "/device",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeviceRetrieveResponse,
        )

    def sync(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeviceSyncResponse:
        """Sync the device"""
        return self._post(
            "/device/sync",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeviceSyncResponse,
        )


class AsyncDeviceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncDeviceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/miruml/python-agent-sdk#accessing-raw-response-data-eg-headers
        """
        return AsyncDeviceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncDeviceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/miruml/python-agent-sdk#with_streaming_response
        """
        return AsyncDeviceResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeviceRetrieveResponse:
        """Get the device"""
        return await self._get(
            "/device",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeviceRetrieveResponse,
        )

    async def sync(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> DeviceSyncResponse:
        """Sync the device"""
        return await self._post(
            "/device/sync",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=DeviceSyncResponse,
        )


class DeviceResourceWithRawResponse:
    def __init__(self, device: DeviceResource) -> None:
        self._device = device

        self.retrieve = to_raw_response_wrapper(
            device.retrieve,
        )
        self.sync = to_raw_response_wrapper(
            device.sync,
        )


class AsyncDeviceResourceWithRawResponse:
    def __init__(self, device: AsyncDeviceResource) -> None:
        self._device = device

        self.retrieve = async_to_raw_response_wrapper(
            device.retrieve,
        )
        self.sync = async_to_raw_response_wrapper(
            device.sync,
        )


class DeviceResourceWithStreamingResponse:
    def __init__(self, device: DeviceResource) -> None:
        self._device = device

        self.retrieve = to_streamed_response_wrapper(
            device.retrieve,
        )
        self.sync = to_streamed_response_wrapper(
            device.sync,
        )


class AsyncDeviceResourceWithStreamingResponse:
    def __init__(self, device: AsyncDeviceResource) -> None:
        self._device = device

        self.retrieve = async_to_streamed_response_wrapper(
            device.retrieve,
        )
        self.sync = async_to_streamed_response_wrapper(
            device.sync,
        )
