import datetime
import os
from pathlib import Path
from unittest import mock

from pytest import fixture

from phylodata import get_files
from phylodata.data_types import (
    Experiment,
    ExperimentType,
    File,
    FileType,
    Metadata,
    Paper,
    PaperWithExperiment,
)
from phylodata.loader.consts import PREFER_PREVIEW_ENV


@fixture()
def set_preview_env_var_to_true(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            PREFER_PREVIEW_ENV: "true",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield


@fixture()
def set_preview_env_var_to_false(monkeypatch):
    with mock.patch.dict(os.environ, clear=True):
        envvars = {
            PREFER_PREVIEW_ENV: "false",
        }
        for k, v in envvars.items():
            monkeypatch.setenv(k, v)
        yield


@fixture
def experiment() -> PaperWithExperiment:
    return PaperWithExperiment(
        files=[
            File(
                name="beast2.xml",
                type=FileType.BEAST2_CONFIGURATION,
                size_bytes=0,
                md5="",
                local_path=Path("beast2.xml"),
            ),
            File(
                name="beast2 (preview).xml",
                type=FileType.BEAST2_CONFIGURATION,
                size_bytes=0,
                md5="",
                local_path=Path("beast2 (preview).xml"),
                is_preview=True,
            ),
            File(
                name="beast2.logs",
                type=FileType.BEAST2_POSTERIOR_LOGS,
                size_bytes=0,
                md5="",
                local_path=Path("beast2.logs"),
            ),
            File(
                name="beast2 (preview).logs",
                type=FileType.BEAST2_POSTERIOR_LOGS,
                size_bytes=0,
                md5="",
                local_path=Path("beast2 (preview).logs"),
                is_preview=True,
            ),
            File(
                name="beast2 (preview).trees",
                type=FileType.POSTERIOR_TREES,
                size_bytes=0,
                md5="",
                local_path=Path("beast2 (preview).trees"),
                is_preview=True,
            ),
        ],
        paper=Paper(
            doi="",
            title="",
            year=2018,
            authors=[],
            abstract="",
            bibtex="",
        ),
        experiment=Experiment(
            type=ExperimentType.BEAST2_Experiment,
            human_readable_id="",
            origin="",
            upload_date=datetime.date.today(),
            version=0,
            title="",
            description="",
        ),
        samples=[],
        evolutionary_model=[],
        trees=None,
        metadata=Metadata(evo_data_pipeline_version=""),
    )


def test_full_files_are_preferred_if_nothing_specified(experiment: PaperWithExperiment):
    files = get_files(experiment)
    assert len(files) == 3
    assert files[0].name == "beast2.xml"
    assert files[1].name == "beast2.logs"
    assert files[2].name == "beast2 (preview).trees"


def test_only_full_files_are_returned_if_preview_is_false(
    experiment: PaperWithExperiment,
):
    files = get_files(experiment, prefer_preview=False)
    assert len(files) == 2
    assert files[0].name == "beast2.xml"
    assert files[1].name == "beast2.logs"


def test_previews_are_preferred_if_preview_is_true(
    experiment: PaperWithExperiment,
):
    files = get_files(experiment, prefer_preview=True)
    assert len(files) == 3
    assert files[0].name == "beast2 (preview).xml"
    assert files[1].name == "beast2 (preview).logs"
    assert files[2].name == "beast2 (preview).trees"
