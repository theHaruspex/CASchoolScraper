#!/usr/bin/env python3
"""
demographic_calculator.py

Refactored into a class-based approach for pipeline integration. This module loads city-level
demographic data from a CSV (keyed by city name) and calculates the black population ratio
for each school JSON in the input directory, then writes the enriched JSON to the output directory.

Usage (standalone):
    python demographic_calculator.py

Usage (in a pipeline):
    from demographic_calculator import DemographicCalculator
    calc = DemographicCalculator(
        csv_file="California_City.csv",
        input_dir="data/schools_normalized",
        output_dir="data/schools_normalized_demo"
    )
    calc.run()
"""

import os
import csv
import json
from pathlib import Path

from ndt_logger import initialize_logging
logger = initialize_logging()


class DemographicCalculator:
    def __init__(self,
                 csv_file: str = "California_City.csv",
                 input_dir: str = "data/schools_normalized",
                 output_dir: str = "data/schools_enriched"):
        """
        :param csv_file: Path to the demographics CSV file.
        :param input_dir: Directory containing normalized JSON files.
        :param output_dir: Directory to store the enriched JSON files.
        """
        self.csv_file = csv_file
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.city_data = {}

        # Ensure the output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        """
        Main entry point for calculating and injecting demographic data into each JSON file.
        """
        logger.info("Starting DemographicCalculator...")
        logger.info(f"Loading city data from CSV: {self.csv_file}")
        self._load_city_data()

        logger.info(f"Processing JSON files in {self.input_dir}")
        for filename in os.listdir(self.input_dir):
            if filename.endswith(".json"):
                json_path = self.input_dir / filename
                self._enrich_single_file(json_path)

        logger.info("DemographicCalculator completed successfully.")

    def _load_city_data(self):
        """
        Load demographic CSV data into a dictionary keyed by city_name.
        """
        try:
            with open(self.csv_file, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    city_name = row.get('placeName', '').strip()
                    total_pop = self._try_int(row.get('Value:Count_Person'))
                    black_pop = self._try_int(row.get('Value:Count_Person_BlackOrAfricanAmericanAlone'))

                    self.city_data[city_name] = {
                        'total_population': total_pop,
                        'black_population': black_pop,
                    }
        except FileNotFoundError:
            logger.error(f"CSV file not found: {self.csv_file}")
        except Exception as e:
            logger.error(f"Error loading CSV '{self.csv_file}': {e}")

    def _enrich_single_file(self, json_path: Path):
        """
        Enrich a single JSON file with black population ratio and save it to output_dir.
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                school_data = json.load(f)
        except Exception as e:
            logger.error(f"Error reading file '{json_path}': {e}")
            return

        city = school_data.get('City')
        ratio = None
        if city and city in self.city_data:
            total = self.city_data[city]['total_population']
            black = self.city_data[city]['black_population']
            if total and total != 0 and black is not None:
                ratio = black / total
            elif black is None:
                logger.warning(f"Black population is None for city '{city}'. Data: {school_data}")

        # Inject the ratio
        school_data['Black Population Ratio'] = ratio

        output_path = self.output_dir / json_path.name
        try:
            with open(output_path, 'w', encoding='utf-8') as outfile:
                json.dump(school_data, outfile, indent=4)
            logger.info(f"Enriched and saved: {output_path}")
        except Exception as e:
            logger.error(f"Error writing file '{output_path}': {e}")

    @staticmethod
    def _try_int(value):
        """
        Safely convert a value to int if possible; else return None or the original.
        """
        if value is None:
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None


# ----------------------------------------------------------------------------
# Standalone Execution
# ----------------------------------------------------------------------------
def main():
    calc = DemographicCalculator(
        csv_file="California_City.csv",
        input_dir="data/schools_normalized",
        output_dir="data/schools_normalized_demo"
    )
    calc.run()

if __name__ == "__main__":
    main()