# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import List, Union, Optional
from datetime import datetime
from typing_extensions import Literal

import httpx

from .parse import (
    ParseResource,
    AsyncParseResource,
    ParseResourceWithRawResponse,
    AsyncParseResourceWithRawResponse,
    ParseResourceWithStreamingResponse,
    AsyncParseResourceWithStreamingResponse,
)
from ...types import task_get_params, task_list_params
from .extract import (
    ExtractResource,
    AsyncExtractResource,
    ExtractResourceWithRawResponse,
    AsyncExtractResourceWithRawResponse,
    ExtractResourceWithStreamingResponse,
    AsyncExtractResourceWithStreamingResponse,
)
from ..._types import NOT_GIVEN, Body, Query, Headers, NoneType, NotGiven
from ..._utils import maybe_transform, async_maybe_transform
from ..._compat import cached_property
from ..._resource import SyncAPIResource, AsyncAPIResource
from ..._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from ...pagination import SyncTasksPage, AsyncTasksPage
from ..._base_client import AsyncPaginator, make_request_options
from ...types.task_response import TaskResponse

__all__ = ["TasksResource", "AsyncTasksResource"]


class TasksResource(SyncAPIResource):
    @cached_property
    def extract(self) -> ExtractResource:
        return ExtractResource(self._client)

    @cached_property
    def parse(self) -> ParseResource:
        return ParseResource(self._client)

    @cached_property
    def with_raw_response(self) -> TasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return TasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return TasksResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        cursor: Union[str, datetime] | NotGiven = NOT_GIVEN,
        end: Union[str, datetime] | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        sort: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        start: Union[str, datetime] | NotGiven = NOT_GIVEN,
        statuses: List[Literal["Starting", "Processing", "Succeeded", "Failed", "Cancelled"]] | NotGiven = NOT_GIVEN,
        task_types: List[Literal["Parse", "Extract"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> SyncTasksPage[TaskResponse]:
        """
        Lists tasks for the authenticated user with cursor-based pagination and optional
        filtering by date range. Supports ascending or descending sort order and
        optional inclusion of chunks/base64 URLs.

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          cursor: Cursor for pagination (timestamp)

          end: End date

          include_chunks: Whether to include chunks in the output response

          limit: Number of tasks per page

          sort: Sort order: 'asc' for ascending, 'desc' for descending (default)

          start: Start date

          statuses: Filter by one or more statuses

          task_types: Filter by one or more task types

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/tasks",
            page=SyncTasksPage[TaskResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "cursor": cursor,
                        "end": end,
                        "include_chunks": include_chunks,
                        "limit": limit,
                        "sort": sort,
                        "start": start,
                        "statuses": statuses,
                        "task_types": task_types,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            model=TaskResponse,
        )

    def delete(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Delete a task by its ID.

        Requirements:

        - Task must have status `Succeeded` or `Failed`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._delete(
            f"/tasks/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    def cancel(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Cancel a task that hasn't started processing yet:

        - For new tasks: Status will be updated to `Cancelled`
        - For updating tasks: Task will revert to the previous state

        Requirements:

        - Task must have status `Starting`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return self._get(
            f"/tasks/{task_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
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
    ) -> TaskResponse:
        """
        Retrieves the current state of a task and, when requested, can wait for
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
            f"/tasks/{task_id}",
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
                    task_get_params.TaskGetParams,
                ),
            ),
            cast_to=TaskResponse,
        )


