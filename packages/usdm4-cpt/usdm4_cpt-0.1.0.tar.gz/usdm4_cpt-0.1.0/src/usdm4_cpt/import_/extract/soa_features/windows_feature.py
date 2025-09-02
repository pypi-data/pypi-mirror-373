from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional, Union


class WindowsFeature:
    def process(
        self, html_content: str, max_rows_to_analyze: int
    ) -> List[Dict[str, Union[int, str]]]:
        """
        Extract time window information from clinical trial Schedule of Activities (SoA) tables.

        Args:
            html_content (str): HTML content containing the table
            max_rows_to_analyze (int): Maximum number of rows to analyze

        Returns:
            List[Dict]: Array of dictionaries containing window information with keys:
                    - 'before': Number of time units before scheduled visit
                    - 'after': Number of time units after scheduled visit
                    - 'unit': Time unit ('day', 'week', 'hour', 'minute')
        """
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table")

        if not table:
            return []

        rows = table.find_all("tr")
        window_values = []

        # Strategy 1: Look for explicit "Study day window" row
        window_row_found = False
        for i, row in enumerate(rows[:max_rows_to_analyze]):
            cells = row.find_all("td")
            if not cells:
                continue

            first_cell_text = self._extract_cell_text(cells[0]).lower()

            # Check if this row contains window information
            if "study day window" in first_cell_text or "window" in first_cell_text:
                window_values = self._extract_from_window_row(cells)
                window_row_found = True
                break

        # Strategy 2: Look for window notation in study day header (e.g., "Study day (+2)a")
        if not window_row_found:
            for i, row in enumerate(rows[:5]):
                cells = row.find_all("td")
                if not cells:
                    continue

                first_cell_text = self._extract_cell_text(cells[0])

                # Look for patterns like "Study day (+n)" or "Study day (±n)"
                window_match = re.search(r"\(([±+]\d+(?:\.\d+)?)\)", first_cell_text)
                if window_match and "study day" in first_cell_text.lower():
                    window_info = self._parse_single_window_value(window_match.group(1))
                    if window_info:
                        # Count visit columns (excluding first and last columns)
                        visit_count = self._count_visit_columns(rows)
                        window_values = [window_info] * visit_count
                        window_row_found = True
                        break

        # Strategy 3: Look for individual cell windows (e.g., "D8 (+1)", "D29 (±2)")
        if not window_row_found:
            for i, row in enumerate(rows[:5]):
                cells = row.find_all("td")
                if not cells:
                    continue

                first_cell_text = self._extract_cell_text(cells[0]).lower()

                # Check if this row contains study day information with windows
                if "study day" in first_cell_text and (
                    "window" in first_cell_text
                    or any("(" in self._extract_cell_text(cell) for cell in cells[1:])
                ):
                    window_values = self._extract_from_individual_cell_windows(cells)
                    break

        return window_values

    def _extract_cell_text(self, cell) -> str:
        """Extract and clean text content from a table cell."""
        if not cell:
            return ""

        # Get all text, joining multiple <p> tags with space
        text_parts = []
        for p in cell.find_all("p"):
            if p.get_text(strip=True):
                text_parts.append(p.get_text(strip=True))

        text = " ".join(text_parts)

        # Clean up special characters
        text = text.replace("Â±", "±").replace("âˆ'", "-")
        return text

    def _extract_from_window_row(self, cells: List) -> List[Dict[str, Union[int, str]]]:
        """Extract window values from a dedicated window row."""
        window_values = []

        # Skip first column, process remaining cells
        for cell in cells[1:]:
            text = self._extract_cell_text(cell)
            if text and text != "":
                window_info = self._parse_single_window_value(text)
                if window_info:
                    window_values.append(window_info)

        return window_values

    def _extract_from_individual_cell_windows(
        self, cells: List
    ) -> List[Dict[str, Union[int, str]]]:
        """Extract window values from individual cells containing day and window info."""
        window_values = []

        # Skip first column, process remaining cells
        for cell in cells[1:]:
            text = self._extract_cell_text(cell)
            if text and text not in ["NA", ""] and "to" not in text:
                # Look for patterns like "D8 (+1)" or "D29 (±2)"
                if re.search(r"D\d+", text):
                    window_match = re.search(r"\(([±+]\d+(?:\.\d+)?)\)", text)
                    if window_match:
                        window_info = self._parse_single_window_value(
                            window_match.group(1)
                        )
                        if window_info:
                            window_values.append(window_info)
                    else:
                        # Day without window specified (e.g., "D1")
                        if re.match(r"^D\d+$", text.strip()):
                            window_values.append(
                                {"before": 0, "after": 0, "unit": "day"}
                            )

        return window_values

    def _parse_single_window_value(
        self, window_text: str
    ) -> Optional[Dict[str, Union[int, str]]]:
        """Parse a single window value like '±2', '+1', or '±7, +7 if EoS'."""
        # Handle complex cases like "±7, +7 if EoS" - take the first valid value
        if "," in window_text:
            parts = window_text.split(",")
            for part in parts:
                result = self._parse_simple_window(part.strip())
                if result:
                    return result

        return self._parse_simple_window(window_text)

    def _parse_simple_window(
        self, window_text: str
    ) -> Optional[Dict[str, Union[int, str]]]:
        """Parse simple window patterns like '±2' or '+1'."""
        # Match ±n pattern (symmetric window)
        plus_minus_match = re.match(r"[±]\s*(\d+(?:\.\d+)?)", window_text)
        if plus_minus_match:
            value = float(plus_minus_match.group(1))
            return {
                "before": int(value),
                "after": int(value),
                "unit": "day",  # Default assumption
            }

        # Match +n pattern (positive-only window)
        plus_match = re.match(r"[+]\s*(\d+(?:\.\d+)?)", window_text)
        if plus_match:
            value = float(plus_match.group(1))
            return {"before": 0, "after": int(value), "unit": "day"}

        # Match -n pattern (negative-only window)
        minus_match = re.match(r"[-]\s*(\d+(?:\.\d+)?)", window_text)
        if minus_match:
            value = float(minus_match.group(1))
            return {"before": int(value), "after": 0, "unit": "day"}

        return None

    def _count_visit_columns(self, rows: List) -> int:
        """Count the number of visit columns in the table."""
        if not rows:
            return 0

        # Find header row (usually first or second row)
        for row in rows[:3]:
            cells = row.find_all("td")
            if not cells:
                continue

            visit_count = 0
            total_columns = 0
            has_visits = False

            for cell in cells:
                # Check for colspan
                colspan = int(cell.get("colspan", 1))
                total_columns += colspan

                text = self._extract_cell_text(cell).strip()

                # Look for visit patterns like V1, V2, etc.
                if re.match(r"^V\d+", text) or text in ["BL", "SCN"]:
                    visit_count += 1
                    has_visits = True

            # If we found visit columns, calculate excluding first and last columns
            if has_visits and visit_count > 0:
                # Typically exclude first column (labels) and last column (references)
                return max(0, total_columns - 2)

        # Fallback: count total columns minus first and last
        if rows:
            first_row = rows[0]
            cells = first_row.find_all("td")
            total_cols = sum(int(cell.get("colspan", 1)) for cell in cells)
            return max(0, total_cols - 2)

        return 0
