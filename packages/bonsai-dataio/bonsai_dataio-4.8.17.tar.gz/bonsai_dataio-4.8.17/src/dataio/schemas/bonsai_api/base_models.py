import re
from datetime import datetime
from typing import Optional

from pydantic import Field, ValidationError, field_validator

from dataio.schemas.bonsai_api.metadata import User, Version
from dataio.tools import BonsaiBaseModel, BonsaiTableModel


class FactBaseModel_uncertainty(BonsaiBaseModel):
    variance: Optional[float] = None
    standard_deviation: Optional[float] = None
    confidence_interval_95min: Optional[float] = None
    confidence_interval_95max: Optional[float] = None
    confidence_interval_68min: Optional[float] = None
    confidence_interval_68max: Optional[float] = None
    distribution: Optional[str] = None
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    uncertainty_comment: Optional[str] = None

    def __str__(self) -> str:
        return self.name


class FactBaseModel_samples(BonsaiBaseModel):
    samples: list[float]

    def __str__(self) -> str:
        return self.name


class DimensionModel(BonsaiBaseModel):
    code: Optional[str] = None
    position: Optional[int] = None
    created_by: Optional[str] = None


class CorrespondenceModel(BonsaiBaseModel):
    created_by: Optional[str] = None
    create_time: datetime = Field(default_factory=datetime.now)


class MatrixModel:
    column_schema: FactBaseModel_uncertainty
    row_schema: FactBaseModel_uncertainty
