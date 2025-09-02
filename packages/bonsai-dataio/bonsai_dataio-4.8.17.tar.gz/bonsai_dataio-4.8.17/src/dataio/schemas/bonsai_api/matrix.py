from dataio.schemas.bonsai_api.base_models import FactBaseModel_uncertainty, MatrixModel


class ProductColumns(FactBaseModel_uncertainty):
    location: str
    product: str
    unit: str
    time: int


class ProductRows(FactBaseModel_uncertainty):
    location: str
    product: str
    unit: str
    time: int


class ActivityRows(FactBaseModel_uncertainty):
    location: str
    activity: str
    unit: str
    time: int


class ActivityColumns(FactBaseModel_uncertainty):
    location: str
    activity: str
    unit: str
    time: int


class EmissionRows(FactBaseModel_uncertainty):
    emission_substance: str
    compartment: str
    unit: str
    time: int


class A_Matrix(MatrixModel):
    column_schema = ActivityColumns
    row_schema = ProductRows


class Inverse(MatrixModel):
    column_schema = ActivityColumns
    row_schema = ProductRows


class IntensitiesMatrix(MatrixModel):
    column_schema = ProductColumns
    row_schema = EmissionRows


class B_Matrix(MatrixModel):
    column_schema = ProductColumns
    row_schema = EmissionRows
