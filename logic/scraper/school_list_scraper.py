import requests
from bs4 import BeautifulSoup

from typing import List, Dict, Optional
from ndt_logger import initialize_logging

from logic.scraper.url_manager import URLManager


logger = initialize_logging()


class SchoolListScraper:
    def __init__(self):
        self.session = requests.Session()

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Fetches HTML content of the given URL.
        """
        try:
            logger.info(f"Fetching school list page: {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Error fetching page {url}: {e}")
            return None

    def parse_school_list(self, html: str) -> List[Dict]:
        """
        Parses the HTML for the school list table and extracts basic school data.
        Expected columns:
            0: CDS Code
            1: County
            2: District
            3: School (contains a hyperlink to details)
            4: School Type
            5: Sector Type
            6: Charter
            7: Status

        Returns a list of dictionaries containing:
            - 'cds_code', 'county', 'district', 'school', 'school_type',
              'sector_type', 'charter', 'status'
            - 'details_relative_url' for the school details page.
        """
        soup = BeautifulSoup(html, 'html.parser')
        schools = []

        # Assume that the table is the first table on the page.
        table = soup.find("table")
        if not table:
            logger.warning("No table found on the page")
            return schools

        rows = table.find_all("tr")
        if not rows:
            logger.warning("No rows found in the table")
            return schools

        # Skip header row; iterate through the remaining rows.
        for row in rows[1:]:
            cols = row.find_all("td")
            if len(cols) < 8:
                continue  # Skip rows that do not meet expected structure.

            school_data = {
                "cds_code": cols[0].get_text(strip=True),
                "county": cols[1].get_text(strip=True),
                "district": cols[2].get_text(strip=True),
                "school": None,
                "school_type": cols[4].get_text(strip=True),
                "sector_type": cols[5].get_text(strip=True),
                "charter": cols[6].get_text(strip=True),
                "status": cols[7].get_text(strip=True),
                "details_relative_url": None,
            }

            # Process the School column which may contain a hyperlink.
            school_link = cols[3].find("a")
            if school_link:
                school_data["school"] = school_link.get_text(strip=True)
                school_data["details_relative_url"] = school_link.get("href")
            else:
                school_data["school"] = cols[3].get_text(strip=True)

            schools.append(school_data)
        logger.info(f"Parsed {len(schools)} schools from the page")
        return schools

    def get_all_schools(self) -> List[Dict]:
        """
        Iterates over pages 0 to 7 and aggregates all school records.
        """
        all_schools = []
        for page in range(28):
            url = URLManager.build_school_list_url(page)
            html = self.fetch_page(url)
            if html:
                schools = self.parse_school_list(html)
                all_schools.extend(schools)
        logger.info(f"Total schools found: {len(all_schools)}")
        return all_schools
