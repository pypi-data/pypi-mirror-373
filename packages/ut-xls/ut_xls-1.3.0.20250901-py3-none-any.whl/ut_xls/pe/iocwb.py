from typing import Any, TypeAlias

import pyexcelerate as pe

TyWb: TypeAlias = pe.Workbook


class IocWb:

    @staticmethod
    def get(**kwargs: Any) -> TyWb:
        wb: TyWb = pe.Workbook(**kwargs)
        return wb
