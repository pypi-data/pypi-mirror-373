from datetime import datetime
from typing import Any

from pydantic import BaseModel, model_validator
from typing_extensions import Self

from elluminate.schemas.template_variables_collection import TemplateVariablesCollection


class TemplateVariables(BaseModel):
    """Template variables model."""

    id: int
    input_values: dict[str, Any]
    collection: TemplateVariablesCollection
    created_at: datetime


class CreateTemplateVariablesRequest(BaseModel):
    """Request to create a new template variables entry in a collection.

    This model intentionally supports two mutually exclusive modes of operation:
    1. Manual Entry Mode:
       - Set input_values with your template variable data
       - Leave prompt_template_id as None
       - Used for direct creation of template variables

    2. AI Generation Mode:
       - Set prompt_template_id to reference a prompt template
       - Leave input_values as None
       - Used for AI-powered generation of template variables
    """

    input_values: dict[str, str] | None = None
    prompt_template_id: int | None = None

    @model_validator(mode="after")
    def validate_exactly_one_field(self) -> Self:
        """Validate that exactly one of input_values or prompt_template_id is set."""
        if (self.input_values is None and self.prompt_template_id is None) or (
            self.input_values is not None and self.prompt_template_id is not None
        ):
            raise ValueError("Exactly one of input_values or prompt_template_id must be provided")
        return self
