import httpx

from elluminate.resources.base import BaseResource
from elluminate.schemas import Project
from elluminate.utils import raise_for_status_with_detail


class ProjectsResource(BaseResource):
    async def aload_project(self, url: str) -> Project:
        """Async version of load_project."""
        response = await self._client.async_session.get(url)
        raise_for_status_with_detail(response)
        projects = [Project.model_validate(project) for project in response.json()["items"]]
        if not projects:
            raise RuntimeError("No projects found.")
        return projects[0]

    def load_project(self, url: str) -> Project:
        """Loads the project associated with the API key.

        Args:
            url (str): The URL where the project is hosted.

        Returns:
            (Project): The project associated with the API key.

        Raises:
            RuntimeError: If no projects are found.

        """
        response = self._client.sync_session.get(url)
        if response.status_code == 404:
            raise httpx.HTTPStatusError(
                "No project found (404). Please double check that your base_url and API key are set correctly (also check your environment variables ELLUMINATE_API_KEY and ELLUMINATE_BASE_URL).",
                request=response.request,
                response=response,
            )
        raise_for_status_with_detail(response)
        projects = [Project.model_validate(project) for project in response.json()["items"]]
        if not projects:
            raise RuntimeError("No projects found.")
        return projects[0]
