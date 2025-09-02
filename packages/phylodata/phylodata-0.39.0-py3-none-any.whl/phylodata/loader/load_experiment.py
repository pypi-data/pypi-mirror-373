import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import msgspec
from tqdm import tqdm

from phylodata.data_types import (
    EditablePaperWithExperiment,
    FileType,
    NonEditablePaperWithExperiment,
    PaperWithExperiment,
)
from phylodata.loader.download_file import download_file

EDITABLE_METADATA_FILE = "editable_phylodata_metadata.json"
NON_EDITABLE_METADATA_FILE = "non_editable_phylodata_metadata"


@dataclass
class ExperimentToLoad:
    id: str
    version: Optional[int] = None


def load_experiments(
    experiments_to_load: list[ExperimentToLoad | str],
    directory: Optional[str | Path] = None,
    download_only_preview: Optional[bool] = None,
    files_to_download: Optional[list[FileType]] = None,
    force_download: bool = False,
) -> list[PaperWithExperiment]:
    """Loads multiple PhyloData experiments.

    Args:
        experiments_to_load:
            List of experiment IDs or ExperimentToLoad objects specifying which experiments
            to load. If only the ID strings are given, the latest version will be downloaded.
        directory:
            Path where the experiment files should be stored.
        download_only_preview:
            Whether to only download preview files. This is useful for testing environments.
            This can also be controlled by setting the environment variable
            PHYLODATA_DOWNLOAD_ONLY_PREVIEW to true or false. Defaults to False.
        files_to_download:
                Optional list to restrict the FileTypes downloaded. Defaults to all.
        force_download:
            Whether to re-download files even if they exist locally. Defaults to False.

    Returns:
        A list of PaperWithExperiment objects containing the loaded experiment data.
    """
    experiments = []

    for experiment_to_load in tqdm(experiments_to_load):
        if isinstance(experiment_to_load, str):
            experiment_to_load = ExperimentToLoad(experiment_to_load)

        experiment = load_experiment(
            experiment_id=experiment_to_load.id,
            directory=directory,
            version=experiment_to_load.version,
            download_only_preview=download_only_preview,
            files_to_download=files_to_download,  # type: ignore
            force_download=force_download,
        )
        experiments.append(experiment)

    return experiments


def load_experiment(
    experiment_id: str,
    directory: Optional[str | Path] = None,
    version: Optional[int] = None,
    download_only_preview: Optional[bool] = None,
    files_to_download: Optional[list[str | FileType]] = None,
    force_download: bool = False,
) -> PaperWithExperiment:
    """Loads a PhyloData experiment.

    Args:
        experiment_id:
            The human-readable ID of the experiment to load (e.g. felsenstein-1992-estimating).
        directory:
            Path where the experiment files are stored.
        version:
            The version of the experiment to load. Defaults to latest.
        download_only_preview:
            Whether to only download preview files. This is useful for testing environments.
            This can also be controlled by setting the environment variable
            PHYLODATA_DOWNLOAD_ONLY_PREVIEW to true or false. Defaults to False.
        files_to_download:
            Optional list to restrict the filenames or FileTypes downloaded. Defaults to all.
        force_download:
            Whether to re-download files even if they exist locally. Defaults to False.

    Returns:
        A PaperWithExperiment object containing the experiment data.
    """
    if not directory:
        directory = Path("data") / experiment_id
    if isinstance(directory, str):
        directory = Path(directory) / experiment_id
    directory.mkdir(parents=True, exist_ok=True)

    if download_only_preview is None:
        download_only_preview = (
            os.environ.get("PHYLODATA_DOWNLOAD_ONLY_PREVIEW") == "true"
        )

    paper_with_experiment = _download_experiment(
        experiment_id,
        directory,
        version,
        download_only_preview,
        files_to_download,
        force_download,
    )
    return paper_with_experiment


def _download_experiment(
    experiment_id: str,
    directory: Path,
    version: Optional[int] = None,
    download_only_preview: bool = False,
    files_to_download: Optional[list[str | FileType]] = None,
    force_download: bool = False,
):
    # download and load metadata files

    editable_metadata_file = download_file(
        directory,
        experiment_id,
        EDITABLE_METADATA_FILE,
        version,
        force_download,
    )
    with open(editable_metadata_file, "rb") as handle:
        editable_metadata = msgspec.json.decode(
            handle.read(), type=EditablePaperWithExperiment
        )

    non_editable_metadata_file = download_file(
        directory,
        experiment_id,
        NON_EDITABLE_METADATA_FILE,
        version,
        force_download,
    )
    with open(non_editable_metadata_file, "rb") as handle:
        non_editable_metadata = msgspec.json.decode(
            handle.read(), type=NonEditablePaperWithExperiment
        )

    # merge metadata

    metadata = PaperWithExperiment.from_partial(
        editable_metadata, non_editable_metadata
    )

    # download remaining files if needed

    for file in non_editable_metadata.files:
        if (
            files_to_download
            and file.name not in files_to_download
            and file.type not in files_to_download
        ):
            continue

        if file.type == FileType.PHYLO_DATA_EXPERIMENT:
            continue

        if (
            download_only_preview
            and file.type in [FileType.BEAST2_POSTERIOR_LOGS, FileType.POSTERIOR_TREES]
            and not file.is_preview
        ):
            continue

        download_file(directory, experiment_id, file.name, version, force_download)

    return metadata


def load_experiment_from_local_dir(directory: str | Path) -> PaperWithExperiment:
    """Loads a PhyloData experiment from a local directory.

    Args:
        directory:
            Path to the directory containing the experiment files.

    Returns:
        A PaperWithExperiment object containing the experiment data.
    """
    if isinstance(directory, str):
        directory = Path(directory)

    # load metadata files

    with open(directory / EDITABLE_METADATA_FILE, "rb") as handle:
        editable_metadata = msgspec.json.decode(
            handle.read(), type=EditablePaperWithExperiment
        )

    with open(directory / NON_EDITABLE_METADATA_FILE, "rb") as handle:
        non_editable_metadata = msgspec.json.decode(
            handle.read(), type=NonEditablePaperWithExperiment
        )

    # merge metadata

    experiment = PaperWithExperiment.from_partial(
        editable_metadata, non_editable_metadata
    )
    return experiment
