from __future__ import annotations

import re
from datetime import datetime
from typing import Any, ClassVar, Dict, List, Literal

from openai.types.beta import AssistantToolChoiceOption, FunctionTool
from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel, model_validator


class TemplateString(BaseModel):
    """Convenience class for rendering a string with template variables."""

    template_str: str
    _PLACEHOLDER_PATTERN: ClassVar[re.Pattern] = re.compile(r"{{\s*(\w+)\s*}}")

    @property
    def is_template(self) -> bool:
        """Return True if the template string contains any placeholders."""
        return bool(self._PLACEHOLDER_PATTERN.search(self.template_str))

    @property
    def placeholders(self) -> set[str]:
        """Return a set of all the placeholders in the template string."""
        return set(self._PLACEHOLDER_PATTERN.findall(self.template_str))

    def render(self, **kwargs: str) -> str:
        """Render the template string with the given variables. Raises ValueError if any placeholders are missing."""
        if not set(self.placeholders).issubset(set(kwargs.keys())):
            missing = set(self.placeholders) - set(kwargs.keys())
            raise ValueError(f"Missing template variables: {str(missing)}")

        def replacer(regex_match: re.Match[str]) -> str:
            var_name = regex_match.group(1)
            return str(kwargs[var_name])

        return self._PLACEHOLDER_PATTERN.sub(replacer, self.template_str)

    def __str__(self) -> str:
        return self.template_str

    def __eq__(self, other: object) -> bool:
        """Compare TemplateString with another object.

        If other is a string, compare with template_str.
        If other is a TemplateString, compare template_str values.
        """
        if isinstance(other, str):
            return self.template_str == other
        if isinstance(other, TemplateString):
            return self.template_str == other.template_str
        return NotImplemented


class PromptTemplateFilter(BaseModel):
    name: str | None = None
    version: int | Literal["latest"] | None = None
    search: str | None = None
    criterion_set_id: int | None = None

    @model_validator(mode="after")
    def validate_version_requires_name(self) -> "PromptTemplateFilter":
        if self.version is not None and not self.name:
            raise ValueError("Version can only be set when name is provided")
        return self


class PromptTemplate(BaseModel):
    """Prompt template model."""

    id: int
    name: str
    version: int
    messages: List[ChatCompletionMessageParam] = []
    placeholders: set[str] = set()
    response_format_json_schema: Dict[str, Any] | None = None
    tools: List[FunctionTool] | None = None
    tool_choice: AssistantToolChoiceOption | None = None
    created_at: datetime
    updated_at: datetime

    def render_messages(self, **kwargs: str) -> List[ChatCompletionMessageParam]:
        """Render the prompt template with the given variables."""
        rendered_messages = []

        for message in self.messages:
            # Create a copy of the message using dict unpacking
            rendered_message = {**message}

            # If the message has content, render it
            if "content" in message and message["content"]:
                template_string = TemplateString(template_str=message["content"])
                rendered_message["content"] = template_string.render(**kwargs)

            rendered_messages.append(rendered_message)

        return rendered_messages

    @model_validator(mode="before")
    @classmethod
    def fix_message_fields(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        # OpenAI's ChatCompletionAssistantMessageParam requires a tool_calls field.
        # Since this field is not always included, we initialize it
        # as an empty list when absent to ensure compatibility.
        if "messages" in data and isinstance(data["messages"], list):
            for i, msg in enumerate(data["messages"]):
                if isinstance(msg, dict):
                    if msg.get("role") == "assistant":
                        if "tool_calls" not in msg or msg["tool_calls"] is None:
                            data["messages"][i]["tool_calls"] = []

        return data


class CreatePromptTemplateRequest(BaseModel):
    """Request to create a new prompt template."""

    name: str | None = None
    messages: List[ChatCompletionMessageParam] = []
    response_format_json_schema: Dict[str, Any] | None = None
    tools: List[FunctionTool] | None = None
    tool_choice: AssistantToolChoiceOption | None = None
    parent_prompt_template_id: int | None = None

    @model_validator(mode="after")
    def validate_tool_choice_requires_tools(self) -> "CreatePromptTemplateRequest":
        """Validate that tool_choice cannot be set without tools."""
        if self.tool_choice is not None and self.tools is None:
            raise ValueError("tool_choice cannot be set without tools")
        return self
