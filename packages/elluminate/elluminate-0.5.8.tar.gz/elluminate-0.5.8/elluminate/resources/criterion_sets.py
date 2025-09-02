from typing import List, Tuple

from loguru import logger

from elluminate.resources.base import BaseResource
from elluminate.schemas import (
    PromptTemplate,
)
from elluminate.schemas.criterion import CriterionIn
from elluminate.schemas.criterion_set import CreateCriterionSetRequest, CriterionSet
from elluminate.utils import retry_request, run_async


class CriterionSetsResource(BaseResource):
    async def alist(self) -> List[CriterionSet]:
        """Async version of list."""
        return await self._paginate(
            path="criterion_sets",
            model=CriterionSet,
            resource_name="Criterion Sets",
        )

    def list(self) -> List[CriterionSet]:
        """List all criterion sets in the project.

        Returns:
            list[CriterionSet]: List of criterion set objects.

        """
        return run_async(self.alist)()

    @retry_request
    async def aget(self, name: str, prompt_template: PromptTemplate) -> CriterionSet:
        """Async version of get."""
        params = {
            "name": name,
            "prompt_template_id": prompt_template.id,
        }
        response = await self._aget("criterion_sets", params=params)

        # Parse response - look for items in the response
        data = response.json()
        items = data.get("items", [])

        if not items:
            raise ValueError(f"No criterion set found with name '{name}' for the specified prompt template")

        return CriterionSet.model_validate(items[0])

    def get(self, name: str, prompt_template: PromptTemplate) -> CriterionSet:
        """Get a specific criterion set by name and prompt template.

        Args:
            name (str): The name of the criterion set.
            prompt_template (PromptTemplate): The prompt template associated with the criterion set.

        Returns:
            CriterionSet: The requested criterion set.

        Raises:
            ValueError: If no criterion set is found with the specified name and prompt template.

        """
        return run_async(self.aget)(name, prompt_template)

    async def aget_by_id(self, id: int) -> CriterionSet:
        """Async version of get_by_id."""
        response = await self._aget(f"criterion_sets/{id}")

        return CriterionSet.model_validate(response.json())

    def get_by_id(self, id: int) -> CriterionSet:
        """Get a criterion set by id.

        Args:
            id (int): The id of the criterion set.

        Returns:
            (CriterionSet): The requested criterion set.

        """
        return run_async(self.aget_by_id)(id)

    @retry_request
    async def acreate(
        self,
        name: str,
        prompt_template: PromptTemplate | None = None,
        criteria: List[str | CriterionIn] | None = None,
    ) -> CriterionSet:
        """Async version of create."""
        # Convert `str` criteria to `CriterionIn` before sending the request
        normalized_criteria = None
        if criteria:
            normalized_criteria = [CriterionIn(criterion_str=c) if isinstance(c, str) else c for c in criteria]

        request_data = CreateCriterionSetRequest(
            name=name,
            criteria=normalized_criteria,
        )
        response = await self._apost("criterion_sets", json=request_data.model_dump())
        criterion_set = CriterionSet.model_validate(response.json())

        # If a prompt template is provided, link it to the criterion set
        if prompt_template:
            criterion_set = await self.aadd_prompt_template(criterion_set, prompt_template)

        return criterion_set

    def create(
        self,
        name: str,
        prompt_template: PromptTemplate | None = None,
        criteria: List[str | CriterionIn] | None = None,
    ) -> CriterionSet:
        """Create a new criterion set and optionally associate it with a prompt template.

        Args:
            name (str): The name of the criterion set.
            prompt_template (PromptTemplate, optional): The prompt template to associate with the criterion set.
                If None, creates a criterion set not linked to any template.
            criteria (list[str | CriterionIn], optional): List of criterion strings or CriterionIn objects.

        Returns:
            CriterionSet: The created criterion set.

        """
        return run_async(self.acreate)(name, prompt_template, criteria)

    async def aget_or_create(
        self,
        name: str,
        prompt_template: PromptTemplate,
        criteria: List[str | CriterionIn] | None = None,
    ) -> Tuple[CriterionSet, bool]:
        """Async version of get_or_create.

        Attempts to get a criterion set first. If it raises ValueError, creates a new one.
        """
        # First attempt to get the existing criterion set
        try:
            existing_criterion_set = await self.aget(name=name, prompt_template=prompt_template)
            logger.info(f"Found existing criterion set '{name}'")
            return existing_criterion_set, False
        except ValueError:
            # Criterion set doesn't exist, create it
            new_criterion_set = await self.acreate(name=name, prompt_template=prompt_template, criteria=criteria)
            return new_criterion_set, True

    def get_or_create(
        self,
        name: str,
        prompt_template: PromptTemplate,
        criteria: List[str | CriterionIn] | None = None,
    ) -> Tuple[CriterionSet, bool]:
        """Get or create a criterion set for a prompt template.

        Attempts to get a criterion set first. If it raises ValueError, creates a new one.

        Args:
            name (str): The name of the criterion set.
            prompt_template (PromptTemplate): The prompt template to associate with the criterion set.
            criteria (list[str | CriterionIn], optional): List of criterion strings or CriterionIn objects.
                if creation is needed.

        Returns:
            Tuple[CriterionSet, bool]: A tuple containing:
                - The criterion set
                - Boolean indicating if a new criterion set was created (True) or existing one returned (False)

        """
        return run_async(self.aget_or_create)(name, prompt_template, criteria)

    async def adelete(self, criterion_set: CriterionSet) -> None:
        """Async version of delete."""
        await self._adelete(f"criterion_sets/{criterion_set.id}")

    def delete(self, criterion_set: CriterionSet) -> None:
        """Delete a criterion set.

        This will also delete all associated criteria.

        Args:
            criterion_set (CriterionSet): The criterion set to delete.

        """
        return run_async(self.adelete)(criterion_set)

    @retry_request
    async def aadd_prompt_template(
        self, criterion_set: CriterionSet, prompt_template: PromptTemplate
    ) -> CriterionSet:
        """Async version of add_prompt_template."""
        response = await self._aput(
            f"criterion_sets/{criterion_set.id}/prompt_templates/{prompt_template.id}",
        )
        return CriterionSet.model_validate(response.json())

    def add_prompt_template(self, criterion_set: CriterionSet, prompt_template: PromptTemplate) -> CriterionSet:
        """Add a prompt template to an existing criterion set.

        Args:
            criterion_set (CriterionSet): The criterion set.
            prompt_template (PromptTemplate): The prompt template to add.

        Returns:
            CriterionSet: The updated criterion set.

        """
        return run_async(self.aadd_prompt_template)(criterion_set, prompt_template)

    async def aremove_prompt_template(self, criterion_set: CriterionSet, prompt_template: PromptTemplate) -> None:
        """Async version of remove_prompt_template."""
        await self._adelete(f"criterion_sets/{criterion_set.id}/prompt_templates/{prompt_template.id}")

    def remove_prompt_template(self, criterion_set: CriterionSet, prompt_template: PromptTemplate) -> None:
        """Remove a prompt template from a criterion set.

        Args:
            criterion_set (CriterionSet): The criterion set.
            prompt_template (PromptTemplate): The prompt template to remove.

        """
        return run_async(self.aremove_prompt_template)(criterion_set, prompt_template)
