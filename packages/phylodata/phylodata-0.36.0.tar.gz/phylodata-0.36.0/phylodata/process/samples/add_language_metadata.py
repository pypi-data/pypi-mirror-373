from rapidfuzz import fuzz, process

from phylodata.data_types import (
    ClassificationEntry,
    ClassificationEntryType,
    DataType,
    Sample,
)
from phylodata.process.samples.language_utils import (
    clean_label,
    cleaned_language_names,
    id_to_language,
    languages,
)


def add_language_metadata(samples: list[Sample]) -> list[Sample]:
    """Tries to add metadata to all samples which correspond to a language."""
    for sample in samples:
        for data in sample.sample_data:
            if data.type not in [DataType.TRAITS, DataType.UNKNOWN]:
                continue

            if sample.classification:
                continue

            if classification := fetch_language_classification(sample.sample_id):
                sample.classification = classification
                sample.scientific_name = classification[0].scientific_name
                break  # we only need one match

    return samples


def fetch_language_classification(
    language_label: str,
) -> list[ClassificationEntry] | None:
    match = process.extractOne(
        clean_label(language_label),
        cleaned_language_names,
        scorer=fuzz.WRatio,
        score_cutoff=90,
    )

    if not match:
        return None

    match_idx = match[2]
    matched_language = languages[match_idx]

    classification = [
        ClassificationEntry(
            classification_id=matched_language["language_id"],
            scientific_name=matched_language["name"],
            common_name=None,
            id_type=ClassificationEntryType.GLOTTOLOG_ID,
        )
    ]
    classification = extend_classification(classification)

    return classification


def extend_classification(
    classification: list[ClassificationEntry],
) -> list[ClassificationEntry]:
    highest_language = id_to_language[classification[-1].classification_id]
    next_parent_id = highest_language["parent_id"]
    next_parent = id_to_language.get(next_parent_id)

    if next_parent:
        classification.append(
            ClassificationEntry(
                classification_id=next_parent["language_id"],
                scientific_name=next_parent["name"],
                id_type=ClassificationEntryType.GLOTTOLOG_ID,
            )
        )
        classification = extend_classification(classification)

    return classification
