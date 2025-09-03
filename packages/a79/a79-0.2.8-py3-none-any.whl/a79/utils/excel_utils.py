from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_serializer, field_validator


class ToggleSection(str, Enum):
    """Toggle sections in the control panel."""

    ACV_BAND = "ACV Band Toggle"
    EMPLOYEE_COUNT = "Employee Count Toggle"
    INDUSTRY = "Industry Toggle"
    PRODUCT = "Product Toggle"
    GEO = "Geo Toggle"


class ToggleOption(BaseModel):
    """Represents a single toggle option."""

    index: int
    value: str
    cell_row: int
    cell_col: int


class ToggleInfo(BaseModel):
    """Represents a toggle configuration in the control panel."""

    section: ToggleSection
    selection_cell: str  # The cell containing "All" or selected value (e.g., "B5")
    selection_cell_row: int
    selection_cell_col: int
    options: list[ToggleOption]
    selected_option_index: Optional[int] = Field(default=1)  # 1-based index

    # Serializer: Convert enum to string
    @field_serializer("section")
    def serialize_section(self, section: ToggleSection) -> str:
        return section.value

    # Validator: Convert string back to enum during deserialization
    @classmethod
    @field_validator("section", mode="before")
    def validate_section(cls, value):
        if isinstance(value, str):
            try:
                # Try to convert string to enum
                return ToggleSection(value)
            except ValueError as e:
                # If the string doesn't match any enum value
                raise ValueError(f"Invalid section value: {value}") from e
        return value


class ToggleSelection(BaseModel):
    """Represents a toggle selection in the control panel."""

    section: str
    selected_value: str


class ToggleConfiguration(BaseModel):
    """Configuration for a single toggle including all options and selection."""

    section: str
    selected_value: str
    available_options: list[str]


class ChartType(str, Enum):
    """Types of charts that can be created."""

    LINE = "line"
    MULTI_COLUMN = "multi-column"
    BAR = "bar"
    AREA = "area"
    STACKED = "stacked"
    STACKED_BAR = "stacked-bar"


class ChartConfig(BaseModel):
    """Configuration for a single chart."""

    cell_range: str
    data_preview: list[Any] = Field(default_factory=list)
    x_axis: list[str]
    y_axis: list[str]
    sheet_name: str
    chart_name: str
    chart_type: str


class ChartConfigData(BaseModel):
    """Complete configuration for a single chart including toggle overrides."""

    chart_toggle_overrides: list[ToggleSelection]
    user_instruction: str = ""
    chart_config: ChartConfig


class RetentionChartingInputData(BaseModel):
    """Complete retention data structure."""

    available_sheets: list[str]
    toggle_choices: list[ToggleInfo]
    global_toggle_values: list[ToggleSelection]
    chart_config_data: list[ChartConfigData]


