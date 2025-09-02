from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ContentFilterResult(BaseModel):
    filtered: Optional[bool] = None
    severity: Optional[str] = None
    detected: Optional[bool] = None


class ToolCall(BaseModel):
    tool_call_id: Optional[str] = None
    content: Optional[str] = None


class Message(BaseModel):
    content: Optional[str] = None
    role: Optional[str] = None
    name: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class CompletionTokensDetails(BaseModel):
    accepted_prediction_tokens: Optional[int] = None
    audio_tokens: Optional[int] = None
    reasoning_tokens: Optional[int] = None
    rejected_prediction_tokens: Optional[int] = None


class PromptTokensDetails(BaseModel):
    audio_tokens: Optional[int] = None
    cached_tokens: Optional[int] = None


class Usage(BaseModel):
    completion_tokens: Optional[int] = None
    prompt_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    completion_tokens_details: Optional[CompletionTokensDetails] = None
    prompt_tokens_details: Optional[PromptTokensDetails] = None


class ChoiceMessage(BaseModel):
    content: Optional[str] = None
    refusal: Optional[str] = None
    role: Optional[str] = None
    audio: Optional[str] = None
    function_call: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


class Choice(BaseModel):
    finish_reason: Optional[str] = None
    index: Optional[int] = None
    logprobs: Optional[Any] = None
    message: Optional[ChoiceMessage] = None
    content_filter_results: Optional[Dict[str, ContentFilterResult]] = None


class PromptFilterResult(BaseModel):
    prompt_index: Optional[int] = None
    content_filter_results: Optional[Dict[str, ContentFilterResult]] = None


class Response(BaseModel):
    id: Optional[str] = None
    choices: Optional[List[Choice]] = None
    created: Optional[int] = None
    model: Optional[str] = None
    object: Optional[str] = None
    service_tier: Optional[str] = None
    system_fingerprint: Optional[str] = None
    usage: Optional[Usage] = None
    prompt_filter_results: Optional[List[PromptFilterResult]] = None


class LLMEventKwargs(BaseModel):
    type: Optional[str] = None
    messages: Optional[List[Message]] = None
    response: Optional[Response] = None
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    agent_id: Optional[str] = None
