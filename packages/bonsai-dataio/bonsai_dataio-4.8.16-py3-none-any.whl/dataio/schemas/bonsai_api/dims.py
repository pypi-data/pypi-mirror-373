from typing import Optional

from pydantic import Field

from dataio.schemas.bonsai_api.base_models import DimensionModel


class Level(DimensionModel):
    name: str
    code: str
    description: Optional[str] = None
    comment: Optional[str] = None


class ClassificationNode(DimensionModel):
    code: str
    parent_code: Optional[str] = None
    level: Optional[str] = None
    description: Optional[str] = None
    comment: Optional[str] = None


class Location(ClassificationNode):
    def __str__(self) -> str:
        return self.name


class ActivityType(ClassificationNode):
    # flow_type: str = Field(None, max_length=30)

    def __str__(self) -> str:
        return self.description


class FlowObject(ClassificationNode):
    def __str__(self) -> str:
        return self.description


class Market(ClassificationNode):
    def __str__(self) -> str:
        return self.description


class Unit(DimensionModel):
    scientific_notation: str = Field(..., max_length=50)
    name: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None
    unit_dimension: str

    def __str__(self) -> str:
        return self.short_name


class UnitConversion(DimensionModel):
    unit: str
    reference_unit: str
    conversion_factor: float


class Calendar(DimensionModel):
    description: str

    def __str__(self) -> str:
        return self.code


class Year(DimensionModel):
    name: str
    calendar: str

    def __str__(self) -> str:
        return self.code


class DataQuality(DimensionModel):
    name: str
    code: str
    description: Optional[str] = None
    comment: Optional[str] = None


class UncertaintyDistribution(DimensionModel):
    name: str
    code: str
    description: Optional[str] = None
    comment: Optional[str] = None


class ChemicalCompound(DimensionModel):
    name: str
    code: str
    description: Optional[str] = None
    comment: Optional[str] = None


class Compartment(DimensionModel):
    name: str
    code: str
    description: Optional[str] = None
    comment: Optional[str] = None


class LCIA(DimensionModel):
    name: str
    code: str
    description: Optional[str] = None
    comment: Optional[str] = None


# Used for fact tables and collection of flags.
class ExternalDimensionTables(DimensionModel):
    description: str
    comment: Optional[str] = None
    urn: Optional[str] = None