def parse_control_panel_sheet(sheet_data: dict) -> list[ToggleInfo]:
    """
    Parse the control panel sheet data to extract toggle configurations.

    Args:
        sheet_data: Dictionary containing sheet data with cells array

    Returns:
        List of ToggleInfo objects representing each toggle section
    """
    toggles = []
    current_section: Optional[ToggleSection] = None
    current_options: list[ToggleOption] = []
    current_cell: Optional[str] = None

    # Create a dictionary for faster cell lookup by row/column
    cell_map = {}
    for cell in sheet_data["cells"]:
        if cell["value"] is None:
            continue
        cell_map[(cell["row"], cell["column"])] = cell["value"]["value"]

    # Get the maximum row to iterate through
    max_row = max(cell["row"] for cell in sheet_data["cells"])

    # Iterate through rows
    for row_idx in range(1, max_row + 1):
        # Get the first cell value in this row (if it exists)
        first_cell_value = cell_map.get((row_idx, 1))
        if first_cell_value is None:
            continue

        first_cell = str(first_cell_value).strip()

        # Check for section headers
        if any(section in first_cell for section in ToggleSection.__members__.values()):
            # If we were processing a previous section, add it to toggles

            if current_section and current_options and current_cell:
                # current_options has values like:
                # [
                #   '{"index":1,"value":"All","cell_row":14,"cell_col":3}',  -> selected option  # noqa: E501
                #   '{"index":1,"value":"All","cell_row":16,"cell_col":3}',
                #   '{"index":2,"value":"Greater than $200,000","cell_row":17,"cell_col":3}',  # noqa: E501
                #   '{"index":3,"value":"Greater than $100,000 up to $200,000","cell_row":18,"cell_col":3}',  # noqa: E501
                #   '{"index":4,"value":"Greater than $0 up to $100,000","cell_row":19,"cell_col":3}'  # noqa: E501
                #  ]
                # so we use the first option as the current chosen value for the toggle.
                # Rest are used as options to expose.

                toggles.append(
                    ToggleInfo(
                        section=current_section,
                        selection_cell=current_cell,
                        options=current_options[1:],
                        selection_cell_row=current_options[0].cell_row,
                        selection_cell_col=current_options[0].cell_col,
                    )
                )

            # Start new section
            current_section = ToggleSection(first_cell)
            current_options = []
            # Selection cell is typically in column C of the next row
            current_cell = f"C{row_idx + 4}"
            continue

        # Process option rows (they start with a number)
        if first_cell and first_cell.isdigit():
            option_index = int(first_cell)
            # Get the option value from column D (index 4)
            option_value = cell_map.get((row_idx, 2))
            option_value = str(option_value).strip()
            if option_value and option_value != "[ ]":
                current_options.append(
                    ToggleOption(
                        index=option_index,
                        value=option_value,
                        cell_row=row_idx + 2,
                        cell_col=3,
                    )
                )

    # Add the last section if exists
    if current_section and current_options and current_cell:  # Add check for current_cell
        toggles.append(
            ToggleInfo(
                section=current_section,
                selection_cell=current_cell,
                selection_cell_row=current_options[0].cell_row,
                selection_cell_col=current_options[0].cell_col,
                options=current_options[1:],
                selected_option_index=current_options[0].index,
            )
        )

    return toggles


def get_toggle_configurations(
    toggle_info: list[ToggleInfo], toggle_values: dict[str, str]
) -> dict[str, ToggleConfiguration]:
    """
    Create toggle configurations with selected values and available options.

    Args:
        toggle_info: List of toggle configurations
        toggle_values: Dictionary of toggle values from user input

    Returns:
        Dictionary mapping section names to their configurations
    """
    configurations = {}

    for toggle in toggle_info:
        section_name = toggle.section.replace(" Toggle", "").lower()
        selected_value = toggle_values.get(
            section_name, toggle.options[0].value if toggle.options else ""
        )

        configurations[section_name] = ToggleConfiguration(
            section=toggle.section,
            selected_value=selected_value,
            available_options=[opt.value for opt in toggle.options],
        )

    return configurations


def get_toggle_edit_operations(
    toggle_info: list[ToggleInfo], toggle_values: dict[str, str]
) -> list[dict[str, Any]]:
    """
    Generate Excel edit operations for each toggle based on selected values.

    Args:
        toggle_info: List of toggle configurations
        toggle_values: Dictionary of toggle values from user input

    Returns:
        List of edit operations with cell locations and values
    """
    edit_operations = []

    for toggle in toggle_info:
        # Get the selected value for this toggle
        section_name = toggle.section.replace(" Toggle", "").lower()
        selected_value = toggle_values.get(section_name)

        # Find the index of the selected value
        selected_index = 1  # Default to first option
        if selected_value:
            for option in toggle.options:
                if option.value.lower() == selected_value.lower():
                    selected_index = option.index
                    break

        # Create edit operation
        edit_operations.append(
            {
                "sheet_name": "Control Panel",
                "cell": toggle.selection_cell,
                "row": toggle.selection_cell_row,
                "column": toggle.selection_cell_col,
                "value": selected_index,
            }
        )

    return edit_operations
