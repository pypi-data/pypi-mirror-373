from __future__ import annotations

import os
from typing import Any, Dict, List

import xlwings as xw

from .exceptions import RangeError, WorkbookError, SheetError

#获取工作簿
def _get_wb(filepath: str) -> xw.main.Book:
    app = xw.apps.active if xw.apps else None
    if app is None:
        raise WorkbookError("No running Excel instance")
    for b in app.books:
        if b.fullname.lower() == os.path.abspath(filepath).lower():
            return b
    raise WorkbookError("Workbook not open")

#读取单元格区域的内容
def read_range(filepath: str, sheet_name: str, address: str) -> Dict[str, Any]:
    wb = _get_wb(filepath)
    ws = wb.sheets[sheet_name]
    if ws is None:
        raise SheetError("Sheet not found")
    rng = ws.range(address)
    return {"address": rng.address, "value": rng.value, "formula": rng.formula}

#编辑单元格区域的内容
def write_range(filepath: str, sheet_name: str, address: str, value: Any = None, formula: str | None = None) -> Dict[str, Any]:
    wb = _get_wb(filepath)
    ws = wb.sheets[sheet_name]
    if ws is None:
        raise SheetError("Sheet not found")
    rng = ws.range(address)
    if formula is not None:
        rng.formula = formula
    else:
        rng.value = value
    return {"written": True}

#删除单元格区域的内容
def clear_range(filepath: str, sheet_name: str, address: str, clear_formats: bool = False) -> Dict[str, Any]:
    wb = _get_wb(filepath)
    ws = wb.sheets[sheet_name]
    if ws is None:
        raise SheetError("Sheet not found")
    rng = ws.range(address)
    if clear_formats:
        rng.clear()
    else:
        rng.clear_contents()
    return {"cleared": True}


