import json
import typing as t

import pandas as pd
from pydantic import BaseModel, Field

from . import citation_models

DEFAULT: t.Any = object()
"""
Sentinel value for when a field has not been provided as input.
"""


class HumanReadableNodeOutput(BaseModel):
    """
    Has presentation details of how to represent or expose node-output to the caller.
    For example, if a node generates an table in GCS, the NodeOutputSummary could be
    returning a preview of few rows of the table.
    """

    text: str = Field(default="")
    citations: list[citation_models.Citation] | None = Field(default_factory=lambda: [])
    # the output variables are stored in the table_data field.
    table_data: dict[str, t.Any] | None = Field(default_factory=lambda: None)
    datasource: int | None = Field(
        default=None, description="Reference to a datasource by its ID"
    )
    liveboard: str | None = Field(
        default=None, description="Reference to a liveboard by its ID"
    )
    stream_id: str | None = Field(
        default=None, description="Reference to a stream by its ID"
    )
    clarifying_questions: str | None = Field(
        default=None, description="Questions that need user input before proceeding"
    )
    sql_output: t.Any | None = Field(default=None)
    image_content: t.Any | None = Field(default=None)
    run_id: str | None = Field(default=None, description="Reference to a run by its ID")

    @staticmethod
    def convert_to_table_data(df: pd.DataFrame) -> dict:
        """Convert a DataFrame to our standard table data format.

        Needs to be json serializable as this is stored in the database.

        Args:
            df: pandas DataFrame to convert

        Returns:
            dict: Table data in standard format with columns and data
        """
        # Convert dates to ISO format to make it json serializable.
        records = json.loads(df.to_json(orient="records", date_format="iso"))

        table_data = {
            "columns": [
                {"name": str(col), "type": str(df[col].dtype)} for col in df.columns
            ],
            "data": records,
        }
        return table_data

    @staticmethod
    def represents_table_data(var: t.Any) -> bool:
        """Check if a variable can be converted to a pandas DataFrame.

        Args:
            var: Variable to check

        Returns:
            bool: True if variable can be converted to DataFrame, False otherwise
        """
        # Check that the variable is a list
        if not isinstance(var, list):
            return False

        if len(var) == 0:
            return False

        # Check that each element in the list is a dict
        if not all(isinstance(item, dict) for item in var):
            return False

        # Check that all dictionaries have the same keys
        first_keys = set(var[0].keys())
        if not all(set(item.keys()) == first_keys for item in var):
            return False

        try:
            # Try converting directly to DataFrame
            records = pd.DataFrame.from_records(var)
            return len(records) > 0
        except (ValueError, TypeError):
            pass
        return False


class ToolSummary(BaseModel):
    short_summary: str
    long_summary: HumanReadableNodeOutput = Field(default_factory=HumanReadableNodeOutput)


class ToolOutput(BaseModel):
    tool_summary: ToolSummary
