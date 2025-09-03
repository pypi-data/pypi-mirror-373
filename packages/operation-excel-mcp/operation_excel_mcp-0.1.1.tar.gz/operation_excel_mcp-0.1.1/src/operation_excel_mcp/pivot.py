from typing import Any, Dict, List
import logging

import xlwings as xw

from .exceptions import ValidationError, PivotError, WorkbookError

logger = logging.getLogger(__name__)

def create_pivot_table(
    filepath: str,
    sheet_name: str,
    data_range: str,
    rows: list[str],
    values: list[str],
    columns: list[str] | None = None,
    agg_func: str = "sum"
) -> dict[str, Any]:
    """Create a native Excel PivotTable (and a PivotChart) using Excel via xlwings.

    - Requires Microsoft Excel installed on the machine running this code.
    - Creates/overwrites a sheet named '{sheet_name}_pivot'.
    """
    #pythoncom.CoInitialize()
    app = None
    wb = None
    try:
        if ':' not in data_range:
            raise ValidationError("Data range must be in format 'A1:B2'")

        # Normalize agg func
        agg_norm = str(agg_func or "").strip().lower()
        if agg_norm == "mean":
            agg_norm = "average"
        agg_map = {
            "sum": xw.constants.ConsolidationFunction.xlSum,
            "average": xw.constants.ConsolidationFunction.xlAverage,
            "count": xw.constants.ConsolidationFunction.xlCount,
            "min": xw.constants.ConsolidationFunction.xlMin,
            "max": xw.constants.ConsolidationFunction.xlMax,
        }
        if agg_norm not in agg_map:
            raise ValidationError("Invalid aggregation function. Must be one of: sum, average, count, min, max")

        # Launch Excel invisibly
        #app = xw.App(visible=True, add_book=False)
        #app.display_alerts = False
        #app.screen_updating = False
        apps = xw.apps
        if apps:
            app = apps[list(xw.apps.keys())[0]]  # 复用已运行的 Excel
        else:
            app = xw.App(visible=True, add_book=False)

        wb = app.books.open(filepath)
        if sheet_name not in [s.name for s in wb.sheets]:
            raise ValidationError(f"Sheet '{sheet_name}' not found")

        src_ws = wb.sheets[sheet_name]
        src_rng = src_ws.range(data_range)

        # Validate there is at least header + one data row
        vals = src_rng.value
        if not vals or not isinstance(vals, list) or len(vals) < 2:
            raise PivotError("Source data must have a header row and at least one data row.")

        headers = [str(h) for h in vals[0]]
        if not headers or any(h is None or h == "" for h in headers):
            raise PivotError("Header row has empty headers; please ensure all columns have names.")

        available_fields = {str(h).strip().lower() for h in headers}

        def clean(field: str) -> str:
            f = str(field).strip()
            for suf in [" (sum)", " (average)", " (count)", " (min)", " (max)"]:
                if f.lower().endswith(suf):
                    return f[:-len(suf)]
            return f

        # Validate fields
        for fld in rows:
            if clean(fld).lower() not in available_fields:
                raise ValidationError(f"Invalid row field '{fld}'. Available: {', '.join(headers)}")
        for fld in values:
            if clean(fld).lower() not in available_fields:
                raise ValidationError(f"Invalid value field '{fld}'. Available: {', '.join(headers)}")
        if columns:
            for fld in columns:
                if clean(fld).lower() not in available_fields:
                    raise ValidationError(f"Invalid column field '{fld}'. Available: {', '.join(headers)}")

        # Prepare/replace pivot sheet
        pivot_sheet_name = f"{sheet_name}_pivot"
        if pivot_sheet_name in [s.name for s in wb.sheets]:
            wb.sheets[pivot_sheet_name].delete()
        pivot_ws = wb.sheets.add(pivot_sheet_name, after=wb.sheets[-1])

		# Build source/destination as A1 strings (use xlwings helper to avoid COM quirks)
        #source_addr = src_rng.get_address(include_sheetname=True, external=False)
        #dest_addr = pivot_ws.range("A3").get_address(include_sheetname=True, external=False)

		# Create PivotCache (use string address + Version)
        #print(f"{sheet_name}!{source_addr}")
        cache = wb.api.PivotCaches().Create(
			SourceType=xw.constants.PivotTableSourceType.xlDatabase,
			#SourceData=source_addr,
            SourceData=f"{sheet_name}!{data_range}"
			#Version=c.xlPivotTableVersionCurrent
		)

		# Create PivotTable at A3 on pivot sheet
        #pt_name = f"PivotTable_{uuid.uuid4().hex[:8]}"
        pt = cache.CreatePivotTable(TableDestination=pivot_ws.range("A3").api, TableName=pivot_sheet_name)

        # Configure fields
        # Row fields
        pos = 1
        for rf in rows:
            pf = pt.PivotFields(clean(rf))
            pf.Orientation = xw.constants.PivotFieldOrientation.xlRowField
            pf.Position = pos
            pos += 1

        # Column fields
        if columns:
            pos = 1
            for cf in columns:
                pf = pt.PivotFields(clean(cf))
                pf.Orientation = xw.constants.PivotFieldOrientation.xlColumnField
                pf.Position = pos
                pos += 1

        # Data fields
        for vf in values:
            field = pt.PivotFields(clean(vf))
            # AddDataField(Field, Caption, Function)
            #pt.AddDataField(field, field.Name, agg_map[agg_norm])
            field.Orientation = xw.constants.PivotFieldOrientation.xlDataField
            #field.Function = xw.constants.ConsolidationFunction.xlSum
            field.Function = agg_map[agg_norm]

        # Auto format/report layout
        try:
            pt.RowAxisLayout(1)  # xlTabularRow = 1
            pt.RepeatAllLabels(2)  # xlRepeatLabels = 2
            pt.HasAutoFormat = True
            pt.ShowTableStyleRowStripes = True
        except Exception:
            pass  # optional cosmetic settings

        # Add a PivotChart (clustered column) on the same sheet
        try:
            shape = pivot_ws.api.Shapes.AddChart2(227, xw.constants.ChartType.xlColumnClustered)  # 227 = default style
            chart = shape.Chart
            chart.SetSourceData(pt.TableRange2)
            chart.ChartTitle.Text = "Pivot Chart"
            # Move/resize near the pivot
            shape.Left = pivot_ws.range("J2").api.Left
            shape.Top = pivot_ws.range("J2").api.Top
            shape.Width = pivot_ws.range("J2:N20").api.Width
            shape.Height = pivot_ws.range("J2:N20").api.Height
        except Exception as e:
            logger.warning(f"Pivot chart creation failed (continuing without chart): {e}")

        #wb.save(filepath)

        return {
            "message": "Pivot table (and chart) created successfully",
            "details": {
                "pivot_sheet": pivot_sheet_name,
                #"pivot_table": pt_name,
                "rows": rows,
                "columns": columns or [],
                "values": values,
                "aggregation": agg_norm
            }
        }

    except (ValidationError, PivotError):
        raise
    except Exception as e:
        logger.error(f"Failed to create native pivot table: {e}")
        raise PivotError(str(e))
