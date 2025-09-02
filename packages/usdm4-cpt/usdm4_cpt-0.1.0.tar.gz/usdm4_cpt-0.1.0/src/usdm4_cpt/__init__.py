from usdm4_cpt.import_.cpt_import import CPTImport
from usdm4.api.wrapper import Wrapper
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class USDM4CPT:
    MODULE = "usdm4_cpt.__init__.USDM4CPT"

    def __init__(self):
        self._errors = Errors()
        self._import = None

    def from_docx(self, filepath: str) -> Wrapper | None:
        try:
            self._import = CPTImport(filepath, self._errors)
            return self._import.process()
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "from_docx")
            self._errors.exception(
                f"Exception raised converting CPT '.docx' file '{filepath}'",
                e,
                location,
            )
            return None

    @property
    def extra(self) -> dict:
        return self._import.extra if self._import else None

    @property
    def source(self) -> dict:
        return self._import.source if self._import else None

    @property
    def source_no_sections(self) -> dict:
        return self._import.source_no_sections if self._import else None

    @property
    def errors(self):
        return self._errors
