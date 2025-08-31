from collections import defaultdict
from io import BytesIO
from typing import Generator
from xml.etree import ElementTree

from phylodata.data_types import (
    DataType,
    Sample,
    SampleData,
)
from phylodata.process.samples.add_language_metadata import add_language_metadata
from phylodata.process.samples.add_nucleotide_metadata import add_nucleotide_metadata
from phylodata.process.samples.add_protein_metadata import add_protein_metadata
from phylodata.process.samples.sequence_utils import (
    contains_sequence,
    is_amino_acid_sequence,
    is_dna_sequence,
    is_rna_sequence,
)
from phylodata.process.utils.bytesio_utils import get_xml_from_bytesio


def parse_beast2_samples(beast2_config: BytesIO) -> list[Sample]:
    """Collects all sample data found in the BEAST 2 XML.

    All top-level <data> tags are traversed in order to find all
    alignments in the file.

    Note that this only works with basic BEAST XML files and will not
    work for every possible configuration."""
    sample_data_per_id: dict[str, list[SampleData]] = collect_sample_data(beast2_config)
    samples = construct_samples_from_data(sample_data_per_id)
    return samples


def collect_sample_data(beast2_config: BytesIO) -> dict[str, list[SampleData]]:
    """Collects all samples from the data tags in the given BEAST 2 XML."""
    xml = get_xml_from_bytesio(beast2_config)
    xml_root = xml.getroot()

    if xml_root is None:
        return {}

    # we first look at all <data> tags to find any sequence

    sample_data: list[tuple[str, SampleData]] = []
    for root_child in xml_root:
        if root_child.tag.lower() == "data":
            sample_data += collect_sample_data_from_data_tag(root_child)

    # group the samples by their id (taxon)

    sample_data_per_id: dict[str, list[SampleData]] = defaultdict(list)
    for sample_id, data in sample_data:
        sample_data_per_id[sample_id].append(data)

    return sample_data_per_id


def collect_sample_data_from_data_tag(
    data_element: ElementTree.Element,
) -> Generator[tuple[str, SampleData], None, None]:
    """Yields all sample data found in BEAST 2 XML <sequence> tags within
    a  given <data> tag."""
    data_type = data_element.attrib.get("dataType", "standard")

    match data_type:
        case "aminoacid":
            data_type = DataType.AMINO_ACIDS
        case "binary" | "integer":
            data_type = DataType.TRAITS
        case _:  # "nucleotide" | "standard" | "twoStateCovarion" | "user defined"
            data_type = DataType.UNKNOWN

    for sequence in data_element:
        if sequence.tag.lower() != "sequence":
            continue

        sample_id = sequence.attrib["taxon"]
        data = sequence.attrib.get("value") or sequence.text

        if not data:
            continue

        # ignore whitespace
        data = "".join(data.split())

        # data can be comma-delimited or just a joined string
        if "," in data:
            data = "".join(data.split(","))

        # if dataType was not given in the <data> tag, we try to infer it from
        # the sequence itself
        if data_type == DataType.UNKNOWN:
            if not contains_sequence(data):
                # we don't have any actual useful characters
                ...
            elif is_dna_sequence(data):
                data_type = DataType.DNA
            elif is_rna_sequence(data):
                data_type = DataType.RNA
            elif is_amino_acid_sequence(data):
                data_type = DataType.AMINO_ACIDS

        yield sample_id, SampleData(type=data_type, length=len(data), data=data)


def construct_samples_from_data(
    sample_data_per_id: dict[str, list[SampleData]],
) -> list[Sample]:
    # generate all samples without any detailed metadata

    samples = [
        Sample(
            sample_id=id,
            scientific_name=id,
            classification=[],
            sample_data=data,
            common_name=None,
        )
        for id, data in sample_data_per_id.items()
    ]

    # try to add metadata if applicable

    add_nucleotide_metadata(samples)
    add_protein_metadata(samples)
    add_language_metadata(samples)

    return samples
