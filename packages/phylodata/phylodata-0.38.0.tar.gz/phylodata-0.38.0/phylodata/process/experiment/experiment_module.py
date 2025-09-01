from datetime import date

import streamlit as st

from phylodata.data_types import (
    EditableExperiment,
    EditablePaper,
    ExperimentType,
    NonEditableExperiment,
)
from phylodata.process.experiment.human_readable_id import generate_human_readable_id
from phylodata.process.module import Module


class ExperimentModule(Module[tuple[EditableExperiment, NonEditableExperiment]]):
    def ui(self):
        with st.container(border=True):
            st.write("""
            ### Experiment

            Optionally, enter some additional information about your experiment. This is useful if you want to register multiple experiments for the same paper.
            """)

            self.title = st.text_input("Experiment title (optional)")
            self.description = st.text_area("Experiment description (optional)")

    def validate(self): ...

    def parse(
        self, paper: EditablePaper
    ) -> tuple[EditableExperiment, NonEditableExperiment]:
        return EditableExperiment(
            title=self.title.strip() or None,
            description=self.description.strip() or None,
            type=ExperimentType.BEAST2_Experiment,
        ), NonEditableExperiment(
            origin="manualUpload",
            version=1,
            upload_date=date.today(),
            human_readable_id=generate_human_readable_id(
                paper.title.strip(),
                paper.year,
                [author.strip() for author in paper.authors],
            ),
        )
