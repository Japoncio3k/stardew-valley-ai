import os

from dotenv import load_dotenv

from data_ingestion.data.local_files_datasource import (
    load_crawl_progress,
    save_crawl_progress,
    save_enriched_chunks,
)
from data_ingestion.data.wiki_datasource import (
    compareable_url,
    compareable_url_list,
    default_url,
    treat_url,
)
from data_ingestion.use_cases.enrich_page_use_case import enrich_page_chunks
from data_ingestion.use_cases.extract_page_use_case import extract_page
from data_ingestion.utils.print_with_timestamp import print_with_timestamp

default_path = "output"


def main() -> None:
    load_dotenv()
    progress = load_crawl_progress()
    if progress is not None:
        urls = progress["urls"]
        checked_urls: list[str] = progress["checked_urls"]
    else:
        urls = ["/Stardew_Valley_Wiki"]
        checked_urls = []

    if os.path.exists(default_path):
        used_urls = [treat_url(url) for url in os.listdir(default_path)]
    else:
        used_urls = []

    for index, url in enumerate(urls):
        try:
            print_with_timestamp(
                f"Processing URL {index + 1}/{len(urls)}: {url} [Access in {default_url}{url}]"
            )

            if compareable_url(url) in compareable_url_list(used_urls):
                print("URL already processed, skipping...")
                continue

            try:
                page_data = extract_page(url, urls)
                checked_urls.append(url)
            except Exception as e:
                save_crawl_progress(checked_urls, urls)
                raise e

            for new_url in page_data.urls:
                if compareable_url(new_url) not in compareable_url_list(urls):
                    urls.append(new_url)

            print("URL not processed yet, enriching chunks...")
            try:
                enriched_chunks = enrich_page_chunks(page_data.chunks, url)
                save_enriched_chunks(url, enriched_chunks)
            except Exception as e:
                save_crawl_progress(checked_urls, urls)
                raise e

            used_urls.append(url)
            print()

        except KeyboardInterrupt:
            print("Process interrupted by user. Saving progress...")
            save_crawl_progress(checked_urls, urls)
            break


if __name__ == "__main__":
    main()
