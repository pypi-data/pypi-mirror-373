from io import BytesIO

import streamlit as st

from phylodata.data_types import Sample
from phylodata.process.module import Module
from phylodata.process.samples.parse_beast2_samples import parse_beast2_samples


class SamplesModule(Module[list[Sample]]):
    def ui(self): ...

    def validate(self): ...

    def parse(self, beast2_configuration: BytesIO) -> list[Sample]:
        st.text(
            "Detecting the samples (e.g. using BEAST2 or language lookup). "
            "This might take a while, especially for amino acid sequences..."
        )
        return parse_beast2_samples(beast2_configuration)
