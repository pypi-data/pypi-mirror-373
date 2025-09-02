"""Tutorial about executing data transformation task."""

from dataio import load, plot, save, validate

print("loading metadata of task")
task = load(full_path="task.dataio.yaml", include_tables=False)

print("loading dependencies")
lookup_path = task.__metadata__["datapackages"][0]["path"]
lookup_name = task.__metadata__["datapackages"][0]["name"]
lookup = load(full_path=f"{lookup_path}/{lookup_name}.dataio.yaml", include_tables=True)
del lookup_name, lookup_path

print("populating tables (example)")
index = lookup.tree_main.loc[lookup.tree_main["dim_level"] == 2].index
for pos, val in enumerate(list(index)):
    print(pos, val)
    task.dim_dimension.loc[val] = {"position": pos}
    task.fact_fact.loc[str(pos)] = {"dim_dimension": val, "value": float(pos)}


print("saving")
save(datapackage=task, increment="minor", overwrite=True, create_path=True)

print("validating")
validate(full_path="task/task.dataio.yaml", overwrite=True, log_name="validate.log")

print("plotting")
plot(full_path="task/task.dataio.yaml", overwrite=True)
