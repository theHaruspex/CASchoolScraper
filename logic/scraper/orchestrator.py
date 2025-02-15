from logic.scraper.school_list_scraper import SchoolListScraper
from logic.scraper.school_details_scraper import SchoolDetailsScraper
from logic.scraper.additional_details_scraper import AdditionalDetailsScraper
from logic.scraper.school_data_merger import SchoolDataMerger
from logic.scraper.json_exporter import JSONExporter

from ndt_logger import initialize_logging

from typing import Dict

logger = initialize_logging()

class Orchestrator:
    def __init__(self, test_mode: bool = True, incremental_update: bool = False):
        """
        :param test_mode: If True, only one school's data will be processed (useful for testing).
        :param incremental_update: If True, update the 'database' (export data for each school)
                                   immediately after processing it.
        """
        self.list_scraper = SchoolListScraper()
        self.details_scraper = SchoolDetailsScraper()
        self.additional_scraper = AdditionalDetailsScraper()
        self.data_merger = SchoolDataMerger()
        self.exporter = JSONExporter()
        self.test_mode = test_mode
        self.incremental_update = incremental_update

    def process_school(self, school_record: Dict) -> Dict:
        """
        Processes an individual school record:
         - Fetches detailed info from the details page (Layer 2).
         - Fetches additional details (Layer 3).
         - Merges all data into a comprehensive record.
        """
        cds_code = school_record.get("cds_code")
        details_relative_url = school_record.get("details_relative_url")
        details_data = {}
        if details_relative_url:
            details_data = self.details_scraper.get_school_details(cds_code, details_relative_url)
        additional_data = self.additional_scraper.get_additional_details(cds_code)
        merged_data = self.data_merger.merge_data(school_record, details_data, additional_data)
        return merged_data

    def run(self) -> None:
        """
        Main method to run the entire scraping process.
        In test mode, only the first school is processed.
        With incremental_update enabled, each school's data is immediately exported.
        """
        logger.info("Starting the scraping process...")
        all_basic_schools = self.list_scraper.get_all_schools()
        total_schools = len(all_basic_schools)
        all_schools_data = {}

        for idx, school in enumerate(all_basic_schools):
            logger.info(f"Processing school {idx + 1} of {total_schools}.")
            cds_code = school.get("cds_code")
            if not cds_code:
                logger.warning(f"Skipping school at index {idx + 1} due to missing CDS code.")
                continue

            try:
                full_data = self.process_school(school)
                all_schools_data[cds_code] = full_data
                logger.info(f"Successfully processed school with CDS {cds_code}.")

                if self.incremental_update:
                    # Update the 'database' immediately after processing this school.
                    # Here we simulate a database update by exporting the individual JSON.
                    self.exporter.export_individual({cds_code: full_data}, "data/schools_incremental")
                    logger.info(f"Incrementally exported data for school with CDS {cds_code}.")

            except Exception as e:
                logger.error(f"Error processing school with CDS {cds_code}: {e}")

            # In test mode, process only one school.
            if self.test_mode and idx >= 9:
                logger.info("Test mode enabled: Processed ten schools; exiting loop.")
                break

        # After processing all (or one) schools, export the aggregated data.
        self.exporter.export_to_file(all_schools_data, "data/all_schools.json")
        self.exporter.export_individual(all_schools_data, "data/schools")
        logger.info("Scraping process completed.")
