from datetime import date, datetime
from enum import Enum
from typing import Annotated, Any, List

from openai.types.chat import ChatCompletionMessage, ChatCompletionMessageParam, ChatCompletionToolMessageParam
from pydantic import AfterValidator, BaseModel, BeforeValidator

from elluminate.schemas.base import BatchCreateStatus
from elluminate.schemas.generation_metadata import GenerationMetadata
from elluminate.schemas.prompt import Prompt
from elluminate.schemas.rating import Rating, RatingValue


def fix_message_tool_calls(messages: List[Any]) -> List[Any]:
    """Fix tool_calls field in assistant messages.

    The backend returns a ChatCompletionMessage (tool_calls is optional) and
    we expect a ChatCompletionAssistantMessageParam (tool_calls is list type, non-None)
    """
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "assistant":
            if "tool_calls" in msg and msg["tool_calls"] is None:
                msg["tool_calls"] = []

    return messages


def ensure_tool_calls_list(messages: List[ChatCompletionMessageParam]) -> List[ChatCompletionMessageParam]:
    """Ensure tool_calls is a proper list for assistant messages with tool_calls.

    The `ChatCompletionMessageParam` parses the tool calls as an Iterator. Convert this to a list for ease of use.
    """
    for msg in messages:
        if isinstance(msg, dict) and msg.get("role") == "assistant" and "tool_calls" in msg:
            msg["tool_calls"] = list(msg["tool_calls"])

    return messages


class PromptResponseFilter(BaseModel):
    """Filter for prompt responses."""

    experiment_id: int | None = None
    prompt_id: int | None = None
    prompt_template_id: int | None = None
    template_variables_id: int | None = None
    collection_id: int | None = None
    llm_model_name: str | None = None
    epoch: int | None = None
    response_ids: list[int] | None = None
    duration_seconds_min: float | None = None
    duration_seconds_max: float | None = None
    input_tokens_min: int | None = None
    input_tokens_max: int | None = None
    output_tokens_min: int | None = None
    output_tokens_max: int | None = None


class PromptResponse(BaseModel):
    """Prompt response model."""

    id: int
    prompt: Prompt
    messages: Annotated[
        List[ChatCompletionMessage | ChatCompletionToolMessageParam],
        BeforeValidator(fix_message_tool_calls),
        AfterValidator(ensure_tool_calls_list),
    ]
    generation_metadata: GenerationMetadata | None
    error: str | None
    epoch: int
    ratings: list[Rating] = []
    created_at: datetime


class CreatePromptResponseRequest(BaseModel):
    """Request to create a new prompt response."""

    prompt_template_id: int
    template_variables_id: int
    experiment_id: int
    epoch: int = 1
    llm_config_id: int | None = None
    messages: Annotated[
        List[ChatCompletionMessage | ChatCompletionToolMessageParam],
        BeforeValidator(fix_message_tool_calls),
        AfterValidator(ensure_tool_calls_list),
    ] = []
    metadata: GenerationMetadata | None = None


class BatchCreatePromptResponseRequest(BaseModel):
    prompt_response_ins: list[CreatePromptResponseRequest]


class BatchCreatePromptResponseStatus(BatchCreateStatus[PromptResponse]):
    # The result is a tuple with epoch and response
    pass


class ResponsesSampleFilter(BaseModel):
    """Filter for responses samples."""

    experiment_id: int
    criteria_filter_by: dict[int, RatingValue] | None = None
    duration_seconds_min: float | None = None
    duration_seconds_max: float | None = None
    input_tokens_min: int | None = None
    input_tokens_max: int | None = None
    output_tokens_min: int | None = None
    output_tokens_max: int | None = None


# TODO Switch to StrEnum when we drop support for Python 3.10
class ResponsesSampleSortBy(str, Enum):
    """Sort by for responses samples."""

    RATING_ASC = "rating-asc"
    RATING_DESC = "rating-desc"
    INPUT_TOKENS_ASC = "input-tokens-asc"
    INPUT_TOKENS_DESC = "input-tokens-desc"
    OUTPUT_TOKENS_ASC = "output-tokens-asc"
    OUTPUT_TOKENS_DESC = "output-tokens-desc"
    DURATION_ASC = "duration-asc"
    DURATION_DESC = "duration-desc"


class ResponsesSample(BaseModel):
    """Responses sample model."""

    experiment_id: int
    template_variables_id: int
    prompt_response_ids: list[int]


class DailyUsageStats(BaseModel):
    """Daily usage stats model."""

    date: date
    requests: int = 0
    input_tokens: int = 0
    output_tokens: int = 0


class ResponsesStats(BaseModel):
    """Responses stats model."""

    total_responses: int
    average_duration_seconds: float | None = None
    min_duration_seconds: float | None = None
    max_duration_seconds: float | None = None
    total_input_tokens: int
    total_output_tokens: int
    average_input_tokens: float
    average_output_tokens: float
    average_rating: float | None = None
    daily_usage: list[DailyUsageStats]
