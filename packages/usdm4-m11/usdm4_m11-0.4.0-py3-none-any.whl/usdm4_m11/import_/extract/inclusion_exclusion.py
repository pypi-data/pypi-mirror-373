from raw_docx.raw_docx import RawDocx
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class InclusionExclusion:
    MODULE = "usdm4_m11.import_.inclusion_exclusion.InclusionExclusion"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        self._errors = errors
        self._raw_docx = raw_docx

    def process(self) -> dict:
        try:
            result = {"inclusion": [], "exclusion": []}
            # Inclusion
            section = self._raw_docx.target_document.section_by_number("5.2")
            if section:
                lists = section.lists()
                if lists:
                    for item in lists[0].items:
                        result["inclusion"].append(item.to_html())
                else:
                    self._errors.error(
                        "Failed to find a list in section 5.2 in M11 document"
                    )
            else:
                self._errors.error("Failed to find section 5.2 in M11 document")

            # Exclusion
            section = self._raw_docx.target_document.section_by_number("5.3")
            if section:
                lists = section.lists()
                if lists:
                    for item in lists[0].items:
                        result["exclusion"].append(item.to_html())
                else:
                    self._errors.error(
                        "Failed to find a list in section 5.3 in M11 document"
                    )
            else:
                self._errors.error("Failed to find section 5.3 in M11 document")

            # Result
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "process")
            self._errors.exception(
                "Failed to decode the Inclusion/Exclusion criteria in the document",
                e,
                location,
            )
            return None
