from data_ingestion.data.wiki_datasource import get_data_from_url
from data_ingestion.models.page_data import PageData


def extract_page(url: str, all_urls: list[str]) -> PageData:
    """Fetches and parses a wiki page, returning discovered URLs and chunks."""
    return get_data_from_url(url, all_urls)
