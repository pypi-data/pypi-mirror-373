import pandas as pd


def get_thoughtspot_data_type(dtype):
    if dtype == "int":
        return "INT64"
    elif dtype in ["float", "float64", "double"]:
        return "FLOAT"
    elif dtype in ["date", "datetime64[ns]", "datetime"]:
        return "DATE"
    else:
        return "VARCHAR"


# Helper function to convert cells to DataFrame
def excel_cells_to_dataframe(cells: list[dict]) -> pd.DataFrame:
    # Extract cells from the content
    max_row = max(cell["row"] for cell in cells)
    max_col = max(cell["column"] for cell in cells)

    # Create an empty DataFrame with appropriate dimensions
    df = pd.DataFrame(index=range(1, max_row + 1), columns=range(1, max_col + 1))

    # Fill the DataFrame with values
    for cell in cells:
        row_idx = cell["row"]
        col_idx = cell["column"]

        # Extract the value based on the data_type
        cell_value = cell["value"]["value"]
        data_type = cell["value"]["data_type"]

        # Convert to the appropriate Python type
        if data_type == "int":
            cell_value = int(cell_value) if cell_value is not None else None
        elif data_type == "float":
            cell_value = float(cell_value) if cell_value is not None else None
        elif data_type == "bool":
            cell_value = bool(cell_value) if cell_value is not None else None
        elif data_type == "datetime":
            cell_value = (
                pd.to_datetime(cell_value, unit="s") if cell_value is not None else None
            )
        # Add more type conversions as needed

        df.at[row_idx, col_idx] = cell_value

    # Rename columns to better match typical DataFrame structure (optional)
    df.columns = [f"col_{i}" for i in df.columns]

    return df


def convert_celldata_to_dataframe_filtered(cell_data_list: list[dict]) -> pd.DataFrame:
    # First create the complete DataFrame
    df_full = excel_cells_to_dataframe(cell_data_list)

    # Filter out rows and columns that are entirely NaN
    # Drop rows where all values are NaN
    df_filtered = df_full.dropna(how="all")

    # Drop columns where all values are NaN
    df_filtered = df_filtered.dropna(axis=1, how="all")

    # Reset the index for cleaner output
    df_filtered = df_filtered.reset_index(drop=True)

    return df_filtered


def transform_wide_to_long(df):
    # Create a copy of the dataframe to avoid modifying the original
    df_copy = df.copy()

    # Find the indices of rows containing the metric names
    # Assuming these are the rows with string values in the first column
    metric_rows = (
        df_copy.iloc[:, 0].apply(lambda x: isinstance(x, str) and x != "NaN").values
    )
    print("metric_rows:", metric_rows, flush=True)

    # Find which row contains the dates (typically the first row)
    date_row_idx = 0

    # Exclude the date row from metric rows
    metric_rows[date_row_idx] = False

    # Extract the metric names from the first column (excluding the date row)
    metric_names = df_copy.iloc[metric_rows, 0].tolist()
    print("metric_names:", metric_names, flush=True)

    # Extract dates from the date row (all columns except the first)
    date_columns = df_copy.columns[1:]  # Skip the first column as it contains labels
    dates = df_copy.loc[date_row_idx, date_columns].tolist()

    # Initialize lists to store the transformed data
    transformed_data = []

    # For each date column, extract the metric values
    for i, date_col in enumerate(date_columns):
        date = dates[i]
        row_data = {"date": date}

        # Extract values for each metric at this date
        for metric_idx, metric_name in zip(df_copy.index[metric_rows], metric_names):
            row_data[metric_name] = df_copy.loc[metric_idx, date_col]

        transformed_data.append(row_data)

    # Create the new dataframe
    new_df = pd.DataFrame(transformed_data)

    # Convert date strings to datetime objects if they're strings
    if new_df["date"].dtype == "object":
        new_df["date"] = pd.to_datetime(new_df["date"], errors="coerce", unit="s")

    # Convert numeric columns to appropriate types
    for col in new_df.columns:
        if col != "date":
            new_df[col] = pd.to_numeric(new_df[col], errors="coerce")

    return new_df

    # Helper function to parse cell range


def parse_cell_range(cell_range_str: str) -> tuple[int, int, int, int]:
    import re

    # Parse A1:C4 format
    match = re.match(r"([A-Z]+)(\d+):([A-Z]+)(\d+)", cell_range_str)
    if not match:
        raise ValueError(f"Invalid cell range format: {cell_range_str}")

    start_col_letter, start_row_str, end_col_letter, end_row_str = match.groups()

    # Convert column letters to numbers (A=1, B=2, etc.)
    def col_letter_to_number(col_letter):
        num = 0
        for c in col_letter:
            num = num * 26 + (ord(c) - ord("A") + 1)
        return num

    start_col = col_letter_to_number(start_col_letter)
    end_col = col_letter_to_number(end_col_letter)
    start_row = int(start_row_str)
    end_row = int(end_row_str)

    return start_col, start_row, end_col, end_row
