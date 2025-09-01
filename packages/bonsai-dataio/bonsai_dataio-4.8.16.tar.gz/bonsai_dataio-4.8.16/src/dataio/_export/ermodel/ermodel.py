"""Tutorial about reverse-engineering entity-relation model."""

from dataio import describe, plot, validate

print("describing datapackage")
describe(full_path="data/ermodel.dataio.yaml", overwrite=True, log_name="describe.log")

print("validating datapackage")
validate(full_path="data/ermodel.dataio.yaml", overwrite=True, log_name="validate.log")

print("plotting entity-relation model")
plot(full_path="data/ermodel.dataio.yaml", overwrite=True, log_name="plot.log")
