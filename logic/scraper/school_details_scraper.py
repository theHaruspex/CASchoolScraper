import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

from ndt_logger import initialize_logging

from logic.scraper.url_manager import URLManager


# Set up logging for debugging and process tracking.
logger = initialize_logging()


class SchoolDetailsScraper:
    def __init__(self):
        self.session = requests.Session()

    def fetch_details(self, url: str) -> Optional[str]:
        """
        Fetches the HTML content of the school details page.
        """
        try:
            logger.info(f"Fetching school details from: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching details page {url}: {e}")
            return None

    def parse_details(self, html: str) -> Dict:
        """
        Parses the school details page (Layer 2) for key-value pairs in a two-column table.
        It now specifically targets a table with class "table table-bordered small".
        Returns a dictionary with keys and corresponding values.
        """
        soup = BeautifulSoup(html, 'html.parser')
        details = {}

        # Attempt to find the table with the expected class.
        table = soup.find("table", class_="table table-bordered small")
        if not table:
            # Fallback: if the specific table isn't found, search for any table.
            table = soup.find("table")
        if not table:
            logger.warning("No details table found on the page")
            return details

        rows = table.find_all("tr")
        for row in rows:
            key_cell = row.find("th")
            value_cell = row.find("td")
            if key_cell and value_cell:
                # Use a separator to keep multi-line values clear.
                key = key_cell.get_text(separator=" ", strip=True)
                value = value_cell.get_text(separator=" ", strip=True)
                details[key] = value
        return details

    def get_school_details(self, cds_code: str, relative_url: str) -> Dict:
        """
        Convenience method:
            1. Constructs the full URL using the relative URL.
            2. Fetches and parses the details.
        """
        full_url = URLManager.normalize_details_url(relative_url)
        html = self.fetch_details(full_url)
        if html:
            return self.parse_details(html)
        return {}
