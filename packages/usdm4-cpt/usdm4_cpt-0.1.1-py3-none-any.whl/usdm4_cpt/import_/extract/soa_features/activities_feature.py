from bs4 import BeautifulSoup
from typing import List, Dict


class ActivitiesFeature:
    def process(
        self, html_content: str, start_row: int, ignore_last: bool = False
    ) -> List[Dict]:
        """
        Extract parent and child activities from a Schedule of Activities HTML table.

        Args:
            html_content (str): HTML content containing the table
            start_row (int): Row number to start processing activities from.
            ignore_last (bool): Ignore the last column in the table (contains notes etc) (default False)

        Returns:
            List of activity dictionaries, either standalone activities or parent activities with nested children
        """

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table")

        if not table:
            raise ValueError("No table found in HTML content")

        # Extract all table rows
        rows = table.find_all("tr")

        # Convert rows to list of cell contents
        table_data = []
        for row in rows:
            cells = row.find_all(["td", "th"])
            row_cells = []
            for cell in cells:
                # Get text content and clean it up
                text = cell.get_text(separator=" ", strip=True)
                # Clean up common HTML entities and extra whitespace
                text = text.replace("\u00a0", " ")  # &nbsp;
                text = text.replace("±", "±")  # Fix encoding issues
                text = text.replace("−", "-")  # Fix minus signs
                text = " ".join(text.split())  # Normalize whitespace
                row_cells.append(text)
            table_data.append(row_cells)

        if not table_data:
            raise ValueError("No data found in table")

        # Extract activities
        activities = self._extract_activities(table_data, start_row, ignore_last)
        return activities

    def _extract_activities(
        self, table_data: List[List[str]], start_row: int, ignore_last: bool
    ) -> List[Dict]:
        """
        Extract parent and child activities from the table data.

        Args:
            table_data: List of rows
            start_row: Row to start processing from
            ignore_last: Ignore last column if true (usually notes or similar)

        Returns:
            List of activity dictionaries
        """
        activities = []
        current_parent = None

        for i in range(start_row, len(table_data)):
            row = table_data[i]
            if not row:
                continue

            activity_name = row[0].strip()
            if not activity_name:
                continue

            # Check if this row has "X" markers (indicating it's a child activity)
            has_x_markers = self._has_x_markers(row)

            if has_x_markers:
                # This is a child activity
                activity = {
                    "name": activity_name,
                    "index": i,
                    "visits": self._extract_visits_for_activity(row, ignore_last),
                }

                # Only include activities that have scheduled visits
                if activity["visits"]:
                    if current_parent:
                        if "children" not in current_parent:
                            current_parent["children"] = []
                        current_parent["children"].append(activity)
                    else:
                        # No parent, add as standalone activity
                        activities.append(activity)

            else:
                # This could be a parent activity (section header)
                current_parent = {"name": activity_name, "index": i, "children": []}
                activities.append(current_parent)

        # Clean up result - remove parents with no children and convert to appropriate format
        final_activities = []
        for item in activities:
            if "children" in item:
                # This is a parent
                if item["children"]:
                    final_activities.append(item)
            else:
                # This is a standalone activity
                final_activities.append(item)

        # If no parent-child relationships were found, return simple list
        if all("children" not in activity for activity in final_activities):
            return final_activities

        return final_activities

    def _has_x_markers(self, row: List[str]) -> bool:
        """
        Check if a row contains "X" markers indicating scheduled activities.

        Args:
            row: List of cell contents for the row

        Returns:
            True if row contains X markers
        """
        # Check all cells except first (activity name) and potentially last (protocol section)
        check_cells = row[1:-1] if len(row) > 2 else row[1:]
        return any(cell.strip().upper() == "X" for cell in check_cells if cell)

    def _extract_visits_for_activity(
        self, row: List[str], ignore_last: bool
    ) -> List[str]:
        """
        Extract which visits an activity is scheduled for based on X markers.

        Args:
            row: Row data containing X markers
            visit_headers: List of visit identifiers

        Returns:
            List of visit names where activity is scheduled
        """
        visits = []
        # Check each cell for X markers, mapping to visit headers
        last_col = len(row) - 1 if ignore_last else len(row)
        for j in range(1, last_col):
            if row[j].strip().upper() == "X":
                visits.append(j)
        return visits
