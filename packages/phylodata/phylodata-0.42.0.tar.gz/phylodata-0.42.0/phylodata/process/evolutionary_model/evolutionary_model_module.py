from io import BytesIO

import streamlit as st

from phylodata.data_types import EvolutionaryModelComponent
from phylodata.process.evolutionary_model.parse_evolutionary_model import (
    parse_evolutionary_model,
)
from phylodata.process.module import Module


class EvolutionaryModelModule(Module[list[EvolutionaryModelComponent]]):
    def ui(self): ...

    def validate(self): ...

    def parse(self, beast2_configuration: BytesIO) -> list[EvolutionaryModelComponent]:
        st.text("Detecting the evolutionary model...")
        return parse_evolutionary_model(beast2_configuration)
