import json
import os
from collections.abc import Iterator
from typing import Any


def save_crawl_progress(checked_urls: list[str], urls: list[str]) -> None:
    """Saves the current crawl progress to a JSON file."""
    with open("data.json", "w+", encoding="utf-8") as fp:
        progress = {
            "checked_urls": checked_urls,
            "urls": urls,
        }
        fp.write(json.dumps(progress, ensure_ascii=False, indent=4))


def load_crawl_progress() -> dict[str, Any] | None:
    """Loads crawl progress from data.json, or returns None if it doesn't exist."""
    if os.path.exists("data.json"):
        with open("data.json") as fp:
            return json.load(fp)  # type:ignore
    return None


def save_enriched_chunks(url: str, chunks: list[dict[str, Any]]) -> None:
    """Saves enriched chunks for a URL to an output JSON file."""
    with open(f"output{url}.json", "w", encoding="utf-8") as fp:
        fp.write(
            json.dumps(
                {"items": chunks},
                ensure_ascii=False,
                indent=4,
            )
        )


def load_enriched_chunks_from_folder(folder: str) -> Iterator[tuple[str, Any]]:
    """Iterates over enriched chunk JSON files in a folder, yielding (file_path, data)."""
    for file_name in os.listdir(folder):
        file_path = os.path.join(folder, file_name)

        if not file_path.endswith(".json"):
            continue

        with open(file_path, encoding="utf-8") as fp:
            try:
                data = json.load(fp)
                yield file_path, data
            except json.JSONDecodeError as e:
                print(f"Error decoding JSON from file {file_path}: {e}")


def save_ingestion_progress(used_files: list[str], next_id: int) -> None:
    """Saves the progress of processed files and current ID."""
    with open("used_files.json", "w", encoding="utf-8") as log_fp:
        json.dump({"files": used_files, "next_id": next_id}, log_fp, indent=2, ensure_ascii=False)


def load_ingestion_progress() -> dict[str, Any]:
    """Loads ingestion progress from used_files.json."""
    with open("used_files.json", encoding="utf-8") as log_fp:
        return json.load(log_fp)  # type:ignore
