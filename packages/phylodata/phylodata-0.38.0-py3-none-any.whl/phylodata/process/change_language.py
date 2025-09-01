from pathlib import Path

import msgspec

from phylodata.data_types import EditablePaperWithExperiment
from phylodata.process.samples.add_language_metadata import (
    fetch_language_classification,
)


def change_language(metadata_file: Path, sample_id: str, language_label: str):
    """
    Changes the classification of a language sample in a editable metadata file.

    Args:
        metadata_file: The path to the metadata file.
        sample_id: The ID of the sample to correct.
        language_label: The label of the language to correct to.
    """

    with open(metadata_file, "r") as file:
        metadata = msgspec.json.decode(file.read(), type=EditablePaperWithExperiment)

    for sample in metadata.samples:
        if sample.sample_id == sample_id:
            if classification := fetch_language_classification(language_label):
                sample.classification = classification
                sample.scientific_name = classification[0].scientific_name
                sample.common_name = classification[0].common_name
                break

    with open(metadata_file, "wb") as file:
        file.write(msgspec.json.format(msgspec.json.encode(metadata), indent=2))
