from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_legacy.import_.extract.title_page import TitlePage


class ExtractStudy:
    MODULE = "usdm4_legacy.import_.extract.__init__.ExtractStudy"

    def __init__(self, sections: list[str], errors: Errors):
        self._sections = sections
        self._errors = errors

    def process(self) -> dict:
        try:
            result = {}
            title_page = TitlePage(self._sections, self._errors)
            tp_result = title_page.process()
            result["identification"] = self._identification(tp_result)
            result["document"] = {
                "document": {
                    "label": "Protocol Document",
                    "version": "",  # @todo
                    "status": "Final",  # @todo
                    "template": "Legacy",
                    "version_date": tp_result["other"]["approval_date"],
                },
                "sections": None,
            }
            result["study_design"] = {
                "label": "Study Design 1",
                "rationale": "",  # @todo
                "trial_phase": tp_result["other"]["phase"],
            }
            result["population"] = {
                "label": "Default population",
                "inclusion_exclusion": {"inclusion": [], "exclusion": []},
            }
            result["amendments"] = {}
            result["study"] = {
                "sponsor_approval_date": tp_result["other"]["approval_date"],
                "version": "1",  # @todo
                "rationale": "Not set",  # @todo
                "name": {
                    "acronym": result["identification"]["titles"]["acronym"],
                    "identifier": tp_result["sponsor"]["identifier"],
                    "compound_code": "",
                },
            }
            print(f"RESULT: {result}")
            result["document"]["sections"] = self._sections
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "process")
            self._errors.exception(
                "Exception raised extracting study data",
                e,
                location,
            )
            return None

    def _identification(self, tp: dict) -> dict:
        try:
            result = {"titles": tp["titles"], "identifiers": []}
            for org in ["ct.gov", "fda"]:
                if org in tp:
                    result["identifiers"].append(
                        {
                            "identifier": tp[org]["identifier"],
                            "scope": {"standard": org},
                        }
                    )
            if "sponsor" in tp:
                label = tp["sponsor"]["label"].strip()
                name = label.upper().replace(" ", "-")
                name = name if name else "SPONSOR"
                label = label if label else "Sponsor"
                result["identifiers"].append(
                    {
                        "identifier": tp["sponsor"]["identifier"],
                        "scope": {
                            "non_standard": {
                                "type": "pharma",
                                "name": tp["sponsor"]["label"]
                                .upper()
                                .replace(" ", "-"),
                                "description": "The sponsor organization",
                                "label": tp["sponsor"]["label"],
                                "identifier": "UNKNOWN",
                                "identifierScheme": "UNKNOWN",
                                "legalAddress": self._validate_address_field(
                                    tp["sponsor"]["legalAddress"]
                                ),
                            }
                        },
                    },
                )
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_identification")
            self._errors.exception(
                "Exception raised building identification data",
                e,
                location,
            )
            return {}

    def _validate_address_field(self, address: dict) -> dict:
        result = {}
        result["lines"] = address["lines"] if "lines" in address else []
        for field in ["city", "district", "state", "postalCode", "country"]:
            result[field] = address[field] if field in address else ""
        return result
