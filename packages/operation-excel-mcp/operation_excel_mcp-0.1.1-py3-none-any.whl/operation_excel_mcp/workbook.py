from __future__ import annotations

import os
from typing import Any, Dict

import xlwings as xw

from .exceptions import WorkbookError

# 打开工作簿
def open_workbook(filepath: str, create_if_missing: bool = True, visible: bool = True) -> Dict[str, Any]:
    try:
        app = None
        apps = xw.apps
        if apps:
            # reuse first app
            app = apps[list(xw.apps.keys())[0]]
        else:
            app = xw.App(visible=visible, add_book=False)

        if not os.path.exists(filepath):
            if create_if_missing:
                wb = app.books.add()
                wb.save(filepath)
            else:
                raise WorkbookError(f"Workbook not found: {filepath}")
        wb = app.books.open(filepath)
        return {"filepath": filepath, "sheets": [s.name for s in wb.sheets]}
    except Exception as e:
        raise WorkbookError(str(e))

# 保存工作簿
def save_workbook(filepath: str) -> Dict[str, Any]:
    try:
        app = xw.apps.active if xw.apps else None
        if app is None:
            raise WorkbookError("No running Excel instance")
        wb = next((b for b in app.books if b.fullname.lower() == os.path.abspath(filepath).lower()), None)
        if wb is None:
            raise WorkbookError("Workbook not open")
        wb.save()
        return {"saved": True, "filepath": filepath}
    except Exception as e:
        raise WorkbookError(str(e))


def close_workbook(filepath: str, save: bool = True) -> Dict[str, Any]:
    try:
        app = xw.apps.active if xw.apps else None
        if app is None:
            raise WorkbookError("No running Excel instance")
        wb = next((b for b in app.books if b.fullname.lower() == os.path.abspath(filepath).lower()), None)
        if wb is None:
            raise WorkbookError("Workbook not open")
        if save:
            wb.save()
        wb.close()
        return {"closed": True}
    except Exception as e:
        raise WorkbookError(str(e))


