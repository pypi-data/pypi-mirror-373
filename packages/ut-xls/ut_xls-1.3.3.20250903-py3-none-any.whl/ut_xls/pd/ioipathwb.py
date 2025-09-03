from typing import Any, TypeAlias, TextIO, BinaryIO
# from typing_extensions import TypeIs

import pandas as pd
from pathlib import Path

from ut_dic.dopddf import DoPdDf
from ut_dfr.pddf import PdDf
from ut_obj.io import Io

TyPdDf: TypeAlias = pd.DataFrame
TyXls: TypeAlias = pd.ExcelFile

TyArr = list[Any]
TyDic = dict[Any, Any]
TyAoA = list[TyArr]
TyAoD = list[TyDic]
TyDoAoA = dict[Any, TyAoA]
TyDoAoD = dict[Any, TyAoD]
TyDoPdDf = dict[str, TyPdDf] | dict[Any, TyPdDf]
# TyDoWsOp = dict[Any, TyWsOp]
TyAoD_DoAoD = TyAoD | TyDoAoD
TyPdDf_DoPdDf = TyPdDf | TyDoPdDf
TyPdFileSrc = str | bytes | TyXls | Path | TextIO | BinaryIO
TySheet = int | str
TySheets = int | str | list[int | str]
TySheetname = str
TySheetnames = list[TySheetname]

TnArr = None | TyArr
TnAoA = None | TyAoA
TnAoD = None | TyAoD
TnAoD_DoAoD = None | TyAoD_DoAoD
TnDic = None | TyDic
TnDoAoA = None | TyDoAoA
TnDoAoD = None | TyDoAoD
# TnDoWsOp = None | TyDoWsOp
TnPdDf = None | TyPdDf
TnPdDf_DoPdDf = None | TyPdDf_DoPdDf
TnDoPdDf = None | TyDoPdDf
# TnDoPlDf = None | TyDoPlDf
TnSheet = None | TySheet
TnSheets = None | TySheets
TnSheetname = None | TySheetname
TnSheetnames = None | TySheetnames
TnDf_DoDf = TnPdDf_DoPdDf


class IoiPathWb:

    @classmethod
    def read_wb_to_aod(
            cls, io: TyPdFileSrc, sheet: TnSheet, **kwargs) -> TnAoD:
        _obj = cls.read_wb_to_aod_or_doaod(io, sheet, **kwargs)
        if not isinstance(_obj, list):
            raise Exception(f"Object: {_obj} should be of type arr")
        return _obj

    @classmethod
    def read_wb_to_doaod(
            cls, io: TyPdFileSrc, sheet: TnSheet, **kwargs) -> TnDoAoD:
        _obj = cls.read_wb_to_aod_or_doaod(io, sheet, **kwargs)
        if not isinstance(_obj, dict):
            raise Exception(f"Object: {_obj} should be of type dict")
        return _obj

    @classmethod
    def read_wb_to_aod_or_doaod(
            cls, io: TyPdFileSrc, sheet: TnSheet, **kwargs) -> Any:
        _obj: TnPdDf_DoPdDf = cls.read_wb_to_df_or_dodf(io, sheet, **kwargs)
        if isinstance(_obj, dict):
            return DoPdDf.to_doaod(_obj)
        return PdDf.to_aod(_obj)

    @classmethod
    def read_wb_to_df(
            cls, io: TyPdFileSrc, sheet: TnSheet, **kwargs) -> TnPdDf:
        _obj = cls.read_wb_to_df_or_dodf(io, sheet, **kwargs)
        if not isinstance(_obj, pd.DataFrame):
            raise Exception(f"Object: {_obj} should be of type TnPdDf")
        return _obj

    @classmethod
    def read_wb_to_dodf(
            cls, io: TyPdFileSrc, sheet: TnSheet, **kwargs) -> TnDoPdDf:
        _obj = cls.read_wb_to_df_or_dodf(io, sheet, **kwargs)
        if not isinstance(_obj, dict):
            raise Exception(f"Object: {_obj} should be of type TnDoPdD")
        return _obj

    @classmethod
    def read_wb_to_df_or_dodf(
            cls, io: TyPdFileSrc, sheet: TnSheet, **kwargs) -> Any:
        Io.verify(io)
        if not (sheet is None or isinstance(sheet, (int, str, list, tuple))):
            msg = f"sheet; {sheet} must be None or of type (int, str, list, tuple)"
            raise Exception(msg)
        obj: TnPdDf_DoPdDf = pd.read_excel(io, sheet_name=sheet, **kwargs)
        if obj is not None:
            return obj
        if sheet is None:
            msg = f"Excel Workbook {io!r} contains no sheets"
        else:
            msg = f"Sheets {sheet} are not contained in Excel Workbook {io!r}"
        raise Exception(msg)
