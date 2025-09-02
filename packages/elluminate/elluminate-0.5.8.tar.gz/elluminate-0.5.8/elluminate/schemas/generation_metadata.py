from pydantic import BaseModel

from elluminate.schemas.llm_config import LLMConfig


class GenerationMetadata(BaseModel):
    """Metadata about an LLM generation."""

    llm_model_config: LLMConfig
    duration_seconds: float | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None

    def __repr__(self) -> str:
        return f"Generation for {self.llm_model_config!s}"
