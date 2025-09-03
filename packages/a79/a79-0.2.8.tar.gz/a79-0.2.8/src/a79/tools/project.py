# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.project_models import CreateProjectInput, CreateProjectOutput

__all__ = ["CreateProjectInput", "CreateProjectOutput", "create_project"]


def create_project(
    *,
    name: str = DEFAULT,
    description: str = DEFAULT,
    datasource_ids: list[int] = DEFAULT,
    worksheet_id: int | None = DEFAULT,
    use_case: str = DEFAULT,
) -> CreateProjectOutput:
    """Create an A79 project from the specified worksheets / datasources."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateProjectInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="project", name="create_project", input=input_model.model_dump()
    )
    return CreateProjectOutput.model_validate(output_model)
