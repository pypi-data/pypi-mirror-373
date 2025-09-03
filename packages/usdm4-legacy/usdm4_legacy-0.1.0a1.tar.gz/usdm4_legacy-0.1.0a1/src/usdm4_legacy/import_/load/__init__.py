from usdm4_legacy.import_.load.to_html import ToHTML
from usdm4_legacy.import_.load.clean_html import CleanHTML
from usdm4_legacy.import_.load.split_html import SplitHTML
from simple_error_log.errors import Errors


class LoadPDF:
    def __init__(self, file_path: str, errors: Errors):
        self._file_path = file_path
        self._errors = errors

    def process(self) -> dict:
        processor = ToHTML(self._file_path, self._errors)
        self._html = processor.process()
        cleaner = CleanHTML(self._html, self._errors)
        self._html = cleaner.process()
        splitter = SplitHTML(self._html, self._errors)
        return splitter.process()
