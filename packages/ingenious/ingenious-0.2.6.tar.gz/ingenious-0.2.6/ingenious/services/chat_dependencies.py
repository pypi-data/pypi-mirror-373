"""
Chat service related dependency injection.

This module provides FastAPI dependency injection functions
for chat services and related repositories.
"""

from fastapi import Depends

from ingenious.db.chat_history_repository import ChatHistoryRepository
from ingenious.services.chat_service import ChatService
from ingenious.services.container import Container, get_container
from ingenious.services.message_feedback_service import MessageFeedbackService


# FastAPI dependency to get the container
def get_di_container() -> Container:
    """Get the dependency injection container."""
    return get_container()


def get_chat_history_repository(
    container: Container = Depends(get_di_container),
) -> ChatHistoryRepository:
    """Get chat history repository from container."""
    return container.chat_history_repository()


def get_chat_service(container: Container = Depends(get_di_container)) -> ChatService:
    """Get chat service from container with conversation flow."""
    # The chat_service_factory is already a factory function
    # We need to call it with the conversation_flow parameter
    return container.chat_service_factory(conversation_flow="")


def get_message_feedback_service(
    container: Container = Depends(get_di_container),
) -> MessageFeedbackService:
    """Get message feedback service from container."""
    return container.message_feedback_service()
