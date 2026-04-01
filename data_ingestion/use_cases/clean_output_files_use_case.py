import json
import os
from urllib.parse import unquote

from data_ingestion.models.strings_to_ignore import strings_to_ignore


def clean_output_files(folder: str) -> None:
    """Removes ignored chunks and fixes URL-encoded filenames in the output folder."""
    for file_name in os.listdir(folder):
        file_name = os.path.join(folder, file_name)

        print(f"Processing file: {file_name}")

        with open(file_name, "r", encoding="utf-8") as fp:
            content = fp.read()
            if content.strip() == "":
                print(f"File is empty, deleting: {file_name}")
                os.remove(file_name)
                continue

            json_content = json.loads(content)

            indexes_to_remove = []

            for index, item in enumerate(json_content["items"]):
                for ignore_string in strings_to_ignore:
                    if ignore_string in item["content"]:
                        indexes_to_remove.append(index)

            for index in sorted(indexes_to_remove, reverse=True):
                del json_content["items"][index]

            fixed_file_name = unquote(file_name)
            if fixed_file_name == file_name:
                print(f"No encoding issues found in file: {file_name}")
                continue
            with open(fixed_file_name, "w", encoding="utf-8") as out_fp:
                out_fp.write(content)
            os.remove(file_name)

        print(f"Finished processing file: {file_name} to {fixed_file_name}")
