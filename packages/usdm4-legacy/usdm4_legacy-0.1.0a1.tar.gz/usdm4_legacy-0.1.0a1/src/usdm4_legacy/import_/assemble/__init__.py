from usdm4 import USDM4
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4.assembler.assembler import Assembler
from usdm4.api.wrapper import Wrapper
from usdm4_legacy.__info__ import (
    __package_version__ as system_version,
    __system_name__ as system_name,
)


class AssembleUSDM:
    MODULE = "usdm4_legacy.import_.assemble/__init__.AssembleUSDM"

    def __init__(self, source_data: dict, errors: Errors):
        self._source_data = source_data
        self._errors = errors
        self._usdm4 = USDM4()
        self._assembler: Assembler = self._usdm4.assembler(self._errors)

    def process(self) -> Wrapper:
        try:
            self._assembler.execute(self._source_data)
            return self._assembler.wrapper(system_name, system_version)
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "process")
            self._errors.exception(
                "Exception raised assembling USDM",
                e,
                location,
            )
            return {}
