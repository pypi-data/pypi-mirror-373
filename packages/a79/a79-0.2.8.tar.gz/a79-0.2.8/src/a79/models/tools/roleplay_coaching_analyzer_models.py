from pydantic import BaseModel, Field

from . import ToolOutput


class CritiqueItem(BaseModel):
    """A specific critique for either human or agent performance."""

    participant: str = Field(
        description="Whether critique is for 'human' or 'agent'", default="human"
    )
    category: str = Field(
        description="Category of feedback (e.g., 'communication', 'objection_handling', 'product_knowledge')",  # noqa: E501
        default="",
    )
    critique: str = Field(
        description="Specific feedback with examples from transcript", default=""
    )
    suggestion: str = Field(description="Actionable improvement suggestion", default="")


class RoleplaySessionCritique(BaseModel):
    """Simplified analysis of a roleplay session for coaching purposes."""

    session_summary: str = Field(
        description="Brief overview of what happened in the roleplay session", default=""
    )
    detailed_critiques: list[CritiqueItem] = Field(
        description="List of specific critiques and suggestions", default=[]
    )
    next_practice_recommendations: list[str] = Field(
        description="Combined list including task prompt updates and coaching suggestions",  # noqa: E501
        default=[],
    )


class RoleplayCoachingAnalyzerInput(BaseModel):
    """Input model for the roleplay coaching analyzer tool."""

    transcript: str = Field(
        json_schema_extra={"mandatory": True},
        description="The roleplay session transcript to analyze",
        default="",
    )
    task_name: str = Field(
        json_schema_extra={"mandatory": True},
        description="Name of the roleplay task",
        default="",
    )
    task_instructions: str = Field(
        json_schema_extra={"mandatory": True},
        description="Instructions for the roleplay task",
        default="",
    )


class RoleplayCoachingAnalyzerOutput(ToolOutput):
    """Output model for the roleplay coaching analyzer tool."""

    critique: RoleplaySessionCritique = Field(
        json_schema_extra={"mandatory": True},
        description="Comprehensive coaching analysis of the roleplay session",
        default_factory=RoleplaySessionCritique,
    )
