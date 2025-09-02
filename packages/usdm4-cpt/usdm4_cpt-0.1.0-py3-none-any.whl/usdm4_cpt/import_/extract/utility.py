import re
from raw_docx.raw_table import RawTable


@staticmethod
def test_filename(id: str, extension: str, prefix: str = "xxx") -> str:
    pattern = r"^[A-Z]{4}-\d{3}-(\d{4})$"
    match = re.match(pattern, id)
    if match:
        return f"{prefix}_{match.group(1)}{extension}"
    return f"{prefix}_filename_error{extension}"


@staticmethod
def text_within(this_text: str, in_text: str) -> bool:
    clean_text = re.sub(
        "\s+", " ", in_text
    )  # Remove any end of line chars and tabs etc
    return this_text.upper() in clean_text.upper()


@staticmethod
def table_get_row(table: RawTable, key: str) -> str:
    # print(f"\n\nTABLE FIND: {key}")
    for row in table.rows:
        if row.cells[0].is_text():
            # print(f"CELL 0: {row.cells[0].text()}")
            if text_within(key, row.cells[0].text()):
                # print(f"FOUND: {key}")
                cell = row.next_cell(0)
                result = cell.text() if cell else ""
                return result
    return ""


@staticmethod
def table_get_row_html(table: RawTable, key: str) -> str:
    for row in table.rows:
        if row.cells[0].is_text():
            if text_within(key, row.cells[0].text()):
                cell = row.next_cell(0)
                return cell.to_html() if cell else ""
    return ""
