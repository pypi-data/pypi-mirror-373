import pandas as pd
import pytest

from ..data_transformation_utils import (
    convert_celldata_to_dataframe_filtered,
    get_thoughtspot_data_type,
    parse_cell_range,
    transform_wide_to_long,
)


class TestGetThoughtspotDataType:
    def test_int_type(self):
        assert get_thoughtspot_data_type("int") == "INT64"

    def test_float_type(self):
        assert get_thoughtspot_data_type("float") == "FLOAT"

    def test_date_types(self):
        assert get_thoughtspot_data_type("date") == "DATE"
        assert get_thoughtspot_data_type("datetime") == "DATE"
        assert get_thoughtspot_data_type("datetime64[ns]") == "DATE"

    def test_other_types(self):
        assert get_thoughtspot_data_type("string") == "VARCHAR"
        assert get_thoughtspot_data_type("object") == "VARCHAR"
        assert get_thoughtspot_data_type("bool") == "VARCHAR"


class TestConvertCelldataToDataframeFiltered:
    def test_filter_empty_rows_and_columns(self):
        cells = [
            {"row": 1, "column": 1, "value": {"value": "Header", "data_type": "string"}},
            {"row": 1, "column": 2, "value": {"value": "Value", "data_type": "string"}},
            # Row 2 is completely empty
            {"row": 3, "column": 1, "value": {"value": "Data", "data_type": "string"}},
            # Column 3 is completely empty
        ]

        df = convert_celldata_to_dataframe_filtered(cells)

        # After filtering, we should have 2 rows (not 3) and 2 columns
        assert df.shape == (2, 2)

        # Check values
        assert df.iloc[0, 0] == "Header"
        assert df.iloc[0, 1] == "Value"
        assert df.iloc[1, 0] == "Data"


class TestTransformWideToLong:
    def test_wide_to_long_transformation(self):
        # Create a sample wide dataframe
        data = {
            "col_1": ["ARR by day", "Metric A", "Metric B"],
            "col_2": [pd.Timestamp("2023-01-01"), 10, 100],
            "col_3": [pd.Timestamp("2023-01-02"), 20, 200],
            "col_4": [pd.Timestamp("2023-01-03"), 30, 300],
        }
        wide_df = pd.DataFrame(data)

        # Transform to long format
        long_df = transform_wide_to_long(wide_df)

        # Check output structure
        assert set(long_df.columns) == {"date", "Metric A", "Metric B"}
        assert len(long_df) == 3  # 3 dates

        # Check values
        assert long_df.iloc[0]["date"] == pd.Timestamp("2023-01-01")
        assert long_df.iloc[0]["Metric A"] == 10
        assert long_df.iloc[0]["Metric B"] == 100

        assert long_df.iloc[1]["date"] == pd.Timestamp("2023-01-02")
        assert long_df.iloc[1]["Metric A"] == 20
        assert long_df.iloc[1]["Metric B"] == 200


class TestParseCellRange:
    def test_simple_cell_range(self):
        start_col, start_row, end_col, end_row = parse_cell_range("A1:C4")
        assert start_col == 1
        assert start_row == 1
        assert end_col == 3
        assert end_row == 4

    def test_multi_letter_columns(self):
        start_col, start_row, end_col, end_row = parse_cell_range("A1:AA10")
        assert start_col == 1
        assert start_row == 1
        assert end_col == 27  # AA = 27
        assert end_row == 10

    def test_invalid_format(self):
        with pytest.raises(ValueError, match="Invalid cell range format"):
            parse_cell_range("Invalid")
