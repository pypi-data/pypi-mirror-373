from typing import Any, TypeAlias

import openpyxl as op
import pandas as pd

from ut_path.path import Path

from ut_xls.op.ioipathwb import IoiPathWb
from ut_xls.op.wb import Wb

TyWb: TypeAlias = op.workbook.workbook.Workbook
TyPdDf: TypeAlias = pd.DataFrame

TyDic = dict[Any, Any]
TyDoPdDf = dict[Any, TyPdDf]
TyPath = str
TnWb = None | TyWb


class IouPathWb:

    @staticmethod
    def update_wb_with_dodf_by_tpl(
            dodf: TyDoPdDf, path_tpl: TyPath, path: TyPath, **kwargs) -> None:
        _wb_tpl: TyWb = IoiPathWb.load(path_tpl)
        wb: TnWb = Wb.update_wb_with_dodf(_wb_tpl, dodf, **kwargs)
        if wb is None:
            return
        Path.mkdir_from_path(path)
        wb.save(path)
