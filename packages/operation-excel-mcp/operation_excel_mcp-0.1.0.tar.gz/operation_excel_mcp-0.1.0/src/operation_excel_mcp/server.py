#import logging
import os
from typing import Any, List, Dict, Optional

from mcp.server.fastmcp import FastMCP

from .workbook import open_workbook, save_workbook, close_workbook
from .sheets import list_sheets, add_sheet, rename_sheet, delete_sheet
from .ranges import read_range, write_range, clear_range
from .charts import add_chart, list_charts, delete_chart, edit_chart_title
from .pivot import create_pivot_table, list_pivot_tables, delete_pivot_sheet

# Initialize FastMCP server
mcp = FastMCP(
    "excel-mcp",
    host=os.environ.get("FASTMCP_HOST", "0.0.0.0"),
    port=int(os.environ.get("FASTMCP_PORT", "8017")),
    instructions="Excel MCP Server for manipulating Excel files"
)


# Workbook
@mcp.tool()
def workbook_open(filepath: str, create_if_missing: bool = True, visible: bool = True) -> Dict[str, Any]:
    return open_workbook(filepath, create_if_missing, visible)


@mcp.tool()
def workbook_save(filepath: str) -> Dict[str, Any]:
    return save_workbook(filepath)


@mcp.tool()
def workbook_close(filepath: str, save: bool = True) -> Dict[str, Any]:
    return close_workbook(filepath, save)


# Sheets
@mcp.tool()
def sheets_list(filepath: str) -> List[str]:
    return list_sheets(filepath)


@mcp.tool()
def sheet_add(filepath: str, sheet_name: str, before: Optional[str] = None, after: Optional[str] = None) -> Dict[str, Any]:
    return add_sheet(filepath, sheet_name, before, after)


@mcp.tool()
def sheet_rename(filepath: str, old_name: str, new_name: str) -> Dict[str, Any]:
    return rename_sheet(filepath, old_name, new_name)


@mcp.tool()
def sheet_delete(filepath: str, sheet_name: str) -> Dict[str, Any]:
    return delete_sheet(filepath, sheet_name)


# Ranges
@mcp.tool()
def range_read(filepath: str, sheet_name: str, address: str) -> Dict[str, Any]:
    return read_range(filepath, sheet_name, address)


@mcp.tool()
def range_write(filepath: str, sheet_name: str, address: str, value: Any | None = None, formula: str | None = None) -> Dict[str, Any]:
    return write_range(filepath, sheet_name, address, value=value, formula=formula)


@mcp.tool()
def range_clear(filepath: str, sheet_name: str, address: str, clear_formats: bool = False) -> Dict[str, Any]:
    return clear_range(filepath, sheet_name, address, clear_formats)


# Charts
@mcp.tool()
def chart_add(filepath: str, sheet_name: str, source_range: str, chart_type: str = "column_clustered", left_cell: str = "G2", bottom_right_cell: str = "N20") -> Dict[str, Any]:
    return add_chart(filepath, sheet_name, source_range, chart_type, left_cell, bottom_right_cell)


@mcp.tool()
def charts_list(filepath: str, sheet_name: str) -> List[str]:
    return list_charts(filepath, sheet_name)


@mcp.tool()
def chart_delete(filepath: str, sheet_name: str, chart_name: str) -> Dict[str, Any]:
    return delete_chart(filepath, sheet_name, chart_name)


@mcp.tool()
def chart_title_edit(filepath: str, sheet_name: str, chart_name: str, title: str) -> Dict[str, Any]:
    return edit_chart_title(filepath, sheet_name, chart_name, title)


# Pivot
@mcp.tool()
def pivot_create(filepath: str, sheet_name: str, data_range: str, rows: List[str], values: List[str], columns: List[str] | None = None, agg_func: str = "sum") -> Dict[str, Any]:
    return create_pivot_table(filepath, sheet_name, data_range, rows, values, columns, agg_func)


@mcp.tool()
def pivot_list(filepath: str, pivot_sheet: str) -> List[str]:
    return list_pivot_tables(filepath, pivot_sheet)


@mcp.tool()
def pivot_delete_sheet(filepath: str, pivot_sheet: str) -> Dict[str, Any]:
    return delete_pivot_sheet(filepath, pivot_sheet)


if __name__ == "__main__":
    mcp.run(transport="stdio")