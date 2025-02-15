#!/usr/bin/env python3
"""
spreadsheet_builder.py

Refactored into a class-based approach for pipeline integration. This module
loads JSON files from a specified data directory, separates schools into
public/private, calculates scores, and writes two sheets (Public and Private)
into an Excel file named "School_Outreach_Contacts.xlsx".

Usage (standalone):
    python spreadsheet_builder.py

Usage (in a pipeline):
    from spreadsheet_builder import SpreadsheetBuilder
    builder = SpreadsheetBuilder(data_dir="data/schools_normalized_demo")
    builder.run()
"""

import os
import json
import pandas as pd
from pathlib import Path
from ndt_logger import initialize_logging

logger = initialize_logging()


class SpreadsheetBuilder:
    def __init__(self,
                 data_dir: str = "data/schools_normalized_demo",
                 output_file: str = "data/School_Outreach_Contacts.xlsx"):
        """
        :param data_dir: Directory where JSON files exist.
        :param output_file: Name (or path) of the output Excel file.
        """
        self.data_dir = Path(data_dir)
        self.output_file = output_file

        # Define columns for public/private schools
        self.public_columns = [
            "School ID", "School Name", "Address", "Phone Number", "Email Address",
            "Enrollment", "Black Population Ratio", "Composite Score",
            "Contact Person", "Email Sent?", "Last Contact Date", "Next Follow-Up",
            "Call Log / Notes", "Campaign Status", "Additional Comments"
        ]
        self.private_columns = [
            "School ID", "School Name", "Address", "Phone Number", "Email Address",
            "Black Population Ratio", "Ranking Score",
            "Contact Person", "Email Sent?", "Last Contact Date", "Next Follow-Up",
            "Call Log / Notes", "Campaign Status", "Additional Comments"
        ]

    def run(self):
        """
        Main entry point to load JSON files, segregate public vs. private,
        calculate scores, and export to an Excel spreadsheet.
        """
        logger.info("Starting SpreadsheetBuilder...")
        logger.info(f"Loading JSON files from: {self.data_dir}")

        schools = self._load_json_files()
        if not schools:
            raise ValueError(f"No valid school data found in {self.data_dir}")

        public_schools, private_schools = self._separate_public_private(schools)
        public_schools_sorted = self._process_public_schools(public_schools)
        private_schools_sorted = self._process_private_schools(private_schools)

        # Build DataFrames and output Excel
        public_df = self._build_public_df(public_schools_sorted)
        private_df = self._build_private_df(private_schools_sorted)

        logger.info(f"Writing final spreadsheet to: {self.output_file}")
        with pd.ExcelWriter(self.output_file, engine="openpyxl") as writer:
            public_df.to_excel(writer, sheet_name="Public Schools", index=False)
            private_df.to_excel(writer, sheet_name="Private Schools", index=False)

        logger.info(f"Spreadsheet created successfully: {self.output_file}")

    def _load_json_files(self):
        """
        Load JSON files from the data_dir and return a list of school dicts.
        """
        schools = []
        for filename in os.listdir(self.data_dir):
            if filename.endswith(".json"):
                filepath = self.data_dir / filename
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        # Safely convert fields
                        data["Enrollment"] = self._safe_int(data.get("Enrollment", 0))
                        data["Black Population Ratio"] = self._safe_float(data.get("Black Population Ratio", 0))
                        schools.append(data)
                except Exception as e:
                    logger.error(f"Error reading JSON file '{filepath}': {e}")
        return schools

    def _separate_public_private(self, schools):
        """
        Separate schools into public vs. private based on the 'Public School' field.
        """
        public_schools = []
        private_schools = []
        for school in schools:
            # Case-insensitive check for "yes"
            if str(school.get("Public School", "")).strip().lower() == "yes":
                public_schools.append(school)
            else:
                private_schools.append(school)
        return public_schools, private_schools

    def _process_public_schools(self, public_schools):
        """
        For public schools, compute a Composite Score = 0.5*(normalized enrollment) + 0.5*(black_ratio).
        Then sort them descending by Composite Score.
        """
        if not public_schools:
            return []

        max_enrollment_public = max(school["Enrollment"] for school in public_schools)
        if max_enrollment_public == 0:
            raise ValueError("Max enrollment among public schools is zero; cannot perform normalization.")

        for school in public_schools:
            enrollment_norm = school["Enrollment"] / max_enrollment_public if max_enrollment_public else 0
            black_ratio = school.get("Black Population Ratio", 0)
            school["Composite Score"] = 0.5 * enrollment_norm + 0.5 * black_ratio

        public_schools_sorted = sorted(public_schools,
                                       key=lambda s: s["Composite Score"],
                                       reverse=True)
        return public_schools_sorted

    def _process_private_schools(self, private_schools):
        """
        For private schools, simply use the 'Black Population Ratio' as the ranking score.
        Then sort them descending by that score.
        """
        for school in private_schools:
            school["Ranking Score"] = school.get("Black Population Ratio", 0)
        private_schools_sorted = sorted(private_schools,
                                        key=lambda s: s["Ranking Score"],
                                        reverse=True)
        return private_schools_sorted

    def _build_public_df(self, public_schools):
        """
        Build a Pandas DataFrame for public schools with the columns in self.public_columns.
        """
        data_dicts = [self._build_public_dict(school) for school in public_schools]
        return pd.DataFrame(data_dicts, columns=self.public_columns)

    def _build_private_df(self, private_schools):
        """
        Build a Pandas DataFrame for private schools with the columns in self.private_columns.
        """
        data_dicts = [self._build_private_dict(school) for school in private_schools]
        return pd.DataFrame(data_dicts, columns=self.private_columns)

    def _build_public_dict(self, school):
        """
        Create a dict for each public school row in the final spreadsheet.
        """
        return {
            "School ID": school.get("CDS Code", ""),
            "School Name": school.get("School", ""),
            "Address": school.get("Full Address", ""),
            "Phone Number": school.get("Phone Number", ""),
            "Email Address": self._get_admin_email(school),
            "Enrollment": school["Enrollment"],
            "Black Population Ratio": school["Black Population Ratio"],
            "Composite Score": school.get("Composite Score", 0),
            "Contact Person": self._get_admin_name(school),
            "Email Sent?": "",
            "Last Contact Date": "",
            "Next Follow-Up": "",
            "Call Log / Notes": "",
            "Campaign Status": "",
            "Additional Comments": ""
        }

    def _build_private_dict(self, school):
        """
        Create a dict for each private school row in the final spreadsheet.
        """
        return {
            "School ID": school.get("CDS Code", ""),
            "School Name": school.get("School", ""),
            "Address": school.get("Full Address", ""),
            "Phone Number": school.get("Phone Number", ""),
            "Email Address": self._get_admin_email(school),
            "Black Population Ratio": school["Black Population Ratio"],
            "Ranking Score": school.get("Ranking Score", 0),
            "Contact Person": self._get_admin_name(school),
            "Email Sent?": "",
            "Last Contact Date": "",
            "Next Follow-Up": "",
            "Call Log / Notes": "",
            "Campaign Status": "",
            "Additional Comments": ""
        }

    @staticmethod
    def _safe_int(value, default=0):
        """Attempt to convert value to int; if it fails, return default."""
        try:
            return int(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _safe_float(value, default=0.0):
        """Attempt to convert value to float; if it fails, return default."""
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def _get_admin_name(school):
        """
        Return the first administrator's name and position from the Administrators key.
        """
        admins = school.get("Administrators", [])
        if admins and isinstance(admins, list):
            return admins[0].get("Name & Position", "")
        return ""

    @staticmethod
    def _get_admin_email(school):
        """
        Return the first administrator's email from the Administrators key.
        """
        admins = school.get("Administrators", [])
        if admins and isinstance(admins, list):
            return admins[0].get("Email", "")
        return ""


# ----------------------------------------------------------------------------
# Standalone Execution
# ----------------------------------------------------------------------------
def main():
    builder = SpreadsheetBuilder(
        data_dir="data/schools_normalized_demo",
        output_file="data/School_Outreach_Contacts.xlsx"
    )
    builder.run()

if __name__ == "__main__":
    main()