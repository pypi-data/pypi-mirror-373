# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.chart_models import (
    ChartType,
    Enum,
    GenerateChartInput,
    GenerateChartOutput,
)

__all__ = ["ChartType", "Enum", "GenerateChartInput", "GenerateChartOutput", "generate"]


def generate(
    *,
    data: list[dict],
    chart_type: ChartType,
    x_column: str | None = DEFAULT,
    y_column: str | list[str] | None = DEFAULT,
    title: str | None = DEFAULT,
    xlabel: str | None = DEFAULT,
    ylabel: str | None = DEFAULT,
    figsize: tuple[float, float] = DEFAULT,
    color_column: str | None = DEFAULT,
    value_column: str | None = DEFAULT,
    label_column: str | None = DEFAULT,
) -> GenerateChartOutput:
    """
    Generate charts from SQL query results using matplotlib.

    This tool creates various types of charts (bar, line, pie, scatter, histogram)
    from data typically returned by execute_sql. The chart is returned as a
    base64-encoded PNG image that can be displayed in web interfaces or saved to disk.

    """
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = GenerateChartInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="chart", name="generate", input=input_model.model_dump()
    )
    return GenerateChartOutput.model_validate(output_model)
