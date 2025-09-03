from typing import Any, TypeAlias

import openpyxl as op
import pandas as pd

from ut_xls.op.iocwb import IocWb
from ut_xls.op.ws import Ws

TyCe: TypeAlias = op.cell.cell.Cell
TyWb: TypeAlias = op.workbook.workbook.Workbook
TyWs: TypeAlias = op.worksheet.worksheet.Worksheet
TyCs: TypeAlias = op.chartsheet.chartsheet.Chartsheet
TyPdDf: TypeAlias = pd.DataFrame

# TyWsCs = Worksheet | WriteOnlyWorksheet | ReadOnlyWorksheet | Chartsheet

TyArr = list[Any]
TyAoA = list[TyArr]
TyAoAoA = list[TyAoA]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyAoS = list[str]
TyAoWs = list[TyWs]
TyDoD = dict[Any, TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoWs = dict[Any, TyWs]
TyDoPdDf = dict[Any, TyPdDf]
TyAoD_DoAoD = TyAoD | TyDoAoD
TySheet = int | str
TyOpSheets = TySheet | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]
TyStrArr = str | TyArr
TyToCe = tuple[TyCe, ...]

TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoD = None | TyAoD
TnDic = None | TyDic
TnDoAoA = None | TyDoAoA
TnAoD_DoAoD = None | TyAoD_DoAoD
TnAoWs = None | TyAoWs
TnDoWs = None | TyDoWs
TnOpSheets = None | TyOpSheets
TnSheet = None | TySheet
TnSheetname = None | TySheetname
TnWb = None | TyWb
TnWs = None | TyWs
TnCs = None | TyCs


class DoAoA:

    @staticmethod
    def create_wb(doaoa: TnDoAoA) -> TyWb:
        # def create_wb_with_doaoa(doaoa: TnDoAoA) -> TyWb:
        wb: TyWb = IocWb.get(write_only=True)
        if not doaoa:
            ws: None | TyWs | TyCs = wb.active
            if ws is None:
                return wb
            wb.remove(ws)
            return wb
        for ws_id, aoa in doaoa.items():
            _ws: None | TyWs = wb.create_sheet()
            if _ws is None:
                continue
            _ws.title = ws_id
            Ws.append_rows(_ws, aoa)
        return wb
