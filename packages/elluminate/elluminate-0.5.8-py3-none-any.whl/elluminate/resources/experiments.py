from httpx import HTTPStatusError
from loguru import logger
from pydantic import BaseModel
from tqdm import tqdm

from elluminate.resources.base import BaseResource
from elluminate.schemas import (
    CreateExperimentRequest,
    Experiment,
    ExperimentFilter,
    ExperimentGenerationStatus,
    LLMConfig,
    PromptTemplate,
    RatingMode,
    TemplateVariablesCollection,
)
from elluminate.utils import deprecated, run_async


class ExperimentsResource(BaseResource):
    async def aget(self, name: str) -> Experiment:
        """Async version of get."""
        response = await self._aget("experiments", params={"experiment_name": name})
        experiments = [Experiment.model_validate(e) for e in response.json()["items"]]

        if not experiments:
            raise ValueError(f"No experiment found with name '{name}'")

        # Since experiment names are unique per project, there should be only one if `experiments` is nonempty.
        experiment = experiments[0]

        responses = await self._client.responses.alist(experiment=experiment)
        experiment.rated_responses = responses
        return experiment

    def get(self, name: str) -> Experiment:
        """Get the experiment with the given name.

        Args:
            name (str): The name of the experiment to get.

        Returns:
            Experiment: The experiment object.

        Raises:
            ValueError: If no experiment is found with the given name.

        """
        return run_async(self.aget)(name)

    async def aget_by_id(self, id: int) -> Experiment:
        """Async version of get_by_id."""
        response = await self._aget(f"experiments/{id}")

        return Experiment.model_validate(response.json())

    def get_by_id(self, id: int) -> Experiment:
        """Get an experiment by id.

        Args:
            id (int): The id of the experiment.

        Returns:
            (Experiment): The requested experiment.

        """
        return run_async(self.aget_by_id)(id)

    async def alist(
        self,
        prompt_template: PromptTemplate | None = None,
        collection: TemplateVariablesCollection | None = None,
        llm_config: LLMConfig | None = None,
    ) -> list[Experiment]:
        """Async version of list."""
        return await self._paginate(
            "experiments",
            model=Experiment,
            params=ExperimentFilter(
                prompt_template_id=prompt_template.id if prompt_template else None,
                collection_id=collection.id if collection else None,
                llm_config_id=llm_config.id if llm_config else None,
            ).model_dump(exclude_none=True),
        )

    def list(
        self,
        prompt_template: PromptTemplate | None = None,
        collection: TemplateVariablesCollection | None = None,
        llm_config: LLMConfig | None = None,
    ) -> list[Experiment]:
        """Get a list of experiments sorted by creation date.

        Args:
            prompt_template (PromptTemplate | None): The prompt template to filter by.
            collection (TemplateVariablesCollection | None): The collection to filter by.
            llm_config (LLMConfig | None): The LLM config to filter by.

        Returns:
            list[Experiment]: A list of experiments.

        """
        return run_async(self.alist)(prompt_template, collection, llm_config)

    async def acreate(
        self,
        name: str,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
        generate: bool = False,
        rating_mode: RatingMode = RatingMode.DETAILED,
        n_epochs: int = 1,
        block: bool = False,
        timeout: float | None = None,
    ) -> Experiment:
        """Async version of create."""
        if not generate and block:
            logger.warning(
                "The block=True parameter has no effect when generate=False. The experiment will be created but no response/rating generation will occur. Set generate=True to enable blocking behavior."
            )

        response = await self._apost(
            "experiments",
            json=CreateExperimentRequest(
                name=name,
                description=description,
                prompt_template_id=prompt_template.id,
                collection_id=collection.id,
                llm_config_id=llm_config.id if llm_config else None,
                generate=generate,
                rating_mode=rating_mode,
                n_epochs=n_epochs,
            ).model_dump(),
        )

        experiment = Experiment.model_validate(response.json())

        if not (generate and block):
            return experiment

        # Stream generation status using SSE
        responses_bar = None
        ratings_bar = None

        try:
            async for status_data in self._aget_stream(
                f"experiments/{experiment.id}/generation/{experiment.generation_task_id}/stream",
                ExperimentGenerationStatus,
                timeout=timeout,
            ):
                if status_data.status == "FAILURE":
                    raise RuntimeError(f"Generation failed: {status_data.error_msg}")

                if status_data.status == "SUCCESS":
                    # Complete the ratings progress bar on success
                    if ratings_bar:
                        ratings_bar.update(ratings_bar.total - ratings_bar.n)
                    # Fetch the full experiment since SSE no longer includes result
                    full_experiment = await self.aget_by_id(experiment.id)
                    responses = await self._client.responses.alist(experiment=experiment)
                    full_experiment.rated_responses = responses
                    return full_experiment

                if not status_data.total_responses:
                    continue

                # Ensure we have both responses and ratings data
                if status_data.completed_responses is not None and status_data.completed_ratings is not None:
                    if not responses_bar:
                        responses_bar = tqdm(
                            total=status_data.total_responses,
                            desc=f"Generating responses ({name})",
                            unit="response",
                        )
                    if not ratings_bar:
                        ratings_bar = tqdm(
                            total=status_data.total_responses, desc=f"Rating responses ({name})", unit="rating"
                        )

                    # Update progress bars
                    responses_bar.update(status_data.completed_responses - responses_bar.n)
                    ratings_bar.update(status_data.completed_ratings - ratings_bar.n)
            else:
                # If we reach here, the stream ended without SUCCESS or FAILURE
                raise RuntimeError("Generation stream ended unexpectedly without completion status")
        finally:
            # Always close progress bars in finally block
            if responses_bar:
                responses_bar.close()
            if ratings_bar:
                ratings_bar.close()

    def create(
        self,
        name: str,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
        generate: bool = False,
        rating_mode: RatingMode = RatingMode.DETAILED,
        n_epochs: int = 1,
        block: bool = False,
        timeout: float | None = None,
    ) -> Experiment:
        """Creates a new experiment.

        Args:
            name (str): The name of the experiment.
            prompt_template (PromptTemplate): The prompt template to use for the experiment.
            collection (TemplateVariablesCollection): The collection of template variables to use for the experiment.
            llm_config (LLMConfig | None): Optional LLMConfig to use for the experiment. Uses platform default if not specified.
            description (str): Optional description for the experiment.
            generate (bool): Whether to generate responses and ratings immediately. Defaults to False.
            rating_mode (RatingMode): The rating mode to use if generating responses (Only used if generate=True). Defaults to RatingMode.DETAILED.
            n_epochs (int): Number of times to run the experiment for each input. Defaults to 1.
            block (bool): Whether to block until the experiment is executed, only relevant if generate=True. Defaults to False.
            timeout (float | None): The timeout for the experiment execution, only relevant if generate=True and block=True. Defaults to None.

        Returns:
            Experiment: The newly created experiment object. If generate=True,
            responses and ratings will be generated. The returned experiment object will
            then include a generation task ID that can be used to check the status of the
            generation.

        Raises:
            httpx.HTTPStatusError: If the experiment with the same name already exists

        """
        return run_async(self.acreate)(
            name=name,
            prompt_template=prompt_template,
            collection=collection,
            llm_config=llm_config,
            description=description,
            generate=generate,
            rating_mode=rating_mode,
            n_epochs=n_epochs,
            block=block,
            timeout=timeout,
        )

    async def aget_or_create(
        self,
        name: str,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
        generate: bool = False,
        rating_mode: RatingMode = RatingMode.DETAILED,
        n_epochs: int = 1,
        block: bool = False,
        timeout: float | None = None,
    ) -> tuple[Experiment, bool]:
        """Async version of get_or_create."""
        # Create a dict of the requested parameters (excluding None values)
        requested_dict = {
            k: v
            for k, v in {
                "name": name,
                "prompt_template": prompt_template,
                "collection": collection,
                "llm_config": llm_config,
                "description": description,
                "generate": generate,
                "rating_mode": rating_mode,
                "n_epochs": n_epochs,
            }.items()
            if v is not None
        }

        try:
            experiment = await self.acreate(
                name=name,
                prompt_template=prompt_template,
                collection=collection,
                llm_config=llm_config,
                description=description,
                generate=generate,
                rating_mode=rating_mode,
                n_epochs=n_epochs,
                block=block,
                timeout=timeout,
            )
            return experiment, True
        except HTTPStatusError as e:
            if e.response.status_code == 409:
                # Try to get existing experiment
                existing_config = await self.aget(name=name)
                existing_dict = existing_config.model_dump()

                differences = []
                for k, v in requested_dict.items():
                    if isinstance(v, BaseModel):
                        v = v.model_dump()

                    if k not in {"name"} and k in existing_dict and v != existing_dict[k]:
                        differences.append(k)

                if differences:
                    logger.warning(
                        f"Experiment with name '{name}' already exists with different values for: {', '.join(differences)}. Returning existing experiment."
                    )

                return existing_config, False

            raise  # Re-raise any other HTTP status errors

    def get_or_create(
        self,
        name: str,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
        generate: bool = False,
        rating_mode: RatingMode = RatingMode.DETAILED,
        n_epochs: int = 1,
        block: bool = False,
        timeout: float | None = None,
    ) -> tuple[Experiment, bool]:
        """Gets an existing experiment by name or creates a new one if it doesn't exist.

        The existence of an experiment is determined solely by its name. If an experiment with the given name exists,
        it will be returned regardless of its other properties. If no experiment exists with that name, a new one
        will be created with the provided parameters.

        Args:
            name (str): The name of the experiment to get or create.
            prompt_template (PromptTemplate): The prompt template to use if creating a new experiment.
            collection (TemplateVariablesCollection): The collection of template variables to use if creating a new experiment.
            llm_config (LLMConfig | None): Optional LLMConfig to use if creating a new experiment.
            description (str): Optional description if creating a new experiment.
            generate (bool): Whether to generate responses and ratings immediately. Defaults to False.
            rating_mode (RatingMode): The rating mode to use if generating responses. Defaults to RatingMode.DETAILED.
            n_epochs (int): Number of times to run the experiment for each input. Defaults to 1.
            block (bool): Whether to block until the experiment is executed when creating a new experiment, only relevant if generate=True. Defaults to False.
            timeout (float | None): The timeout for the experiment execution when creating a new experiment, only relevant if generate=True and block=True. Defaults to None.

        Returns:
            tuple[Experiment | ExperimentGenerationStatus, bool]: A tuple containing:
                - The experiment object (either existing or newly created)
                - Boolean indicating if a new experiment was created (True) or existing one returned (False)

        """
        return run_async(self.aget_or_create)(
            name=name,
            prompt_template=prompt_template,
            collection=collection,
            llm_config=llm_config,
            description=description,
            generate=generate,
            rating_mode=rating_mode,
            n_epochs=n_epochs,
            block=block,
            timeout=timeout,
        )

    @deprecated(since="0.3.12", removal_version="0.4.0", alternative="acreate(..., generate=True, block=True, ...)")
    async def acreate_and_run(
        self,
        name: str,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
        rating_mode: RatingMode = RatingMode.DETAILED,
        timeout: float | None = None,
        n_epochs: int = 1,
    ) -> Experiment:
        """Asynchronous version of create_and_run_experiment."""
        # Create experiment with generate flag
        return await self.acreate(
            name,
            prompt_template=prompt_template,
            collection=collection,
            llm_config=llm_config,
            description=description,
            generate=True,
            rating_mode=rating_mode,
            n_epochs=n_epochs,
            block=True,
            timeout=timeout,
        )

    @deprecated(since="0.3.12", removal_version="0.4.0", alternative="create(..., generate=True, block=True, ...)")
    def create_and_run(
        self,
        name: str,
        prompt_template: PromptTemplate,
        collection: TemplateVariablesCollection,
        llm_config: LLMConfig | None = None,
        description: str = "",
        rating_mode: RatingMode = RatingMode.DETAILED,
        timeout: float | None = None,
        n_epochs: int = 1,
    ) -> Experiment:
        """Creates a new experiment and runs it (generates responses and ratings) in one go.

        Args:
            name (str): The name of the experiment.
            prompt_template (PromptTemplate): The prompt template to use for the experiment.
            collection (TemplateVariablesCollection): The collection of template variables to use for the experiment.
            llm_config (LLMConfig | None): Optional LLMConfig to use for the experiment.
            description (str): Optional description for the experiment.
            rating_mode (RatingMode): The rating mode to use for evaluating responses. Defaults to DETAILED.
            timeout (float | None): Optional timeout in seconds. Defaults to None (no timeout).
            n_epochs (int): Number of times to run the experiment for each input. Defaults to 1.

        Returns:
            ExperimentOut: The experiment with generated responses and ratings.

        Raises:
            RuntimeError: If generation fails or returns no result.
            TimeoutError: If the operation times out.

        """
        return run_async(self.acreate_and_run)(
            name=name,
            prompt_template=prompt_template,
            collection=collection,
            llm_config=llm_config,
            description=description,
            rating_mode=rating_mode,
            timeout=timeout,
            n_epochs=n_epochs,
        )

    async def adelete(self, experiment: Experiment) -> None:
        """Async version of delete."""
        await self._adelete(f"experiments/{experiment.id}")

    def delete(self, experiment: Experiment) -> None:
        """Deletes an experiment.

        Args:
            experiment (Experiment): The experiment to delete.

        Raises:
            httpx.HTTPStatusError: If the experiment doesn't exist or belongs to a different project.

        """
        return run_async(self.adelete)(experiment)
