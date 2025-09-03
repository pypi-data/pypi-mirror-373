import os


def add_file_name_suffix(file_name: str, suffix: str, delimiter: str = "") -> str:
    """Appends the suffix to the file name while preserving
    the file extension."""
    base, ext = os.path.splitext(file_name)
    return f"{base}{delimiter}{suffix}{ext}"
