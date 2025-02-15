import json
import os
from typing import Dict

from ndt_logger import initialize_logging

# Set up logging for debugging and process tracking.
logger = initialize_logging()

class JSONExporter:
    @staticmethod
    def export_to_file(school_data: Dict, filename: str) -> None:
        """
        Exports the entire school_data dictionary to a JSON file.
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(school_data, f, indent=4)
            logger.info(f"Exported data to {filename}")
        except Exception as e:
            logger.error(f"Error exporting data to file {filename}: {e}")

    @staticmethod
    def export_individual(schools: Dict[str, Dict], directory: str) -> None:
        """
        Exports each school record as an individual JSON file named with the CDS code.
        """
        if not os.path.exists(directory):
            os.makedirs(directory)
        for cds_code, data in schools.items():
            filename = os.path.join(directory, f"{cds_code}.json")
            try:
                with open(filename, "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)
                logger.info(f"Exported data for CDS {cds_code} to {filename}")
            except Exception as e:
                logger.error(f"Error exporting data for CDS {cds_code}: {e}")
