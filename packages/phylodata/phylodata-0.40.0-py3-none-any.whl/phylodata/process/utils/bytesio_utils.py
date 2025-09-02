import itertools
from io import BytesIO
from xml.etree import ElementTree

from commonnexus import Nexus

from phylodata.errors import ValidationError


def get_nexus_from_bytesio(file: BytesIO) -> Nexus:
    file.seek(0)
    try:
        lines = itertools.chain.from_iterable(
            (string_line.decode("utf-8") for string_line in file)
        )
        return Nexus(lines)
    except Exception:
        raise ValidationError("BEAST 2 trees file is no valid NEXUS file.")


def get_xml_from_bytesio(file: BytesIO) -> ElementTree.ElementTree:
    file.seek(0)
    try:
        return ElementTree.parse(file)  # type: ignore
    except Exception as e:
        raise ValidationError(f"BEAST 2 configuration is no valid XML file. ({e})")
