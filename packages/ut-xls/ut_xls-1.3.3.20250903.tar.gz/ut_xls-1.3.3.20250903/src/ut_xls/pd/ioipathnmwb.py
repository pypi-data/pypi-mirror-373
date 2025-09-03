from typing import Any, TypeAlias

import pandas as pd

from ut_xls.pd.ioipathwb import IoiPathWb
from ut_path.pathnm import PathNm

TyPdDf: TypeAlias = pd.DataFrame

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[str, TyPdDf] | dict[Any, TyPdDf]
# TyDoPlDf = dict[str, TyPlDf] | dict[Any, TyPlDf]
# TyDoWsOp = dict[Any, TyWsOp]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPdDf_DoPdDf = TyPdDf | dict[str, TyPdDf] | dict[Any, TyPdDf]
# TyPath = str
TyPathnm = str

TySheet = int | str
TySheets = int | str | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]

TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDoAoD = None | TyDoAoD
TnPdDf = None | TyPdDf
TnPdDf_DoPdDf = None | TyPdDf_DoPdDf
TnDoPdDf = None | TyDoPdDf
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetname = None | TySheetname
TnSheetnames = None | TySheetnames
# TnWbOp = None | TyWbOp
# TnWsOp = None | TyWsOp
# TnPath = None | TyPath


class IoiPathnmWb:

    @staticmethod
    def read_wb_to_aod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic, **kwargs_wb) -> TnAoD:
        path = PathNm.sh_path(pathnm, kwargs)
        aod: TnAoD = IoiPathWb.read_wb_to_aod(path, sheet, **kwargs_wb)
        return aod

    @staticmethod
    def read_wb_to_doaod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic, **kwargs_wb) -> TnDoAoD:
        path = PathNm.sh_path(pathnm, kwargs)
        doaod: TnDoAoD = IoiPathWb.read_wb_to_doaod(path, **kwargs_wb)
        return doaod

    @staticmethod
    def read_wb_to_aod_or_doaod(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic, **kwargs_wb
    ) -> TnAoD_DoAoD:
        path = PathNm.sh_path(pathnm, kwargs)
        obj: TnAoD_DoAoD = IoiPathWb.read_wb_to_aod_or_doaod(path, sheet, **kwargs_wb)
        return obj

    @staticmethod
    def read_wb_to_df(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic, **kwargs_wb) -> TnPdDf:
        path = PathNm.sh_path(pathnm, kwargs)
        _pddf: TnPdDf = IoiPathWb.read_wb_to_df(path, sheet, **kwargs_wb)
        return _pddf

    @staticmethod
    def read_wb_to_dodf(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic, **kwargs_wb) -> TnDoPdDf:
        path = PathNm.sh_path(pathnm, kwargs)
        _dopddf: TnDoPdDf = IoiPathWb.read_wb_to_dodf(path, sheet, **kwargs_wb)
        return _dopddf

    @staticmethod
    def read_wb_to_df_or_dodf(
            pathnm: TyPathnm, sheet: TnSheet, kwargs: TyDic, **kwargs_wb
    ) -> TnPdDf_DoPdDf:
        path = PathNm.sh_path(pathnm, kwargs)
        obj: TnPdDf_DoPdDf = IoiPathWb.read_wb_to_df_or_dodf(path, sheet, **kwargs_wb)
        return obj
