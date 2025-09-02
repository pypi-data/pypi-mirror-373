from typing import List

from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from ingenious.core.structured_logging import get_logger
from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.models.http_error import HTTPError
from ingenious.models.message import Message
from ingenious.services.fastapi_dependencies import get_chat_history_repository

logger = get_logger(__name__)
router = APIRouter()


@router.get(
    "/conversations/{thread_id}",
    responses={400: {"model": HTTPError, "description": "Bad Request"}},
)
async def get_conversation(
    thread_id: str,
    chat_history_repository: Annotated[
        ChatHistoryRepository, Depends(get_chat_history_repository)
    ],
) -> List[Message]:
    try:
        messages = await chat_history_repository.get_thread_messages(thread_id)
        return messages or []
    except Exception as e:
        logger.error(
            "Failed to get conversation",
            thread_id=thread_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(e))
