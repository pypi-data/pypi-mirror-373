from usdm4_m11.import_.m11_import import M11Import
from usdm4.api.wrapper import Wrapper
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class USDM4M11:
    MODULE = "src.usdm4_m11.__init__.USDM4M11"

    def __init__(self):
        self._errors = Errors()
        self._m11_import = None

    def from_docx(self, filepath: str) -> Wrapper | None:
        try:
            self._m11_import = M11Import(filepath, self._errors)
            return self._m11_import.process()
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "from_docx")
            self._errors.exception(
                f"Exception raised converting M11 '-docx' file '{filepath}'",
                e,
                location,
            )
            return None

    @property
    def extra(self) -> dict:
        return self._m11_import.extra if self._m11_import else None

    @property
    def source(self) -> dict:
        return self._m11_import.source if self._m11_import else None

    @property
    def source_no_sections(self) -> dict:
        return self._m11_import.source_no_sections if self._m11_import else None

    @property
    def errors(self):
        return self._errors
