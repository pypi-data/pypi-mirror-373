from bosa_connectors.models.action import ActionResponseData as ActionResponseData, InitialExecutorRequest as InitialExecutorRequest
from bosa_connectors.models.file import ConnectorFile as ConnectorFile
from typing import Any, Callable

class ActionResponse:
    '''Represents the response from an action execution.

    Currently supports 2 pagination modes:
    1. Page-based pagination: Using page numbers (page=1, page=2, etc.)
    2. Cursor-based pagination: Using cursor tokens for forwards and backwards navigation

    The class automatically detects which pagination mode to use based on the response metadata:
    - If "forwards_cursor" and "backwards_cursor" are present, cursor-based pagination is used
    - Otherwise, it falls back to page-based pagination using "page" parameter

    Common pagination attributes:
    - total: Total number of items
    - total_page: Total number of pages
    - has_next: Whether there is a next page
    - has_prev: Whether there is a previous page

    Followed by optional attributes
    Cursor-based pagination attributes:
    - forwards_cursor: Cursor for next page
    - backwards_cursor: Cursor for previous page

    Page-based pagination attributes:
    - page: Current page number
    - limit: Number of items per page

    If the response is ConnectorFile, it will not support pagination and will return the file directly.
    '''
    def __init__(self, response_data: dict[str, Any] | ConnectorFile | None, status: int, response_creator: Callable[..., 'ActionResponse'], initial_executor_request: dict[str, Any]) -> None:
        '''Initialize response wrapper.

        Args:
            response_data: Response data which could be:
                 - List response: {"data": [...], "meta": {...}}
                 - Single item response: {"data": {...}, "meta": {...}}
            status: HTTP status code
            response_creator: Callable to create a new ActionResponse
            initial_executor_request: Initial action request attributes as dict
        '''
    def get_data(self) -> list[dict[str, Any]] | dict[str, Any] | ConnectorFile:
        """Get the current page data.

        Returns:
            List of objects for paginated responses, or
            Single object for single item responses
        """
    def get_meta(self) -> dict[str, Any]:
        """Get the meta data."""
    def get_status(self) -> int:
        """Get the HTTP status code."""
    def is_list(self) -> bool:
        """Check if the response data is a list."""
    def has_next(self) -> bool:
        """Check if there is a next page.

        Returns False if this is a single item response.
        """
    def has_prev(self) -> bool:
        """Check if there is a previous page.

        Returns False if this is a single item response.
        """
    def next_page(self) -> ActionResponse:
        """Move to the next page and get the response.

        Supports both page-based and cursor-based navigation:
        1. If forwards_cursor is available, uses cursor-based navigation
        2. Otherwise, falls back to page-based navigation

        Returns self if this is a single item response or there is no next page.
        """
    def prev_page(self) -> ActionResponse:
        """Move to the previous page and get the response.

        Supports both page-based and cursor-based navigation:
        1. If backwards_cursor is available, uses cursor-based navigation
        2. Otherwise, falls back to page-based navigation

        Returns self if this is a single item data or there is no previous page.
        """
    def get_all_items(self) -> list[Any]:
        """Get all items from all pages."""
