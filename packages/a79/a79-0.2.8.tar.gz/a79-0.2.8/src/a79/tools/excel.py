# This is a generated file by scripts/codegen/tools.py, do not edit manually
# ruff: noqa


from ..client import A79Client
from ..models.tools import DEFAULT
from ..models.tools.excel_models import (
    CellData,
    CellRange,
    CellValue,
    CreateSheetInput,
    CreateSheetOutput,
    EditCellInput,
    EditCellOperation,
    EditCellOutput,
    ListSheetInput,
    ListSheetOutput,
    ReadSheetInput,
    ReadSheetOutput,
    UpdateSheetInput,
    UpdateSheetOutput,
)

__all__ = [
    "CellData",
    "CellRange",
    "CellValue",
    "CreateSheetInput",
    "CreateSheetOutput",
    "EditCellInput",
    "EditCellOperation",
    "EditCellOutput",
    "ListSheetInput",
    "ListSheetOutput",
    "ReadSheetInput",
    "ReadSheetOutput",
    "UpdateSheetInput",
    "UpdateSheetOutput",
    "create_sheet",
    "edit_cell",
    "update_sheet",
    "read_sheet",
    "list_sheets",
]


def create_sheet(
    *, datasource_id: int = DEFAULT, sheet_name: str, cells: list[CellData] = DEFAULT
) -> CreateSheetOutput:
    """Creates a new sheet in the Excel file with specified content."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = CreateSheetInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="excel", name="create_sheet", input=input_model.model_dump()
    )
    return CreateSheetOutput.model_validate(output_model)


def edit_cell(
    *, datasource_id: int = DEFAULT, operations: list[EditCellOperation] = DEFAULT
) -> EditCellOutput:
    """Edits a specific cell in a sheet of the Excel file."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = EditCellInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="excel", name="edit_cell", input=input_model.model_dump()
    )
    return EditCellOutput.model_validate(output_model)


def update_sheet(
    *,
    datasource_id: int = DEFAULT,
    sheet_name: str,
    start_row: int,
    start_column: int,
    values: list[list[CellValue]],
    batch_size: int = DEFAULT,
) -> UpdateSheetOutput:
    """ "Updates a range of cells in a sheet of the Excel file."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = UpdateSheetInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="excel", name="update_sheet", input=input_model.model_dump()
    )
    return UpdateSheetOutput.model_validate(output_model)


def read_sheet(
    *,
    datasource_id: int = DEFAULT,
    sheet_name: str,
    cell_range: CellRange | None = DEFAULT,
    recalculate_formula: bool = DEFAULT,
    parse_dates_as_epoch: bool = DEFAULT,
) -> ReadSheetOutput:
    """Reads data from a specific sheet in the Excel file."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ReadSheetInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="excel", name="read_sheet", input=input_model.model_dump()
    )
    return ReadSheetOutput.model_validate(output_model)


def list_sheets(*, datasource_id: int = DEFAULT) -> ListSheetOutput:
    """Handler for reading data from a specific sheet."""
    kwargs = locals()
    kwargs = {k: v for k, v in kwargs.items() if v is not DEFAULT}
    input_model = ListSheetInput.model_validate(kwargs)

    client = A79Client()
    output_model = client.execute_tool(
        package="excel", name="list_sheets", input=input_model.model_dump()
    )
    return ListSheetOutput.model_validate(output_model)
