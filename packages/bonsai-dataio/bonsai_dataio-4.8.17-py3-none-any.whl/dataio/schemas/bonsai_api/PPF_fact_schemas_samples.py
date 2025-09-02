from typing import ClassVar, Dict, Optional, Tuple

from pydantic import Field

import dataio.schemas.bonsai_api.facts as schemas
from dataio.schemas.bonsai_api.base_models import FactBaseModel_samples
from dataio.tools import BonsaiTableModel


class Use_samples(FactBaseModel_samples):
    location: str
    product: str
    activity: str
    unit: str
    value: float
    associated_product: Optional[str] = None
    flag: Optional[str] = (
        None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    )
    time: int
    product_origin: Optional[str] = None  # Where the used product comes from.
    product_type: str = Field(
        default="use"
    )  # set automatically based on what data class is used
    account_type: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.product_type}-{self.activity}-{self.time}-{self.value}-{self.unit}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "use-samples/": "Endpoint for use samples for both list and detail view.",
    }


class Supply_samples(FactBaseModel_samples):
    location: str
    product: str
    activity: str
    unit: str
    value: float
    product_destination: Optional[str] = None
    associated_product: Optional[str] = None
    flag: Optional[str] = (
        None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    )
    time: int
    product_type: str = Field(
        default="supply"
    )  # set automatically based on what data class is used. This can also be joint or combined product, but maybe needs to be a different attribute?
    account_type: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.product_type}-{self.activity}-{self.time}-{self.value}-{self.unit}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "supply-samples/": "Endpoint for supply samples for both list and detail view.",
    }


class Imports_samples(FactBaseModel_samples):
    location: str
    product: str
    product_origin: str  # Where the product comes from
    unit: str
    value: float
    time: int
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "import-samples/": "Endpoint for import samples for both list and detail view.",
    }


class Valuation_samples(FactBaseModel_samples):
    location: str
    product: str
    valuation: str
    unit: str
    value: float
    time: int
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "valuation-samples/": "Endpoint for valuation samples for both list and detail view.",
    }


class FinalUses_samples(FactBaseModel_samples):
    location: str
    product: str
    final_user: str  # Final use ctivity that uses the product
    unit: str
    value: float
    time: int
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "final-use-samples/": "Endpoint for final-use samples for both list and detail view.",
    }


class SUTAdjustments_samples(FactBaseModel_samples):
    location: str
    adjustment: str
    product: Optional[str] = None
    product_origin: Optional[str] = None  # Where the product comes from
    final_user: Optional[str] = None  # Where the product is used
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "sut-adjustment-samples/": "Endpoint for sut-adjustment samples for both list and detail view.",
    }


class OutputTotals_samples(FactBaseModel_samples):
    location: str
    activity: str
    output_compartment: str  # Where the outputs are used
    unit: str
    value: float
    time: int
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "output-total-samples/": "Endpoint for output-total samples for both list and detail view.",
    }


class ValueAdded_samples(FactBaseModel_samples):
    location: str
    activity: str
    value_added_component: str  # Component of value added
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "value-added-samples/": "Endpoint for value-added samples for both list and detail view.",
    }


class SocialSatellite_samples(FactBaseModel_samples):
    location: str
    activity: str
    social_flow: str  # Type of social flow
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "social-satellite-samples/": "Endpoint for social-satellite samples for both list and detail view.",
    }


class ProductionVolumes_samples(FactBaseModel_samples):
    location: str
    product: str
    activity: Optional[str] = None
    unit: str
    value: float
    flag: Optional[str] = None  # TODO flag rework
    time: int
    inventory_time: Optional[int] = None
    source: Optional[str] = None
    comment: Optional[str] = None
    price_type: Optional[str] = None
    account_type: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "production-volume-samples/": "Endpoint for production-volume samples for both list and detail view.",
    }


class Emissions_samples(FactBaseModel_samples):
    time: int
    year_emission: Optional[int] = (
        None  # TODO Rework into how we want to handle delayed emissions
    )
    location: str
    activity: str
    activity_unit: str
    emission_substance: str
    compartment: str  # location of emission, such as "Emission to air"
    product: str
    product_unit: str
    value: float
    unit: str
    flag: Optional[str] = None

    elementary_type: str = Field(default="emission")

    def __str__(self) -> str:
        return f"{self.location}-{self.emission_substance}-{self.activity}-{self.activity_unit}-{self.time}-{self.value}-{self.unit}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "emission-samples/": "Endpoint for emission samples for both list and detail view.",
    }


class TransferCoefficient_samples(FactBaseModel_samples):  # Similar to use
    location: Optional[str] = None
    output: str
    input_product: str
    activity: str
    coefficient_value: float
    unit: str
    flag: Optional[str] = (
        None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    )
    time: Optional[int] = None
    transfer_type: str  # Should be one of these three value: "product", "emission" or "waste" TODO Validator

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.coefficient_value}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "transfer-coefficient-samples/": "Endpoint for transfer-coefficient samples for both list and detail view.",
    }


class Resource_samples(Emissions_samples):
    def __init__(self, **data):
        super().__init__(**data)
        self.elementary_type = "resource"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "resource-samples/": "Endpoint for resource samples for both list and detail view.",
    }


class PackagingData_samples(Supply_samples):
    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "packaging_data"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "packaging-data-samples/": "Endpoint for packaging-data samples for both list and detail view.",
    }


class WasteUse_samples(Use_samples):
    waste_fraction: bool

    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "waste_use"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "waste-use-samples/": "Endpoint for waste-use samples for both list and detail view.",
    }


class WasteSupply_samples(Supply_samples):
    waste_fraction: bool

    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "waste_supply"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product_code": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "waste-supply-samples/": "Endpoint for waste-supply samples for both list and detail view.",
    }


class PropertyOfProducts_samples(FactBaseModel_samples):
    location: Optional[str] = None
    product: str
    value: float
    activity: Optional[str] = None
    unit: str
    description: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "property-of-product-samples/": "Endpoint for property-of-product samples for both list and detail view.",
    }


class Trade_samples(FactBaseModel_samples):
    time: int
    product: str
    export_location: str
    import_location: str
    value: float
    unit: str
    flag: Optional[str] = None  # TODO flag rework
    price_type: Optional[str] = None
    source: Optional[str] = None
    account_type: Optional[str] = None
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "trade-samples/": "Endpoint for trade samples for both list and detail view.",
    }



class PopulationData_samples(FactBaseModel_samples):
    location: str
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "import-uncertainty/": "Endpoint for import uncertainty for both list and detail view.",
    }