from io import BytesIO

from phylodata.process.trees.parse_trees import parse_trees


def to_bytes_io(text: str):
    bytesio = BytesIO(bytes(text, "ascii"))
    bytesio.name = "Test"
    return bytesio


def test_parse_trees():
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
        tree STATE_1 = ((0: 1.5, 1: 1.5): 2.0, 2: 3.5):0.5;
        tree STATE_2 = ((0: 1.5, 1: 1.5): 2.0, 2: 3.5):0.5;
        tree STATE_3 = ((0: 1.5, 1: 1.5): 2.0, 2: 3.5):0.5;
        tree STATE_4 = ((0: 1.5, 1: 1.5): 2.0, 2: 3.5):0.5;
    End;
    """

    file = to_bytes_io(raw_nexus)
    parsed = parse_trees(file)

    assert parsed.number_of_trees == 4
    assert parsed.number_of_tips == 3
    assert parsed.time_tree
    assert parsed.ultrametric
    assert parsed.rooted
    assert parsed.average_root_age == 3.5
