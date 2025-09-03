class ExcelMCPError(Exception):
    """Base class for Excel MCP related errors."""


class ValidationError(ExcelMCPError):
    pass


class WorkbookError(ExcelMCPError):
    pass


class SheetError(ExcelMCPError):
    pass


class RangeError(ExcelMCPError):
    pass


class PivotError(ExcelMCPError):
    pass


class ChartError(ExcelMCPError):
    pass


