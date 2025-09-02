# Elluminate SDK

Elluminate SDK is a Software Development Kit that provides a convenient way to interact with the Elluminate platform programmatically. It enables developers to evaluate and optimize prompts, manage experiments, and integrate Elluminate's powerful evaluation capabilities directly into their applications.

## Installation

Install the Elluminate SDK using pip:

```bash
pip install elluminate
```

## 📚 Full Documentation

The full documentation of Elluminate including the SDK can be found at: <https://docs.elluminate.de/>

## Quick Start

### Prerequisites

Before you begin, you'll need to set up your API key:

1. Visit your project's "Keys" dashboard to create a new API key
2. Export your API key and service address as environment variables:

```bash
export ELLUMINATE_API_KEY=<your_api_key>
export ELLUMINATE_BASE_URL=<your_elluminate_service_address>
```

Never commit your API key to version control. For detailed information about API key management and security best practices, see our [API Key Management Guide](https://docs.elluminate.de/get_started/api_keys/).

### Basic Usage

Here's a simple example to evaluate your first prompt:

```python
from elluminate import Client
from elluminate.schemas import RatingMode

# Initialize the client
client = Client()

# Create a prompt template
template, _ = client.prompt_templates.get_or_create(
    "Explain the concept of {{concept}} in simple terms.",
    name="Concept Explanation"
)

# Generate evaluation criteria for the template
client.criteria.get_or_generate_many(template)

# Create a collection for our variables
collection, _ = client.collections.get_or_create(
    name="Concept Variables",
    description="Template variables for concept explanations"
)

# Add template variables to the collection
variables = client.template_variables.add_to_collection(
    template_variables={"concept": "recursion"},
    collection=collection
)

# Create an experiment with response generation and rating
experiment = client.experiments.create(
    "Concept Evaluation Test",
    prompt_template=template,
    collection=collection,
    description="Evaluating concept explanation responses",
    rating_mode=RatingMode.FAST,
    generate=True,
    block=True,
)

# Print results
print(f"Response: {experiment.rated_responses[0].messages[-1].content}")
for rating in experiment.rated_responses[0].ratings:
    print(f"Criterion: {rating.criterion.criterion_str}")
    print(f"Rating: {rating.rating}")
```

### Alternative Client Initialization

You can also initialize the client by directly passing the API key and/or base url:

```python
client = Client(api_key="your-api-key", base_url="your-base-url")
```

## Advanced Features

### Batch Evaluation with Experiments

For evaluating prompts across multiple test cases, you can use experiments with collections:

```python
from elluminate import Client
from elluminate.schemas import RatingMode

client = Client()

# Create a collection of template variables
collection, _ = client.collections.get_or_create(
    name="Math Teaching Test Cases",
    description="Various math concepts and grade levels"
)

# Add test cases to the collection
test_cases = [
    {"math_concept": "fractions", "grade_level": "5th grade"},
    {"math_concept": "algebra", "grade_level": "8th grade"},
    {"math_concept": "geometry", "grade_level": "6th grade"}
]

for test_case in test_cases:
    client.template_variables.add_to_collection(
        template_variables=test_case,
        collection=collection
    )

# Create a prompt template
template, _ = client.prompt_templates.get_or_create(
    "Explain {{math_concept}} to a {{grade_level}} student using simple examples.",
    name="Math Teaching Prompt"
)

# Generate evaluation criteria
client.criteria.get_or_generate_many(template)

# Create an experiment for this evaluation
experiment, _ = client.experiments.get_or_create(
    "Math Teaching Evaluation",
    prompt_template=template,
    collection=collection,
    description="Evaluating math explanations across different concepts and grade levels"
)

# Generate responses for all test cases
responses = client.responses.generate_many(
    prompt_template=template,
    experiment=experiment,
    collection=collection
)

# Rate all responses
for response in responses:
    ratings = client.ratings.rate(response, rating_mode=RatingMode.DETAILED)

    # Print results for each response
    variables = response.prompt.template_variables.input_values
    print(f"\nConcept: {variables['math_concept']}, Grade: {variables['grade_level']}")
    print(f"Response: {response.messages[-1].content[:100]}...")

    for rating in ratings:
        print(f"  • {rating.criterion.criterion_str}: {rating.rating}")
```

## Additional Resources

- [General Documentation](https://docs.elluminate.de/)
- [Key Concepts Guide](https://docs.elluminate.de/get_started/key_concepts/)
- [API Documentation](https://docs.elluminate.de/elluminate/client/)
