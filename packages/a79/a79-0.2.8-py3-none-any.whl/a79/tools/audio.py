# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.audio_models import CreateAudioInput, CreateAudioOutput

__all__ = ["CreateAudioInput", "CreateAudioOutput", "create_audio"]


def create_audio(
    *,
    conversation: list[tuple[str, str]] = DEFAULT,
    pause_duration: float = DEFAULT,
    voice: dict[str, str] = DEFAULT,
) -> CreateAudioOutput:
    """
    Takes a list of conversation turns with specified voices and generates an audio file
    with appropriate pauses between turns.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateAudioInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="audio", name="create_audio", input=input_model.model_dump()
    )
    return CreateAudioOutput.model_validate(output_model)
