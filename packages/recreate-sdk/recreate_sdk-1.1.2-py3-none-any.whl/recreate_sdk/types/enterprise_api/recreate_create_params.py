# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Required, TypedDict

from ..._types import FileTypes

__all__ = ["RecreateCreateParams"]


class RecreateCreateParams(TypedDict, total=False):
    file: Required[FileTypes]

    selected_pages: Required[str]

    is_ppt_process_enabled: str

    is_xls_process_charts_enabled: str

    is_xls_process_tables_enabled: str

    selected_table_format: str
