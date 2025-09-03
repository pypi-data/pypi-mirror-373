from typing import Any, TypeAlias

import pyexcelerate as pe

from ut_xls.pe.iocwb import IocWb
from ut_xls.pe.doaoa import DoAoA
from ut_xls.pe.doaod import DoAoD

TyWb: TypeAlias = pe.Workbook

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
    def write_wb_from_doaoa(doaoa: TyDoAoA, path: str) -> None:
        # def write_xls_wb_from_doaoa(doaoa: TyDoAoA, path: str) -> None:
        if not doaoa:
            return
        wb: TyWb = DoAoA.create_wb(doaoa)
        wb.save(path)

    @staticmethod
    def write_wb_from_doaod(doaod: TyDoAoD, path: str) -> None:
        # def write_xls_wb_from_doaod(doaod: TyDoAoD, path: str) -> None:
        if not doaod:
            return
        wb: TyWb = DoAoD.create_wb(doaod)
        wb.save(path)

    @staticmethod
    def write_wb_from_aod(
            aod: TyAoD, path: str, sheet: TySheet) -> None:
        # def write_xls_wb_from_aod(aod: TyAoD, path: str, sheet_id: str) -> None:
        if not aod:
            return
        wb: TyWb = IocWb.get()
        a_header: TyArr = [list(aod[0].keys())]
        a_data: TyArr = [list(d.values()) for d in aod]
        a_row: TyArr = a_header + a_data
        wb.new_sheet(sheet, data=a_row)
        wb.save(path)
