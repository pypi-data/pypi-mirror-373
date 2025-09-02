# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Generic, TypeVar, Optional
from datetime import datetime
from typing_extensions import override

from ._base_client import BasePage, PageInfo, BaseSyncPage, BaseAsyncPage

__all__ = ["SyncTasksPage", "AsyncTasksPage", "SyncFilesPage", "AsyncFilesPage"]

_T = TypeVar("_T")


class SyncTasksPage(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    tasks: List[_T]
    next_cursor: Optional[datetime] = None
    has_more: Optional[bool] = None
    """Whether there are more pages available"""

    @override
    def _get_page_items(self) -> List[_T]:
        tasks = self.tasks
        if not tasks:
            return []
        return tasks

    @override
    def has_next_page(self) -> bool:
        has_more = self.has_more
        if has_more is not None and has_more is False:
            return False

        return super().has_next_page()

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_cursor = self.next_cursor
        if not next_cursor:
            return None

        return PageInfo(params={"cursor": next_cursor})


class AsyncTasksPage(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    tasks: List[_T]
    next_cursor: Optional[datetime] = None
    has_more: Optional[bool] = None
    """Whether there are more pages available"""

    @override
    def _get_page_items(self) -> List[_T]:
        tasks = self.tasks
        if not tasks:
            return []
        return tasks

    @override
    def has_next_page(self) -> bool:
        has_more = self.has_more
        if has_more is not None and has_more is False:
            return False

        return super().has_next_page()

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_cursor = self.next_cursor
        if not next_cursor:
            return None

        return PageInfo(params={"cursor": next_cursor})


class SyncFilesPage(BaseSyncPage[_T], BasePage[_T], Generic[_T]):
    files: List[_T]
    next_cursor: Optional[datetime] = None
    has_more: Optional[bool] = None
    """Whether there are more pages available"""

    @override
    def _get_page_items(self) -> List[_T]:
        files = self.files
        if not files:
            return []
        return files

    @override
    def has_next_page(self) -> bool:
        has_more = self.has_more
        if has_more is not None and has_more is False:
            return False

        return super().has_next_page()

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_cursor = self.next_cursor
        if not next_cursor:
            return None

        return PageInfo(params={"cursor": next_cursor})


class AsyncFilesPage(BaseAsyncPage[_T], BasePage[_T], Generic[_T]):
    files: List[_T]
    next_cursor: Optional[datetime] = None
    has_more: Optional[bool] = None
    """Whether there are more pages available"""

    @override
    def _get_page_items(self) -> List[_T]:
        files = self.files
        if not files:
            return []
        return files

    @override
    def has_next_page(self) -> bool:
        has_more = self.has_more
        if has_more is not None and has_more is False:
            return False

        return super().has_next_page()

    @override
    def next_page_info(self) -> Optional[PageInfo]:
        next_cursor = self.next_cursor
        if not next_cursor:
            return None

        return PageInfo(params={"cursor": next_cursor})
