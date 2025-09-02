import re
from bs4 import BeautifulSoup
from typing import Dict, List, Any


class NotesFeature:
    def process(self, html_content: str) -> Dict[str, Any]:
        """
        Analyze the last column of a Schedule of Activities (SoA) table to determine
        if it contains comments, notes, or references to document sections.

        Args:
            html_content (str): HTML content containing the SoA table

        Returns:
            Dict[str, Any]: JSON structure with analysis results
        """

        # Parse HTML content
        soup = BeautifulSoup(html_content, "html.parser")

        # Find all tables with the SoA class
        tables = soup.find_all("table", class_="ich-m11-table")

        if not tables:
            return {
                "hasCommentsNotesOrReferences": False,
                "contentType": "No Table Found",
                "description": "No table with class 'ich-m11-table' found in the HTML content",
                "lastColumnContent": [],
            }

        # Process the first/main table
        table = tables[0]
        rows = table.find_all("tr")

        if not rows:
            return {
                "hasCommentsNotesOrReferences": False,
                "contentType": "Empty Table",
                "description": "Table found but contains no rows",
                "lastColumnContent": [],
            }

        last_column_content = []

        # Extract content from the last column of each row
        for index, row in enumerate(rows):
            cells = row.find_all(["td", "th"])

            if cells:
                # Get the last cell in the row
                last_cell = cells[-1]

                # Extract text content, handling nested <p> tags
                cell_text = ""
                paragraphs = last_cell.find_all("p")
                if paragraphs:
                    # Join text from all paragraphs in the cell
                    cell_text = " ".join([p.get_text(strip=True) for p in paragraphs])
                else:
                    cell_text = last_cell.get_text(strip=True)

                last_column_content.append({"text": cell_text, "index": index})
            else:
                # Empty row
                last_column_content.append({"text": "", "index": index})

        # Analyze the content to determine type and characteristics
        content_analysis = self._analyze_content_type(last_column_content)

        return {
            "hasCommentsNotesOrReferences": content_analysis["has_references"],
            "contentType": content_analysis["content_type"],
            "description": content_analysis["description"],
            "lastColumnContent": last_column_content,
        }

    def _analyze_content_type(self, content_list: List[str]) -> Dict[str, Any]:
        """
        Analyze the content of the last column to determine its type and characteristics.

        Args:
            content_list (List[str]): List of strings from the last column

        Returns:
            Dict[str, Any]: Analysis results
        """

        # Remove empty strings for analysis
        non_empty_content = [
            item["text"] for item in content_list if item["text"].strip()
        ]

        if not non_empty_content:
            return {
                "has_references": False,
                "content_type": "Empty Column",
                "description": "The last column contains no content",
            }

        # Count different types of content
        section_references = 0
        protocol_references = 0
        notes_comments = 0
        other_content = 0

        # Patterns to identify different content types
        section_pattern = re.compile(r"section\s+\d+(\.\d+)*", re.IGNORECASE)
        protocol_pattern = re.compile(r"protocol|procedure|guideline", re.IGNORECASE)
        note_comment_patterns = [
            re.compile(r"note[:;]?", re.IGNORECASE),
            re.compile(r"comment[:;]?", re.IGNORECASE),
            re.compile(r"remark[:;]?", re.IGNORECASE),
            re.compile(r"see\s+", re.IGNORECASE),
            re.compile(r"refer\s+", re.IGNORECASE),
        ]

        for item in non_empty_content:
            item_lower = item.lower()

            if section_pattern.search(item):
                section_references += 1
            elif protocol_pattern.search(item):
                protocol_references += 1
            elif any(pattern.search(item) for pattern in note_comment_patterns):
                notes_comments += 1
            elif item_lower not in [
                "applicable protocol sections",
                "references",
                "notes",
                "comments",
            ]:
                # Skip common headers
                other_content += 1

        # Determine content type based on analysis
        total_analyzed = len(non_empty_content) - 1  # Exclude likely header

        if section_references > 0 and section_references >= total_analyzed * 0.5:
            return {
                "has_references": True,
                "content_type": "Protocol Section References",
                "description": "References to specific sections of the clinical trial protocol document that provide detailed information about each study activity",
            }
        elif protocol_references > 0:
            return {
                "has_references": True,
                "content_type": "Protocol References",
                "description": "References to protocol documents or procedures",
            }
        elif notes_comments > 0:
            return {
                "has_references": True,
                "content_type": "Notes and Comments",
                "description": "Additional notes, comments, or explanatory text for study activities",
            }
        elif other_content > 0:
            return {
                "has_references": True,
                "content_type": "Mixed Content",
                "description": "Contains various types of supplementary information",
            }
        else:
            return {
                "has_references": False,
                "content_type": "Header Only",
                "description": "Column appears to contain only header information",
            }
