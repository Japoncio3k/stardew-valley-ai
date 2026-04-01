import os
import time

from dotenv import load_dotenv

from data_ingestion.data.local_files_datasource import (
    load_ingestion_progress,
    save_ingestion_progress,
)
from data_ingestion.data.qdrant_datasource import QdrantDatasource
from data_ingestion.use_cases.ingest_chunks_use_case import (
    COLLECTION_NAME,
    get_embedding_model_size,
    ingest_file,
)

folder_path = "output/"


def main() -> None:
    load_dotenv()
    qdrant_ds = QdrantDatasource()
    used_files = []
    next_id = 0

    try:
        if not os.path.exists("used_files.json"):
            print("progress file not found, creating new collection")
            qdrant_ds.ensure_collection(COLLECTION_NAME, get_embedding_model_size())
            save_ingestion_progress([], 0)

        progress = load_ingestion_progress()
        used_files = progress.get("files", [])
        next_id = progress.get("next_id", 0)

        for file_name in os.listdir(folder_path):
            file_name = os.path.join(folder_path, file_name)

            if not file_name.endswith(".json") or file_name in used_files:
                continue

            print(file_name)
            next_id = ingest_file(file_name, next_id, qdrant_ds)
            used_files.append(file_name)

    except KeyboardInterrupt:
        print("Process interrupted. Saving progress...")
        save_ingestion_progress(used_files, next_id)
    except Exception as e:
        print(f"An error occurred: {e}")
        save_ingestion_progress(used_files, next_id)
        if "502 (Bad Gateway)" in str(e):
            print("Encountered 502 Bad Gateway error, retrying in 10 seconds.")
            time.sleep(10)
            main()
        if "timed out" in str(e):
            print("Encountered timeout error, retrying in 10 seconds.")
            time.sleep(10)
            main()


if __name__ == "__main__":
    main()
