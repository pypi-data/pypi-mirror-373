from typing import List, Tuple, overload

from httpx import HTTPStatusError

from elluminate.resources.base import BaseResource
from elluminate.schemas import (
    Criterion,
    CriterionSet,
    PromptTemplate,
)
from elluminate.schemas.criterion import CreateCriteriaRequest, CriterionIn
from elluminate.utils import retry_request, run_async


class CriteriaResource(BaseResource):
    async def alist(
        self,
        prompt_template: PromptTemplate,
    ) -> List[Criterion]:
        """Async version of list."""
        params = {"prompt_template_id": prompt_template.id}
        return await self._paginate(
            path="criteria",
            model=Criterion,
            params=params,
            resource_name="Criteria",
        )

    def list(
        self,
        prompt_template: PromptTemplate,
    ) -> List[Criterion]:
        """Get the evaluation criteria for a prompt template.

        This method retrieves all criteria associated with the prompt template via criterion sets.

        Args:
            prompt_template (PromptTemplate): The prompt template to get criteria for.

        Returns:
            list[Criterion]: List of criterion objects, ordered by creation date.

        """
        return run_async(self.alist)(prompt_template)

    async def _aadd_many_impl(
        self,
        criteria: List[str | CriterionIn],
        prompt_template: PromptTemplate | None = None,
        criterion_set: CriterionSet | None = None,
        delete_existing: bool = False,
    ) -> List[Criterion]:
        """Internal implementation for adding criteria.

        Either prompt_template or criterion_set must be provided, but not both.
        """
        if prompt_template is None and criterion_set is None:
            raise ValueError("Either prompt_template or criterion_set must be provided.")
        if prompt_template is not None and criterion_set is not None:
            raise ValueError("Cannot provide both prompt_template and criterion_set.")

        # Convert `str` criteria to `CriterionIn` before sending the request
        normalized_criteria = [CriterionIn(criterion_str=c) if isinstance(c, str) else c for c in criteria]

        request_data = CreateCriteriaRequest(
            prompt_template_id=prompt_template.id if prompt_template else None,
            criterion_set_id=criterion_set.id if criterion_set else None,
            criteria=normalized_criteria,
            delete_existing=delete_existing,
        )
        response = await self._apost("criteria", json=request_data.model_dump())
        return [Criterion.model_validate(criterion) for criterion in response.json()]

    @overload
    async def aadd_many(
        self,
        criteria: List[str | CriterionIn],
        prompt_template: PromptTemplate,
        *,
        delete_existing: bool = False,
    ) -> List[Criterion]: ...

    @overload
    async def aadd_many(
        self,
        criteria: List[str | CriterionIn],
        *,
        criterion_set: CriterionSet,
        delete_existing: bool = False,
    ) -> List[Criterion]: ...

    @retry_request
    async def aadd_many(
        self,
        criteria: List[str | CriterionIn],
        prompt_template: PromptTemplate | None = None,
        criterion_set: CriterionSet | None = None,
        delete_existing: bool = False,
    ) -> List[Criterion]:
        """Async version of add_many."""
        return await self._aadd_many_impl(
            criteria=criteria,
            prompt_template=prompt_template,
            criterion_set=criterion_set,
            delete_existing=delete_existing,
        )

    @overload
    def add_many(
        self,
        criteria: List[str | CriterionIn],
        prompt_template: PromptTemplate,
        *,
        delete_existing: bool = False,
    ) -> List[Criterion]: ...

    @overload
    def add_many(
        self,
        criteria: List[str | CriterionIn],
        *,
        criterion_set: CriterionSet,
        delete_existing: bool = False,
    ) -> List[Criterion]: ...

    def add_many(
        self,
        criteria: List[str | CriterionIn],
        prompt_template: PromptTemplate | None = None,
        criterion_set: CriterionSet | None = None,
        delete_existing: bool = False,
    ) -> List[Criterion]:
        """Adds custom evaluation criteria to a prompt template or criterion set.

        If criteria with the same strings already exist, they will be reused rather than duplicated.

        There are two ways to use this method:
        1. With a prompt template: add criteria to the default criterion set associated with the template
        2. With a criterion set: add criteria directly to the specified criterion set

        Args:
            criteria (list[str | CriterionIn]): List of criterion strings or CriterionIn objects to add.
            prompt_template (PromptTemplate, optional): The prompt template to add criteria to.
            criterion_set (CriterionSet, optional): A CriterionSet object to add criteria to directly.
            delete_existing (bool): If True, deletes any existing criteria before adding
                new ones. Defaults to False.

        Returns:
            list[Criterion]: List of created and/or existing criterion objects.

        Raises:
            ValueError: If both prompt_template and criterion_set are provided, or if neither is provided.
            httpx.HTTPStatusError: If the provided objects don't belong to the project or other API errors occur.

        """
        return run_async(self._aadd_many_impl)(
            criteria=criteria,
            prompt_template=prompt_template,
            criterion_set=criterion_set,
            delete_existing=delete_existing,
        )

    @retry_request
    async def agenerate_many(
        self,
        prompt_template: PromptTemplate,
        delete_existing: bool = False,
    ) -> List[Criterion]:
        """Async version of generate."""
        request_data = CreateCriteriaRequest(
            prompt_template_id=prompt_template.id,
            delete_existing=delete_existing,
        )
        response = await self._apost("criteria", json=request_data.model_dump())
        return [Criterion.model_validate(criterion) for criterion in response.json()]

    def generate_many(
        self,
        prompt_template: PromptTemplate,
        delete_existing: bool = False,
    ) -> List[Criterion]:
        """Automatically generates evaluation criteria for the prompt template using an LLM.

        This method uses the project's default LLM to analyze the prompt template and generate
        appropriate evaluation criteria. The criteria will be added to a criterion set which is
        associated with the prompt template.

        Note: Unlike add_many, this method only works with prompt templates and not directly with criterion sets,
        as generation requires a prompt template to analyze.

        Args:
            prompt_template (PromptTemplate): The prompt template to generate criteria for.
            delete_existing (bool): If True, deletes any existing criteria before generating
                new ones. If False and criteria exist, raises an error. Defaults to False.

        Returns:
            list[Criterion]: List of generated criterion objects. Each criterion includes
                the generation metadata from the LLM.

        Raises:
            httpx.HTTPStatusError: If criteria already exist and delete_existing is False, if the template variables are not found in the project

        """
        return run_async(self.agenerate_many)(
            prompt_template=prompt_template,
            delete_existing=delete_existing,
        )

    async def aget_or_generate_many(
        self,
        prompt_template: PromptTemplate,
    ) -> Tuple[List[Criterion], bool]:
        """Async version of get_or_generate_criteria."""
        try:
            criteria = await self.agenerate_many(prompt_template=prompt_template, delete_existing=False)
            return criteria, True
        except HTTPStatusError as e:
            if e.response.status_code == 409:
                criteria = await self.alist(prompt_template)
                return criteria, False
            raise  # Re-raise any other HTTP status errors

    def get_or_generate_many(
        self,
        prompt_template: PromptTemplate,
    ) -> Tuple[List[Criterion], bool]:
        """Gets existing criteria or generates new ones if none exist.

        This method generates new criteria if none exist, otherwise it returns the existing criteria.
        The criteria are associated with the prompt template via a criterion set.

        Args:
            prompt_template (PromptTemplate): The prompt template to get or generate criteria for.

        Returns:
            tuple[list[Criterion], bool]: A tuple containing:
                - List of criterion objects, either existing or newly generated
                - Boolean indicating if criteria were generated (True) or existing ones returned (False)

        Raises:
            httpx.HTTPStatusError: If criteria already exist and delete_existing is False, if the template variables are not found in the project

        """
        return run_async(self.aget_or_generate_many)(prompt_template)

    async def aget_by_id(self, id: int) -> Criterion:
        """Async version of get_by_id."""
        response = await self._aget(f"criteria/{id}")

        return Criterion.model_validate(response.json())

    def get_by_id(self, id: int) -> Criterion:
        """Get a criterion by id.

        Args:
            id (int): The id of the criterion.

        Returns:
            (Criterion): The requested criterion.

        """
        return run_async(self.aget_by_id)(id)

    async def adelete(self, criterion: Criterion) -> None:
        """Async version of delete."""
        await self._adelete(f"criteria/{criterion.id}")

    def delete(self, criterion: Criterion) -> None:
        """Delete a criterion.

        Args:
            criterion (Criterion): The criterion to delete.

        """
        return run_async(self.adelete)(criterion)
