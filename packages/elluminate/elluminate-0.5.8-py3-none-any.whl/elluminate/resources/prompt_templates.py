from typing import Any, Dict, List, Literal, Tuple, Type

import httpx
from openai.types.beta import AssistantToolChoiceOption, FunctionTool
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionUserMessageParam
from pydantic import BaseModel

from elluminate.resources.base import BaseResource
from elluminate.schemas import (
    CreatePromptTemplateRequest,
    CriterionSet,
    PromptTemplate,
    PromptTemplateFilter,
    TemplateVariablesCollection,
)
from elluminate.utils import run_async


def _convert_response_format_to_backend_format(response_format: Type[BaseModel] | Dict[str, Any]) -> Dict[str, Any]:
    """Convert a response format to the format expected by the backend.

    Args:
        response_format: Either a Pydantic model class or an OpenAI-style dict format

    Returns:
        Dictionary in the format expected by the backend

    """
    if isinstance(response_format, type) and issubclass(response_format, BaseModel):
        # Create a `json_schema` from this Pydantic model definition
        # Models the behavior of `openai.lib._pydantic.to_strict_json_schema`, but chose to not
        # use since it is a part of the private `_pydantic` module of the `openai` package
        schema = response_format.model_json_schema()
        if "additionalProperties" not in schema:
            schema["additionalProperties"] = False
        return {
            "type": "json_schema",
            "json_schema": {
                "name": response_format.__name__.lower(),
                "schema": schema,
                "strict": True,
            },
        }
    elif isinstance(response_format, dict):
        return response_format
    else:
        raise ValueError("response_format must be either a Pydantic model class or OpenAI structured outputs dict")


