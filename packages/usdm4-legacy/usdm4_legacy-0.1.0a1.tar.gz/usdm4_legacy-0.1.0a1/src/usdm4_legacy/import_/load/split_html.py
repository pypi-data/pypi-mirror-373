import warnings
import re
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from bs4 import BeautifulSoup


class SplitHTML:
    MODULE = "usdm4_legacy.import_.load.split_html.SplitHTML"

    def __init__(self, html: str, errors: Errors):
        self._html = html
        self._errors = errors
        self._soup = None

    def process(self) -> list[dict] | None:
        """
        Split HTML document into sections based on section headings.

        Returns:
            list[dict]: Array of dictionaries, each containing:
                - section_number: The section number (e.g., "1", "1.1", "1.2.3")
                - section_title: The section title text
                - text: The HTML content of the section
        """
        try:
            self._soup: BeautifulSoup = self._get_soup(self._html)
            sections = self._extract_sections()
            return sections
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "execute")
            self._errors.exception(
                "Exception raised splitting document into sections", e, location
            )
            return None

    def _extract_sections(self) -> list[dict]:
        """
        Extract sections from the HTML document.

        Returns:
            list[dict]: List of section dictionaries
        """
        sections = []

        try:
            # Find all heading tags
            headings = self._soup.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])

            # Find the first numbered section heading
            first_numbered_heading = None
            # first_numbered_index = -1

            for i, heading in enumerate(headings):
                section_info = self._parse_section_heading(heading)
                if section_info:
                    first_numbered_heading = heading
                    # first_numbered_index = i
                    break

            # If there's content before the first numbered section, capture it
            if first_numbered_heading:
                pre_section_content = self._get_pre_section_content(
                    first_numbered_heading
                )
                if pre_section_content.strip():
                    pre_section_dict = {
                        "section_number": "",
                        "section_title": "",
                        "text": pre_section_content,
                    }
                    sections.append(pre_section_dict)

            # Process numbered sections
            for i, heading in enumerate(headings):
                section_info = self._parse_section_heading(heading)

                if section_info:
                    # Get the content between this heading and the next section heading
                    content = self._get_section_content(heading, headings[i + 1 :])

                    section_dict = {
                        "section_number": section_info["number"],
                        "section_title": section_info["title"],
                        "text": content,
                    }

                    sections.append(section_dict)

            return sections

        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_extract_sections")
            self._errors.exception(
                "Exception raised while extracting sections",
                e,
                location,
            )
            return []

    def _parse_section_heading(self, heading) -> dict | None:
        """
        Parse a heading to extract section number and title.

        Args:
            heading: BeautifulSoup heading element

        Returns:
            dict: Dictionary with 'number' and 'title' keys, or None if not a section heading
        """
        try:
            heading_text = heading.get_text().strip()

            # Pattern to match section numbers: digits separated by dots, followed by text
            # Examples: "1. Introduction", "1.2.3 Study Design", "10.3.1.2. Secondary Efficacy Analyses"
            pattern = r"^(\d+(?:\.\d+)*\.?)\s+(.+)$"
            match = re.match(pattern, heading_text)

            if match:
                section_number = match.group(1).rstrip(
                    "."
                )  # Remove trailing dot if present
                section_title = match.group(2).strip()

                return {"number": section_number, "title": section_title}

            # Also check for patterns where the number might be in a separate element
            # or have different formatting
            alt_patterns = [
                r"^(\d+(?:\.\d+)*)\s*[-–—]\s*(.+)$",  # "1.2 - Title"
                r"^(\d+(?:\.\d+)*)\s+(.+)$",  # "1.2 Title" (no dot)
            ]

            for pattern in alt_patterns:
                match = re.match(pattern, heading_text)
                if match:
                    return {"number": match.group(1), "title": match.group(2).strip()}

            return None

        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_parse_section_heading")
            self._errors.exception(
                f"Exception raised while parsing section heading: {heading}",
                e,
                location,
            )
            return None

    def _get_section_content(self, current_heading, remaining_headings) -> str:
        """
        Get the HTML content between the current heading and the next section heading.

        Args:
            current_heading: The current section heading element
            remaining_headings: List of remaining heading elements

        Returns:
            str: HTML content of the section
        """
        try:
            content_elements = []

            # Start from the element after the current heading
            current_element = current_heading.next_sibling

            # Find the next section heading (if any)
            next_section_heading = None
            for heading in remaining_headings:
                if self._parse_section_heading(heading):
                    next_section_heading = heading
                    break

            # Collect all elements until we reach the next section heading
            while current_element:
                if current_element == next_section_heading:
                    break

                # Include the element if it has content
                if hasattr(current_element, "name") and current_element.name:
                    # Skip if this is another section heading
                    if current_element.name in [
                        "h1",
                        "h2",
                        "h3",
                        "h4",
                        "h5",
                        "h6",
                    ] and self._parse_section_heading(current_element):
                        break

                    content_elements.append(str(current_element))
                elif hasattr(current_element, "strip") and current_element.strip():
                    # Include text nodes that have content
                    content_elements.append(current_element.strip())

                current_element = current_element.next_sibling

            # Combine all content elements
            content = "".join(content_elements)

            # Clean up the content
            content = content.strip()

            return content

        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_get_section_content")
            self._errors.exception(
                "Exception raised while getting section content",
                e,
                location,
            )
            return ""

    def _get_pre_section_content(self, first_numbered_heading) -> str:
        """
        Get the HTML content that appears before the first numbered section heading.

        Args:
            first_numbered_heading: The first numbered section heading element

        Returns:
            str: HTML content before the first numbered section
        """
        try:
            content_elements = []

            # Start from the beginning of the body (or document)
            body = self._soup.find("body")
            if not body:
                # If no body tag, start from the root
                start_element = self._soup
            else:
                start_element = body

            # Collect all elements until we reach the first numbered heading
            def collect_elements(element):
                for child in element.children:
                    if child == first_numbered_heading:
                        return False  # Stop collecting

                    if hasattr(child, "name") and child.name:
                        # If this is a heading, check if it's a numbered section
                        if child.name in [
                            "h1",
                            "h2",
                            "h3",
                            "h4",
                            "h5",
                            "h6",
                        ] and self._parse_section_heading(child):
                            return False  # Stop if we hit another numbered section

                        # If it contains the first numbered heading, recurse
                        if first_numbered_heading in child.descendants:
                            if not collect_elements(child):
                                return False
                        else:
                            # Add this element if it doesn't contain the first numbered heading
                            content_elements.append(str(child))
                    elif hasattr(child, "strip") and child.strip():
                        # Include text nodes that have content
                        content_elements.append(child.strip())

                return True

            collect_elements(start_element)

            # Combine all content elements
            content = "".join(content_elements)

            # Clean up the content
            content = content.strip()

            return content

        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_get_pre_section_content")
            self._errors.exception(
                "Exception raised while getting pre-section content",
                e,
                location,
            )
            return ""

    def _get_soup(self, text: str) -> BeautifulSoup:
        """
        Parse HTML text into BeautifulSoup object.

        Args:
            text: HTML text to parse

        Returns:
            BeautifulSoup: Parsed HTML object
        """
        try:
            with warnings.catch_warnings(record=True) as warning_list:
                result = BeautifulSoup(text, "html.parser")
            if warning_list:
                for item in warning_list:
                    self._errors.debug(
                        f"Warning raised within Soup package, processing '{text[:100]}...'\nMessage returned '{item.message}'",
                        KlassMethodLocation(self.MODULE, "_get_soup"),
                    )
            return result
        except Exception as e:
            self._errors.exception(
                "Parsing HTML with soup",
                e,
                KlassMethodLocation(self.MODULE, "_get_soup"),
            )
            return BeautifulSoup("", "html.parser")
