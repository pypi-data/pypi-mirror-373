# Tutorials

Following the instructions on the 'Getting started' section gives access to two tutorials, on which some notes are presented here:

1. [Entity-relation model](tutorial-erm) shows how to generate metadata file.
2. [Data transformation](tutorial-task) shows how to populate a datapackage.


(tutorial-erm)=
## Entity-relation model

The Python script `ermodel.py` executes three functions: `describe()`, `validate()` and `plot()`. All functions have optional parameters, and are set to write logs which can be inspected for errors, warnings and general information.

Initially the tutorial has a `data/` folder with files that illustrate four tabletypes, and a minimal metadata file (which is identical to `backup.dataio.yaml`). The files names and header names follow the conventions required by the `describe()` function to infer table type constraints, including foreign key relations.

Executing `describe()` edits the metadata file. In particular, now there is a `tables` field (see Syntax section) which describes the various tables in the datapackage.

Executing `validate()` creates a validate yaml file, which can be inspected to identify errors in the content of the tables and was created by frictionless. The log was created by dataio and can also be inspected for errors concerning the metadata file itself, not the tables.

Executing `plot()` creates a plot of the entity-relation model. There are several output options, the default is a `.png` file.


(tutorial-task)=
## Data transformation

The Python script `task.py` executes two functions which were not explored in the previous tutorial: `load()` and `save()`, and repeats validation and plotting.

The first action of the script is loading the metadata of the output datapackage as `load(..., include_tables=False)`. This metadata file was created beforehand, and references an external datapackage stored in folder `lookup/`.

The second action is to extract information from the metadata and import the external datapackage `lookup` using `load(..., include_tables=True)`. This datapackage is a stand-in for any data that are required to perform the task. This datapackage illustrates non-standard delimiters and quotation characters.

The third action is to populate the tables of the datapackage. The specifics are purely illustrative, what matters for the tutorial is that the tables are filled in.

The fourth action is to save the datapackage. Notice that while in all other functions so far the path argument was 'full_path' now there is only an optional argument 'root_path', since all other paths are already specified in the metadata.

The script concludes with validation and plotting. There should be no errors in the default setting. However, feel free to edit the metadata and tables in the third action (i.e., before saving) and repeat the last steps.