from raw_docx.raw_docx import RawDocx, RawTable, RawTableRow
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_cpt.import_.extract.soa_features.activity_row_feature import (
    ActivityRowFeature,
)
from usdm4_cpt.import_.extract.soa_features.notes_feature import NotesFeature
from usdm4_cpt.import_.extract.soa_features.epochs_feature import EpochsFeature
from usdm4_cpt.import_.extract.soa_features.visits_feature import VisitsFeature
from usdm4_cpt.import_.extract.soa_features.timepoints_feature import TimepointsFeature
from usdm4_cpt.import_.extract.soa_features.windows_feature import WindowsFeature
from usdm4_cpt.import_.extract.soa_features.activities_feature import ActivitiesFeature
# from usdm4_cpt.import_.extract.utility import test_filename


class SoA:
    MODULE = "usdm4_cpt.import_.soa.SoA"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        self._raw_docx = raw_docx
        self._errors = errors

    def process(self, id: str) -> dict | None:
        try:
            self._id = id
            section = self._raw_docx.target_document.section_by_title(
                "Schedule of Activities"
            )
            if section:
                soa_tables = self._merge_tables(section.tables())
                raw_result = self._decode_soa(soa_tables[0])
                final_result = self._format_results(raw_result)
            else:
                self._errors.error(
                    "Failed to find the SoA section in the document",
                    KlassMethodLocation(self.MODULE, "process"),
                )
                raw_result = None
                final_result = None
            return raw_result, final_result
        except Exception as e:
            self._errors.exception(
                "Error processing SoA", e, KlassMethodLocation(self.MODULE, "process")
            )

    def _decode_soa(self, soa_table: RawTable) -> dict:
        html = soa_table.to_html()
        result = {}
        result["activity_row"] = ActivityRowFeature().process(html)
        activity_row = result["activity_row"]["first_activity_row"]
        last_header_row = activity_row + 1
        self._errors.info(
            f"Activity Row: {result['activity_row']}",
            KlassMethodLocation(self.MODULE, "_decode_soa"),
        )
        result["notes"] = NotesFeature().process(html)
        ignore_last = result["notes"]["hasCommentsNotesOrReferences"]
        self._errors.info(
            f"Notes: {result['notes']}", KlassMethodLocation(self.MODULE, "_decode_soa")
        )
        result["epochs"] = EpochsFeature().process(html, ignore_last)
        self._errors.info(
            f"Epochs: {result['epochs']}",
            KlassMethodLocation(self.MODULE, "_decode_soa"),
        )
        result["visits"] = VisitsFeature().process(html, last_header_row)
        self._errors.info(
            f"Visits: {result['visits']}",
            KlassMethodLocation(self.MODULE, "_decode_soa"),
        )
        result["timepoints"] = TimepointsFeature().process(html, last_header_row)
        self._errors.info(
            f"Timepoints: {result['timepoints']}",
            KlassMethodLocation(self.MODULE, "_decode_soa"),
        )
        result["windows"] = WindowsFeature().process(html, last_header_row)
        self._errors.info(
            f"Windows: {result['windows']}",
            KlassMethodLocation(self.MODULE, "_decode_soa"),
        )
        result["activities"] = ActivitiesFeature().process(
            html, activity_row, ignore_last
        )
        self._errors.info(
            f"Activities: {result['activities']}",
            KlassMethodLocation(self.MODULE, "_decode_soa"),
        )
        return result

    def _merge_tables(self, tables: list[RawTable]) -> list[RawTable]:
        new_tables = []
        previous_table = None
        table: RawTable
        for index, table in enumerate(tables):
            if index > 0:
                matching, rows = self._matching_header(previous_table, table)
                if matching:
                    self._errors.info("Matching tables detected")
                    new_table = self._combine_tables(previous_table, table)
                    new_tables.append(new_table)
                else:
                    new_tables.append(table)
            else:
                new_tables.append(table)
            previous_table = table
        # self._dump_tables(new_tables, test_filename(self._id, ".html", "tables"))
        return new_tables

    def _combine_tables(
        self, first_table: RawTable, second_table: RawTable
    ) -> RawTable:
        self._errors.warning("Need to merge tables, but not yet implemented!")

    def _matching_header(self, first_table: RawTable, second_table: RawTable) -> bool:
        match_count = 0
        for index, row in enumerate(first_table.rows):
            other_row = second_table.rows[index]
            if self._matching_row(row, other_row):
                match_count += 1
            else:
                break
        return (True, match_count) if match_count >= 2 else (False, 0)

    def _matching_row(self, a: RawTableRow, b: RawTableRow) -> bool:
        result = True
        for index, cell in enumerate(a.cells):
            other_cell = b.cells[index]
            self._errors.debug(
                f"Cell comparison {cell.to_html()} === {other_cell.to_html()}"
            )
            if cell.to_html() != other_cell.to_html():
                result = False
                break
        self._errors.debug(f"Matching row result: {result}")
        return result

    # def _dump_tables(self, tables: list[RawTable], filename):
    #     html = ""
    #     for table in tables[0:1]:
    #         # html += table.to_html()
    #         html += self._table_to_html(table)
    #     self._save_html(html, filename)

    # def _save_html(self, contents, filename):
    #     try:
    #         with open(filename, "w", encoding="utf-8") as f:
    #             f.write(contents)
    #     except Exception as e:
    #         self._errors.exception(
    #             "Exception saving timeline file",
    #             e,
    #             KlassMethodLocation(self.MODULE, "_save_html"),
    #         )

    def _table_to_html(self, table: RawTable):
        lines = []
        open_tag = "<table>"
        lines.append(open_tag)
        for item in table.rows[0:12]:
            lines.append(item.to_html())
        lines.append("</table>")
        return ("\n").join(lines)

    def _format_results(self, results: dict):
        result = {
            "table-001": {
                "table_id": "table-001",
                "table_title": f"Schedule of Events for Protocol {self._id}",
                "activity_rows": self._format_activities(results),
                "annotations": {},  # Not used
                "grid_columns": self._format_visits(results),
                "schedule_columns_data": self._format_timepoints(results),
                "scheduled_activities": self._format_scheduled_activities(results),
                "grid_metadata": {},  # Not used
                "schedule_property_metadata": {},  # Not used
            }
        }
        # print(f"FORMATTED RESULTS: {result}")
        return result

    def _format_activities(self, results: dict) -> dict:
        formatted_results = {}
        index = 1
        for activity in results["activities"]:
            key = f"ar-{index:03d}"
            formatted_results[key] = {
                "table_id": "table-001",
                "activity_id": key,
                "activity_name": activity["name"],
                "parent_flag": "No",
                "annotation_markers": "",
            }
            index += 1
            if "children" in activity:
                for child in activity["children"]:
                    key = f"ar-{index:03d}"
                    formatted_results[key] = {
                        "table_id": "table-001",
                        "activity_id": key,
                        "activity_name": child["name"],
                        "parent_flag": "Yes",
                        "annotation_markers": "",
                    }
                    index += 1
        return formatted_results

    def _format_visits(self, results: dict) -> dict:
        formatted_results = {}
        index = 1
        if results["visits"]:
            for item in results["visits"]:
                key = f"sc-{index:03d}"
                formatted_results[key] = {
                    "table_id": "table-001",
                    "col_id": key,
                    "position": index,
                    "header_text": item,
                }
                index += 1
            return formatted_results
        else:
            for index, item in enumerate(results["timepoints"]):
                key = f"sc-{(index + 1):03d}"
                # window = results["windows"][index] # @todo
                formatted_results[key] = {
                    "table_id": "table-001",
                    "col_id": key,
                    "position": str(index + 1),
                    "header_text": f"{item['unit']} {item['value']}",
                }
            # print(f"THE FORMATTED RESULTS: {formatted_results}")
            return formatted_results

    def _format_timepoints(self, results: dict) -> dict:
        formatted_results = {}
        # print(f"RESULTS RAW: {results}")
        for index, item in enumerate(results["timepoints"]):
            key = f"sc-{(index + 1):03d}"
            # window = results["windows"][index] # @todo
            formatted_results[key] = {
                "table_id": "table-001",
                "col_id": key,
                "timepoint_reference": str(index + 1),
                "period": "",
                "temporal_value": f"{item['value']} {item['unit']}",
                "temporal_dict": item,
                "tolerance_window": "",
                # "tolerance_dict": window, # @todo
                "annotation_markers": "",
            }
        # print(f"THE FORMATTED RESULTS: {formatted_results}")
        return formatted_results

    def _format_scheduled_activities(self, results: dict) -> dict:
        formatted_results = {}
        item_index = 1
        for item in results["activities"]:
            # print(f"ITEM: {item}")
            key = f"ar-{item_index:03d}"
            if "children" in item:
                for child in item["children"]:
                    a_key = f"ar-{item_index:03d}"
                    for visit in child["visits"]:
                        v_key = f"sc-{visit:03d}"
                        formatted_results[key] = {
                            "table_id": "table-001",
                            "activity_id": a_key,
                            "col_id": v_key,
                            "marker": "X",
                            "activity_comment": "",
                            "annotation_markers": "",
                        }
                    item_index += 1
            else:
                a_key = f"ar-{item_index:03d}"
                for visit in item["visits"]:
                    v_key = f"sc-{visit:03d}"
                    formatted_results[key] = {
                        "table_id": "table-001",
                        "activity_id": a_key,
                        "col_id": v_key,
                        "marker": "X",
                        "activity_comment": "",
                        "annotation_markers": "",
                    }
                item_index += 1
        return formatted_results
