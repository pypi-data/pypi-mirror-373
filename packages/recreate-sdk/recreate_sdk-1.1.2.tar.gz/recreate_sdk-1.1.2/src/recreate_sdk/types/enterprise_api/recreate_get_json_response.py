# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Dict, List, Optional

from ..._models import BaseModel

__all__ = ["RecreateGetJsonResponse", "Table", "TableRow", "TableRowCell"]


class TableRowCell(BaseModel):
    column_header: str

    value: str

    bbox: Optional[Dict[str, float]] = None


class TableRow(BaseModel):
    cells: List[TableRowCell]

    row_identifier: str

    row_type: Optional[str] = None


class Table(BaseModel):
    headers: List[str]

    rows: List[TableRow]


class RecreateGetJsonResponse(BaseModel):
    tables: List[Table]
