from pathlib import Path
from typing import Optional

import msgspec

from phylodata.data_types import EditablePaperWithExperiment


def remove_classification(metadata_file: Path, sample_id: Optional[str] = None):
    """
    Removes the classification of a language sample in a editable metadata file.
    If no sample_id is provided, all samples are removed.

    Args:
        metadata_file: The path to the metadata file.
        sample_id: The ID of the sample to remove the classification from.
    """

    with open(metadata_file, "r") as file:
        metadata = msgspec.json.decode(file.read(), type=EditablePaperWithExperiment)

    for sample in metadata.samples:
        if not sample_id or sample.sample_id == sample_id:
            sample.classification = []
            sample.scientific_name = sample.sample_id
            sample.common_name = None

    with open(metadata_file, "wb") as file:
        file.write(msgspec.json.format(msgspec.json.encode(metadata), indent=2))
