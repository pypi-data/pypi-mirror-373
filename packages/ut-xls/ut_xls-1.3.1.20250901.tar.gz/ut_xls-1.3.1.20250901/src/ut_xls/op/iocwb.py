from typing import Any, TypeAlias

import openpyxl as op

TyWb: TypeAlias = op.workbook.workbook.Workbook
TnWb = None | TyWb


class IocWb:

    @staticmethod
    def get(**kwargs: Any) -> TyWb:
        wb: TyWb = op.Workbook(**kwargs)
        return wb
