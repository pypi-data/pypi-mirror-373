from datetime import datetime

import streamlit as st

from phylodata.data_types import EditablePaper, NonEditablePaper
from phylodata.errors import ValidationError
from phylodata.process.module import Module
from phylodata.process.paper.bibtex import (
    get_bibtex_value,
    is_valid_bibtex,
    yield_bibtex_authors,
)
from phylodata.process.paper.doi import get_doi_url, is_doi
from phylodata.process.paper.mail import is_valid_email


class PaperModule(Module[tuple[EditablePaper, NonEditablePaper]]):
    def fill_using_bibtex(self):
        if "paper_bibtex_title" in st.session_state:
            # we only set it the first time to avoid overwriting manual corrections
            return

        bibtex: str = st.session_state["paper_bibtex"]

        if name := get_bibtex_value(bibtex, "title"):
            st.session_state["paper_bibtex_title"] = name
        if abstract := get_bibtex_value(bibtex, "abstract"):
            st.session_state["paper_bibtex_abstract"] = abstract
        if (year := get_bibtex_value(bibtex, "year")) and year.isdigit():
            st.session_state["paper_bibtex_year"] = int(year)
        if authors := get_bibtex_value(bibtex, "author"):
            st.session_state["paper_bibtex_authors"] = "\n".join(
                yield_bibtex_authors(authors)
            )
        if doi := get_bibtex_value(bibtex, "doi"):
            st.session_state["paper_bibtex_doi"] = get_doi_url(doi)

    def ui(self):
        with st.container(border=True):
            st.write("""
            ### Paper

            Enter the following general information about your paper:
            """)
            self.bibtex = st.text_area(
                "BibTex citation",
                on_change=self.fill_using_bibtex,
                key="paper_bibtex",
                height=200,
            )
            self.title = st.text_input(
                "Title", value=st.session_state.get("paper_bibtex_title")
            )
            self.year = st.number_input(
                "Publication year",
                step=1,
                value=st.session_state.get("paper_bibtex_year"),
            )
            self.abstract = st.text_area(
                "Abstract", value=st.session_state.get("paper_bibtex_abstract")
            )
            self.authors = st.text_area(
                "Authors", value=st.session_state.get("paper_bibtex_authors")
            )
            st.markdown(
                """One author per line. Use *Name Surname* like *Joseph Felsenstein*."""
            )
            self.doi = st.text_input(
                "DOI", value=st.session_state.get("paper_bibtex_doi")
            )
            st.markdown(
                """Use the URL format (like *https://doi.org/10.1093/sysbio/22.3.240*).
                Experiments with the same paper DOI will be linked to the same paper."""
            )
            self.email = st.text_input("E-Mail")
            st.markdown(
                """We need your E-Mail in order to contact you if there are any issues with the experiment."""
            )
            self.url = st.text_input("URL (optional)")

    def validate(self):
        if not self.title or not self.title.strip():
            raise ValidationError("Specify a paper title.")
        if not self.year or self.year < 1800 or datetime.now().year + 1 < self.year:
            raise ValidationError("Specify a valid paper publication year.")
        if not self.abstract or not self.abstract.strip():
            raise ValidationError("Specify a paper abstract.")
        if not self.authors or not self.authors.strip():
            raise ValidationError("Specify at least one paper author.")
        if not is_valid_bibtex(self.bibtex):
            raise ValidationError("Specify exactly one bibtex entry.")
        if not is_valid_email(self.email.strip()):
            raise ValidationError("Specify a valid email address.")
        if not self.doi or not is_doi(self.doi.strip()):
            raise ValidationError("Specify a DOI (like https://doi.org/10.1000/182).")

    def parse(self) -> tuple[EditablePaper, NonEditablePaper]:
        if (
            not self.title
            or not self.year
            or not self.authors
            or not self.abstract
            or not self.doi
        ):
            raise ValidationError("Paper info missing.")

        return EditablePaper(
            title=self.title.strip(),
            year=int(self.year),
            authors=[author.strip() for author in self.authors.split("\n")],
            abstract=self.abstract.strip(),
            bibtex=self.bibtex.strip(),
            url=self.url.strip() or None,
            email=self.email.strip(),
        ), NonEditablePaper(doi=self.doi.strip())
