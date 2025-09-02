# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Optional
from typing_extensions import Literal

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
from ...types.tasks import parse_get_params, parse_create_params
from ..._base_client import make_request_options
from ...types.llm_processing_param import LlmProcessingParam
from ...types.chunk_processing_param import ChunkProcessingParam
from ...types.segment_processing_param import SegmentProcessingParam
from ...types.tasks.parse_get_response import ParseGetResponse
from ...types.tasks.parse_create_response import ParseCreateResponse

__all__ = ["ParseResource", "AsyncParseResource"]


class ParseResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ParseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return ParseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ParseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return ParseResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        file: str,
        chunk_processing: ChunkProcessingParam | NotGiven = NOT_GIVEN,
        error_handling: Literal["Fail", "Continue"] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        file_name: Optional[str] | NotGiven = NOT_GIVEN,
        llm_processing: LlmProcessingParam | NotGiven = NOT_GIVEN,
        ocr_strategy: Literal["All", "Auto"] | NotGiven = NOT_GIVEN,
        pipeline: Literal["Azure", "Chunkr"] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[SegmentProcessingParam] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Literal["LayoutAnalysis", "Page"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ParseCreateResponse:
        """
        Queues a document for processing and returns a `TaskResponse` with the assigned
        `task_id`, initial configuration, file metadata, and timestamps. The initial
        status is `Starting`.

        Creates a parse task and returns its metadata immediately.

        Args:
          file:
              The file to be parsed. Supported inputs:

              - `ch://files/{file_id}`: Reference to an existing file. Upload via the Files
                API
              - `http(s)://...`: Remote URL to fetch
              - `data:*;base64,...` or raw base64 string

          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          file_name: The name of the file to be parsed. If not set a name will be generated.

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          segment_processing: Configuration for how each document segment is processed and formatted.

              Each segment has sensible defaults, but you can override specific settings:

              - `format`: Output as `Html` or `Markdown`
              - `strategy`: `Auto` (rule-based), `LLM` (AI-generated), or `Ignore` (skip)
              - `crop_image`: Whether to crop images to segment bounds
              - `extended_context`: Use full page as context for LLM processing
              - `description`: Generate descriptions for segments

              **Defaults per segment type:** Check the documentation for more details.

              Only specify the fields you want to change - everything else uses the defaults.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking.
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return self._post(
            "/tasks/parse",
            body=maybe_transform(
                {
                    "file": file,
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "file_name": file_name,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                parse_create_params.ParseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ParseCreateResponse,
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
    ) -> ParseGetResponse:
        """
        Retrieves the current state of a parse task and, when requested, can wait for
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
            f"/tasks/{task_id}/parse",
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
                    parse_get_params.ParseGetParams,
                ),
            ),
            cast_to=ParseGetResponse,
        )


class AsyncParseResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncParseResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return AsyncParseResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncParseResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return AsyncParseResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        file: str,
        chunk_processing: ChunkProcessingParam | NotGiven = NOT_GIVEN,
        error_handling: Literal["Fail", "Continue"] | NotGiven = NOT_GIVEN,
        expires_in: Optional[int] | NotGiven = NOT_GIVEN,
        file_name: Optional[str] | NotGiven = NOT_GIVEN,
        llm_processing: LlmProcessingParam | NotGiven = NOT_GIVEN,
        ocr_strategy: Literal["All", "Auto"] | NotGiven = NOT_GIVEN,
        pipeline: Literal["Azure", "Chunkr"] | NotGiven = NOT_GIVEN,
        segment_processing: Optional[SegmentProcessingParam] | NotGiven = NOT_GIVEN,
        segmentation_strategy: Literal["LayoutAnalysis", "Page"] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> ParseCreateResponse:
        """
        Queues a document for processing and returns a `TaskResponse` with the assigned
        `task_id`, initial configuration, file metadata, and timestamps. The initial
        status is `Starting`.

        Creates a parse task and returns its metadata immediately.

        Args:
          file:
              The file to be parsed. Supported inputs:

              - `ch://files/{file_id}`: Reference to an existing file. Upload via the Files
                API
              - `http(s)://...`: Remote URL to fetch
              - `data:*;base64,...` or raw base64 string

          chunk_processing: Controls the setting for the chunking and post-processing of each chunk.

          error_handling:
              Controls how errors are handled during processing:

              - `Fail`: Stops processing and fails the task when any error occurs
              - `Continue`: Attempts to continue processing despite non-critical errors (eg.
                LLM refusals etc.)

          expires_in: The number of seconds until task is deleted. Expired tasks can **not** be
              updated, polled or accessed via web interface.

          file_name: The name of the file to be parsed. If not set a name will be generated.

          llm_processing: Controls the LLM used for the task.

          ocr_strategy: Controls the Optical Character Recognition (OCR) strategy.

              - `All`: Processes all pages with OCR. (Latency penalty: ~0.5 seconds per page)
              - `Auto`: Selectively applies OCR only to pages with missing or low-quality
                text. When text layer is present the bounding boxes from the text layer are
                used.

          segment_processing: Configuration for how each document segment is processed and formatted.

              Each segment has sensible defaults, but you can override specific settings:

              - `format`: Output as `Html` or `Markdown`
              - `strategy`: `Auto` (rule-based), `LLM` (AI-generated), or `Ignore` (skip)
              - `crop_image`: Whether to crop images to segment bounds
              - `extended_context`: Use full page as context for LLM processing
              - `description`: Generate descriptions for segments

              **Defaults per segment type:** Check the documentation for more details.

              Only specify the fields you want to change - everything else uses the defaults.

          segmentation_strategy:
              Controls the segmentation strategy:

              - `LayoutAnalysis`: Analyzes pages for layout elements (e.g., `Table`,
                `Picture`, `Formula`, etc.) using bounding boxes. Provides fine-grained
                segmentation and better chunking.
              - `Page`: Treats each page as a single segment. Faster processing, but without
                layout element detection and only simple chunking.

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        return await self._post(
            "/tasks/parse",
            body=await async_maybe_transform(
                {
                    "file": file,
                    "chunk_processing": chunk_processing,
                    "error_handling": error_handling,
                    "expires_in": expires_in,
                    "file_name": file_name,
                    "llm_processing": llm_processing,
                    "ocr_strategy": ocr_strategy,
                    "pipeline": pipeline,
                    "segment_processing": segment_processing,
                    "segmentation_strategy": segmentation_strategy,
                },
                parse_create_params.ParseCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=ParseCreateResponse,
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
    ) -> ParseGetResponse:
        """
        Retrieves the current state of a parse task and, when requested, can wait for
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
            f"/tasks/{task_id}/parse",
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
                    parse_get_params.ParseGetParams,
                ),
            ),
            cast_to=ParseGetResponse,
        )


class ParseResourceWithRawResponse:
    def __init__(self, parse: ParseResource) -> None:
        self._parse = parse

        self.create = to_raw_response_wrapper(
            parse.create,
        )
        self.get = to_raw_response_wrapper(
            parse.get,
        )


class AsyncParseResourceWithRawResponse:
    def __init__(self, parse: AsyncParseResource) -> None:
        self._parse = parse

        self.create = async_to_raw_response_wrapper(
            parse.create,
        )
        self.get = async_to_raw_response_wrapper(
            parse.get,
        )


class ParseResourceWithStreamingResponse:
    def __init__(self, parse: ParseResource) -> None:
        self._parse = parse

        self.create = to_streamed_response_wrapper(
            parse.create,
        )
        self.get = to_streamed_response_wrapper(
            parse.get,
        )


class AsyncParseResourceWithStreamingResponse:
    def __init__(self, parse: AsyncParseResource) -> None:
        self._parse = parse

        self.create = async_to_streamed_response_wrapper(
            parse.create,
        )
        self.get = async_to_streamed_response_wrapper(
            parse.get,
        )
