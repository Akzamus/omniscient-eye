import textwrap
from datetime import datetime
from typing import Union

from openpyxl.styles import Alignment, Font
from openpyxl.worksheet.worksheet import Worksheet


def _wrap_text_manual(text: str, max_chars: int) -> str:
    if not text:
        return ""
    return "\n".join(textwrap.wrap(str(text), width=max_chars))


def _estimate_row_height(wrapped_text: str, font_size=11) -> float:
    lines = wrapped_text.count("\n") + 1
    return lines * (font_size + 4)


def fill_excel_sheet(sheet: Worksheet, data: list[list[Union[str, int, float, None]]]):
    max_col_width = 40
    max_chars_per_line = 30

    for row_idx, row in enumerate(data, start=1):
        max_row_height = 15

        for col_idx, value in enumerate(row, start=1):
            str_val = str(value) if value else ""
            wrapped = _wrap_text_manual(str_val, max_chars_per_line)
            cell = sheet.cell(row=row_idx, column=col_idx, value=wrapped)

            cell.alignment = Alignment(
                wrap_text=True,
                vertical="top",
                horizontal="left"
            )

            if row_idx == 1:
                cell.font = Font(bold=True)

            row_height = _estimate_row_height(wrapped)
            max_row_height = max(max_row_height, row_height)

            col_letter = cell.column_letter
            sheet.column_dimensions[col_letter].width = max_col_width

        sheet.row_dimensions[row_idx].height = max_row_height


def generate_unique_filename(base_name: str, extension: str = ".xlsx") -> str:
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return f"{base_name}_{now}{extension}"