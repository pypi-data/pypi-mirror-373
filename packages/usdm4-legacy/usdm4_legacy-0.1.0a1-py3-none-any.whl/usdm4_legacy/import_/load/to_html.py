from docling.document_converter import DocumentConverter
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class ToHTML:
    MODULE = "usdm4_legacy.import_.load.to_html.ToHTML"

    def __init__(self, full_path: str, errors: Errors):
        self._converter = DocumentConverter()
        self._full_path = full_path
        self._errors = errors

    def process(self):
        try:
            result = self._converter.convert(self._full_path)
            return result.document.export_to_html()
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception(
                "Exception raised converting document to HTML", e, location
            )
            return None
