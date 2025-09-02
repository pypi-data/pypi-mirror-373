from typing import Tuple

import httpx
from loguru import logger

from elluminate.resources.base import BaseResource
from elluminate.schemas import InferenceType, LLMConfig
from elluminate.utils import run_async


class LLMConfigsResource(BaseResource):
    async def aget(self, name: str) -> LLMConfig:
        """Async version of get."""
        response = await self._aget("llm_configs", params={"name": name})
        configs = [LLMConfig.model_validate(config) for config in response.json()["items"]]

        if not configs:
            raise ValueError(f"No LLM config found with name '{name}'")
        return configs[0]

    def get(self, name: str) -> LLMConfig:
        """Get an LLM config by name.

        Args:
            name (str): Name of the LLM config.

        Returns:
            (LLMConfig): The requested LLM config.

        Raises:
            ValueError: If no LLM config is found with the given name.

        """
        return run_async(self.aget)(name)

    async def aget_by_id(self, id: int) -> LLMConfig:
        """Async version of get_by_id."""
        response = await self._aget(f"llm_configs/{id}")

        return LLMConfig.model_validate(response.json())

    def get_by_id(self, id: int) -> LLMConfig:
        """Get an LLM config by id.

        Args:
            id (int): The id of the LLM config.

        Returns:
            (LLMConfig): The requested LLM config.

        """
        return run_async(self.aget_by_id)(id)

    async def acreate(
        self,
        name: str,
        llm_model_name: str,
        api_key: str,
        description: str = "",
        llm_base_url: str | None = None,
        api_version: str | None = None,
        max_connections: int = 10,
        max_retries: int | None = None,
        timeout: int | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        temperature: float | None = None,
        best_of: int | None = None,
        top_k: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        reasoning_effort: str | None = None,
        inference_type: InferenceType = InferenceType.OPENAI,
        custom_api_config: dict | None = None,
        custom_response_parser: str | None = None,
    ) -> LLMConfig:
        """Async version of create."""
        # The create request data is the same as the `LLMConfig`, just without the ID
        create_request_data = LLMConfig(
            name=name,
            description=description,
            llm_model_name=llm_model_name,
            api_key=api_key,
            llm_base_url=llm_base_url,
            api_version=api_version,
            max_connections=max_connections,
            max_retries=max_retries,
            timeout=timeout,
            system_message=system_message,
            max_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature,
            best_of=best_of,
            top_k=top_k,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
            reasoning_effort=reasoning_effort,
            inference_type=inference_type,
            custom_api_config=custom_api_config,
            custom_response_parser=custom_response_parser,
        ).model_dump(exclude={"id"})
        response = await self._apost("llm_configs", json=create_request_data)
        return LLMConfig.model_validate(response.json())

    def create(
        self,
        name: str,
        llm_model_name: str,
        api_key: str,
        description: str = "",
        llm_base_url: str | None = None,
        api_version: str | None = None,
        max_connections: int = 10,
        max_retries: int | None = None,
        timeout: int | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        temperature: float | None = None,
        best_of: int | None = None,
        top_k: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        reasoning_effort: str | None = None,
        inference_type: InferenceType = InferenceType.OPENAI,
        custom_api_config: dict | None = None,
        custom_response_parser: str | None = None,
    ) -> LLMConfig:
        """Create a new LLM configuration.

        Args:
            name (str): Name for the LLM config.
            llm_model_name (str): Name of the LLM model.
            api_key (str): API key for the LLM service.
            description (str): Optional description for the LLM config.
            llm_base_url (str | None): Optional base URL for the LLM service.
            api_version (str | None): Optional API version.
            max_connections (int): Maximum number of concurrent connections to the LLM provider.
            max_retries (int | None): Optional maximum number of retries.
            timeout (int | None): Optional timeout in seconds.
            system_message (str | None): Optional system message for the LLM.
            max_tokens (int | None): Optional maximum tokens to generate.
            top_p (float | None): Optional nucleus sampling parameter.
            temperature (float | None): Optional temperature parameter.
            best_of (int | None): Optional number of completions to generate.
            top_k (int | None): Optional top-k sampling parameter.
            logprobs (bool | None): Optional flag to return log probabilities.
            top_logprobs (int | None): Optional number of top log probabilities to return.
            reasoning_effort (str | None): Optional reasoning effort parameter for o-series models.
            inference_type (InferenceType): Type of Inference Provider to use.
            custom_api_config (dict | None): Optional configuration template for custom API providers.
            custom_response_parser (str | None): Optional Python code to parse custom API responses.

        Returns:
            (LLMConfig): The created LLM configuration.

        Raises:
            httpx.HTTPStatusError: If an LLM config with the same name already exists.

        """
        return run_async(self.acreate)(
            name=name,
            llm_model_name=llm_model_name,
            api_key=api_key,
            description=description,
            llm_base_url=llm_base_url,
            api_version=api_version,
            max_connections=max_connections,
            max_retries=max_retries,
            timeout=timeout,
            system_message=system_message,
            max_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature,
            best_of=best_of,
            top_k=top_k,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
            reasoning_effort=reasoning_effort,
            inference_type=inference_type,
            custom_api_config=custom_api_config,
            custom_response_parser=custom_response_parser,
        )

    async def aget_or_create(
        self,
        name: str,
        llm_model_name: str,
        api_key: str,
        description: str = "",
        llm_base_url: str | None = None,
        api_version: str | None = None,
        max_connections: int = 10,
        max_retries: int | None = None,
        timeout: int | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        temperature: float | None = None,
        best_of: int | None = None,
        top_k: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        reasoning_effort: str | None = None,
        inference_type: InferenceType = InferenceType.OPENAI,
        custom_api_config: dict | None = None,
        custom_response_parser: str | None = None,
    ) -> Tuple[LLMConfig, bool]:
        """Async version of get_or_create."""
        # Create a dict of the requested parameters (excluding None values)
        requested_dict = {
            k: v
            for k, v in {
                "name": name,
                "description": description,
                "llm_model_name": llm_model_name,
                "api_key": api_key,
                "llm_base_url": llm_base_url,
                "api_version": api_version,
                "max_connections": max_connections,
                "max_retries": max_retries,
                "timeout": timeout,
                "system_message": system_message,
                "max_tokens": max_tokens,
                "top_p": top_p,
                "temperature": temperature,
                "best_of": best_of,
                "top_k": top_k,
                "logprobs": logprobs,
                "top_logprobs": top_logprobs,
                "reasoning_effort": reasoning_effort,
                "inference_type": inference_type,
                "custom_api_config": custom_api_config,
                "custom_response_parser": custom_response_parser,
            }.items()
            if v is not None
        }

        try:
            return await self.acreate(**requested_dict), True
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                existing_config = await self.aget(name=name)
                existing_dict = existing_config.model_dump()

                differences = []
                for k, v in requested_dict.items():
                    if k not in {"name", "api_key"} and k in existing_dict and v != existing_dict[k]:
                        differences.append(f"{k} (expected: {v}, actual: {existing_dict[k]})")

                if differences:
                    logger.warning(
                        f"LLM config '{name}' already exists with different values for: {', '.join(differences)}. Returning existing config."
                    )

                return existing_config, False
            raise

    def get_or_create(
        self,
        name: str,
        llm_model_name: str,
        api_key: str,
        description: str = "",
        llm_base_url: str | None = None,
        api_version: str | None = None,
        max_connections: int = 10,
        max_retries: int | None = None,
        timeout: int | None = None,
        system_message: str | None = None,
        max_tokens: int | None = None,
        top_p: float | None = None,
        temperature: float | None = None,
        best_of: int | None = None,
        top_k: int | None = None,
        logprobs: bool | None = None,
        top_logprobs: int | None = None,
        reasoning_effort: str | None = None,
        inference_type: InferenceType = InferenceType.OPENAI,
        custom_api_config: dict | None = None,
        custom_response_parser: str | None = None,
    ) -> tuple[LLMConfig, bool]:
        """Get an existing LLM config or create a new one.

        The existence check is only based on the name parameter - if an LLM config with
        the given name exists, it will be returned regardless of the other parameters.
        If no config with that name exists, a new one will be created using all provided
        parameters.

        Args:
            name (str): Name for the LLM config.
            llm_model_name (str): Name of the LLM model.
            api_key (str): API key for the LLM service.
            description (str): Optional description for the LLM config.
            llm_base_url (str | None): Optional base URL for the LLM service.
            api_version (str | None): Optional API version.
            max_connections (int): Maximum number of concurrent connections to the LLM provider.
            max_retries (int | None): Optional maximum number of retries.
            timeout (int | None): Optional timeout in seconds.
            system_message (str | None): Optional system message for the LLM.
            max_tokens (int | None): Optional maximum tokens to generate.
            top_p (float | None): Optional nucleus sampling parameter.
            temperature (float | None): Optional temperature parameter.
            best_of (int | None): Optional number of completions to generate.
            top_k (int | None): Optional top-k sampling parameter.
            logprobs (bool | None): Optional flag to return log probabilities.
            top_logprobs (int | None): Optional number of top log probabilities to return.
            reasoning_effort (str | None): Optional reasoning effort parameter for o-series models.
            inference_type (InferenceType): Type of Inference Provider to use.
            custom_api_config (dict | None): Optional configuration template for custom API providers.
            custom_response_parser (str | None): Optional Python code to parse custom API responses.

        Returns:
            tuple[LLMConfig, bool]: A tuple containing:
                - The LLM configuration
                - Boolean indicating if a new config was created (True) or existing one returned (False)

        """
        return run_async(self.aget_or_create)(
            name=name,
            llm_model_name=llm_model_name,
            api_key=api_key,
            description=description,
            llm_base_url=llm_base_url,
            api_version=api_version,
            max_connections=max_connections,
            max_retries=max_retries,
            timeout=timeout,
            system_message=system_message,
            max_tokens=max_tokens,
            top_p=top_p,
            temperature=temperature,
            best_of=best_of,
            top_k=top_k,
            logprobs=logprobs,
            top_logprobs=top_logprobs,
            reasoning_effort=reasoning_effort,
            inference_type=inference_type,
            custom_api_config=custom_api_config,
            custom_response_parser=custom_response_parser,
        )

    async def adelete(self, llm_config: LLMConfig) -> None:
        """Async version of delete."""
        await self._adelete(f"llm_configs/{llm_config.id}")

    def delete(self, llm_config: LLMConfig) -> None:
        """Deletes an LLM configuration.

        Args:
            llm_config (LLMConfig): The LLM configuration to delete.

        Raises:
            httpx.HTTPStatusError: If the LLM config doesn't exist or belongs to a different project.

        """
        return run_async(self.adelete)(llm_config)