class PromptTemplatesResource(BaseResource):
    async def aget(
        self,
        name: str,
        version: int | Literal["latest"] = "latest",
    ) -> PromptTemplate:
        """Async version of get_prompt_template."""
        params = {}
        if name:
            params["name"] = name
        if version != "latest":
            params["version"] = str(version)

        response = await self._aget("prompt_templates", params=params)
        templates = [PromptTemplate.model_validate(template) for template in response.json().get("items", [])]
        if not templates:
            raise ValueError(f"No prompt template found with name {name} and version {version}")
        return templates[0]

    def get(
        self,
        name: str,
        version: int | Literal["latest"] = "latest",
    ) -> PromptTemplate:
        """Get a prompt template by name and version.

        Args:
            name (str): Name of the prompt template.
            version (int | Literal["latest"]): Version number or "latest". Defaults to "latest".

        Returns:
            (PromptTemplate): The requested prompt template.

        Raises:
            ValueError: If no template is found with given name and version.

        """
        return run_async(self.aget)(name, version)

    async def aget_by_id(self, id: int) -> PromptTemplate:
        """Async version of get_by_id."""
        response = await self._aget(f"prompt_templates/{id}")

        return PromptTemplate.model_validate(response.json())

    def get_by_id(self, id: int) -> PromptTemplate:
        """Get a prompt template by id.

        Args:
            id (int): The id of the prompt template.

        Returns:
            (PromptTemplate): The requested prompt template.

        """
        return run_async(self.aget_by_id)(id)

    async def alist(
        self,
        name: str | None = None,
        criterion_set: CriterionSet | None = None,
        compatible_collection: TemplateVariablesCollection | None = None,
    ) -> list[PromptTemplate]:
        """Async version of list."""
        filter = PromptTemplateFilter(
            name=name,
            criterion_set_id=criterion_set.id if criterion_set else None,
        ).model_dump(exclude_none=True)

        # Add empty sort options (required by the API)
        filter["sort_options"] = {}
        # Add compatible_collection_id separately if it exists
        if compatible_collection:
            filter["compatible_collection_id"] = compatible_collection.id

        return await self._paginate(
            path="prompt_templates",
            model=PromptTemplate,
            params=filter,
        )

    def list(
        self,
        name: str | None = None,
        criterion_set: CriterionSet | None = None,
        compatible_collection: TemplateVariablesCollection | None = None,
    ) -> list[PromptTemplate]:
        """Get a list of prompt templates.

        Args:
            name (str | None): Name of the prompt template to filter by.
            criterion_set (CriterionSet | None): Criterion set to filter by.
            compatible_collection (TemplateVariablesCollection | None): Compatible template variables collection to filter by.

        Returns:
            list[PromptTemplate]: A list of prompt templates.

        """
        return run_async(self.alist)(
            name=name,
            criterion_set=criterion_set,
            compatible_collection=compatible_collection,
        )

    async def acreate(
        self,
        user_prompt_template: str | List[ChatCompletionMessageParam],
        name: str,
        parent_prompt_template: PromptTemplate | None = None,
        response_format: Type[BaseModel] | Dict[str, Any] | None = None,
        tools: List[FunctionTool] | None = None,
        tool_choice: AssistantToolChoiceOption | None = None,
    ) -> PromptTemplate:
        """Async version of create."""
        if isinstance(user_prompt_template, str):
            messages = [ChatCompletionUserMessageParam(role="user", content=user_prompt_template)]
        else:
            messages = user_prompt_template

        # Convert response_format to response_format_json_schema if provided
        response_format_json_schema = None
        if response_format is not None:
            response_format_json_schema = _convert_response_format_to_backend_format(response_format)

        prompt_template_create = CreatePromptTemplateRequest(
            name=name,
            messages=messages,
            response_format_json_schema=response_format_json_schema,
            tools=tools,
            tool_choice=tool_choice,
            parent_prompt_template_id=parent_prompt_template.id if parent_prompt_template else None,
        )

        response = await self._apost("prompt_templates", json=prompt_template_create.model_dump())
        return PromptTemplate.model_validate(response.json())

    def create(
        self,
        user_prompt_template: str | List[ChatCompletionMessageParam],
        name: str,
        parent_prompt_template: PromptTemplate | None = None,
        response_format: Type[BaseModel] | Dict[str, Any] | None = None,
        tools: List[FunctionTool] | None = None,
        tool_choice: AssistantToolChoiceOption | None = None,
    ) -> PromptTemplate:
        """Create a new prompt template.

        Args:
            user_prompt_template (str | ChatCompletionMessageParam): The template containing variables in {{variable}} format.
            name (str): Name for the template.
            parent_prompt_template (PromptTemplate | None): Optional parent template to inherit from.
            response_format (Type[BaseModel] | Dict[str, Any] | None): Optional Pydantic model or OpenAI-style dict for structured output generation.
            tools (List[FunctionTool] | None): Optional list of tools available to the model.
            tool_choice (AssistantToolChoiceOption | None): Optional tool choice setting.

        """
        return run_async(self.acreate)(
            name=name,
            user_prompt_template=user_prompt_template,
            parent_prompt_template=parent_prompt_template,
            response_format=response_format,
            tools=tools,
            tool_choice=tool_choice,
        )

    async def aget_or_create(
        self,
        user_prompt_template: str | List[ChatCompletionMessageParam],
        name: str,
        parent_prompt_template: PromptTemplate | None = None,
        response_format: Type[BaseModel] | None = None,
        tools: List[FunctionTool] | None = None,
        tool_choice: AssistantToolChoiceOption | None = None,
    ) -> Tuple[PromptTemplate, bool]:
        """Async version of get_or_create_prompt_template."""
        try:
            return await self.acreate(
                user_prompt_template=user_prompt_template,
                name=name,
                parent_prompt_template=parent_prompt_template,
                response_format=response_format,
                tools=tools,
                tool_choice=tool_choice,
            ), True
        except httpx.HTTPStatusError as e:
            # Code 409 means resource already exists, simply get and return it
            if e.response.status_code == 409:
                ## If we got a conflict, extract the existing template ID and fetch it
                error_data = e.response.json()
                template_id = error_data.get("prompt_template_id")
                if template_id is None:
                    raise ValueError("Received 409 without prompt_template_id") from e

                response = await self._aget(f"prompt_templates/{template_id}")
                prompt_template = PromptTemplate.model_validate(response.json())
                return prompt_template, False
            raise  # Re-raise any other HTTP status errors

    def get_or_create(
        self,
        user_prompt_template: str | List[ChatCompletionMessageParam],
        name: str,
        parent_prompt_template: PromptTemplate | None = None,
        response_format: Type[BaseModel] | None = None,
        tools: List[FunctionTool] | None = None,
        tool_choice: AssistantToolChoiceOption | None = None,
    ) -> tuple[PromptTemplate, bool]:
        """Gets the prompt template by its name and user prompt contents if it exists.
        If the prompt template name does not exist, it creates a new prompt template with version 1.
        If a prompt template with the same name exists, but the user prompt is new,
        then it creates a new prompt template version with the new user prompt
        which will be the new latest version. When a prompt template with the same name and
        user prompt already exists, it returns the existing prompt template, ignoring the given
        parent_prompt_template.

        Args:
            user_prompt_template (str | ChatCompletionMessageParam): The template containing variables in {{variable}} format.
            name (str): Name for the template.
            parent_prompt_template (PromptTemplate | None): Optional parent template to inherit from.
            response_format (Type[BaseModel] | None): Optional Pydantic model for structured output generation.
            tools (List[FunctionTool] | None): Optional list of tools available to the model.
            tool_choice (AssistantToolChoiceOption | None): Optional tool choice setting.

        Returns:
            tuple[PromptTemplate, bool]: A tuple containing:
                - The prompt template
                - Boolean indicating if a new template was created (True) or existing one returned (False)

        Raises:
            ValueError: If a 409 response is received without a prompt_template_id.

        """
        return run_async(self.aget_or_create)(
            user_prompt_template=user_prompt_template,
            name=name,
            parent_prompt_template=parent_prompt_template,
            response_format=response_format,
            tools=tools,
            tool_choice=tool_choice,
        )

    async def adelete(self, prompt_template: PromptTemplate) -> None:
        """Async version of delete."""
        await self._adelete(f"prompt_templates/{prompt_template.id}")

    def delete(self, prompt_template: PromptTemplate) -> None:
        """Deletes a prompt template.

        Args:
            prompt_template (PromptTemplate): The prompt template to delete.

        Raises:
            httpx.HTTPStatusError: If the prompt template doesn't exist or belongs to a different project.

        """
        return run_async(self.adelete)(prompt_template)
