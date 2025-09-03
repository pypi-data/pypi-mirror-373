# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.podcast_models import (
    CreatePodcastInput,
    CreatePodcastOutput,
    PodcastSection,
)

__all__ = [
    "CreatePodcastInput",
    "CreatePodcastOutput",
    "PodcastSection",
    "create_podcast",
]


def create_podcast(
    *,
    model: str = DEFAULT,
    user_1_profile: str = DEFAULT,
    user_2_profile: str = DEFAULT,
    content: str = DEFAULT,
) -> CreatePodcastOutput:
    """Execute the podcast creation with the provided input data."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreatePodcastInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="podcast", name="create_podcast", input=input_model.model_dump()
    )
    return CreatePodcastOutput.model_validate(output_model)
