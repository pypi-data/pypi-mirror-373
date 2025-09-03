from __future__ import annotations

import os
from typing import Any, Dict, List

import xlwings as xw

from .exceptions import SheetError, WorkbookError

#获取工作簿
def _get_wb(filepath: str) -> xw.main.Book:
    app = xw.apps.active if xw.apps else None
    if app is None:
        raise WorkbookError("No running Excel instance")
    for b in app.books:
        if b.fullname.lower() == os.path.abspath(filepath).lower():
            return b
    raise WorkbookError("Workbook not open")

#读取所有sheet
def list_sheets(filepath: str) -> List[str]:
    wb = _get_wb(filepath)
    return [s.name for s in wb.sheets]

#新增sheet
def add_sheet(filepath: str, sheet_name: str, before: str | None = None, after: str | None = None) -> Dict[str, Any]:
    wb = _get_wb(filepath)
    if sheet_name in [s.name for s in wb.sheets]:
        raise SheetError("Sheet already exists")
    before_ws = wb.sheets[before] if before else None
    after_ws = wb.sheets[after] if after else None
    ws = wb.sheets.add(sheet_name, before=before_ws, after=after_ws)
    return {"added": ws.name}

#重命名sheet
def rename_sheet(filepath: str, old_name: str, new_name: str) -> Dict[str, Any]:
    wb = _get_wb(filepath)
    ws = wb.sheets[old_name]
    if ws is None:
        raise SheetError("Sheet not found")
    ws.name = new_name
    return {"renamed": [old_name, new_name]}

#删除sheet
def delete_sheet(filepath: str, sheet_name: str) -> Dict[str, Any]:
    wb = _get_wb(filepath)
    ws = wb.sheets[sheet_name]
    if ws is None:
        raise SheetError("Sheet not found")
    ws.delete()
    return {"deleted": sheet_name}

#复制sheet

