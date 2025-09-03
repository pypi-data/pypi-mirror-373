from io import BytesIO

import pytest

from phylodata.errors import ValidationError
from phylodata.process.files.parse_files import parse_beast2_config


def to_bytes_io(text: str):
    bytesio = BytesIO(bytes(text, "ascii"))
    bytesio.name = "Test"
    return bytesio


def test_simple_beast_config_is_ok():
    file = to_bytes_io("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
        <data></data>
        <run></run>
    </beast>""")
    all(parse_beast2_config(file))


def test_simple_beast_config_with_alignment_is_ok():
    file = to_bytes_io("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
    <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
        <alignment></alignment>
        <run></run>
    </beast>""")
    all(parse_beast2_config(file))


def test_beast1_xml_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast version="1.10.4">
            <data></data>
            <run></run>
        </beast>""")
        all(parse_beast2_config(file))


def test_missing_data_tag_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
            <run></run>
        </beast>""")
        all(parse_beast2_config(file))


def test_missing_run_tag_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <beast namespace="beast.core" required="BEAST.base v2.7.7" version="2.7">
            <data></data>
        </beast>""")
        all(parse_beast2_config(file))


def test_empty_file_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("")
        all(parse_beast2_config(file))


def test_non_xml_file_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("""
        beast2_config:
            - "this is a YAML and no XML file"
        """)
        all(parse_beast2_config(file))


def test_missing_beast_tag_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("""<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <some-other-tag></some-other-tag>""")
        all(parse_beast2_config(file))
