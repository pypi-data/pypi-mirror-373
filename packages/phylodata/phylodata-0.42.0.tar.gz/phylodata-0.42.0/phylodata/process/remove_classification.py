from pathlib import Path
from typing import Optional

import msgspec

from phylodata.data_types import ClassificationEntryType, EditablePaperWithExperiment


def remove_classification(
    metadata_file: Path,
    sample_id: Optional[str] = None,
    classification_type: Optional[ClassificationEntryType] = None,
):
    """
    Removes the classification of a language sample in a editable metadata file.
    If no sample_id is provided, all samples are removed.
    If classification_type is given, all samples with that classification type are removed.

    Args:
        metadata_file: The path to the metadata file.
        sample_id: The ID of the sample to remove the classification from.
        classification_type: The type of classifications to remove.
    """

    with open(metadata_file, "r") as file:
        metadata = msgspec.json.decode(file.read(), type=EditablePaperWithExperiment)

    for sample in metadata.samples:
        if sample_id and sample.sample_id != sample_id:
            continue

        if classification_type and classification_type not in {
            data.id_type for data in sample.classification
        }:
            continue

        sample.classification = []
        sample.scientific_name = sample.sample_id
        sample.common_name = None

    with open(metadata_file, "wb") as file:
        file.write(msgspec.json.format(msgspec.json.encode(metadata), indent=2))
