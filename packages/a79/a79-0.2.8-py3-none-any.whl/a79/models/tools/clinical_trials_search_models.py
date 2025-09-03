from typing import Optional

from pydantic import BaseModel, Field

from . import ToolOutput


class ClinicalTrialsSearchInput(BaseModel):
    """
    Defines the input parameters for a clinical trials search query.
    """

    condition: str = Field(
        ...,
        description="The medical condition to search for (e.g. Alzheimer's).",
        examples=["Alzheimer's disease"],
    )
    location: Optional[str] = Field(
        None,
        description="Location filter for clinical trials (optional).",
        examples=["United States"],
    )
    status: Optional[str] = Field(
        None, description="Recruitment status filter (optional).", examples=["RECRUITING"]
    )
    page_size: Optional[int] = Field(
        10, description="Number of results to return per page.", examples=[5]
    )

    class Config:
        schema_extra = {
            "example": {
                "condition": "Alzheimer's disease",
                "location": "United States",
                "status": "RECRUITING",
                "page_size": 5,
            }
        }


class ClinicalTrialResult(BaseModel):
    """
    Represents a single clinical trial result.
    """

    id: str
    title: str
    status: str
    location: Optional[str] = None
    summary: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sponsor: Optional[str] = None


class ClinicalTrialsSearchResponse(BaseModel):
    """
    Represents the search response containing a list of clinical trials.
    """

    total_count: int
    trials: list[ClinicalTrialResult]


class ClinicalTrialsSearchOutput(ToolOutput):
    """
    Defines the output structure for a clinical trials search operation.
    """

    trials: list[ClinicalTrialResult]
    total_count: int
    page_number: Optional[int] = None
    page_size: Optional[int] = None


class ClinicalTrialRecord(BaseModel):
    """
    Represents a detailed clinical trial record.
    """

    id: str
    title: str
    status: str
    location: Optional[str] = None
    summary: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    sponsor: Optional[str] = None
    condition: Optional[str] = None
    phase: Optional[str] = None
    study_type: Optional[str] = None
    eligibility_criteria: Optional[str] = None
