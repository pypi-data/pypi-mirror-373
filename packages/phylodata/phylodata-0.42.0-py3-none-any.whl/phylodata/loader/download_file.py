from pathlib import Path
from typing import Optional

import requests


def download_file(
    directory: Path,
    experiment: str,
    file_name: str,
    version: Optional[int] = None,
    force_download: Optional[bool] = False,
) -> Path:
    """Downloads an experiment file and stores it in the given directory. If no version is given,
    the most recent one is downloaded.

    Raises a ValueError if the file could not be found."""
    downloaded_file = directory / file_name

    if not force_download and downloaded_file.exists():
        return downloaded_file

    if version:
        download_link = requests.get(
            f"https://phylodata.com/api/getDownloadLink/{experiment}/{file_name}/{version}"
        ).text
    else:
        download_link = requests.get(
            f"https://phylodata.com/api/getDownloadLink/{experiment}/{file_name}"
        ).text

    response = requests.get(
        download_link, headers={"content-type": "multipart/form-data"}
    )

    if response.status_code == 404:
        raise ValueError("Unknown experiment or file.")

    with open(downloaded_file, mode="wb") as file:
        file.write(response.content)

    return downloaded_file
