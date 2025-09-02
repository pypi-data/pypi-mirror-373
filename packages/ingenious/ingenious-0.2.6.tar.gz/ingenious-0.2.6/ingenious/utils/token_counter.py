from typing import Dict, List, Set

import tiktoken
from openai.types.chat import ChatCompletionMessageParam

from ingenious.core.structured_logging import get_logger

logger = get_logger(__name__)


def get_max_tokens(model: str = "gpt-3.5-turbo-0125") -> int:
    # Return the maximum number of tokens for a given model
    ## TODO: Move this to a configuration file
    max_tokens: Dict[str, int] = {
        "gpt-3.5-turbo": 4096,
        "gpt-3.5-turbo-0613": 4096,
        "gpt-3.5-turbo-16k": 16384,
        "gpt-3.5-turbo-0125": 16384,
        "gpt-4": 8192,
        "gpt-4-0314": 8192,
        "gpt-4-32k": 32768,
        "gpt-4-32k-0314": 32768,
        "gpt-4-0613": 8192,
        "gpt-4-32k-0613": 32768,
    }
    return max_tokens.get(model, 4096)


def num_tokens_from_messages(
    messages: List[ChatCompletionMessageParam], model: str = "gpt-3.5-turbo-0613"
) -> int:
    # Return the number of tokens used by a list of messages
    try:
        encoding: tiktoken.Encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        logger.warning(
            "Model not found, using fallback encoding",
            model=model,
            encoding="cl100k_base",
        )
        encoding = tiktoken.get_encoding("cl100k_base")

    ## TODO: Move this to a configuration file
    supported_models: Set[str] = {
        "gpt-3.5-turbo-0613",
        "gpt-3.5-turbo-16k-0125",
        "gpt-4-0314",
        "gpt-4-32k-0314",
        "gpt-4-0613",
        "gpt-4-32k-0613",
    }

    if model in supported_models:
        tokens_per_message: int = 3
        tokens_per_name: int = 1
    elif model == "gpt-3.5-turbo-0301":
        tokens_per_message = 4
        tokens_per_name = -1
    elif "gpt-3.5-turbo" in model:
        logger.warning(
            "Model may update over time, using fallback",
            model=model,
            fallback_model="gpt-3.5-turbo-0613",
        )
        return num_tokens_from_messages(messages, model="gpt-3.5-turbo-0613")
    elif "gpt-4" in model:
        logger.warning(
            "Model may update over time, using fallback",
            model=model,
            fallback_model="gpt-4-0613",
        )
        return num_tokens_from_messages(messages, model="gpt-4-0613")
    else:
        raise NotImplementedError(f"""num_tokens_from_messages() is not implemented for model {
            model
        }. See https://github.com/openai/openai-python/blob/main/chatml.md for information
            on how messages are converted to tokens.""")

    num_tokens: int = 0
    for message in messages:
        num_tokens += tokens_per_message
        for key, value in message.items():
            if isinstance(value, str):
                num_tokens += len(encoding.encode(value))
            if key == "name":
                num_tokens += tokens_per_name
    num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
    return num_tokens
