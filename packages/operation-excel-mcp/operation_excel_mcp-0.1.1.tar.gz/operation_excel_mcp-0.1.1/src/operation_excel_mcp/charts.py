from __future__ import annotations

import os
from typing import Any, Dict, List

import xlwings as xw

from .exceptions import ChartError, WorkbookError, SheetError

#获取工作簿
def _get_wb(filepath: str) -> xw.main.Book:
    app = xw.apps.active if xw.apps else None
    if app is None:
        raise WorkbookError("No running Excel instance")
    for b in app.books:
        if b.fullname.lower() == os.path.abspath(filepath).lower():
            return b
    raise WorkbookError("Workbook not open")

#新增图表
def add_chart(filepath: str, sheet_name: str, source_range: str, chart_type: str = "column_clustered", left_cell: str = "G2", bottom_right_cell: str = "N20") -> Dict[str, Any]:
    wb = _get_wb(filepath)
    ws = wb.sheets[sheet_name]
    if ws is None:
        raise SheetError("Sheet not found")
    chart_type_map = {
        #"column_clustered": xw.constants.ChartType.xlColumnClustered,
        "column_clustered": 'column_clustered',
        "column_stacked": 'column_stacked',
        "line": 'line',
        "pie": 'pie',
        "bar_clustered": 'bar_clustered',
        "area": 'area',
    }
    if chart_type not in chart_type_map:
        raise ChartError("Unsupported chart type")
    try:
        # 创建图表
        chart_range = ws.range(source_range)
        chart = ws.charts.add()

        # 设置数据源
        chart.set_source_data(chart_range)

        # 设置图表类型
        chart.chart_type = chart_type_map[chart_type]

        # 安全地设置位置（使用默认值作为备选）
        try:
            left_pos = ws.range(left_cell).left if left_cell else 100
            top_pos = ws.range(left_cell).top if left_cell else 50
            chart.left = left_pos
            chart.top = top_pos
        except:
            # 使用默认位置
            chart.left = 100
            chart.top = 50

        # 安全地设置尺寸
        try:
            if left_cell and bottom_right_cell:
                width_val = ws.range(f"{left_cell}:{bottom_right_cell}").width
                height_val = ws.range(f"{left_cell}:{bottom_right_cell}").height
                chart.width = width_val if width_val > 0 else 400
                chart.height = height_val if height_val > 0 else 300
            else:
                # 使用默认尺寸
                chart.width = 400
                chart.height = 300
        except:
            # 使用默认尺寸
            chart.width = 400
            chart.height = 300

        return {"added": True, "type": chart_type, "chart_name": chart.name}

    except Exception as e:
        raise ChartError(f"Failed to create chart: {str(e)}")

#读取图表
def list_charts(filepath: str, sheet_name: str) -> List[str]:
    wb = _get_wb(filepath)
    ws = wb.sheets[sheet_name]
    if ws is None:
        raise SheetError("Sheet not found")
    try:
        # 优先使用xlwings的charts属性
        return [chart.name for chart in ws.charts]
    except Exception:
        # 备用方案
        try:
            return [sh.name for sh in ws.api.Shapes if hasattr(sh, "Chart")]
        except Exception:
            return []

#删除图表
def delete_chart(filepath: str, sheet_name: str, chart_name: str) -> Dict[str, Any]:
    wb = _get_wb(filepath)
    ws = wb.sheets[sheet_name]
    if ws is None:
        raise SheetError("Sheet not found")
    try:
        # 优先使用xlwings的charts属性
        chart = ws.charts[chart_name]
        chart.delete()
        return {"deleted": chart_name}
    except Exception:
        # 备用方案：直接访问COM对象
        try:
            for sh in ws.api.Shapes:
                if sh.Name == chart_name and hasattr(sh, "Chart"):
                    sh.Delete()
                    return {"deleted": chart_name}
        except Exception:
            pass
        raise ChartError("Chart not found")

#编辑图表名称
def edit_chart_title(filepath: str, sheet_name: str, chart_name: str, title: str) -> Dict[str, Any]:
    wb = _get_wb(filepath)
    ws = wb.sheets[sheet_name]
    if ws is None:
        raise SheetError("Sheet not found")
    try:
        # 优先使用xlwings的charts属性
        chart = ws.charts[chart_name]
        chart.api.ChartTitle.Text = title
        return {"updated": True}
    except Exception:
        # 备用方案：直接访问COM对象
        try:
            for sh in ws.api.Shapes:
                if sh.Name == chart_name and hasattr(sh, "Chart"):
                    sh.Chart.ChartTitle.Text = title
                    return {"updated": True}
        except Exception:
            pass
        raise ChartError("Chart not found")


