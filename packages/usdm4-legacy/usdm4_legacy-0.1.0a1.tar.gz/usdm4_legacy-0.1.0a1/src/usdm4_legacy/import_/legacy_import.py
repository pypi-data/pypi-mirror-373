import copy
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_legacy.import_.load import LoadPDF
from usdm4_legacy.import_.extract import ExtractStudy
from usdm4_legacy.import_.assemble import AssembleUSDM
from usdm4.api.wrapper import Wrapper


class LegacyImport:
    MODULE = "usdm4.legacy.import_.legacy_import.LegacyImport"

    def __init__(self, file_path: str, errors: Errors):
        self._file_path = file_path
        self._errors = errors
        self._study = None

    def process(self) -> Wrapper:
        try:
            loader = LoadPDF(self._file_path, self._errors)
            sections = loader.process()
            extractor = ExtractStudy(sections, self._errors)
            self._study = extractor.process()
            assembler = AssembleUSDM(self._study, self._errors)
            wrapper = assembler.process()
            return wrapper
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "process")
            self._errors.exception(
                f"Exception raised processing legacy '.pdf' file '{self._file_path}'",
                e,
                location,
            )
            return None

    @property
    def source(self) -> dict:
        return self._study

    @property
    def source_no_sections(self) -> dict:
        the_copy = copy.deepcopy(self._study)
        the_copy["document"]["sections"] = []
        return the_copy

    @property
    def extra(self) -> dict:
        return {
            "title_page": {
                "compound_codes": "",
                "compound_names": "",
                "amendment_identifier": "",
                "sponsor_confidentiality": "",
                # Not used?
                "amendment_details": "",
                "amendment_scope": "",
                "manufacturer_name_and_address": "",
                "medical_expert_contact": "",
                "original_protocol": "",
                "regulatory_agency_identifiers": "",
                "sae_reporting_method": "",
                "sponsor_approval_date": "",
                "sponsor_name_and_address": "",
                "sponsor_signatory": "",
            },
            "amendment": {
                "amendment_details": "",
                "robustness_impact": False,
                "robustness_impact_reason": "",
                "safety_impact": False,
                "safety_impact_reason": "",
            },
            "miscellaneous": {
                "medical_expert_contact": "",
                "sae_reporting_method": "",
                "sponsor_signatory": "",
            },
        }
