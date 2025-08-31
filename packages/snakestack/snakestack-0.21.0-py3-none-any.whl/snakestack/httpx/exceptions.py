from typing import Self


class SnakeHTTPError(Exception):
    """Base exception for SnakeStack HTTP errors."""


class RequestHTTPError(SnakeHTTPError):
    """Raised when requesting fails."""

    def __init__(self: Self, api: str, original_exception: Exception) -> None:
        super().__init__(f"Failed to request to api '{api}': {original_exception}")
        self.api = api
        self.original_exception = original_exception
