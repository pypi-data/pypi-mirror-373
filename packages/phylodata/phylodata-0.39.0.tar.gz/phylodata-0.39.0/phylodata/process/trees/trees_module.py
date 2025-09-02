from io import BytesIO

import streamlit as st

from phylodata.data_types import Trees
from phylodata.process.module import Module
from phylodata.process.trees.parse_trees import parse_trees


class TreesModule(Module[Trees | None]):
    def ui(self): ...

    def validate(self): ...

    def parse(self, beast2_trees: BytesIO | None) -> Trees | None:
        if not beast2_trees:
            return None
        st.text("Processing the trees...")
        return parse_trees(beast2_trees)
