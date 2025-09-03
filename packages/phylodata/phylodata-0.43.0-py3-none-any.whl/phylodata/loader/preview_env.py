import os

PREFER_PREVIEW_ENV = "PHYLODATA_PREFER_PREVIEW"


def prefer_preview():
    """Sets the PHYLODATA_PREFER_PREVIEW environment variable to true."""
    os.environ[PREFER_PREVIEW_ENV] = "true"


def prefer_full():
    """Sets the PHYLODATA_PREFER_PREVIEW environment variable to false."""
    os.environ[PREFER_PREVIEW_ENV] = "false"
