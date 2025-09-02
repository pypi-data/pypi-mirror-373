import csv
from io import BytesIO, TextIOWrapper
from math import floor
from typing import Generator, Optional

from commonnexus.blocks.trees import Trees

from phylodata.data_types import File, FileType
from phylodata.errors import ValidationError
from phylodata.process.utils.bytesio_utils import (
    get_nexus_from_bytesio,
    get_xml_from_bytesio,
)
from phylodata.process.utils.file_utils import add_file_name_suffix

MIN_NUM_SNAPSHOTS = 50
"""The minimum number of snapshots required for a valid BEAST 2 posterior log file.
When the number of snapshots is less than this value, the log file is considered invalid."""

PREVIEW_FRACTION = 0.05
"""The fraction of state snapshots that are stored in the preview files."""


def parse_file(
    file: BytesIO, file_type: Optional[FileType] = FileType.UNKNOWN
) -> Generator[File, None, None]:
    match file_type:
        case FileType.BEAST2_CONFIGURATION:
            yield from parse_beast2_config(file)
        case FileType.BEAST2_POSTERIOR_LOGS:
            yield from parse_beast2_logs(file)
        case FileType.POSTERIOR_TREES:
            yield from parse_beast2_trees(file)
        case _:
            yield from parse_other_file(file)


def parse_beast2_config(file: BytesIO) -> Generator[File, None, None]:
    """Parses a BEAST 2 config file. If the file does not seem to be a valid
    BEAST config, a ValidationError is raised."""
    xml = get_xml_from_bytesio(file)
    root = xml.getroot()

    if root is None or root.tag.lower() != "beast":
        raise ValidationError("BEAST 2 configuration has no root BEAST tag.")

    if not root.attrib.get("version", "").startswith("2."):
        raise ValidationError(
            "The BEAST configuration file is not for BEAST 2 (likely, it is for BEAST X)."
        )

    if not any(child.tag.lower() == "data" for child in root) and not any(
        child.tag.lower() == "alignment" for child in root
    ):
        raise ValidationError("BEAST 2 has no <data> tag.")

    if not any(child.tag.lower() == "run" for child in root):
        raise ValidationError("BEAST 2 has no <run> tag.")

    yield File.from_bytes(
        file,
        name=file.name,
        type=FileType.BEAST2_CONFIGURATION,
    )


def parse_beast2_logs(file: BytesIO) -> Generator[File, None, None]:
    """Parses a BEAST 2 log file. If the file does not seem to be a valid
    BEAST log, a ValidationError is raised."""
    try:
        wrapper = TextIOWrapper(file)

        def uncomment_lines(wrapper: TextIOWrapper):
            for line in wrapper:
                if not line.lstrip().startswith("#"):
                    yield line

        tsv_file = csv.DictReader(uncomment_lines(wrapper), delimiter="\t")
    except Exception:
        raise ValidationError("BEAST 2 log file is not a tab-separated file.")

    rows = list(tsv_file)
    num_rows = len(rows)

    if num_rows < MIN_NUM_SNAPSHOTS:
        raise ValidationError(
            f"BEAST 2 log file should contain at least {MIN_NUM_SNAPSHOTS} entries."
        )

    # detach wrapper to avoid closing the BytesIO when wrapper is garbage collected
    wrapper.detach()

    # yield full file

    yield File.from_bytes(
        file,
        name=file.name,
        type=FileType.BEAST2_POSTERIOR_LOGS,
    )

    # generate preview file

    preview_lines = rows[: floor(len(rows) * PREVIEW_FRACTION)]

    preview_file = BytesIO()
    preview_wrapper = TextIOWrapper(preview_file, encoding="utf-8", newline="")

    preview_writer = csv.DictWriter(
        preview_wrapper, fieldnames=preview_lines[0].keys(), delimiter="\t"
    )
    preview_writer.writeheader()
    preview_writer.writerows(preview_lines)

    # detach wrapper to avoid closing the BytesIO when wrapper is garbage collected

    preview_wrapper.detach()

    # yield preview file

    yield File.from_bytes(
        preview_file,
        name=add_file_name_suffix(file.name, " (preview)"),
        type=FileType.BEAST2_POSTERIOR_LOGS,
        is_preview=True,
    )


def parse_beast2_trees(file: BytesIO) -> Generator[File, None, None]:
    """Parses a BEAST 2 trees file. If the file does not seem to be a valid
    BEAST trees file, a ValidationError is raised."""
    nexus = get_nexus_from_bytesio(file)

    if not nexus.TREES or not nexus.TREES.trees:
        raise ValidationError("BEAST 2 trees contains no actual trees.")

    num_trees = len(nexus.TREES.trees)

    if num_trees < MIN_NUM_SNAPSHOTS:
        raise ValidationError(
            f"BEAST 2 trees should contain at least {MIN_NUM_SNAPSHOTS} trees."
        )

    # yield full trees file

    yield File.from_bytes(
        file,
        name=file.name,
        type=FileType.POSTERIOR_TREES,
    )

    # generate preview file

    preview_trees_commands = []
    num_previewed_trees = 0

    for command in nexus.TREES:
        # test if it is a TREE command
        if command.name.lower() == "tree":
            if num_previewed_trees < num_trees * PREVIEW_FRACTION:
                preview_trees_commands.append(command)
                num_previewed_trees += 1
        else:
            # this is not a tree command
            # we keep it
            preview_trees_commands.append(command)

    nexus.replace_block(nexus.TREES, Trees(nexus, preview_trees_commands))

    preview_file = BytesIO()
    preview_file.write(str(nexus).encode("utf-8"))

    # yield preview file

    yield File.from_bytes(
        preview_file,
        name=add_file_name_suffix(file.name, " (preview)"),
        type=FileType.POSTERIOR_TREES,
        is_preview=True,
    )


def parse_other_file(file: BytesIO) -> Generator[File, None, None]:
    # if the file contains a single tree => summary tree

    try:
        nexus = get_nexus_from_bytesio(file)
        if nexus.TREES and nexus.TREES.trees and len(nexus.TREES.trees) == 1:
            yield File.from_bytes(
                file,
                name=file.name,
                type=FileType.SUMMARY_TREE,
            )
            return
    except ValidationError:
        # file is not a valid trees file
        ...

    # otherwise we yield an UNKNOWN file

    yield File.from_bytes(
        file,
        name=file.name,
        type=FileType.UNKNOWN,
    )
