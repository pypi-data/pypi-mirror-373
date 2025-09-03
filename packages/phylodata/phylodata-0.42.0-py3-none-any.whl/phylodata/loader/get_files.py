import os
from collections import defaultdict
from typing import Optional

from phylodata.data_types import File, FileType, PaperWithExperiment
from phylodata.loader.consts import PREFER_PREVIEW_ENV


def get_files(
    experiment: PaperWithExperiment,
    prefer_preview: Optional[bool] = None,
) -> list[File]:
    """Retrieves all downloaded files of the experiment.
    For every file, either the full or preview version is returned.

    Args:
        experiment:
            The experiement to retrieve files from.
        prefer_preview:
            If None, prefers a full file but falls back to a preview file if no full file exists.
            If True, prefers and returns a preview file if available.
            If False, only retrieves full files.
            This can also be controlled by setting the environment variable PHYLODATA_PREFER_PREVIEW
            to true or false.

    Returns:
        A list of File objects containing the experiment data.
    """
    if prefer_preview is None and os.environ.get(PREFER_PREVIEW_ENV) is not None:
        prefer_preview = os.environ.get(PREFER_PREVIEW_ENV) == "true"

    downloaded_files = [file for file in experiment.files if file.local_path]

    downloaded_file_variants = defaultdict(list[File])
    for file in downloaded_files:
        downloaded_file_variants[_strip_preview_suffix(file)].append(file)

    print(downloaded_file_variants)

    result = []
    for variants in downloaded_file_variants.values():
        preview_variant = [file for file in variants if file.is_preview]
        full_variant = [file for file in variants if not file.is_preview]

        if prefer_preview is None:
            # Prefer full, fall back to preview
            if full_variant:
                result.extend(full_variant)
            elif preview_variant:
                result.extend(preview_variant)

        elif prefer_preview:
            # Prefer preview, fall back to full
            if preview_variant:
                result.extend(preview_variant)
            elif full_variant:
                result.extend(full_variant)

        else:
            # Only full, skip if none exists
            if full_variant:
                result.extend(full_variant)

    return result


def _strip_preview_suffix(file: File) -> str:
    name = file.name
    extension = name.split(".")[-1]

    if name.endswith(f" (preview).{extension}"):
        return name[: -len(" (preview)") - len(extension) - 1] + "." + extension

    return name


def get_files_of_type(
    experiment: PaperWithExperiment,
    file_type: FileType,
    prefer_preview: Optional[bool] = None,
) -> list[File]:
    """Retrieves all downloaded files of the experiment of a specific type.
    For every file, either the full or preview version is returned.

    Args:
        experiment:
            The experiement to retrieve files from.
        file_type:
            The FileType to retrieve.
        prefer_preview:
            If None, prefers a full file but falls back to a preview file if no full file exists.
            If True, prefers and returns a preview file if available.
            If False, only retrieves full files.
            This can also be controlled by setting the environment variable PHYLODATA_PREFER_PREVIEW
            to true or false.

    Returns:
        A list of File objects containing the experiment data.
    """
    return [
        file for file in get_files(experiment, prefer_preview) if file.type == file_type
    ]


def get_file(
    experiment: PaperWithExperiment,
    name: str,
    prefer_preview: Optional[bool] = None,
) -> Optional[File]:
    """Retrieves a file of a specific name from a PaperWithExperiment object.

    Args:
        experiment:
            The PaperWithExperiment object containing the files.
        name:
            The name of the file to retrieve.
        prefer_preview:
            If None, prefers a full file but falls back to a preview file if no full file exists.
            If True, prefers and returns a preview file if available.
            If False, only retrieves full files.
            This can also be controlled by setting the environment variable PHYLODATA_PREFER_PREVIEW
            to true or false.

    Returns:
        The first matching File object, or None if no such file exists.
    """
    matching_files = [
        file
        for file in get_files(experiment, prefer_preview)
        if _strip_preview_suffix(file) == name
    ]
    return matching_files[0] if matching_files else None


def get_file_of_type(
    experiment: PaperWithExperiment,
    file_type: FileType,
    prefer_preview: Optional[bool] = None,
) -> Optional[File]:
    """
    Retrieves a file of a specified type from a PaperWithExperiment object.

    Args:
        experiment:
            The PaperWithExperiment object containing the files.
        file_type:
            The FileType to retrieve.
        prefer_preview:
            If None, prefers a full file but falls back to a preview file if no full file exists.
            If True, prefers and returns a preview file if available.
            If False, always retrieves a full file.
            This can also be controlled by setting the environment variable PHYLODATA_PREFER_PREVIEW
            to true or false.

    Returns:
        The first matching File object, or None if no such file exists.
    """
    matching_files = get_files_of_type(experiment, file_type, prefer_preview)
    return matching_files[0] if matching_files else None
