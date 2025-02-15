from typing import Dict

from ndt_logger import initialize_logging

# Set up logging for debugging and process tracking.
logger = initialize_logging()


class SchoolDataMerger:
    @staticmethod
    def merge_data(basic: Dict, details: Dict, additional: Dict) -> Dict:
        """
        Merges the three dictionaries into a single record.
        In case of overlapping keys, details and additional values may override basic.
        """
        merged = {}
        merged.update(basic)
        merged.update(details)
        merged.update(additional)
        return merged
