from io import BytesIO

from phylodata.data_types import EvolutionaryModelComponent
from phylodata.process.evolutionary_model.parse_beast2_packages import (
    BEAST2_PACKAGE_PARSERS,
)
from phylodata.process.utils.bytesio_utils import get_xml_from_bytesio


def parse_evolutionary_model(
    beast2_config: BytesIO,
) -> list[EvolutionaryModelComponent]:
    xml = get_xml_from_bytesio(beast2_config)

    models = []

    for parser in BEAST2_PACKAGE_PARSERS:
        if parser.is_used(xml):
            model = EvolutionaryModelComponent(
                name=parser.get_name(),
                parameters=parser.get_parameters(xml),
                type=parser.get_type(),
            )
            models.append(model)

    return models
