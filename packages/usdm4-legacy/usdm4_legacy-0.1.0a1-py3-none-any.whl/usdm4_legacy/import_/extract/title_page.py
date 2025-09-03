from simple_error_log.errors import Errors
from usdm4_legacy.claude.claude import Claude


class TitlePage:
    MODULE = "usdm4_legacy.import_.extract.title_page.TitlePage"

    def __init__(self, sections: list[dict], errors: Errors):
        self._sections = sections
        self._errors = errors
        self._ai = Claude(self._errors)

    def process(self):
        text = ""
        index = 0
        not_numbered = True
        while not_numbered:
            if self._sections[index]["section_number"] != "":
                not_numbered = False
            else:
                text += self._sections[index]["text"]
            index += 1
            if index > 10:
                break
        prompt = f"""
            from the html below

            {text}

            Extract the following information into a JSON structure using the structure detailed below:
            - Several top levels sections:
                - a section called "titles":
                    - The title of the clinical trial protocol document, placed into the field "official"
                    - The acronym for the study, placed into the field "acronym"
                    - The brief title of the study, placed into the field "brief"
                
                - a section called "ct.gov"
                    - The NCT number allocated to the study. 
                    - The NCT number takes for the format "NCT" followed by 8 digits. 
                    - Place into a field called "identifier"

                - a section called "fda"
                    - The IND number allocated to the study. 
                    - IND is the acronym for Investigational New Drug  
                    - Place into a field called "identifier"
                    
                - a section called "sponsor":
                    - The sponsor's company name 
                        - Place into the field "label"
                    - The sponsor's study or trial identifier
                        - placed into a field "identifier"
                    - The sponsor's address placed into field "legalAddress"
                        - The address should be split into several fields
                            - The city placed into a "city" field
                            - the zip or postal code placed into a "postalCode" field 
                            - The state or region placed into a "state" field
                            - The country returned in a "country" field as a ISO 3166 country code
                            - Any other data returned as lines as an array in a "lines" field
                        - If a field is not found, set the field value to an empty string

                - a section called "other":
                    - The trial phase placed into the field "phase"
                    - The document approval date placed into the field "approval_date" in ISO 8601 YYYY-MM-DD format
                    - The document version, normall an integer, placed into a field "document_version"

                If no results can be found return an empty JSON structure.
            """
        prompt_result = self._ai.prompt(prompt)
        result = self._ai.extract_json(prompt_result)
        return result
