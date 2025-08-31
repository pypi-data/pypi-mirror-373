import os
import shutil
from io import BytesIO
from pathlib import Path
from typing import Optional

import msgspec

from phylodata.data_types import (
    EditableExperiment,
    EditablePaper,
    EditablePaperWithExperiment,
    EvolutionaryModelComponent,
    File,
    FileType,
    Metadata,
    NonEditableExperiment,
    NonEditablePaper,
    NonEditablePaperWithExperiment,
    Sample,
    Trees,
)
from phylodata.process.utils.file_utils import add_file_name_suffix

WASABI_BUCKET_NAME = "phylodata-experiments"

EDITABLE_METADATA_FILE = "editable_phylodata_metadata.json"
NON_EDITABLE_METADATA_FILE = "non_editable_phylodata_metadata"


def generate_output(
    editable_experiment: EditableExperiment,
    non_editable_experiment: NonEditableExperiment,
    editable_paper: EditablePaper,
    non_editable_paper: NonEditablePaper,
    samples: list[Sample],
    files: list[File],
    evolutionary_model: list[EvolutionaryModelComponent],
    trees: Optional[Trees],
    metadata: Metadata,
) -> Path:
    """Creates the output folder for the given experiment metadata."""
    files = clean_up_file_names(files)
    files = add_non_editable_metadata_file(
        files,
        non_editable_paper,
        non_editable_experiment,
        evolutionary_model,
        trees,
        metadata,
    )
    files = add_editable_metadata_file(
        files, editable_paper, editable_experiment, samples
    )

    output_folder = create_output_folder(non_editable_experiment)
    store_files(files, output_folder)

    return output_folder


def clean_up_file_names(files: list[File]) -> list[File]:
    """Makes sure all file names are unique and do not correspond to the
    metadata file names."""
    filename_counter = {EDITABLE_METADATA_FILE: 1, NON_EDITABLE_METADATA_FILE: 1}

    for file in files:
        if file.name in filename_counter:
            filename_counter[file.name] += 1
            file.name = add_file_name_suffix(
                file.name, str(filename_counter[file.name]), "_"
            )
        else:
            filename_counter[file.name] = 1

    return files


def add_editable_metadata_file(
    files: list[File],
    editable_paper: EditablePaper,
    editable_experiment: EditableExperiment,
    samples: list[Sample],
) -> list[File]:
    """Adds a new File object to the files list corresponding to the
    editable metadata json."""
    editable_metadata = EditablePaperWithExperiment(
        editable_paper, editable_experiment, samples
    )

    data_bytes = msgspec.json.format(msgspec.json.encode(editable_metadata), indent=2)
    data_bytes_io = BytesIO()
    data_bytes_io.write(data_bytes)

    editable_metadata_file = File.from_bytes(
        data_bytes_io,
        name=EDITABLE_METADATA_FILE,
        type=FileType.PHYLO_DATA_EXPERIMENT,
    )
    files.append(editable_metadata_file)

    return files


def add_non_editable_metadata_file(
    files: list[File],
    non_editable_paper: NonEditablePaper,
    non_editable_experiment: NonEditableExperiment,
    evolutionary_model: list[EvolutionaryModelComponent],
    trees: Optional[Trees],
    metadata: Metadata,
) -> list[File]:
    """Adds a new File object to the files list corresponding to the
    non-editable metadata json."""
    non_editable_metadata = NonEditablePaperWithExperiment(
        files=files,
        experiment=non_editable_experiment,
        paper=non_editable_paper,
        evolutionary_model=evolutionary_model,
        trees=trees,
        metadata=metadata,
    )

    data_bytes = msgspec.json.encode(non_editable_metadata)
    data_bytes_io = BytesIO()
    data_bytes_io.write(data_bytes)

    non_editable_metadata_file = File.from_bytes(
        data_bytes_io,
        name=NON_EDITABLE_METADATA_FILE,
        type=FileType.PHYLO_DATA_EXPERIMENT,
    )
    files.append(non_editable_metadata_file)

    return files


def create_output_folder(experiment: NonEditableExperiment) -> Path:
    """Creates the output folder. If the folder already exists,
    it gets deleted first."""
    output_folder = Path(experiment.human_readable_id)

    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)

    return output_folder


def store_files(files: list[File], output_folder: Path):
    """Stores the files in the output folder."""
    for file in files:
        if not file.bytes:
            raise ValueError(
                f"Trying to store a file without bytes ({file.name}). This should not happen."
            )

        with open(f"{output_folder}/{file.name}", "wb") as f:
            f.write(file.bytes.getbuffer())
