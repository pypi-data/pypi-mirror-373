from enum import Enum
from typing import Literal

from pydantic import BaseModel


class InferenceType(str, Enum):
    OPENAI = "openai"
    BOTARIO = "botario"
    CUSTOM_API = "custom_api"


class LLMConfig(BaseModel):
    """Model for an LLM configuration."""

    # These fields will be set properly when `LLMConfig` is used as a response (output) model
    id: int | None = None
    name: str | None = None
    description: str = ""

    # LLM configuration settings
    llm_model_name: str
    llm_base_url: str | None = None
    api_key: str | None = None
    api_version: str | None = None
    max_connections: int = 10
    inference_type: InferenceType = InferenceType.OPENAI

    # Sampling parameters
    max_retries: int | None = None
    timeout: int | None = None
    system_message: str | None = None
    max_tokens: int | None = None
    top_p: float | None = None
    temperature: float | None = None
    best_of: int | None = None
    top_k: int | None = None
    logprobs: bool | None = None
    top_logprobs: int | None = None
    reasoning_effort: None | Literal["low", "medium", "high"] = (
        None  # reasoning effort for o-series models. Mutually exclusive with temperature.
    )

    # Custom API configuration for generic API providers
    custom_api_config: dict | None = None

    # Custom response parser code for parsing non-standard API responses
    custom_response_parser: str | None = None
