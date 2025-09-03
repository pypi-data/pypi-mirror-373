from usdm4_legacy.import_.legacy_import import LegacyImport
from usdm4.api.wrapper import Wrapper
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class USDM4Legacy:
    MODULE = "usdm4_legacy.__init__.USDM4Legacy"

    def __init__(self):
        self._errors = Errors()
        self._import = None

    def from_pdf(self, file_path: str) -> Wrapper | None:
        try:
            self._import = LegacyImport(file_path, self._errors)
            return self._import.process()
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "from_pdf")
            self._errors.exception(
                f"Exception raised converting legacy '.pdf' file '{file_path}'",
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
