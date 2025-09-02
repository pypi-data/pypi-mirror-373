import re
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import unicodedata


class TimepointsFeature:
    def process(
        self, html_content: str, max_rows_to_analyze: int
    ) -> List[Dict[str, Any]]:
        """
        Alternative implementation using BeautifulSoup for more robust HTML parsing.

        Args:
            html_file_path (str): Path to the HTML file containing the SoA table
            max_rows_to_analyze (int): Maximum number of rows to analyze

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing timing values and units
        """

        try:
            soup = BeautifulSoup(html_content, "html.parser")
            tables = soup.find_all("table")

            if not tables:
                return []

            # Analyze rows from all tables
            for table in tables:
                rows = table.find_all("tr")

                # Check first 5 rows without merged cells
                for i, row in enumerate(rows[:max_rows_to_analyze]):
                    cells = row.find_all(["td", "th"])

                    # Skip rows with merged cells
                    if any(
                        cell.get("colspan") or cell.get("rowspan") for cell in cells
                    ):
                        continue

                    if not cells:
                        continue

                    first_cell_text = self._clean_text(cells[0].get_text())

                    if self._is_timing_row(first_cell_text):
                        unit = self._get_time_unit(first_cell_text)
                        timing_data = []

                        # Process remaining cells (skip first column)
                        for cell in cells[1:]:
                            cell_text = self._clean_text(cell.get_text())

                            if not cell_text:
                                timing_data.append({"value": "", "unit": ""})
                                continue

                            # Skip non-timing content
                            skip_patterns = [
                                "related",
                                "sections",
                                "n/a",
                                "protocol",
                                "weeks",
                                "cycles",
                            ]
                            if any(
                                pattern in cell_text.lower()
                                for pattern in skip_patterns
                            ):
                                timing_data.append({"value": "", "unit": ""})
                                continue

                            # Handle ranges
                            if " to " in cell_text:
                                cell_text = cell_text.split(" to ")[0].strip()

                            # Clean up
                            cell_text = re.sub(r"[()a-zA-Z]+", "", cell_text).strip()

                            # Skip window indicators
                            if "±" in cell_text or ">=" in cell_text:
                                timing_data.append({"value": "", "unit": ""})
                                continue

                            # Extract numeric values
                            if re.match(r"^-?\d+\.?\d*$", cell_text):
                                timing_data.append({"value": cell_text, "unit": unit})

                        if timing_data:
                            return timing_data

                # Second pass: look for "Study Day" with merged cells
                for row in rows:
                    cells = row.find_all(["td", "th"])
                    if cells:
                        first_cell_text = self._clean_text(cells[0].get_text())
                        if "study day" in first_cell_text.lower():
                            unit = self._get_time_unit(first_cell_text)
                            timing_data = []

                            for cell in cells[1:]:
                                cell_text = self._clean_text(cell.get_text())
                                if not cell_text or "n/a" in cell_text.lower():
                                    timing_data.append({"value": "", "unit": ""})
                                    continue

                                if " to " in cell_text:
                                    cell_text = cell_text.split(" to ")[0].strip()

                                cell_text = re.sub(
                                    r"[()a-zA-Z]+", "", cell_text
                                ).strip()

                                if re.match(r"^-?\d+$", cell_text):
                                    timing_data.append(
                                        {"value": cell_text, "unit": unit}
                                    )

                            if timing_data:
                                return timing_data

            return []

        except Exception:
            return []

    def _clean_text(self, text: str) -> str:
        """Clean and normalize text content."""
        if not text:
            return ""

        # Normalize unicode
        text = unicodedata.normalize("NFKD", text)

        # Convert unicode minus characters
        minus_chars = ["−", "‒", "–", "—", "âˆ'"]
        for minus_char in minus_chars:
            text = text.replace(minus_char, "-")

        # Handle other unicode
        text = text.replace("Â±", "±")
        text = text.replace("â‰¥", ">=")

        # Normalize whitespace
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _is_timing_row(self, cell_text: str) -> bool:
        """Check if first cell indicates timing row."""
        if not cell_text:
            return False

        cell_lower = cell_text.lower()
        timing_keywords = ["study day", "study week", "target day", "week", "month"]

        if "day" in cell_lower and "window" not in cell_lower:
            if any(kw in cell_lower for kw in ["study", "(+", "target"]):
                return True

        return any(kw in cell_lower for kw in timing_keywords)

    def _get_time_unit(self, cell_text: str) -> str:
        """Determine time unit from first cell."""
        cell_lower = cell_text.lower()
        if "week" in cell_lower:
            return "week"
        elif "month" in cell_lower:
            return "month"
        return "day"
