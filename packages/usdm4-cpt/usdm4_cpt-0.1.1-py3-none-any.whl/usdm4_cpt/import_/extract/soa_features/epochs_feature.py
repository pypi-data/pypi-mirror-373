from bs4 import BeautifulSoup


class EpochsFeature:
    def process(self, html_table: str, ignore_last: bool = False) -> dict:
        """
        Extract clinical trial period information with detailed analysis.

        Args:
            html_table (str): HTML string containing the table
            ignore_last (bool): Ignore the last column in the table (contains notes etc) (default: False)

        Returns:
            dict: Detailed analysis including whether period info was found,
                the extracted columns, and analysis details
        """
        result = {
            "contains_period_info": False,
            "period_columns": None,
            "analysis": {"total_columns": 0, "period_cells_found": [], "raw_cells": []},
        }

        # Parse the HTML
        soup = BeautifulSoup(html_table, "html.parser")

        # Find the first table and its first row
        table = soup.find("table")
        if not table:
            result["analysis"]["error"] = "No table found"
            return result

        first_row = table.find("tr")
        if not first_row:
            result["analysis"]["error"] = "No rows found in table"
            return result

        # Get all cells in the first row
        cells = first_row.find_all(["td", "th"])

        # Define period-related terms
        period_terms = [
            "screening",
            "scn",
            "treatment",
            "follow-up",
            "follow up",
            "baseline",
            "washout",
            "run-in",
            "eos",
            "end of study",
            "edv",
            "early discontinuation",
        ]

        period_columns = []

        for i, cell in enumerate(cells):
            text = cell.get_text(strip=True)
            text_lower = text.lower()
            colspan = int(cell.get("colspan", 1))

            # Store raw cell info for analysis
            result["analysis"]["raw_cells"].append(
                {"index": i, "text": text, "colspan": colspan}
            )

            # Skip first column
            if i == 0:
                continue
            # Skip last if directed
            if i >= (len(cells) - 1) and ignore_last:
                continue

            # Check for period information
            matching_terms = [term for term in period_terms if term in text_lower]
            is_period_cell = len(matching_terms) > 0

            if is_period_cell:
                result["contains_period_info"] = True
                result["analysis"]["period_cells_found"].append(
                    {"text": text, "matching_terms": matching_terms, "colspan": colspan}
                )

            # Add to result columns (expanding colspan)
            for _ in range(colspan):
                period_columns.append({"text": text, "index": i})

        # Build final result
        result["analysis"]["total_columns"] = len(period_columns)
        if result["contains_period_info"]:
            result["period_columns"] = period_columns
        return result
