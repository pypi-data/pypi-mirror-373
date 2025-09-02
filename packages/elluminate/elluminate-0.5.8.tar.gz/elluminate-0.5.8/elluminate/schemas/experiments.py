from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel

from elluminate.schemas.llm_config import LLMConfig
from elluminate.schemas.prompt_template import PromptTemplate
from elluminate.schemas.rating import RatingMode
from elluminate.schemas.response import PromptResponse
from elluminate.schemas.template_variables_collection import TemplateVariablesCollection


class MeanRating(BaseModel):
    """Schema for mean rating scores."""

    yes: float
    no: float


class ExperimentResults(BaseModel):
    """Schema for experiment results."""

    mean_all_ratings: MeanRating
    mean_rating_by_criterion_id: Dict[int, MeanRating]
    mean_duration_seconds: float
    mean_input_tokens: float
    mean_output_tokens: float
    input_tokens_per_response: List[int]
    output_tokens_per_response: List[int]
    duration_seconds_per_response: List[float]
    num_rated_responses: int
    num_failed_responses: int

    def print_summary(self, criterion_names: Dict[int, str] | None = None) -> None:
        """Print a human-readable summary of the experiment results.

        Args:
            criterion_names: Optional mapping of criterion IDs to their descriptions

        """
        print("\n===== Experiment Results Summary =====")
        print(f"Number of rated responses: {self.num_rated_responses}")
        print(f"Number of failed responses: {self.num_failed_responses}")
        print(f"\nOverall Success Rate: {self.mean_all_ratings.yes:.2%}")

        print("\nResponse Generation Metrics:")
        print(f"  Mean Duration: {self.mean_duration_seconds:.2f} seconds")
        print(f"  Mean Input Tokens: {self.mean_input_tokens:.1f}")
        print(f"  Mean Output Tokens: {self.mean_output_tokens:.1f}")

        if self.mean_rating_by_criterion_id:
            print("\nSuccess Rate by Criterion:")
            for criterion_id, rating in self.mean_rating_by_criterion_id.items():
                criterion_name = (
                    criterion_names.get(criterion_id, f"Criterion {criterion_id}")
                    if criterion_names
                    else f"Criterion {criterion_id}"
                )
                print(f"  {criterion_name}: {rating.yes:.2%}")

        print("=====================================")

    def get_criterion_summary(self, criterion_id: int) -> str:
        """Get a summary for a specific criterion.

        Args:
            criterion_id: The ID of the criterion to summarize

        Returns:
            A formatted string with the criterion's success rate

        """
        rating = self.mean_rating_by_criterion_id.get(criterion_id)
        if not rating:
            return f"No data for Criterion {criterion_id}"

        return f"Success rate: {rating.yes:.2%} (Yes: {rating.yes:.2%}, No: {rating.no:.2%})"


class Experiment(BaseModel):
    """Schema for an experiment."""

    id: int
    name: str
    description: str | None = None
    prompt_template: PromptTemplate
    collection: TemplateVariablesCollection
    llm_config: LLMConfig
    rated_responses: List[PromptResponse] = []
    created_at: datetime
    updated_at: datetime
    generation_task_id: str | None = None
    results: ExperimentResults | None = None

    def print_results_summary(self) -> None:
        """Print a summary of the experiment results if available.

        If results are not available, prints a message indicating why.
        """
        if not self.results:
            if not self.rated_responses:
                print("\nNo results available - experiment has no rated responses.")
            else:
                print(
                    f"\nNo aggregated results available, but experiment has {len(self.rated_responses)} rated responses."
                )
                print("Consider fetching the experiment again to get the latest results.")
            return

        # Build a dictionary of criterion names from the rated responses
        criterion_names = {
            rating.criterion.id: rating.criterion.criterion_str for rating in self.rated_responses[0].ratings
        }

        # Print the summary with criterion names
        print(f"\nResults for experiment '{self.name}':")
        self.results.print_summary(criterion_names)


class ExperimentGenerationStatus(BaseModel):
    """Schema for generation status response."""

    status: str
    error_msg: str | None = None
    completed_responses: int | None = None
    completed_ratings: int | None = None
    total_responses: int | None = None


class CreateExperimentRequest(BaseModel):
    """Request to create a new experiment."""

    name: str
    description: str
    prompt_template_id: int
    collection_id: int
    llm_config_id: int | None = None
    generate: bool = False
    rating_mode: RatingMode = RatingMode.DETAILED
    n_epochs: int = 1


class ExperimentFilter(BaseModel):
    """Filter for experiments."""

    experiment_name: str | None = None
    experiment_name_search: str | None = None
    date_from: datetime | None = None
    date_to: datetime | None = None
    prompt_template_id: int | None = None
    prompt_template_name: str | None = None
    collection_id: int | None = None
    llm_config_id: int | None = None
    created_by_schedule_id: int | None = None
