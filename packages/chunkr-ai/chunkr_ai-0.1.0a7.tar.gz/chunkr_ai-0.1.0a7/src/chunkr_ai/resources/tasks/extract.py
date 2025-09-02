# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional

import httpx

from ..._types import NOT_GIVEN, Body, Query, Headers, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...types.tasks import extract_get_params, extract_create_params
from ..._base_client import make_request_options
from ...types.parse_configuration_param import ParseConfigurationParam
from ...types.tasks.extract_get_response import ExtractGetResponse
from ...types.tasks.extract_create_response import ExtractCreateResponse

__all__ = ["ExtractResource", "AsyncExtractResource"]


class ExtractResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ExtractResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return ExtractResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ExtractResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return ExtractResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        file: str,
        schema: object,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        file_name: Optional[str] | NotGiven = NOT_GIVEN,
        parse_configuration: Optional[ParseConfigurationParam] | NotGiven = NOT_GIVEN,
        system_prompt: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ExtractCreateResponse:
        """
        Queues a document/parsed task for extraction and returns a `TaskResponse` with
        the assigned `task_id`, initial configuration, file metadata, and timestamps.
        The initial status is `Starting`.

        Creates an extract task and returns its metadata immediately.

        Args:
          file:
              The file to be extracted. Supported inputs:

              - `ch://files/{file_id}`: Reference to an existing file. Upload via the Files
                API
              - `http(s)://...`: Remote URL to fetch
              - `data:*;base64,...` or raw base64 string
              - `task_id`: Reference to an existing `parse`task.

          schema: The schema to be used for the extraction.

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          file_name: The name of the file to be extracted. If not set a name will be generated. Can
              not be provided if the `file` is a `task_id`.

          parse_configuration: Optional configuration for the `parse` task. Can not be used if `file` is a
              `task_id`.

          system_prompt: The system prompt to be used for the extraction.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/tasks/extract",
            body=maybe_transform(
                {
                    "file": file,
                    "schema": schema,
                    "expires_in": expires_in,
                    "file_name": file_name,
                    "parse_configuration": parse_configuration,
                    "system_prompt": system_prompt,
                },
                extract_create_params.ExtractCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ExtractCreateResponse,
        )

    def get(
        self,
        task_id: Optional[str],
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        wait_for_completion: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExtractGetResponse:
        """
        Retrieves the current state of an extract task and, when requested, can wait for
        completion.

        Returns task details such as processing status, configuration, output (when
        available), file metadata, and timestamps. If `wait_for_completion=true` is
        provided, the server will hold the request briefly. If the task does not reach a
        terminal state during that window, the response will indicate a retry with
        appropriate headers.

        Typical uses:

        - Poll a task during processing
        - Retrieve the final output once processing is complete
        - Access task metadata and configuration

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          include_chunks: Whether to include chunks in the output response

          wait_for_completion: Whether to wait for the task to complete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return self._get(
            f"/tasks/{task_id}/extract",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "include_chunks": include_chunks,
                        "wait_for_completion": wait_for_completion,
                    },
                    extract_get_params.ExtractGetParams,
                ),
            ),
            cast_to=ExtractGetResponse,
        )


class AsyncExtractResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncExtractResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return AsyncExtractResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncExtractResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return AsyncExtractResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        file: str,
        schema: object,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        file_name: Optional[str] | NotGiven = NOT_GIVEN,
        parse_configuration: Optional[ParseConfigurationParam] | NotGiven = NOT_GIVEN,
        system_prompt: Optional[str] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ExtractCreateResponse:
        """
        Queues a document/parsed task for extraction and returns a `TaskResponse` with
        the assigned `task_id`, initial configuration, file metadata, and timestamps.
        The initial status is `Starting`.

        Creates an extract task and returns its metadata immediately.

        Args:
          file:
              The file to be extracted. Supported inputs:

              - `ch://files/{file_id}`: Reference to an existing file. Upload via the Files
                API
              - `http(s)://...`: Remote URL to fetch
              - `data:*;base64,...` or raw base64 string
              - `task_id`: Reference to an existing `parse`task.

          schema: The schema to be used for the extraction.

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          file_name: The name of the file to be extracted. If not set a name will be generated. Can
              not be provided if the `file` is a `task_id`.

          parse_configuration: Optional configuration for the `parse` task. Can not be used if `file` is a
              `task_id`.

          system_prompt: The system prompt to be used for the extraction.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/tasks/extract",
            body=await async_maybe_transform(
                {
                    "file": file,
                    "schema": schema,
                    "expires_in": expires_in,
                    "file_name": file_name,
                    "parse_configuration": parse_configuration,
                    "system_prompt": system_prompt,
                },
                extract_create_params.ExtractCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ExtractCreateResponse,
        )

    async def get(
        self,
        task_id: Optional[str],
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        wait_for_completion: bool | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> ExtractGetResponse:
        """
        Retrieves the current state of an extract task and, when requested, can wait for
        completion.

        Returns task details such as processing status, configuration, output (when
        available), file metadata, and timestamps. If `wait_for_completion=true` is
        provided, the server will hold the request briefly. If the task does not reach a
        terminal state during that window, the response will indicate a retry with
        appropriate headers.

        Typical uses:

        - Poll a task during processing
        - Retrieve the final output once processing is complete
        - Access task metadata and configuration

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          include_chunks: Whether to include chunks in the output response

          wait_for_completion: Whether to wait for the task to complete

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        return await self._get(
            f"/tasks/{task_id}/extract",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "include_chunks": include_chunks,
                        "wait_for_completion": wait_for_completion,
                    },
                    extract_get_params.ExtractGetParams,
                ),
            ),
            cast_to=ExtractGetResponse,
        )


class ExtractResourceWithRawResponse:
    def __init__(self, extract: ExtractResource) -> None:
        self._extract = extract

        self.create = to_raw_response_wrapper(
            extract.create,
        )
        self.get = to_raw_response_wrapper(
            extract.get,
        )


class AsyncExtractResourceWithRawResponse:
    def __init__(self, extract: AsyncExtractResource) -> None:
        self._extract = extract

        self.create = async_to_raw_response_wrapper(
            extract.create,
        )
        self.get = async_to_raw_response_wrapper(
            extract.get,
        )


class ExtractResourceWithStreamingResponse:
    def __init__(self, extract: ExtractResource) -> None:
        self._extract = extract

        self.create = to_streamed_response_wrapper(
            extract.create,
        )
        self.get = to_streamed_response_wrapper(
            extract.get,
        )


class AsyncExtractResourceWithStreamingResponse:
    def __init__(self, extract: AsyncExtractResource) -> None:
        self._extract = extract

        self.create = async_to_streamed_response_wrapper(
            extract.create,
        )
        self.get = async_to_streamed_response_wrapper(
            extract.get,
        )
