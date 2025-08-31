 phylodata

"""
Download single experiment without using it at all in python.
"""
phylodata.load_experiment(
    "gavryushkina-2017-bayesian", directory="data", only_preview=False
)

"""
Download single experiment, but only certain files that satisify a grep pattern.
"""
phylodata.load_experiment(
    "gavryushkina-2017-bayesian", directory="data", only_preview=False, files="*khk.png"
)

"""
Download multiple experiments without using it at all in python.
"""
phylodata.load_experiments(
    ["gavryushkina-2017-bayesian/1", "drummond-2010-bayesian/1"],
    directory="data",
    only_preview=False,
)

"""
Download single experiment and print all files.
"""
experiment = phylodata.load_experiment("gavryushkina-2017-bayesian", directory="data")

for file in experiment:
    print(file.name)

"""
Download single experiment and load the trees.
"""
experiment = phylodata.load_experiment("gavryushkina-2017-bayesian", directory="data")

for file in experiment:
    if file.type == FileType.BEAST2_POSTERIOR_TREES:
        trees_path = file.path
        break

trees_path = experiment[FileType.BEAST2_POSTERIOR_TREES].path

trees_path = experiment.files.posterior_trees
trees_path = experiment.posterior_trees
trees_path = get_posterior_trees_file(experiment)

"""
Download single experiment and load the samples.
"""
experiment = phylodata.load_experiment("gavryushkina-2017-bayesian", directory="data")

for sample in experiment.samples:
    print(sample.scientific_name)

"""
Only download metadata.
"""
experiment = phylodata.load_experiment(
    "gavryushkina-2017-bayesian", files_to_download=[]
)

for file in experiment:
    print(file.name)


"""
Load experiment from folder.
"""
experiment = phylodata.load_experiment(directory="jlsafd/gavryushkina-2017-bayesian")

for file in experiment:
    print(file.name)


"""
Download single experiment and load the trees using ecosystem library.
"""
import phylotrees

experiment = phylodata.load_experiment(
    "gavryushkina-2017-bayesian", directory="data", version=10
)
trees = phylotrees.load_trees(experiment)
