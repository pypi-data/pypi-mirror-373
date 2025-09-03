import csv
import re
from pathlib import Path
from typing import TypedDict

import phylodata


def clean_label(label: str) -> str:
    label = label.replace("sequence", "")
    label = label.replace("seq", "")
    return re.sub(r"[^A-Za-z ]+", " ", label).lower().strip()


class Language(TypedDict):
    language_id: str

    parent_id: str
    name: str


languages: list[Language] = []
id_to_language: dict[str, Language] = {}
cleaned_language_names: list[str] = []

# the following is a hacky way to retrieve the glottolog languoid data file
# TODO: check if there is a better way to do this
with open(
    Path(phylodata.__path__[0]) / "process" / "data" / "glottolog_languoid_5.2.csv"  # type: ignore
) as csv_file:  # type: ignore
    glottolog_languages = csv.reader(csv_file)

    for row in glottolog_languages:
        languages.append(
            {
                "language_id": row[0],
                "parent_id": row[2],
                "name": row[3],
            }
        )
        id_to_language[row[0]] = {
            "language_id": row[0],
            "parent_id": row[2],
            "name": row[3],
        }
        cleaned_language_names.append(clean_label(row[3]))
