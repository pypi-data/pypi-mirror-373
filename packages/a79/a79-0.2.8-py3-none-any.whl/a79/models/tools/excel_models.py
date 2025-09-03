import typing as t
from typing import Any, Optional

from pydantic import BaseModel, Field

from . import ToolOutput


class CellValue(BaseModel):
    """Model representing a cell's value"""

    value: Any | None = Field(default=None, description="Cell value")
    formula: Optional[str] = Field(default=None, description="Cell formula")
    data_type: str = Field(default="str", description="Cell value type")


class CellData(BaseModel):
    """Model representing a cell's data"""

    value: CellValue = Field(..., description="Cell value")
    row: int = Field(..., description="Row index (1-based)")
    column: int = Field(..., description="Column index (1-based)")


class CellRange(BaseModel):
    """Model representing a range of cells in a sheet"""

    start_row: int = Field(..., description="Start row index (1-based)")
    start_column: int = Field(..., description="Start column index (1-based)")
    end_row: int = Field(..., description="End row index (1-based)")
    end_column: int = Field(..., description="End column index (1-based)")


class CreateSheetInput(BaseModel):
    datasource_id: int = Field(
        default=0, description="ID of the datasource for the Excel file"
    )
    sheet_name: str = Field(description="Name of the new sheet")
    cells: list[CellData] = Field(
        default_factory=list, description="Cells to populate in the new sheet"
    )


class CreateSheetOutput(ToolOutput):
    sheet_name: str = Field(description="Name of the new sheet")


class EditCellOperation(BaseModel):
    """Configuration for editing a cell."""

    sheet_name: str = Field(description="Name of the sheet")
    row: int = Field(description="Row index (1-based)")
    column: int | str = Field(description="Column index or name")
    value: t.Any = Field(description="New value for the cell")


class EditCellInput(BaseModel):
    datasource_id: int = Field(
        default=0, description="ID of the datasource for the Excel file"
    )
    operations: list[EditCellOperation] = Field(default_factory=list)


class EditCellOutput(ToolOutput):
    pass


class UpdateSheetInput(BaseModel):
    datasource_id: int = Field(
        default=0, description="ID of the datasource for the Excel file"
    )

    sheet_name: str = Field(description="Name of the sheet")
    start_row: int = Field(description="Start row index (1-based)")
    start_column: int = Field(description="Start column index (1-based)")
    values: list[list[CellValue]] = Field(description="2D array of values to set")
    batch_size: int = Field(
        default=2, description="Number of columns to update at once (default: 5)"
    )


class UpdateSheetOutput(ToolOutput):
    pass


class ReadSheetInput(BaseModel):
    datasource_id: int = Field(
        default=0, description="ID of the datasource for the Excel file"
    )

    sheet_name: str = Field(description="Name of the sheet to read")
    cell_range: CellRange | None = Field(None, description="Range of cells to read")
    recalculate_formula: bool = Field(
        default=True, description="Whether to recalculate formulas"
    )
    parse_dates_as_epoch: bool = Field(
        default=False, description="Whether to parse Excel dates as epoch timestamps"
    )


class ReadSheetOutput(ToolOutput):
    sheet_name: str = Field(description="Name of the sheet")
    cells: list[CellData] = Field(description="Cells in the sheet")
    range: CellRange | None = Field(None, description="Range of cells")


class ListSheetInput(BaseModel):
    datasource_id: int = Field(
        default=0, description="ID of the datasource for the Excel file"
    )


class ListSheetOutput(ToolOutput):
    sheet_names: list[str] = Field(description="List of sheet names")
