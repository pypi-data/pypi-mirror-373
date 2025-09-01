from typing import Any, TypeAlias

import pyexcelerate as pe

from ut_xls.pe.iocwb import IocWb

TyWb: TypeAlias = pe.Workbook

TyArr = list[Any]
TyAoA = list[TyArr]
TyAoAoA = list[TyAoA]
TyDic = dict[Any, Any]
TyAoD = list[TyDic]
TyDoD = dict[Any, TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TnArr = None | TyArr
TnAoA = None | TyAoA
TnDic = None | TyDic
TnDoAoA = None | TyDoAoA


class DoAoD:

    @staticmethod
    def create_wb(doaod: TyDoAoD) -> TyWb:
        # if not doaod:
        #    raise Exception('doaod is empty')
        wb: TyWb = IocWb.get()
        if not doaod:
            return wb
        for sheet, aod in doaod.items():
            if not aod:
                continue
            a_header = [list(aod[0].keys())]
            a_data = [list(d.values()) for d in aod]
            a_row = a_header + a_data
            wb.new_sheet(sheet, data=a_row)
        return wb
