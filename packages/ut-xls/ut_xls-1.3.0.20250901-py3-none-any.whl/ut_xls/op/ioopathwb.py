from typing import Any, TypeAlias

import openpyxl as op

from ut_xls.op.doaod import DoAoD

TyWb: TypeAlias = op.workbook.workbook.Workbook

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyPath = str
TyPathnm = str
TySheet = int | str

TnWb = None | TyWb


class IooPathWb:

    @staticmethod
    def write(wb: TnWb, path: TyPath) -> None:
        if wb is not None:
            wb.save(path)

    @staticmethod
    def write_wb_from_doaod(doaod: TyDoAoD, path: str) -> None:
        if not doaod:
            return
        wb: TyWb = DoAoD.create_wb(doaod)
        wb.save(path)
