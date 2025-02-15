import requests
from bs4 import BeautifulSoup
from typing import Dict, Optional

from ndt_logger import initialize_logging

from logic.scraper.url_manager import URLManager


# Set up logging for debugging and process tracking.
logger = initialize_logging()



class AdditionalDetailsScraper:
    def __init__(self):
        self.session = requests.Session()

    def fetch_additional_details(self, url: str) -> Optional[str]:
        """
        Fetches the HTML content for the additional details page.
        """
        try:
            logger.info(f"Fetching additional details from: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching additional details page {url}: {e}")
            return None

    def parse_additional_details(self, html: str) -> Dict:
        """
        Parses additional details (Layer 3) from the page.
        This method looks for the div with class "panel-body" and then finds all tables
        with class "table table-bordered" inside it.
        Returns a merged dictionary of all key-value pairs.
        """
        soup = BeautifulSoup(html, 'html.parser')
        details = {}

        # Look for the panel-body container.
        panel = soup.find("div", class_="panel-body")
        if panel:
            tables = panel.find_all("table", class_="table table-bordered")
        else:
            # Fallback to any table with the class if the panel isn't found.
            tables = soup.find_all("table", class_="table table-bordered")

        if not tables:
            logger.warning("No additional details tables found on the page")
            return details

        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                key_cell = row.find("th")
                value_cell = row.find("td")
                if key_cell and value_cell:
                    key = key_cell.get_text(separator=" ", strip=True)
                    value = value_cell.get_text(separator=" ", strip=True)
                    details[key] = value
        return details

    def get_additional_details(self, cds_code: str) -> Dict:
        """
        Convenience method:
            1. Builds the URL for additional details.
            2. Fetches and parses the details.
        """
        url = URLManager.build_additional_details_url(cds_code)
        html = self.fetch_additional_details(url)
        if html:
            return self.parse_additional_details(html)
        return {}
