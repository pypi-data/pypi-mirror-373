from io import BytesIO

import pytest

from phylodata.errors import ValidationError
from phylodata.process.files.parse_files import parse_beast2_logs


def to_bytes_io(text: str):
    bytesio = BytesIO(bytes(text, "ascii"))
    bytesio.name = "Test"
    return bytesio


def test_simple_log_is_ok():
    raw_logs = "state   posterior"
    for s in range(1000):
        raw_logs += f"\n{s}   0"

    file = to_bytes_io(raw_logs)
    list(parse_beast2_logs(file))


def test_log_file_with_few_lines_fails():
    with pytest.raises(ValidationError):
        raw_logs = "state   posterior"
        for s in range(5):
            raw_logs += f"\n{s} 0"

        file = to_bytes_io(raw_logs)
        list(parse_beast2_logs(file))


def test_empty_file_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("")
        list(parse_beast2_logs(file))


def test_no_tsv_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("""This is some random file:khklhdsf
            asdfsadfsadf""")
        list(parse_beast2_logs(file))


def test_preview_file_is_returned():
    raw_logs = "state   posterior"
    for s in range(1000):
        raw_logs += f"\n{s}   0"

    file = to_bytes_io(raw_logs)
    assert len(list(parse_beast2_logs(file))) == 2


def test_size_of_preview_file():
    raw_logs = "state   posterior"
    for s in range(1000):
        raw_logs += f"\n{s}   0"

    file = to_bytes_io(raw_logs)
    files = parse_beast2_logs(file)

    full_file = next(files)
    preview_file = next(files)

    assert full_file.bytes and preview_file.bytes
    assert (
        0 < preview_file.bytes.getbuffer().nbytes < full_file.bytes.getbuffer().nbytes
    )
