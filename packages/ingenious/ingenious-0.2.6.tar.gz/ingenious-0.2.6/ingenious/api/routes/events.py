from fastapi import APIRouter

from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)
router = APIRouter()
