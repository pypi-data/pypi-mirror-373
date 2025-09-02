from fastapi import APIRouter, Depends, HTTPException
from typing_extensions import Annotated

from ingenious.core.structured_logging import get_logger
from ingenious.models.http_error import HTTPError
from ingenious.models.message_feedback import (
    MessageFeedbackRequest,
    MessageFeedbackResponse,
)
from ingenious.services.fastapi_dependencies import get_message_feedback_service
from ingenious.services.message_feedback_service import MessageFeedbackService

logger = get_logger(__name__)
router = APIRouter()


@router.put(
    "/messages/{message_id}/feedback",
    responses={400: {"model": HTTPError, "description": "Bad Request"}},
)
async def submit_message_feedback(
    message_id: str,
    message_feedback_request: MessageFeedbackRequest,
    feedback_service: Annotated[
        MessageFeedbackService, Depends(get_message_feedback_service)
    ],
) -> MessageFeedbackResponse:
    try:
        return await feedback_service.update_message_feedback(
            message_id, message_feedback_request
        )
    except ValueError as e:
        logger.error(
            "Failed to submit message feedback",
            message_id=message_id,
            error=str(e),
            exc_info=True,
        )
        raise HTTPException(status_code=400, detail=str(e))
