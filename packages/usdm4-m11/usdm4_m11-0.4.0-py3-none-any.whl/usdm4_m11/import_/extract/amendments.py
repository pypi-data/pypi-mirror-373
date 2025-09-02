import re
from raw_docx.raw_docx import RawDocx, RawTable, RawSection, RawParagraph, RawTableRow
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation
from usdm4_m11.import_.extract.utility import (
    table_get_row,
    table_get_row_html,
    text_within,
)


class Amendments:
    MODULE = "usdm4_m11.import_.amendments.Amendments"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        self._errors = errors
        self._raw_docx = raw_docx

    def process(self):
        try:
            result = None
            section = self._raw_docx.target_document.section_by_ordinal(1)
            amend_item, amend_index = section.find_first_at_start("Amendment Details")
            table, table_index = self._amendment_table(section)
            if amend_item and table:
                result = {}
                result["amendment_details"] = section.to_html_between(
                    amend_index, table_index
                )
            if table:
                result = result if result else {}
                result["enrollment"] = self._enrollment(table)
                result["reasons"] = self._reasons(table)
                result["summary"] = self._summary(table)
                result["impact"] = self._safety_and_reliability_impact(table)
                result["changes"] = self._changes()
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "process")
            self._errors.exception(
                "Failed to extract amendment information", e, location
            )
            return None

    def _safety_and_reliability_impact(self, table: RawTable) -> dict:
        try:
            return {
                "safety": self._safety_impact(table),
                "reliability": self._reliability_impact(table),
            }
        except Exception as e:
            location = KlassMethodLocation(
                self.MODULE, "_safety_and_reliability_impact"
            )
            self._errors.exception(
                "Failed to decode the safety and reliability impact", e, location
            )
            return None

    def _safety_impact(self, table: RawTable) -> dict:
        try:
            result = self._impact(
                table,
                "Is this amendment likely to have a substantial impact on the safety",
            )
            self._errors.info(f"Safety impact: {result}")
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_safety impact")
            self._errors.exception("Failed to decode the safety impact", e, location)
            return None

    def _reliability_impact(self, table: RawTable) -> dict:
        try:
            result = self._impact(
                table,
                "Is this amendment likely to have a substantial impact on the reliability",
            )
            self._errors.info(f"Reliability impact: {result}")
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_reliability_impact")
            self._errors.exception(
                "Failed to decode the reliability impact", e, location
            )
            return None

    def _summary(self, table: RawTable) -> dict:
        try:
            result = table_get_row_html(table, "Amendment Summary")
            if result:
                self._errors.info("Amendment summary found")
            return result
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_summary")
            self._errors.exception(
                "Failed to decode the amendment summary", e, location
            )
            return None

    def _impact(self, table: RawTable, text: str) -> dict:
        try:
            impact = False
            reason = ""
            row, index = table.find_row(text)
            if row:
                cell = row.cells[1]
                impact = cell.text().upper().startswith("YES")
                if impact:
                    reason = cell.to_html()
            return {"impact": impact, "reason": reason}
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_impact")
            self._errors.exception("Failed to decode the imaoct", e, location)
            return None

    def _reasons(self, table: RawTable) -> dict | None:
        try:
            row: RawTableRow
            row, _ = table.find_row("Reason(s) for Amendment:")
            if row:
                return {
                    "primary": row.find_cell("primary").text(),
                    "secondary": row.find_cell("secondary").text(),
                }
            else:
                return None
        except Exception:
            location = KlassMethodLocation(self.MODULE, "_reasons")
            self._errors.exception("Failed to decode the amendment reasons", location)
            return None

    def _changes(self) -> list[dict] | None:
        try:
            results = []
            table = self._changes_table()
            if table:
                for index, row in enumerate(table.rows):
                    if index == 0:
                        continue
                    results.append(
                        {
                            "description": row.cells[0].text(),
                            "rationale": row.cells[1].text(),
                            "section": row.cells[2].text(),
                        }
                    )
            return results
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_changes")
            self._errors.exception(
                "Failed to decode the amendment changes", e, location
            )
            return None

    def _amendment_table(self, section: RawSection):
        try:
            for index, item in enumerate(section.items):
                if isinstance(item, RawParagraph):
                    if text_within(
                        "The table below describes the current amendment", item.text
                    ):
                        table = section.next_table(index + 1)
                        self._errors.info(
                            f"Amendment table {'' if table else 'not '} found"
                        )
                        return table, index
            return None, -1
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_amendment_table")
            self._errors.exception("Failed to find the amendment table", e, location)
            return None, -1

    def _changes_table(self) -> RawTable | None:
        try:
            section = self._raw_docx.target_document.section_by_ordinal(1)
            for index, item in enumerate(section.items):
                if isinstance(item, RawParagraph):
                    if text_within(
                        "Overview of Changes in the Current Amendment", item.text
                    ):
                        table = section.next_table(index + 1)
                        self._errors.info(
                            f"Changes table {'' if table else 'not '}found"
                        )
                        return table
            return None
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_changes_table")
            self._errors.exception("Failed to find the changes table", e, location)
            return None

    def _enrollment(self, table):
        try:
            text = table_get_row(table, "Enrolled at time ")
            number = re.findall("[0-9]+", text)
            value = int(number[0]) if number else 0
            unit = "%" if "%" in text else ""
            return {"value": value, "unit": unit}
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_enrollment")
            self._errors.exception("Failed to find the enrollment", e, location)
            return None
