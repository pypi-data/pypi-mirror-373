from typing import TypeAlias

import openpyxl as op

TyCe: TypeAlias = op.cell.cell.Cell
TyMergedCell: TypeAlias = op.cell.cell.MergedCell
TyTupleCell = tuple[TyCe | TyMergedCell, ...]


class Ro:

    sw_add_sheet_name: str = 'sw_add_sheet_name'
    sheet_name: str = 'sheet_name'

    @classmethod
    def iter_cell_value(cls, row: TyTupleCell, **kwargs):
        sw_add_sheet_name: bool = kwargs.get(cls.sw_add_sheet_name, False)
        if sw_add_sheet_name:
            sheet_name = kwargs.get(cls.sheet_name)
            yield sheet_name
        for cell in row:
            yield cell.value
