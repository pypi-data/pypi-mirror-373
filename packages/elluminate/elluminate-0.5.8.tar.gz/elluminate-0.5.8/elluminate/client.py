import asyncio
import os
from typing import Any, ClassVar

import httpx
from loguru import logger

from elluminate.resources import (
    CriteriaResource,
    CriterionSetsResource,
    ExperimentsResource,
    LLMConfigsResource,
    ProjectsResource,
    PromptTemplatesResource,
    RatingsResource,
    ResponsesResource,
    TemplateVariablesCollectionsResource,
    TemplateVariablesResource,
)
from elluminate.utils import raise_for_status_with_detail


class Client:
    _semaphore: ClassVar[asyncio.Semaphore] = asyncio.Semaphore(10)

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        api_key_env: str = "ELLUMINATE_API_KEY",
        base_url_env: str = "ELLUMINATE_BASE_URL",
        timeout: float = 120.0,
    ) -> None:
        """Initialize the Elluminate SDK client.

        Args:
            base_url (str): Base URL of the Elluminate API. Defaults to "https://app.elluminate.de".
            api_key (str | None): API key for authentication. If not provided, will look for key in environment variable given by `api_key_env`.
            api_key_env (str): Name of environment variable containing API key. Defaults to "ELLUMINATE_API_KEY".
            base_url_env (str): Name of environment variable containing base URL. Defaults to "ELLUMINATE_BASE_URL". If set, overrides base_url.
            timeout (float): Timeout in seconds for API requests. Defaults to 120.0.

        Raises:
            ValueError: If no API key is provided or found in environment.

        """
        # Init the API key
        self.api_key = api_key or os.getenv(api_key_env)
        if not self.api_key:
            raise ValueError(f"{api_key_env} not set.")

        # Init the base URL. Use a sane default if no values are provided
        self.base_url = base_url or os.getenv(base_url_env) or "https://app.elluminate.de"
        if not base_url and os.getenv(base_url_env):
            logger.debug(f"Using base URL from environment: {self.base_url}")

        # Get the SDK version for headers
        # Local import to avoid circular imports
        from elluminate import __version__

        headers = {"X-API-Key": self.api_key, "SDK-Version": __version__}

        # Create sessions with complete headers
        self.timeout = timeout
        timeout_config = httpx.Timeout(self.timeout)
        self.async_session = httpx.AsyncClient(headers=headers, timeout=timeout_config, follow_redirects=True)
        # This is only needed to get the project synchronously
        self.sync_session = httpx.Client(headers=headers, timeout=timeout_config, follow_redirects=True)

        # Check the SDK version compatibility and print warning if needed
        self.check_version()

        # Load the project and set the route prefix
        self.projects = ProjectsResource(self)
        self.project = self.projects.load_project(url=f"{self.base_url}/api/v0/projects")
        self.project_route_prefix = f"{self.base_url}/api/v0/projects/{self.project.id}"

        # Initialize the resources
        self.prompt_templates = PromptTemplatesResource(self)
        self.collections = TemplateVariablesCollectionsResource(self)
        self.template_variables = TemplateVariablesResource(self)
        self.responses = ResponsesResource(self)
        self.criteria = CriteriaResource(self)
        self.criterion_sets = CriterionSetsResource(self)
        self.llm_configs = LLMConfigsResource(self)
        self.experiments = ExperimentsResource(self)
        self.ratings = RatingsResource(self)

    def check_version(self) -> None:
        """Check if the SDK version is compatible with the required version."""
        # Import locally to avoid circular imports
        from elluminate import __version__

        response = self.sync_session.post(
            f"{self.base_url}/api/v0/version/compatible",
            json={"current_sdk_version": __version__},
        )
        raise_for_status_with_detail(response)
        compatibility = response.json()
        if not compatibility["is_compatible"]:
            response = httpx.get("https://pypi.org/pypi/elluminate/json")
            current_pypi_version = response.json()["info"]["version"]
            logger.warning(
                f"Current SDK version ({__version__}) is not compatible with the required version ({compatibility['required_sdk_version']}). "
                "Some features may not work as expected. "
                f"Please upgrade the SDK to the latest version ({current_pypi_version}) by running `pip install -U elluminate`."
            )

    async def _aget(self, path: str, **kwargs: Any) -> httpx.Response:
        response = await self.async_session.get(f"{self.project_route_prefix}/{path}", **kwargs)
        raise_for_status_with_detail(response)
        return response

    async def _apost(self, path: str, **kwargs: Any) -> httpx.Response:
        response = await self.async_session.post(f"{self.project_route_prefix}/{path}", **kwargs)
        raise_for_status_with_detail(response)
        return response

    async def _aput(self, path: str, **kwargs: Any) -> httpx.Response:
        response = await self.async_session.put(f"{self.project_route_prefix}/{path}", **kwargs)
        raise_for_status_with_detail(response)
        return response

    async def _adelete(self, path: str, **kwargs: Any) -> httpx.Response:
        response = await self.async_session.delete(f"{self.project_route_prefix}/{path}", **kwargs)
        raise_for_status_with_detail(response)
        return response