class AsyncTasksResource(AsyncAPIResource):
    @cached_property
    def extract(self) -> AsyncExtractResource:
        return AsyncExtractResource(self._client)

    @cached_property
    def parse(self) -> AsyncParseResource:
        return AsyncParseResource(self._client)

    @cached_property
    def with_raw_response(self) -> AsyncTasksResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTasksResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTasksResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/lumina-ai-inc/chunkr-python#with_streaming_response
        """
        return AsyncTasksResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        base64_urls: bool | NotGiven = NOT_GIVEN,
        cursor: Union[str, datetime] | NotGiven = NOT_GIVEN,
        end: Union[str, datetime] | NotGiven = NOT_GIVEN,
        include_chunks: bool | NotGiven = NOT_GIVEN,
        limit: int | NotGiven = NOT_GIVEN,
        sort: Literal["asc", "desc"] | NotGiven = NOT_GIVEN,
        start: Union[str, datetime] | NotGiven = NOT_GIVEN,
        statuses: List[Literal["Starting", "Processing", "Succeeded", "Failed", "Cancelled"]] | NotGiven = NOT_GIVEN,
        task_types: List[Literal["Parse", "Extract"]] | NotGiven = NOT_GIVEN,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> AsyncPaginator[TaskResponse, AsyncTasksPage[TaskResponse]]:
        """
        Lists tasks for the authenticated user with cursor-based pagination and optional
        filtering by date range. Supports ascending or descending sort order and
        optional inclusion of chunks/base64 URLs.

        Args:
          base64_urls: Whether to return base64 encoded URLs. If false, the URLs will be returned as
              presigned URLs.

          cursor: Cursor for pagination (timestamp)

          end: End date

          include_chunks: Whether to include chunks in the output response

          limit: Number of tasks per page

          sort: Sort order: 'asc' for ascending, 'desc' for descending (default)

          start: Start date

          statuses: Filter by one or more statuses

          task_types: Filter by one or more task types

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get_api_list(
            "/tasks",
            page=AsyncTasksPage[TaskResponse],
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "base64_urls": base64_urls,
                        "cursor": cursor,
                        "end": end,
                        "include_chunks": include_chunks,
                        "limit": limit,
                        "sort": sort,
                        "start": start,
                        "statuses": statuses,
                        "task_types": task_types,
                    },
                    task_list_params.TaskListParams,
                ),
            ),
            model=TaskResponse,
        )

    async def delete(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
        idempotency_key: str | None = None,
    ) -> None:
        """
        Delete a task by its ID.

        Requirements:

        - Task must have status `Succeeded` or `Failed`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds

          idempotency_key: Specify a custom idempotency key for this request
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._delete(
            f"/tasks/{task_id}",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                idempotency_key=idempotency_key,
            ),
            cast_to=NoneType,
        )

    async def cancel(
        self,
        task_id: Optional[str],
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = NOT_GIVEN,
    ) -> None:
        """
        Cancel a task that hasn't started processing yet:

        - For new tasks: Status will be updated to `Cancelled`
        - For updating tasks: Task will revert to the previous state

        Requirements:

        - Task must have status `Starting`

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not task_id:
            raise ValueError(f"Expected a non-empty value for `task_id` but received {task_id!r}")
        extra_headers = {"Accept": "*/*", **(extra_headers or {})}
        return await self._get(
            f"/tasks/{task_id}/cancel",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=NoneType,
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
    ) -> TaskResponse:
        """
        Retrieves the current state of a task and, when requested, can wait for
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
            f"/tasks/{task_id}",
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
                    task_get_params.TaskGetParams,
                ),
            ),
            cast_to=TaskResponse,
        )


class TasksResourceWithRawResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.list = to_raw_response_wrapper(
            tasks.list,
        )
        self.delete = to_raw_response_wrapper(
            tasks.delete,
        )
        self.cancel = to_raw_response_wrapper(
            tasks.cancel,
        )
        self.get = to_raw_response_wrapper(
            tasks.get,
        )

    @cached_property
    def extract(self) -> ExtractResourceWithRawResponse:
        return ExtractResourceWithRawResponse(self._tasks.extract)

    @cached_property
    def parse(self) -> ParseResourceWithRawResponse:
        return ParseResourceWithRawResponse(self._tasks.parse)


class AsyncTasksResourceWithRawResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.list = async_to_raw_response_wrapper(
            tasks.list,
        )
        self.delete = async_to_raw_response_wrapper(
            tasks.delete,
        )
        self.cancel = async_to_raw_response_wrapper(
            tasks.cancel,
        )
        self.get = async_to_raw_response_wrapper(
            tasks.get,
        )

    @cached_property
    def extract(self) -> AsyncExtractResourceWithRawResponse:
        return AsyncExtractResourceWithRawResponse(self._tasks.extract)

    @cached_property
    def parse(self) -> AsyncParseResourceWithRawResponse:
        return AsyncParseResourceWithRawResponse(self._tasks.parse)


class TasksResourceWithStreamingResponse:
    def __init__(self, tasks: TasksResource) -> None:
        self._tasks = tasks

        self.list = to_streamed_response_wrapper(
            tasks.list,
        )
        self.delete = to_streamed_response_wrapper(
            tasks.delete,
        )
        self.cancel = to_streamed_response_wrapper(
            tasks.cancel,
        )
        self.get = to_streamed_response_wrapper(
            tasks.get,
        )

    @cached_property
    def extract(self) -> ExtractResourceWithStreamingResponse:
        return ExtractResourceWithStreamingResponse(self._tasks.extract)

    @cached_property
    def parse(self) -> ParseResourceWithStreamingResponse:
        return ParseResourceWithStreamingResponse(self._tasks.parse)


class AsyncTasksResourceWithStreamingResponse:
    def __init__(self, tasks: AsyncTasksResource) -> None:
        self._tasks = tasks

        self.list = async_to_streamed_response_wrapper(
            tasks.list,
        )
        self.delete = async_to_streamed_response_wrapper(
            tasks.delete,
        )
        self.cancel = async_to_streamed_response_wrapper(
            tasks.cancel,
        )
        self.get = async_to_streamed_response_wrapper(
            tasks.get,
        )

    @cached_property
    def extract(self) -> AsyncExtractResourceWithStreamingResponse:
        return AsyncExtractResourceWithStreamingResponse(self._tasks.extract)

    @cached_property
    def parse(self) -> AsyncParseResourceWithStreamingResponse:
        return AsyncParseResourceWithStreamingResponse(self._tasks.parse)
