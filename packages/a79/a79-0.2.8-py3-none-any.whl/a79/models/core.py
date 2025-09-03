from pydantic import BaseModel


class CSVDataResponse(BaseModel):
    total_rows: int
    page: int
    page_size: int
    data: list[dict]
    column_types: dict[str, str] | None = None
