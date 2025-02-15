from ndt_logger import initialize_logging

logger = initialize_logging()

class URLManager:
    BASE_URL = "https://www.cde.ca.gov"
    SCHOOL_LIST_BASE = (
            BASE_URL +
            "/SchoolDirectory/Results?title=California%20School%20Directory"
            "&status=1%2C2&types=0&nps=0&multilingual=0&charter=0&magnet=0"
            "&yearround=0&qdc=0&qsc=0&sax=True&tab=1&order=0&items=500"
            "&hidecriteria=False&isstaticreport=False&page={page}"
    )

    @classmethod
    def build_school_list_url(cls, page_number: int) -> str:
        """
        Constructs the school list URL for the given page number.
        """
        url = cls.SCHOOL_LIST_BASE.format(page=page_number)
        logger.debug(f"Constructed school list URL: {url}")
        return url

    @classmethod
    def normalize_details_url(cls, relative_url: str) -> str:
        """
        Converts a relative details URL into an absolute URL.
        """
        if not relative_url.startswith("/"):
            relative_url = "/" + relative_url
        full_url = cls.BASE_URL + relative_url
        logger.debug(f"Normalized details URL: {full_url}")
        return full_url

    @classmethod
    def build_additional_details_url(cls, cds_code: str) -> str:
        """
        Constructs the additional details URL for the given CDS code.
        """
        url = f"{cls.BASE_URL}/sdprofile/details.aspx?cds={cds_code}"
        logger.debug(f"Constructed additional details URL: {url}")
        return url
