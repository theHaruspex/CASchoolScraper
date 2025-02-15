#!/usr/bin/env python3
"""
normalizer.py

Refactored into a class-based approach for easier import into pipeline.py.
This module normalizes raw school JSON files by cleaning text fields,
parsing addresses, extracting administrator info, and saving
the results in a new directory.

Usage (standalone):
    python normalizer.py

Usage (in a pipeline):
    from normalizer import SchoolDataNormalizer
    normalizer = SchoolDataNormalizer(
        input_dir="data/schools_incremental",
        output_dir="data/schools_normalized"
    )
    normalizer.run()
"""

import json
import re
import usaddress
from pathlib import Path

from ndt_logger import initialize_logging
logger = initialize_logging()


class SchoolDataNormalizer:
    def __init__(self,
                 input_dir: str = "data/schools_incremental",
                 output_dir: str = "data/schools_normalized"):
        """
        :param input_dir: Directory with raw JSON files to normalize.
        :param output_dir: Directory to store the normalized JSON files.
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        # Ensure the output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """
        Main entry point to process all JSON files in self.input_dir,
        normalize them, and save them in self.output_dir.
        """
        logger.info(f"Normalizer started. Reading from: {self.input_dir}")
        logger.info(f"Output will be saved to: {self.output_dir}")

        for json_file in self.input_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    raw_data = json.load(f)
            except Exception as e:
                logger.error(f"Error reading {json_file}: {e}")
                continue

            # Normalize data
            normalized_data = self.normalize_school_data(raw_data)

            # Write output
            output_file = self.output_dir / json_file.name
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(normalized_data, f, indent=4)
                logger.info(f"Processed and saved: {output_file}")
            except Exception as e:
                logger.error(f"Error writing {output_file}: {e}")

        logger.info("Normalizer completed successfully.")

    def normalize_school_data(self, raw_data: dict) -> dict:
        """
        Given a single school's raw data, return a normalized dictionary.
        """
        norm = {}

        # Normalize basic fields using common key options.
        norm["CDS Code"] = self.get_value(raw_data, ['cds_code', 'CDS Code'])
        if norm["CDS Code"]:
            norm["CDS Code"] = norm["CDS Code"].replace(" ", "")

        norm["County"] = self.get_value(raw_data, ['county', 'County'])
        norm["District"] = self.get_value(raw_data, ['district', 'District'])
        norm["School"] = self.get_value(raw_data, ['school', 'School'])
        norm["School Type"] = self.get_value(raw_data, ['school_type', 'School Type'])
        norm["Sector Type"] = self.get_value(raw_data, ['sector_type'])
        norm["Charter School"] = self.get_value(raw_data, ['charter', 'Charter School'])
        norm["Status"] = self.get_value(raw_data, ['status', 'Status'])
        norm["Open Date"] = self.get_value(raw_data, ['Open Date'])
        norm["Educational Program Type"] = self.get_value(raw_data, ['Educational Program Type'])

        # Low and High Grades: try to convert to int if possible
        low_grade = self.get_value(raw_data, ['Low Grade'])
        high_grade = self.get_value(raw_data, ['High Grade'])
        norm["Low Grade"] = self.try_int(low_grade)
        norm["High Grade"] = self.try_int(high_grade)

        norm["Public School"] = self.get_value(raw_data, ['Public School'])
        norm["Charter Number"] = self.get_value(raw_data, ['Charter Number'])
        norm["Charter Funding Type"] = self.get_value(raw_data, ['Charter Funding Type'])
        norm["Magnet School"] = self.get_value(raw_data, ['Magnet', 'Magnet School'])
        norm["Year Round"] = self.get_value(raw_data, ['Year Round'])
        norm["Virtual Instruction"] = self.get_value(raw_data, ['Virtual Instruction'])
        norm["Multilingual Instruction"] = self.get_value(raw_data, ['Multilingual Instruction'])
        norm["Federal Charter District ID"] = self.get_value(raw_data, ['Federal Charter District ID'])
        norm["NCES Federal School ID"] = self.get_value(raw_data, ['NCES/Federal School ID'])

        # Enrollment: convert to int if possible
        enrollment = self.get_value(raw_data, ['Enrollment'])
        norm["Enrollment"] = self.try_int(enrollment)

        # English Language Learners
        ell_value = self.get_value(raw_data, ['English Language Learners'])
        norm["English Language Learners"] = self.parse_english_language_learners(ell_value)

        # Address fields: clean full address and then break it out.
        full_addr = self.get_value(raw_data, ['School Address', 'Address'])
        full_addr = self.clean_text(full_addr)
        norm["Full Address"] = full_addr

        (street_address,
         address_line_2,
         city,
         state,
         zip_code) = self.extract_address_components(full_addr)

        norm["Street Address"] = street_address
        norm["Address Line 2"] = address_line_2
        norm["City"] = city
        norm["State"] = state
        norm["Zip Code"] = zip_code

        # Mailing Address
        mailing_addr = self.get_value(raw_data, ['Mailing Address'])
        norm["Mailing Address"] = self.clean_text(mailing_addr)

        # Contact info
        norm["Phone Number"] = self.get_value(raw_data, ['Phone Number', 'Phone'])
        norm["Fax Number"] = self.get_value(raw_data, ['Fax Number'])
        email_val = self.get_value(raw_data, ['Email'])
        norm["Email"] = self.clean_text(email_val) if email_val else ""

        # Web Address
        web_addr = self.get_value(raw_data, ['Web Address', 'Web site*'])
        norm["Web Address"] = self.clean_text(web_addr)

        # Administrators
        admin_str = self.get_value(raw_data, ['Administrator'])
        norm["Administrators"] = self.parse_administrators(admin_str)

        # CDS Coordinator
        coord_str = self.get_value(raw_data, ['CDS Coordinator (Contact for Data Updates)'])
        norm["CDS Coordinator"] = self.parse_cds_coordinator(coord_str)

        norm["Last Updated"] = self.get_value(raw_data, ['Last Updated'])

        return norm

    # -------------------------
    # HELPER METHODS
    # -------------------------
    @staticmethod
    def clean_text(text: str) -> str:
        """Remove extraneous phrases from text."""
        if not text:
            return ""
        removals = [
            r'Link opens new browser tab',
            r'Google Map(?: Link)?',
            r'Link opens new Email'
        ]
        for pattern in removals:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text.strip()

    @staticmethod
    def parse_english_language_learners(value):
        """If value matches '43 (19.3 %)', extract count and percentage."""
        if not value:
            return value
        match = re.search(r'(\d+)\s*\(\s*([\d.]+)', str(value))
        if match:
            count = int(match.group(1))
            percentage = float(match.group(2))
            return {"Count": count, "Percentage": percentage}
        return value

    @staticmethod
    def parse_administrators(admin_str: str):
        """
        Parse the Administrator field into a list of dicts, capturing email addresses.
        """
        admins = []
        if not admin_str:
            return admins

        admin_str = SchoolDataNormalizer.clean_text(admin_str)
        email_pattern = r'(\S+@\S+)'
        # Split by email addresses (capturing them)
        parts = re.split(email_pattern, admin_str)
        # parts like: [text_before, email, text_between, email, ...]

        for i in range(1, len(parts), 2):
            email = parts[i].strip()
            text_before = parts[i - 1].strip()
            phone_match = re.search(r'\(\d{3}\)\s*\d{3}-\d{4}', text_before)
            phone = phone_match.group(0) if phone_match else ""
            if phone:
                text_before = text_before.replace(phone, "").strip()
            # Remove stray tokens like an isolated "0"
            tokens = text_before.split()
            tokens = [tok for tok in tokens if tok != "0"]
            name_pos = " ".join(tokens).strip()
            admins.append({
                "Name & Position": name_pos,
                "Phone": phone,
                "Email": email
            })
        return admins

    @staticmethod
    def parse_cds_coordinator(coord_str: str):
        """
        Parse the CDS Coordinator field for name and phone.
        e.g.: "Abraham Zamora (510) 670-4131 Request Data Update(s)"
        """
        if not coord_str:
            return {}
        coord_str = SchoolDataNormalizer.clean_text(coord_str)
        phone_pattern = r'\(\d{3}\)\s*\d{3}-\d{4}'
        phone_match = re.search(phone_pattern, coord_str)
        phone = phone_match.group(0) if phone_match else ""
        if phone_match:
            name = coord_str[:phone_match.start()].strip()
        else:
            name = coord_str
        return {"Name": name, "Phone": phone}

    @staticmethod
    def split_street_city(street_city_str: str):
        """
        Attempt to split a string containing street + city
        using known street delimiters (St, Ave, Blvd, etc.).
        """
        if not street_city_str:
            return "", ""
        delimiters = {
            "st", "ave", "blvd", "rd", "dr", "ln", "way",
            "ct", "pl", "cir", "terr", "loop", "hwy", "pkwy"
        }
        tokens = street_city_str.split()
        last_delim_index = -1
        for i, token in enumerate(tokens):
            token_clean = token.rstrip(".,").lower()
            if token_clean in delimiters:
                last_delim_index = i
        if last_delim_index != -1 and last_delim_index < len(tokens) - 1:
            street = " ".join(tokens[:last_delim_index + 1])
            city = " ".join(tokens[last_delim_index + 1:])
        else:
            street = street_city_str
            city = ""
        return street, city

    @staticmethod
    def extract_address_components(address_str: str):
        """
        Uses usaddress to parse street addresses and extract their components.
        Returns (street_address, address_line_2, city, state, zip_code).
        """
        if not address_str:
            return "", "", "", "", ""

        address_str = SchoolDataNormalizer.clean_text(address_str)

        try:
            # Attempt to parse
            tagged_address, address_type = usaddress.tag(address_str)

            street_address = " ".join([
                tagged_address.get("AddressNumber", ""),
                tagged_address.get("StreetName", ""),
                tagged_address.get("StreetNamePostType", "")
            ]).strip()

            address_line_2 = " ".join([
                tagged_address.get("OccupancyType", ""),
                tagged_address.get("OccupancyIdentifier", "")
            ]).strip()

            city = tagged_address.get("PlaceName", "")
            state = tagged_address.get("StateName", "")
            zip_code = tagged_address.get("ZipCode", "")

        except usaddress.RepeatedLabelError:
            logger.warning(f"Address parsing failed for: {address_str}. Returning raw format.")
            return address_str, "", "", "", ""

        return street_address, address_line_2, city, state, zip_code

    @staticmethod
    def get_value(data: dict, keys: list, default=None):
        """
        Utility to try multiple possible keys for a single field.
        """
        for key in keys:
            if key in data and data[key]:
                return data[key]
        return default

    @staticmethod
    def try_int(value):
        """
        Attempt to convert `value` to int. If it fails, return the original value.
        """
        if value and str(value).isdigit():
            return int(value)
        return value


# ----------------------------------------------------------------------------
# Standalone Execution
# ----------------------------------------------------------------------------
def main():
    # Default directories for standalone usage
    normalizer = SchoolDataNormalizer(
        input_dir="data/schools_incremental",
        output_dir="data/schools_normalized"
    )
    normalizer.run()

if __name__ == "__main__":
    main()