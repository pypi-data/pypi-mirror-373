from datetime import datetime
from typing import List

from openai.types.chat import ChatCompletionMessageParam
from pydantic import BaseModel

from elluminate.schemas.prompt_template import PromptTemplate
from elluminate.schemas.template_variables import TemplateVariables


class Prompt(BaseModel):
    """New prompt model."""

    id: int
    prompt_template: PromptTemplate
    template_variables: TemplateVariables
    messages: List[ChatCompletionMessageParam] = []
    created_at: datetime
