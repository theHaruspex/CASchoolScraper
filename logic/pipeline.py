#!/usr/bin/env python3
"""
pipeline.py

This script orchestrates the entire data pipeline:
1. Scrape California school data (DirectoryScraper).
2. Normalize the scraped JSON files (normalizer).
3. Enrich with demographic data (demographic_calculator).
4. Build a final spreadsheet (spreadsheet_builder).

Usage:
  python pipeline.py
"""

from ndt_logger import initialize_logging

# Initialize your custom logger (NaturalDatetimeLogger)
logger = initialize_logging()


def run_pipeline(test_mode=True, incremental_update=True):
    """
    Executes the full data pipeline in sequence.

    :param test_mode: If True, only processes one school (useful for quick debugging).
    :param incremental_update: If True, exports each school’s data immediately after processing.
    """
    logger.info("Starting the pipeline...")

    # 1. Scrape the data
    logger.info("Step 1: Scraping data from CA School Directory.")
    from logic.scraper.orchestrator import Orchestrator
    scraper = Orchestrator(test_mode=test_mode, incremental_update=incremental_update)
    scraper.run()

    # 2. Normalize the data
    logger.info("Step 2: Normalizing scraped JSON data.")
    from logic.normalizer import SchoolDataNormalizer
    normalizer = SchoolDataNormalizer(
        input_dir="data/schools",
        output_dir="data/schools_normalized"
    )
    normalizer.run()

    # 3. Enrich with demographic data
    logger.info("Step 3: Enriching data with demographics.")
    from logic.demographic_calculator import DemographicCalculator
    calc = DemographicCalculator(
        csv_file="data/California_City.csv",
        input_dir="data/schools_normalized",
        output_dir="data/schools_normalized_demo"
    )
    calc.run()

    # 4. Build final spreadsheet
    logger.info("Step 4: Generating final spreadsheet from enriched data.")
    from logic.spreadsheet_builder import SpreadsheetBuilder
    builder = SpreadsheetBuilder(
        data_dir="data/schools_normalized_demo",
        output_file="data/School_Outreach_Contacts.xlsx"
    )
    builder.run()

