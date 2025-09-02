from bs4 import BeautifulSoup


class ActivityRowFeature:
    def process(self, html_content, verbose=False):
        """
        Enhanced version that provides detailed analysis of the table structure.

        Args:
            html_content (str): HTML content containing table structure
            verbose (bool): If True, prints detailed information about each row

        Returns:
            dict: Analysis results including first_x_row, total_rows, and row_details
        """
        soup = BeautifulSoup(html_content, "html.parser")
        tables = soup.find_all("table")

        if not tables:
            return {"error": "No tables found", "first_activity_row": -1}

        table = tables[0]
        rows = table.find_all("tr")

        result = {"first_activity_row": -1, "total_rows": len(rows)}

        for row_index, row in enumerate(rows, start=1):
            cells = row.find_all(["td", "th"])
            cell_contents = [cell.get_text(strip=True) for cell in cells]

            # Check for single "X" cells
            single_x_cells = [content for content in cell_contents if content == "X"]
            has_single_x = len(single_x_cells) > 0

            # Set first_x_row if not already set and this row has single X
            if result["first_activity_row"] == -1 and has_single_x:
                result["first_activity_row"] = row_index

        return result
