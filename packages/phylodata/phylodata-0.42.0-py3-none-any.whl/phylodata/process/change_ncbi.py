from pathlib import Path

import msgspec

from phylodata.data_types import EditablePaperWithExperiment
from phylodata.process.samples.taxon_classification import look_up_taxon_classification


def change_ncbi(metadata_file: Path, sample_id: str, ncbi_taxon_id: int):
    """
    Changes the classification of a NCBI sample in a editable metadata file.

    Args:
        metadata_file: The path to the metadata file.
        sample_id: The ID of the sample to correct.
        ncbi_taxon_id: The NCBI taxon ID.
    """

    with open(metadata_file, "r") as file:
        metadata = msgspec.json.decode(file.read(), type=EditablePaperWithExperiment)

    for sample in metadata.samples:
        if sample.sample_id == sample_id:
            if classification := look_up_taxon_classification(ncbi_taxon_id):
                sample.classification = classification
                sample.scientific_name = classification[0].scientific_name
                sample.common_name = classification[0].common_name
                break

    with open(metadata_file, "wb") as file:
        file.write(msgspec.json.format(msgspec.json.encode(metadata), indent=2))
