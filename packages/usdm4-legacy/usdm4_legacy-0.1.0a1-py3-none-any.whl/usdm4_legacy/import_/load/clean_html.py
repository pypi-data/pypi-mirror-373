import warnings
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from bs4 import BeautifulSoup


class CleanHTML:
    MODULE = "usdm4_legacy.import_.load.clean_html.cleanHTML"

    def __init__(self, html: str, errors: Errors):
        self._html = html
        self._errors = errors
        self._soup = None

    def process(self) -> str | None:
        try:
            self._soup: BeautifulSoup = self._get_soup(self._html)
            self._extract_toc()
            return str(self._soup)
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception(
                "Exception raised converting document to HTML", e, location
            )
            return None

    def _extract_toc(self):
        """
        Remove table of contents from HTML document.

        This method handles various TOC structures:
        1. Single or multiple consecutive tables after TOC heading
        2. Optional intermediate headings between TOC heading and tables
        3. Different heading formats ("Table of Contents", "TABLE OF CONTENTS", etc.)
        4. Tables containing section numbers, page numbers, or other TOC indicators
        """
        try:
            for heading in self._soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"]):
                if "TABLE OF CONTENTS" in heading.get_text().upper():
                    elements_to_remove = []

                    # Start with the TOC heading itself
                    elements_to_remove.append(heading)

                    # Look for elements after the TOC heading
                    current_element = heading.next_sibling

                    # Track if we've found any TOC tables
                    found_toc_tables = False

                    # Look ahead to find all TOC-related content
                    while current_element:
                        if hasattr(current_element, "name"):
                            # Check if it's a heading that might be part of TOC structure
                            if current_element.name in [
                                "h1",
                                "h2",
                                "h3",
                                "h4",
                                "h5",
                                "h6",
                            ]:
                                heading_text = current_element.get_text().strip()
                                # If it's another TOC-related heading or document title repetition
                                if not found_toc_tables and (
                                    len(heading_text)
                                    > 50  # Likely a repeated document title
                                    or "LIST OF" in heading_text.upper()
                                    or "APPENDICES" in heading_text.upper()
                                ):
                                    elements_to_remove.append(current_element)
                                else:
                                    # If we've found tables and hit a new section, stop
                                    if found_toc_tables:
                                        break

                            # Check if it's a table
                            elif current_element.name == "table":
                                if self._is_toc_table(current_element):
                                    elements_to_remove.append(current_element)
                                    found_toc_tables = True
                                else:
                                    # If we've already found TOC tables and this isn't one, stop
                                    if found_toc_tables:
                                        break

                            # Stop if we hit actual content (paragraphs with substantial text)
                            elif current_element.name == "p":
                                text = current_element.get_text().strip()
                                if len(text) > 100 and not self._looks_like_toc_content(
                                    text
                                ):
                                    break

                        current_element = current_element.next_sibling

                    # Remove all identified elements
                    for element in elements_to_remove:
                        if element and element.parent:  # Make sure element still exists
                            element.extract()

                    return

        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_extract_toc")
            self._errors.exception(
                "Exception raised while attempting to extract ToC",
                e,
                location,
            )

    def _is_toc_table(self, table):
        """
        Determine if a table is likely part of a table of contents.

        Args:
            table: BeautifulSoup table element

        Returns:
            bool: True if the table appears to be part of a TOC
        """
        try:
            # Get all text content from the table
            table_text = table.get_text().lower()

            # Look for common TOC indicators
            toc_indicators = [
                "section",
                "page",
                "chapter",
                "appendix",
                "protocol",
                "synopsis",
                "objective",
                "endpoint",
                "study design",
                "inclusion",
                "exclusion",
                "assessment",
                "statistical",
                "safety",
                "efficacy",
                "analysis",
            ]

            # Count how many TOC indicators are present
            indicator_count = sum(
                1 for indicator in toc_indicators if indicator in table_text
            )

            # Check for page number patterns (numbers at end of lines/cells)
            import re

            page_numbers = re.findall(r"\b\d{1,3}\b", table_text)

            # Check table structure - TOC tables often have 2-3 columns
            rows = table.find_all("tr")
            if rows:
                # Check if most rows have 2-3 cells (section name, page number, etc.)
                cell_counts = []
                for row in rows[:5]:  # Check first 5 rows
                    cells = row.find_all(["td", "th"])
                    if cells:
                        cell_counts.append(len(cells))

                avg_cells = sum(cell_counts) / len(cell_counts) if cell_counts else 0
                has_toc_structure = 2 <= avg_cells <= 4
            else:
                has_toc_structure = False

            # Decision logic
            return (
                indicator_count >= 3  # Many TOC-related terms
                or (
                    indicator_count >= 1 and len(page_numbers) >= 3
                )  # Some indicators + page numbers
                or (
                    has_toc_structure and indicator_count >= 1
                )  # Good structure + some indicators
                or (has_toc_structure and len(page_numbers) >= 2)
            )  # Good structure + some page numbers

        except Exception:
            # If analysis fails, err on the side of caution
            return False

    def _looks_like_toc_content(self, text):
        """
        Check if text looks like it could be TOC-related content.

        Args:
            text: String to analyze

        Returns:
            bool: True if text appears to be TOC-related
        """
        text_lower = text.lower()
        return any(
            phrase in text_lower
            for phrase in [
                "table of contents",
                "list of tables",
                "list of figures",
                "list of appendices",
                "page",
                "section",
            ]
        )

    def _get_soup(self, text: str) -> BeautifulSoup:
        try:
            with warnings.catch_warnings(record=True) as warning_list:
                result = BeautifulSoup(text, "html.parser")
            if warning_list:
                for item in warning_list:
                    self._errors.debug(
                        f"Warning raised within Soup package, processing '{text}'\nMessage returned '{item.message}'",
                        KlassMethodLocation(self.MODULE, "get_soup"),
                    )
            return result
        except Exception as e:
            self._errors.exception(
                f"Parsing '{text}' with soup",
                e,
                KlassMethodLocation(self.MODULE, "get_soup"),
            )
            return BeautifulSoup("", "html.parser")
