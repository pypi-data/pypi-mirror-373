from typing import Optional

from dataio.tools import BonsaiBaseModel


class PedigreeMatrix(BonsaiBaseModel):
    reliability: Optional[int] = None
    completeness: Optional[int] = None
    temporal_correlation: Optional[int] = None
    geographical_correlation: Optional[int] = None
    technological_correlation: Optional[int] = None


class Uncertainty(BonsaiBaseModel):
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
        return f"{self.variance if self.variance else 'None'}-{self.standard_deviation if self.standard_deviation else 'None'}"
