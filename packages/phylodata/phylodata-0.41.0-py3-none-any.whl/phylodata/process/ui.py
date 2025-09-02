from enum import Enum

import streamlit as st

from phylodata.data_types import (
    Metadata,
)
from phylodata.errors import ValidationError
from phylodata.process.evolutionary_model.evolutionary_model_module import (
    EvolutionaryModelModule,
)
from phylodata.process.experiment.experiment_module import ExperimentModule
from phylodata.process.files.files_module import FilesModule
from phylodata.process.paper.paper_module import PaperModule
from phylodata.process.samples.samples_module import SamplesModule
from phylodata.process.trees.trees_module import TreesModule
from phylodata.process.utils.generate_output import generate_output
from phylodata.version import __version__


class Stage(str, Enum):
    INPUT = "Input"
    NEXT_STEPS = "Next Steps"


STAGE = "stage"
OUTPUT_FOLDER = "output_folder"

paper_module = PaperModule()
experiment_module = ExperimentModule()
files_module = FilesModule()
evolutionary_model_module = EvolutionaryModelModule()
samples_module = SamplesModule()
trees_module = TreesModule()

if STAGE not in st.session_state:
    st.session_state[STAGE] = Stage.INPUT


if st.session_state[STAGE] == Stage.INPUT:
    """
    # 🌴 Process Experiment

    Let's process your Bayesian Phylogenetics experiment to prepare it for upload to the PhyloData repository.

    Note that right now, we only support BEAST 2 experiments.

    This usually takes less than five minutes.
    """

    paper_module.ui()
    experiment_module.ui()
    files_module.ui()

    """
    Almost done!
    """

    def process_input():
        with st.status("Processing your analysis...", expanded=True):
            try:
                paper_module.validate()
                experiment_module.validate()
                files_module.validate()
                experiment_module.validate()
                samples_module.validate()
                trees_module.validate()

                editable_paper, non_editable_paper = paper_module.parse()
                editable_experiment, non_editable_experiment = experiment_module.parse(
                    editable_paper
                )
                files = files_module.parse()
                parsed_evolutionary_model = evolutionary_model_module.parse(
                    files_module.beast2_configuration  # type: ignore
                )
                parsed_samples = samples_module.parse(files_module.beast2_configuration)  # type: ignore
                parsed_trees = trees_module.parse(files_module.beast2_trees)  # type: ignore
            except ValidationError as error:
                st.toast(error.message)
                return

            metadata = Metadata(evo_data_pipeline_version=__version__)

            st.text("Creating PhyloData folder...")

            output_folder = generate_output(
                editable_experiment,
                non_editable_experiment,
                editable_paper,
                non_editable_paper,
                parsed_samples,
                files,
                parsed_evolutionary_model,
                parsed_trees,
                metadata,
            )

            st.session_state[STAGE] = Stage.NEXT_STEPS
            st.session_state[OUTPUT_FOLDER] = output_folder
            st.rerun()

    process_experiment_button = st.button("Process experiment", type="primary")
    if process_experiment_button:
        process_input()


if st.session_state[STAGE] == Stage.NEXT_STEPS:
    """
    # 🚀 Next Steps

    You successfully processed your experiment! These are your next steps:

    1. Create a ZIP file of the newly created folder.
    2. Upload it on the [PhyloData website](http://phylodata.com/new-experiment).
    """
