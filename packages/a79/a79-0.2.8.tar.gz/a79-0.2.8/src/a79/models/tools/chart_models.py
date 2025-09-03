from enum import Enum
from typing import Optional, Union

from pydantic import BaseModel, Field


class ChartType(str, Enum):
    """Supported chart types"""

    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    SCATTER = "scatter"
    HISTOGRAM = "histogram"
    HEATMAP = "heatmap"


class GenerateChartInput(BaseModel):
    """Input for chart generation"""

    data: list[dict] = Field(description="Data from ExecuteSQLOutput.data")
    chart_type: ChartType = Field(description="Type of chart to generate")
    x_column: Optional[str] = Field(None, description="Column name for X axis")
    y_column: Optional[Union[str, list[str]]] = Field(
        None, description="Column name(s) for Y axis"
    )
    title: Optional[str] = Field(None, description="Chart title")
    xlabel: Optional[str] = Field(None, description="X axis label")
    ylabel: Optional[str] = Field(None, description="Y axis label")
    figsize: tuple[float, float] = Field(
        (10, 6), description="Figure size as (width, height)"
    )
    color_column: Optional[str] = Field(
        None, description="Column to use for color coding (scatter plots)"
    )
    value_column: Optional[str] = Field(
        None, description="Column for values (pie charts)"
    )
    label_column: Optional[str] = Field(
        None, description="Column for labels (pie charts)"
    )


class GenerateChartOutput(BaseModel):
    """Output containing the generated chart"""

    chart_base64: str = Field(description="Base64 encoded PNG image")
    chart_type: str = Field(description="Type of chart generated")
    mime_type: str = Field(default="image/png", description="MIME type of the image")
