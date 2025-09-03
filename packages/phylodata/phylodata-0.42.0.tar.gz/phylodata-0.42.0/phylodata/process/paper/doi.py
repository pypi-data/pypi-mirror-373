import re

DOI_REGEX = r"^https?:\/\/(?:www\.)?(?:dx\.)?doi\.org\/10\.\d{4,}\/[^\s]+$"


def is_doi(doi: str) -> bool:
    """Checks whether the given string is a valid DOI URL."""
    pattern = re.compile(DOI_REGEX)
    return bool(pattern.match(doi))


def get_doi_url(doi: str) -> str:
    """Returns the URL for the given DOI."""
    if is_doi(doi):
        return doi
    else:
        return f"https://doi.org/{doi}"
