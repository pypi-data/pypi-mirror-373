from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Message(BaseModel):
    user_id: Optional[str]
    thread_id: str
    message_id: Optional[str] = None
    positive_feedback: Optional[bool] = None
    timestamp: Optional[datetime] = None
    role: str
    content: Optional[str] = None
    content_filter_results: Optional[dict[str, object]] = None
    tool_calls: Optional[list[dict[str, object]]] = None
    tool_call_id: Optional[str] = None
    tool_call_function: Optional[dict[str, object]] = None