#    finally:
#        try:
#            if wb is not None:
#                wb.close()
#        except Exception:
#            pass
#        try:
#            if app is not None:
#                app.quit()
#        except Exception:
#            pass
#        pythoncom.CoUninitialize()

#读取数据透视表
def list_pivot_tables(filepath: str, pivot_sheet: str) -> List[str]:
    apps = xw.apps
    if not apps:
        raise WorkbookError("No running Excel instance")
    app = apps.active
    wb = next((b for b in app.books if b.fullname.lower() == filepath.lower()), None)
    if wb is None:
        raise WorkbookError("Workbook not open")
    ws = wb.sheets.get(pivot_sheet)
    if ws is None:
        raise PivotError("Pivot sheet not found")
    names = []
    try:
        for pt in ws.api.PivotTables():
            names.append(pt.Name)
    except Exception:
        pass
    return names

#删除数据透视表
def delete_pivot_sheet(filepath: str, pivot_sheet: str) -> Dict[str, Any]:
    apps = xw.apps
    if not apps:
        raise WorkbookError("No running Excel instance")
    app = apps.active
    wb = next((b for b in app.books if b.fullname.lower() == filepath.lower()), None)
    if wb is None:
        raise WorkbookError("Workbook not open")
    ws = wb.sheets.get(pivot_sheet)
    if ws is None:
        raise PivotError("Pivot sheet not found")
    ws.delete()
    return {"deleted": pivot_sheet}