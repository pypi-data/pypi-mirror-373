from typing import Optional

from pydantic import Field

import dataio.schemas.bonsai_api.dims as dim
from dataio.schemas.bonsai_api.base_models import FactBaseModel_uncertainty


class Footprint(FactBaseModel_uncertainty):
    flow_code: str
    description: str | None = None
    unit_reference: str | None = None
    region_code: str
    value: float = 0.0
    unit_emission: str = "tonnes CO2eq"

    def __str__(self) -> str:
        return f"{self.flow_code} - {self.region_code} - {self.unit_reference}"


class Recipe(FactBaseModel_uncertainty):
    prefixed_id: str
    flow: str
    region_reference: str
    unit_reference: str
    flow_input: str
    region_inflow: str | None = None
    value_inflow: float | None = None
    unit_inflow: str | None = None
    value_emission: float
    unit_emission: str
    metrics: str


class CountryFootprint(FactBaseModel_uncertainty):
    act_code: str
    region_code: str
    value: float
    unit_emission: str

    class ConfigDict:
        from_attributes = True

    def __str__(self) -> str:
        return f"{self.act_code.code}-{self.region_code.code}"


class CountryRecipe(FactBaseModel_uncertainty):
    product_code: Optional[str] = None  # Assuming DimProductBase is defined
    unit_reference: Optional[str] = None
    act_code: str
    region_code: str
    value: float
    unit_emission: str

    class ConfigDict:
        from_attributes = True

    def __str__(self) -> str:
        return f"{self.product_code.code if self.product_code else 'None'}-{self.act_code.code}-{self.region_code.code}"
