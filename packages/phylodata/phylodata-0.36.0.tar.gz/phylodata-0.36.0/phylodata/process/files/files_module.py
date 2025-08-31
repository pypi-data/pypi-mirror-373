import sys
from io import BytesIO
from pathlib import Path

import streamlit as st

from phylodata.data_types import File, FileType
from phylodata.errors import ValidationError
from phylodata.process.files.parse_files import parse_file
from phylodata.process.module import Module


class FilesModule(Module[list[File]]):
    def __init__(self):
        files_given_as_args = [
            path for file in sys.argv[1:] if (path := Path(file)).is_file()
        ]

        self.beast2_configuration = None
        self.beast2_logs = None
        self.beast2_trees = None
        self.other_files = []

        for file in files_given_as_args:
            bytes = BytesIO(file.read_bytes())
            bytes.name = file.name

            if not self.beast2_configuration and file.suffix == ".xml":
                self.beast2_configuration = bytes
            elif not self.beast2_logs and file.suffix == ".log":
                self.beast2_logs = bytes
            elif not self.beast2_trees and file.suffix == ".trees":
                self.beast2_trees = bytes
            else:
                self.other_files.append(bytes)

    def ui(self):
        with st.container(border=True):
            st.write("""
            ### Files
            """)

            if not self.beast2_configuration:
                st.write("""
                    Select the BEAST 2 XML configuration:
                """)

                self.beast2_configuration = st.file_uploader(
                    "BEAST 2 XML configuration", type=["xml"]
                )

            if not self.beast2_logs:
                st.write("""
                If possible, select the file containing the logs (.log):
                """)
                self.beast2_logs = st.file_uploader("BEAST 2 log file", type=["log"])

            if not self.beast2_trees:
                st.write("""
                If possible, select the file containing the posterior trees (.trees):
                """)
                self.beast2_trees = st.file_uploader(
                    "BEAST 2 posterior trees", type=["trees"]
                )

            if not self.other_files:
                st.write("""
                Optionally, you can also select other files (like summary trees) which you consider an important part of your analysis.
                """)

                self.other_files = st.file_uploader(
                    "Other files (optional)", accept_multiple_files=True
                )

    def validate(self):
        if not self.beast2_configuration:
            raise ValidationError("Specify a BEAST 2 configuration file.")

    def parse(self) -> list[File]:
        st.text("Processing the given files...")
        if not self.beast2_configuration:
            raise ValidationError("Specify a BEAST 2 configuration file.")

        files = list(
            parse_file(self.beast2_configuration, FileType.BEAST2_CONFIGURATION)
        )

        if self.beast2_logs:
            files += parse_file(self.beast2_logs, FileType.BEAST2_POSTERIOR_LOGS)

        if self.beast2_trees:
            files += parse_file(self.beast2_trees, FileType.POSTERIOR_TREES)

        for other_file in self.other_files:
            files += parse_file(other_file, FileType.UNKNOWN)

        return files
