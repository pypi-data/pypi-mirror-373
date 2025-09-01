from io import BytesIO

from phylodata.data_types import Trees
from phylodata.errors import ValidationError
from phylodata.process.utils.bytesio_utils import get_nexus_from_bytesio

ULTRAMETRIC_REL_THRESHOLD = 1e-6
"""The absolute relative differences of the tip ages for a tree to be ultrametric. We
use an approximate check because of numerical precision issues."""


def parse_trees(beast2_trees_file: BytesIO) -> Trees:
    """Parses a BEAST 2 trees file in the NEXUS format."""
    nexus = get_nexus_from_bytesio(beast2_trees_file)

    if not nexus.TREES or not nexus.TREES.trees:
        raise ValidationError("Invalid BEAST 2 trees file.")

    # we use the last tree as a representative
    # (the first one could be biased due to initialization.
    # optimally, we would check all trees though.)
    example_tree = nexus.TREES.trees[-1]

    return Trees(
        number_of_trees=len(nexus.TREES.trees),
        number_of_tips=get_number_of_tips(example_tree.newick),
        ultrametric=is_ultrametric(example_tree.newick),
        time_tree=True,
        rooted=True,  # BEAST 2 always produces rooted trees
        ccd1_entropy=0,  # TODO
        tree_ess=0,  # TODO
        ccd0_map_tree="",  # TODO
        hipstr_tree="",  # TODO
        leaf_to_sample_map={},  # TODO
        average_root_age=get_average_root_age(nexus.TREES.trees),
    )


def get_number_of_tips(newick_node):
    """Returns the number of tips for the given commonnexus newick tree."""
    if not newick_node._descendants:
        return 1
    else:
        return sum(map(get_number_of_tips, newick_node._descendants))


def is_ultrametric(newick_node):
    """Returns if the given commonnexus newick tree is ultrametric
    up to ULTRAMETRIC_REL_THRESHOLD."""
    tip_dates = _get_tip_times_since_origin(newick_node, 0.0)
    min_date = min(tip_dates)
    max_date = max(tip_dates)
    return (max_date - min_date) <= ULTRAMETRIC_REL_THRESHOLD * max_date


def get_average_root_age(trees):
    """Returns the average age between the root and the most recent tip for
    the given commonnexus trees."""
    root_ages = []

    for tree in trees:
        tip_dates = _get_tip_times_since_origin(tree.newick, 0.0)
        root_age = max(tip_dates) - tree.newick.length
        root_ages.append(root_age)

    return sum(root_ages) / len(root_ages)


def _get_tip_times_since_origin(newick_node, accumulated_height):
    """A helper function returning the time between the origin and the given
    commonnexus newick node."""
    if not newick_node._descendants:
        return [accumulated_height + newick_node.length]
    else:
        return [
            date
            for child in newick_node._descendants
            for date in _get_tip_times_since_origin(
                child, accumulated_height + newick_node.length
            )
        ]
