from elluminate.resources.base import BaseResource
from elluminate.schemas import (
    CreateTemplateVariablesRequest,
    TemplateVariables,
    TemplateVariablesCollection,
)
from elluminate.schemas.prompt_template import PromptTemplate
from elluminate.utils import run_async


class TemplateVariablesResource(BaseResource):
    async def alist(self, collection: TemplateVariablesCollection) -> list[TemplateVariables]:
        """Async version of list."""
        return await self._paginate(
            path=f"collections/{collection.id}/entries",
            model=TemplateVariables,
            resource_name="Template Variables",
        )

    def list(self, collection: TemplateVariablesCollection) -> list[TemplateVariables]:
        """Returns all template variables for a collection.

        Args:
            collection (TemplateVariablesCollection): The collection to get entries for.

        Returns:
            list[TemplateVariables]: List of template variables.

        Raises:
            httpx.HTTPStatusError: If the collection is not found

        """
        return run_async(self.alist)(collection)

    async def aget_by_id(self, collection_id: int, id: int) -> TemplateVariables:
        """Async version of get_by_id."""
        response = await self._aget(f"collections/{collection_id}/entries/{id}")

        return TemplateVariables.model_validate(response.json())

    def get_by_id(self, collection_id: int, id: int) -> TemplateVariables:
        """Get a template variable by id.

        Args:
            collection_id (int): The id of the collection containing the template variable.
            id (int): The id of the template variable.

        Returns:
            (TemplateVariables): The requested template variable.

        """
        return run_async(self.aget_by_id)(collection_id, id)

    async def aadd_to_collection(
        self, template_variables: dict[str, str], collection: TemplateVariablesCollection
    ) -> TemplateVariables:
        """Async version of add_to_collection."""
        response = await self._apost(
            f"collections/{collection.id}/entries",
            json=CreateTemplateVariablesRequest(input_values=template_variables).model_dump(),
        )
        return TemplateVariables.model_validate(response.json())

    def add_to_collection(
        self, template_variables: dict[str, str], collection: TemplateVariablesCollection
    ) -> TemplateVariables:
        """Adds a new entry to a collection. If the entry already exists, it will be returned.

        Args:
            template_variables (dict[str, str]): The template variables to add.
            collection (TemplateVariablesCollection): The collection to add the entry to.

        Returns:
            TemplateVariables: The retrieved or created template variables object

        """
        return run_async(self.aadd_to_collection)(template_variables, collection)

    async def agenerate(
        self, collection: TemplateVariablesCollection, prompt_template: PromptTemplate
    ) -> TemplateVariables:
        """Async version of generate."""
        async with self._semaphore:
            response = await self._apost(
                f"collections/{collection.id}/entries",
                json=CreateTemplateVariablesRequest(
                    input_values=None, prompt_template_id=prompt_template.id
                ).model_dump(),
            )
        return TemplateVariables.model_validate(response.json())

    def generate(
        self, collection: TemplateVariablesCollection, prompt_template: PromptTemplate
    ) -> TemplateVariables:
        """Generates a new template variable in a collection using a prompt template.

        Args:
            collection (TemplateVariablesCollection): The collection to add the generated template variable to.
            prompt_template (PromptTemplate): The prompt template to use for generation.

        Returns:
            TemplateVariables: The newly generated template variables object.

        """
        return run_async(self.agenerate)(collection, prompt_template)

    async def adelete(self, template_variables: TemplateVariables, collection: TemplateVariablesCollection) -> None:
        """Async version of delete."""
        await self._adelete(f"collections/{collection.id}/entries/{template_variables.id}")

    def delete(self, template_variables: TemplateVariables, collection: TemplateVariablesCollection) -> None:
        """Deletes a template variables.

        Args:
            template_variables (TemplateVariables): The template variables to delete.
            collection (TemplateVariablesCollection): The collection containing the template variables.

        Raises:
            httpx.HTTPStatusError: If the template variables doesn't exist, belongs to a different collection,
                or belongs to a different project.

        """
        return run_async(self.adelete)(template_variables, collection)

    async def adelete_all(self, collection: TemplateVariablesCollection) -> None:
        """Async version of delete_all."""
        await self._adelete(f"collections/{collection.id}/entries")

    def delete_all(self, collection: TemplateVariablesCollection) -> None:
        """Deletes all template variables for a collection.

        Args:
            collection (TemplateVariablesCollection): The collection to delete all template variables for.

        Raises:
            httpx.HTTPStatusError: If the collection doesn't exist or belongs to a different project.

        """
        return run_async(self.adelete_all)(collection)
