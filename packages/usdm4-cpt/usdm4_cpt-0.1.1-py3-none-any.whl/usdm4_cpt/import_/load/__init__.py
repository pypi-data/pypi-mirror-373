from raw_docx.raw_docx import RawDocx
from simple_error_log.errors import Errors


class LoadDocx:
    def __init__(self, file_path: str, errors: Errors):
        self._file_path = file_path
        self._errors = errors

    def process(self) -> RawDocx:
        raw_docx = RawDocx(self._file_path)
        self._errors.merge(raw_docx.errors)
        return raw_docx
