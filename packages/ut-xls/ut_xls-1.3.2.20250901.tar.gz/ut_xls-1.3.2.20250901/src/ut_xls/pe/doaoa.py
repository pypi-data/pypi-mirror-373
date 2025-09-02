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


class DoAoA:

    @staticmethod
    def create_wb(doaoa: TyDoAoA) -> TyWb:
        # if not doaoa:
        #    raise Exception('doaoa is empty')
        wb: TyWb = IocWb.get()
        if not doaoa:
            return wb
        for sheet, aoa in doaoa.items():
            if not aoa:
                continue
            wb.new_sheet(sheet, data=aoa)
        return wb
