import re
from typing import List
from bs4 import BeautifulSoup


class VisitsFeature:
    def process(self, html_content: str, max_rows_to_analyze: int) -> List[str]:
        """
        Extract visit names from Schedule of Activities (SoA) HTML table.

        This function analyzes the first few rows of an HTML table to find visit identifiers,
        typically study day numbers or visit codes like SCN, V1, V2, etc.

        Args:
            html_content (str): HTML content containing the SoA table
            max_rows_to_analyze (int): Maximum number of rows to analyze

        Returns:
            List[str]: Array of visit names/identifiers, excluding the first column.
                    Returns empty list if no valid visit row is found.

        Rules applied:
            1. Looks for visit names in rows 1-N (where N = max_rows_to_analyze)
            2. Visits typically named "SCR", "SCN", "V1", "V2", "V3", study days, etc.
            3. May have "Visit" or "Study Visit" in the first column
            4. Ignores rows with merged cells (colspan > 1)
            5. Falls back to "study day" rows if traditional visit names not found
            6. Excludes first column from output
        """

        # Parse HTML content
        try:
            soup = BeautifulSoup(html_content, "html.parser")

            # Find the main table (assumes ich-m11-table class or first table)
            table = soup.find("table", class_="ich-m11-table")
            if not table:
                table = soup.find("table")

            if not table:
                return []

            # Get all table rows
            rows = table.find_all("tr")

            if not rows:
                return []

            # Analyze specified number of rows
            best_visit_row = None
            best_score = -1

            for i in range(min(max_rows_to_analyze, len(rows))):
                row = rows[i]
                cells = row.find_all(["td", "th"])

                if not cells:
                    continue

                # Extract cell information
                cell_info = []
                has_merged_cells = False

                for j, cell in enumerate(cells):
                    text = cell.get_text(strip=True)
                    colspan = int(cell.get("colspan", "1"))

                    if colspan > 1:
                        has_merged_cells = True

                    cell_info.append({"index": j, "text": text, "colspan": colspan})

                # Get first column text
                first_column_text = cell_info[0]["text"].lower() if cell_info else ""

                # Skip rows with merged cells as per instructions
                if has_merged_cells:
                    continue

                # Extract visit candidates (excluding first column)
                visit_candidates = [cell["text"] for cell in cell_info[1:]]

                # Score this row based on visit patterns
                score = self._score_visit_row(visit_candidates, first_column_text)

                if score > best_score:
                    best_score = score
                    best_visit_row = visit_candidates

            # Return best result or empty list
            if best_visit_row is not None and best_score > 0:
                # Clean up empty strings at the end
                cleaned_visits = [
                    visit.strip() for visit in best_visit_row if visit.strip()
                ]
                return cleaned_visits
            else:
                return []

        except Exception:
            return []

    def _score_visit_row(
        self, visit_candidates: List[str], first_column_text: str
    ) -> int:
        """
        Score a row based on how likely it contains visit information.

        Args:
            visit_candidates (List[str]): List of potential visit names
            first_column_text (str): Text from the first column (lowercased)

        Returns:
            int: Score indicating likelihood this row contains visits (higher = better)
        """
        score = 0

        # Check if first column indicates this is a visit row
        visit_indicators = ["visit", "study day", "day"]
        for indicator in visit_indicators:
            if indicator in first_column_text:
                score += 10
                break

        # Count how many cells match visit patterns
        visit_patterns = [
            r"^(SCN|SCR)$",  # Screening visits
            r"^V\d+$",  # Visit numbers (V1, V2, etc.)
            r"^Visit\s*\d+$",  # Visit 1, Visit 2, etc.
            r"^-?\d+(\s*to\s*-?\d+)?$",  # Study days (1, -1, -28 to -2, etc.)
            r"^−\d+(\s*to\s*−\d+)?$",  # Study days with Unicode minus
            r"^(EoS|EDV)$",  # End of study, Early discontinuation visit
            r"^Day\s*-?\d+$",  # Day 1, Day -1, etc.
        ]

        for candidate in visit_candidates:
            if not candidate.strip():
                continue

            for pattern in visit_patterns:
                if re.match(pattern, candidate.strip(), re.IGNORECASE):
                    score += 5
                    break

        # Bonus for having many non-empty visit candidates
        non_empty_count = len([c for c in visit_candidates if c.strip()])
        if non_empty_count >= 5:
            score += 5
        elif non_empty_count >= 3:
            score += 2

        return score
