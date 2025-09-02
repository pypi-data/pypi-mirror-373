import re
import dateutil.parser as parser
from raw_docx.raw_docx import RawDocx, RawTable
from usdm4_m11.import_.extract.utility import table_get_row
from simple_error_log.errors import Errors
from simple_error_log.error_location import KlassMethodLocation


class TitlePage:
    MODULE = "usdm4_m11.import_.title_page.TitlePage"

    def __init__(self, raw_docx: RawDocx, errors: Errors):
        self._raw_docx = raw_docx
        self._sections = self._raw_docx.target_document.sections
        self._errors = errors

    def process(self):
        table: RawTable = self._title_table()
        if table:
            table.replace_class("ich-m11-table", "ich-m11-title-page-table")
            address = table_get_row(table, "Legal Registered Address")
            sponsor = table_get_row(table, "Sponsor Name")
            acronym = table_get_row(table, "Acronym")
            identifier = table_get_row(table, "Sponsor Protocol Identifier")
            compund_code = table_get_row(table, "Compound Code")
            result = {
                "identification": {
                    "titles": {
                        "official": table_get_row(table, "Full Title"),
                        "acronym": acronym,
                        "brief": table_get_row(table, "Short Title"),
                    },
                    "identifiers": [
                        {
                            "identifier": identifier,
                            "scope": {
                                "non_standard": {
                                    "type": "pharma",
                                    "description": "The sponsor organization",
                                    "label": sponsor,
                                    "identifier": "UNKNOWN",
                                    "identifierScheme": "UNKNOWN",
                                    "legalAddress": self._get_sponsor_address_simple(
                                        address
                                    ),
                                }
                            },
                        }
                    ],
                },
                "compounds": {
                    "compound_codes": compund_code,
                    "compound_names": table_get_row(table, "Compound Name"),
                },
                "amendments": {
                    "amendment_identifier": table_get_row(
                        table, "Amendment Identifier"
                    ),
                    "amendment_scope": table_get_row(table, "Amendment Scope"),
                    "amendment_details": table_get_row(table, "Amendment Details"),
                },
                "study_design": {
                    "label": "Study Design 1",
                    "rationale": "Not set",
                    "trial_phase": table_get_row(table, "Trial Phase"),
                },
                "study": {
                    "sponsor_approval_date": self._get_sponsor_approval_date(table),
                    "version_date": self._get_protocol_date(table),
                    "version": table_get_row(table, "Version Number"),
                    "rationale": "Not set",
                    "name": {
                        "acronym": acronym,
                        "identifier": identifier,
                        "compound_code": compund_code,
                    },
                },
                "other": {
                    "confidentiality": table_get_row(table, "Sponsor Confidentiality"),
                    "regulatory_agency_identifiers": table_get_row(
                        table, "Regulatory Agency Identifier Number(s)"
                    ),
                },
                # self.manufacturer_name_and_address = table_get_row(table, "Manufacturer")
                # self.sponsor_signatory = table_get_row(table, "Sponsor Signatory")
                # self.medical_expert_contact = table_get_row(table, "Medical Expert")
                # self.sae_reporting_method = table_get_row(table, "SAE Reporting")
            }
            return result
        else:
            location = KlassMethodLocation(self.MODULE, "process")
            self._errors.error(
                "Failed to find the title page table in the document", location
            )
            return None

    # def _extra_data(self, table: RawTable) -> None:
    #     self._extra = {
    #         "original_protocol": table_get_row(table, "Original Protocol"),
    #         "regulatory_agency_identifiers": table_get_row(
    #             table, "Regulatory Agency Identifier Number(s)"
    #         ),
    #         "manufacturer_name_and_address": table_get_row(table, "Manufacturer"),
    #         "sponsor_signatory": table_get_row(table, "Sponsor Signatory"),
    #         "medical_expert_contact": table_get_row(table, "Medical Expert"),
    #         "sae_reporting_method": table_get_row(table, "SAE Reporting"),
    #         "sponsor_approval_date": self._get_sponsor_approval_date(table),
    #     }

    def _get_sponsor_address_simple(self, text: str) -> dict:
        """Simplified version of _get_sponsor_name_and_address without using the address service"""
        raw_parts = text.split("\n") if text else []
        params = {
            "lines": [],
            "city": "",
            "district": "",
            "state": "",
            "postalCode": "",
            "country": "",
        }
        parts = []
        for part in raw_parts:
            if not part.upper().startswith(("TEL", "FAX", "PHONE", "EMAIL")):
                parts.append(part)
        if len(parts) > 0:
            params["lines"] = [part.strip() for part in parts[1:]]
            if len(parts) > 2:
                params["country"] = parts[-1].strip()
        self._errors.info(
            f"Address result '{params}'",
            location=KlassMethodLocation(self.MODULE, "_get_sponsor_address_simple"),
        )
        return params

    def _get_sponsor_approval_date(self, table):
        return self._get_date(table, "Sponsor Approval Date")

    def _get_protocol_date(self, table):
        return self._get_date(table, "Version Date")

    def _get_date(self, table, text):
        try:
            date_text = table_get_row(table, text)
            if date_text:
                date = parser.parse(date_text)
                return date
            else:
                return None
        except Exception as e:
            location = KlassMethodLocation(self.MODULE, "_get_date")
            self._errors.exception(
                f"Exception raised during date processing for '{text}'", e, location
            )
            return None

    def _title_table(self):
        section = self._sections[0]
        for table in section.tables():
            title = table_get_row(table, "Protocol Title")
            if title:
                self._errors.info(
                    "Found CPT title page table",
                    location=KlassMethodLocation(self.MODULE, "_title_table"),
                )
                return table
        self._errors.warning(
            "Cannot locate CPT title page table!",
            location=KlassMethodLocation(self.MODULE, "_title_table"),
        )
        return None

    def _preserve_original(self, original_parts, value):
        for part in original_parts:
            for item in re.split(r"[,\s]+", part):
                if item.upper() == value.upper():
                    return item
        return value

    def extra(self):
        return {
            "sponsor_confidentiality": self.sponosr_confidentiality,
            "compound_codes": self.compound_codes,
            "compound_names": self.compound_names,
            "amendment_identifier": self.amendment_identifier,
            "amendment_scope": self.amendment_scope,
            "amendment_details": self.amendment_details,
            "sponsor_name_and_address": self.sponsor_name_and_address,
            "original_protocol": self.original_protocol,
            "regulatory_agency_identifiers": self.regulatory_agency_identifiers,
            "manufacturer_name_and_address": self.manufacturer_name_and_address,
            "sponsor_signatory": self.sponsor_signatory,
            "medical_expert_contact": self.medical_expert_contact,
            "sae_reporting_method": self.sae_reporting_method,
            "sponsor_approval_date": self.sponsor_approval_date,
        }

    def _get_sponsor_name_and_address_simple(self):
        """Simplified version of _get_sponsor_name_and_address without using the address service"""
        name = "[Sponsor Name]"
        parts = (
            self.sponsor_name_and_address.split("\n")
            if self.sponsor_name_and_address
            else []
        )
        params = {
            "lines": [],
            "city": "",
            "district": "",
            "state": "",
            "postalCode": "",
            "country": None,
        }
        if len(parts) > 0:
            name = parts[0].strip()
            self._errors.info(f"Sponsor name set to '{name}'")
        if len(parts) > 1:
            # Simple address parsing - just store the address lines
            params["lines"] = [part.strip() for part in parts[1:]]
            # Try to extract country from the last line
            if len(parts) > 2:
                last_line = parts[-1].strip()
                country_code = self._builder.iso3166_code(last_line)
                if country_code:
                    params["country"] = country_code

        self._errors.info(f"Name and address result '{name}', '{params}'")
        return name, params

    def _get_sponsor_approval_date(self, table: RawTable) -> str:
        return self._get_date(table, "Sponsor Approval")

    def _get_protocol_date(self, table):
        return self._get_date(table, "Version Date")

    def _get_date(self, table: RawTable, header_text: str) -> str:
        try:
            date_text = table_get_row(table, header_text)
            if date_text:
                return date_text.strip()
            else:
                return ""
        except Exception as e:
            data = date_text if date_text else ""
            self._errors.exception(
                f"Exception raised during date processing for '{data}'",
                e,
                KlassMethodLocation(self.MODULE, "_get_date"),
            )
            return ""

    def _title_table(self):
        section = self._sections[0]
        for table in section.tables():
            title = table_get_row(table, "Full Title")
            if title:
                self._errors.info(
                    "Found M11 title page table",
                    location=KlassMethodLocation(self.MODULE, "_title_table"),
                )
                return table
        self._errors.warning(
            "Cannot locate M11 title page table!",
            location=KlassMethodLocation(self.MODULE, "_title_table"),
        )
        return None

    def _preserve_original(self, original_parts, value):
        for part in original_parts:
            for item in re.split(r"[,\s]+", part):
                if item.upper() == value.upper():
                    return item
        return value
