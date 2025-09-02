from raw_docx.raw_docx import RawDocx
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.title_page import TitlePage
from usdm4_cpt.import_.extract.soa import SoA


class ExtractStudy:
    MODULE = "usdm4_cpt.import_.extract.__init__.ExtractStudy"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        self._raw_docx = raw_docx
        self._sections = self._raw_docx.target_document.sections
        self._errors = errors

    def process(self) -> dict:
        try:
            result = {}
            title_page = TitlePage(self._raw_docx, self._errors)
            soa = SoA(self._raw_docx, self._errors)
            result = title_page.process()
            id = result["identification"]["identifiers"][0]["identifier"]
            raw, final = soa.process(id)
            result["soa"] = {"raw": raw, "final": final}
            result["document"] = {
                "document": {
                    "label": "Protocol Document",
                    "version": "",  # @todo
                    "status": "Final",  # @todo
                    "template": "Legacy",
                    "version_date": result["study"]["version_date"],
                },
                "sections": [
                    {
                        "section_number": str(x.number) if x.number else "",
                        "section_title": x.title,
                        "text": x.to_html(),
                    }
                    for x in self._sections
                ],
            }
            result["population"] = {
                "label": "Default population",
                "inclusion_exclusion": {"inclusion": [], "exclusion": []},
            }
            result["amendments"] = {}
            return result
        except Exception as e:
            self._errors.exception(
                "Exception raised extracting study data",
                e,
                KlassMethodLocation(self.MODULE, "process"),
            )
            return None
