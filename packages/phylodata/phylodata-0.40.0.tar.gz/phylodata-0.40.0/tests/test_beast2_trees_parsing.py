from io import BytesIO

import pytest

from phylodata.errors import ValidationError
from phylodata.process.files.parse_files import parse_beast2_trees


def to_bytes_io(text: str):
    bytesio = BytesIO(bytes(text, "ascii"))
    bytesio.name = "Test"
    return bytesio


def test_simple_nexus_is_ok():
    raw_nexus = """
    #NEXUS
    Begin taxa;
       	Dimensions ntax=3;
        Taxlabels
    taxa_0
    taxa_1
            taxa_2;
    End;
    Begin trees;"""
    for s in range(1000):
        raw_nexus += f"\ntree STATE_{s} = ((0, 1), 2);"
    raw_nexus += "\nEnd;"

    file = to_bytes_io(raw_nexus)
    list(parse_beast2_trees(file))


def test_trees_file_with_few_lines_fails():
    with pytest.raises(ValidationError):
        raw_nexus = """
        #NEXUS
        Begin taxa;
        	Dimensions ntax=3;
        		Taxlabels
        			0
        			1
                    2;
        End;
        Begin trees;
            tree STATE_1 = ((0, 1), 2);
            tree STATE_2 = ((0, 1), 2);
            tree STATE_3 = ((0, 1), 2);
        End;
        """

        file = to_bytes_io(raw_nexus)
        list(parse_beast2_trees(file))


def test_empty_file_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("")
        list(parse_beast2_trees(file))


def test_no_nexus_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("""This is some random file:khklhdsf
            asdfsadfsadf""")
        list(parse_beast2_trees(file))
