from typing import Any, Dict, Optional


class ContentFilterError(Exception):
    """Exception raised when the user message violates the OpenAI content filter."""

    DEFAULT_MESSAGE = (
        "The users prompt violates the content filter, please start a new conversation."
    )

    def __init__(
        self,
        message: str = DEFAULT_MESSAGE,
        content_filter_results: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.message = message
        self.content_filter_results = content_filter_results or {}
        super().__init__(self.message)
