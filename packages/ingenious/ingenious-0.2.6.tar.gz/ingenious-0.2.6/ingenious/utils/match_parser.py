"""
Match data parser utility module - Stub implementation for testing
"""

from datetime import datetime
from typing import Any, Optional, Tuple


class MatchDataParser:
    """
    Stub implementation of MatchDataParser for testing purposes.
    This handles sports/match data parsing but provides fallback for general testing.
    """

    def __init__(
        self, payload: Optional[Any] = None, event_type: Optional[str] = None
    ) -> None:
        self.payload: Optional[Any] = payload
        self.event_type: Optional[str] = event_type

    def create_detailed_summary(self) -> Tuple[str, str, str, str, str]:
        """
        Create a detailed summary from match data.
        For testing purposes, this returns default values.

        Returns:
            tuple: (message, overBall, timestamp, match_id, feed_id)
        """
        # For testing, just return the payload as the message with default values
        message: str = str(self.payload) if self.payload else "test payload"
        overBall: str = "test_over"
        timestamp: str = str(datetime.now())
        match_id: str = "test_match_123"
        feed_id: str = "test_feed_456"

        return message, overBall, timestamp, match_id, feed_id
