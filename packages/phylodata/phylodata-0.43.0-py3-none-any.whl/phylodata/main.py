import subprocess
from pathlib import Path
from typing import Optional

import click

import phylodata
from phylodata.data_types import (
    ClassificationEntryType,
    get_schema,
    validate_editable_json,
)
from phylodata.process.change_language import (
    change_language as change_language_handler,
)
from phylodata.process.change_ncbi import (
    change_ncbi as change_ncbi_handler,
)
from phylodata.process.remove_classification import (
    remove_classification as remove_classification_handler,
)


@click.group()
def cli(): ...


@cli.command(help="Process an experiment before uploading it to PhyloData.")
@click.argument("files", nargs=-1, type=click.UNPROCESSED)
def process(files):
    subprocess.run(
        [
            "streamlit",
            "run",
            "--server.maxUploadSize=10000",
            "--theme.primaryColor=#54763d",
            "--theme.backgroundColor=#f5f5ef",
            "--theme.secondaryBackgroundColor=white",
            str(Path(phylodata.__path__[0]) / "process/ui.py"),
            *files,
        ],
    )  # type: ignore


@cli.command(
    help="Validate if a given JSON file contains valid editable PhyloData metadata."
)
@click.argument("file_path", type=click.Path(exists=True))
def validate(file_path: str):
    validate_editable_json(file_path)
    print("File is valid!")


@cli.command(help="Prints the JSON schema for valid PhyloData editable metadata files.")
def schema():
    print(get_schema())


@cli.command(help="Corrects the language of a sample in a metadata file.")
@click.argument("metadata_file", type=click.Path(exists=True))
@click.argument("sample_id", type=str)
@click.argument("language_label", type=str)
def change_language(metadata_file: str, sample_id: str, language_label: str):
    change_language_handler(Path(metadata_file), sample_id, language_label)


@cli.command(
    help="Corrects the NCBI taxon classification of a sample in a metadata file."
)
@click.argument("metadata_file", type=click.Path(exists=True))
@click.argument("sample_id", type=str)
@click.argument("ncbi_taxon_id", type=int)
def change_ncbi(metadata_file: str, sample_id: str, ncbi_taxon_id: str):
    change_ncbi_handler(Path(metadata_file), sample_id, int(ncbi_taxon_id))


@cli.command(
    help="Removes the classification of a sample in a metadata file. If no sample_id is provided, all samples are removed."
)
@click.argument("metadata_file", type=click.Path(exists=True))
@click.option("--sample_id", type=str, required=False)
@click.option(
    "--classification_type",
    type=click.Choice(ClassificationEntryType, case_sensitive=False),
    required=False,
)
def remove_classification(
    metadata_file: str,
    sample_id: Optional[str] = None,
    classification_type: Optional[ClassificationEntryType] = None,
):
    remove_classification_handler(Path(metadata_file), sample_id, classification_type)
