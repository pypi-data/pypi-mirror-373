# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.roleplay_coaching_analyzer_models import (
    CritiqueItem,
    RoleplayCoachingAnalyzerInput,
    RoleplayCoachingAnalyzerOutput,
    RoleplaySessionCritique,
)

__all__ = [
    "CritiqueItem",
    "RoleplayCoachingAnalyzerInput",
    "RoleplayCoachingAnalyzerOutput",
    "RoleplaySessionCritique",
    "analyze_roleplay_coaching",
]


def analyze_roleplay_coaching(
    *,
    transcript: str = DEFAULT,
    task_name: str = DEFAULT,
    task_instructions: str = DEFAULT,
) -> RoleplayCoachingAnalyzerOutput:
    """
    Analyze a roleplay session transcript to provide comprehensive coaching feedback.

    This tool specializes in sales roleplay analysis, providing detailed feedback
    for both human participants and AI agents, with suggestions for improvement.
    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = RoleplayCoachingAnalyzerInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="roleplay_coaching_analyzer",
        name="analyze_roleplay_coaching",
        input=input_model.model_dump(),
    )
    return RoleplayCoachingAnalyzerOutput.model_validate(output_model)
