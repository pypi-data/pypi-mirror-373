from typing import ClassVar, Dict, Optional, Tuple

import pandas as pd
from pydantic import Field

import dataio.schemas.bonsai_api.facts as schemas
from dataio.schemas.bonsai_api.base_models import FactBaseModel_uncertainty
from dataio.tools import BonsaiTableModel


class Use_uncertainty(FactBaseModel_uncertainty):
    location: str
    product: str
    activity: str
    unit: str
    value: float
    associated_product: Optional[str] = None
    flag: Optional[
        str
    ] = None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
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
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "use-uncertainty/": "Endpoint for use uncertainty for both list and detail view.",
    }


class Supply_uncertainty(FactBaseModel_uncertainty):
    location: str
    product: str
    activity: str
    unit: str
    value: float
    product_destination: Optional[str] = None
    associated_product: Optional[str] = None
    flag: Optional[
        str
    ] = None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
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
        "supply-uncertainty/": "Endpoint for supply uncertainty for both list and detail view.",
    }


class Imports_uncertainty(FactBaseModel_uncertainty):
    location: str
    product: str
    product_origin: str  # Where the product comes from
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "import-uncertainty/": "Endpoint for import uncertainty for both list and detail view.",
    }


class Valuation_uncertainty(FactBaseModel_uncertainty):
    location: str
    product: str
    valuation: str
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "valuation-uncertainty/": "Endpoint for valuation uncertainty for both list and detail view.",
    }


class FinalUses_uncertainty(FactBaseModel_uncertainty):
    location: str
    product: str
    final_user: str  # Final use ctivity that uses the product
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "final-use-uncertainty/": "Endpoint for final-use uncertainty for both list and detail view.",
    }


class SUTAdjustments_uncertainty(FactBaseModel_uncertainty):
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
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "sut-adjustment-uncertainty/": "Endpoint for sut-adjustment uncertainty for both list and detail view.",
    }


class OutputTotals_uncertainty(FactBaseModel_uncertainty):
    location: str
    activity: str
    output_compartment: str  # Where the outputs are used
    unit: str
    value: float
    time: int
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "output-total-uncertainty/": "Endpoint for output-total uncertainty for both list and detail view.",
    }


class ValueAdded_uncertainty(FactBaseModel_uncertainty):
    location: str
    activity: str
    value_added_component: str  # Component of value added
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "value-added-uncertainty/": "Endpoint for value-added uncertainty for both list and detail view.",
    }


class SocialSatellite_uncertainty(FactBaseModel_uncertainty):
    location: str
    activity: str
    social_flow: str  # Type of social flow
    unit: str
    value: float
    time: int

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "social-satellite-uncertainty/": "Endpoint for social-satellite uncertainty for both list and detail view.",
    }


class ProductionVolumes_uncertainty(FactBaseModel_uncertainty):
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
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "production-volume-uncertainty/": "Endpoint for production-volume uncertainty for both list and detail view.",
    }


class Emissions_uncertainty(FactBaseModel_uncertainty):
    time: int
    year_emission: Optional[
        int
    ] = None  # TODO Rework into how we want to handle delayed emissions
    location: str
    activity: Optional[str] = None
    activity_unit: Optional[str] = None
    emission_substance: str
    compartment: str  # location of emission, such as "Emission to air"
    product: Optional[str] = None
    product_unit: Optional[str] = None
    value: float
    unit: str
    flag: Optional[str] = None

    elementary_type: str = Field(default="emission")

    def __str__(self) -> str:
        return f"{self.location}-{self.emission_substance}-{self.activity}-{self.activity_unit}-{self.time}-{self.value}-{self.unit}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "emission-uncertainty/": "Endpoint for emission uncertainty for both list and detail view.",
    }


class TransferCoefficient_uncertainty(FactBaseModel_uncertainty):  # Similar to use
    location: Optional[str] = None
    output_product: str
    input_product: str
    activity: str
    coefficient_value: float
    unit: str
    flag: Optional[
        str
    ] = None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    time: Optional[int] = None
    transfer_type: str  # Should be one of these three value: "product", "emission" or "waste" TODO Validator

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.coefficient_value}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "activity": ("bonsai", "activitytype"),
        "output_product": ("bonsai", "flowobject"),
        "input_product": ("bonsai", "flowobject"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "transfer-coefficient-uncertainty/": "Endpoint for transfer-coefficient uncertainty for both list and detail view.",
    }


class Resource_uncertainty(Emissions_uncertainty):
    def __init__(self, **data):
        super().__init__(**data)
        self.elementary_type = "resource"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "resource-uncertainty/": "Endpoint for resource uncertainty for both list and detail view.",
    }


class PackagingData_uncertainty(Supply_uncertainty):
    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "packaging_data"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "packaging-data-uncertainty/": "Endpoint for packaging-data uncertainty for both list and detail view.",
    }


class WasteUse_uncertainty(Use_uncertainty):
    waste_fraction: bool

    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "waste_use"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "waste-use-uncertainty/": "Endpoint for waste-use uncertainty for both list and detail view.",
    }


class WasteSupply_uncertainty(Supply_uncertainty):
    waste_fraction: bool

    def __init__(self, **data):
        super().__init__(**data)
        self.product_type = "waste_supply"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "product": ("bonsai", "flowobject"),
        "activity": ("bonsai", "activitytype"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "waste-supply-uncertainty/": "Endpoint for waste-supply uncertainty for both list and detail view.",
    }


class PropertyOfProducts_uncertainty(FactBaseModel_uncertainty):
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
        "property-of-product-uncertainty/": "Endpoint for property-of-product uncertainty for both list and detail view.",
    }


class Trade_uncertainty(FactBaseModel_uncertainty):
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
        "trade-uncertainty/": "Endpoint for trade uncertainty for both list and detail view.",
    }


class PopulationData_uncertainty(FactBaseModel_uncertainty):
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


class LCICoefficients_uncertainty(FactBaseModel_uncertainty):
    location: str
    flowobject: str
    ref_product: str
    activity: str
    value: float
    flowobject_unit: str
    ref_product_unit: str
    flowobject_compartment: Optional[str]
    flag: Optional[
        str
    ] = None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    time: Optional[int] = None
    table_type: str  # Should be one of these five value: "use", "supply", "resource", "emission" or "waste" TODO Validator

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.coefficient_value}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "activity": ("bonsai", "activitytype"),
        "product": ("bonsai", "flowobject"),
        "ref_product": ("bonsai", "flowobject"),
        "flowobject": ("bonsai", "flowobject"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "lci-coefficient-uncertainty/": "Endpoint for lci-coefficient uncertainty for both list and detail view.",
    }


class ProductionShares_uncertainty(FactBaseModel_uncertainty):
    location: str
    product: str
    activity: str
    sub_product: str
    value: float
    unit: str
    flag: Optional[
        str
    ] = None  # TODO flag rework. Can be uncertainty, can be other. Different meanings across data sources.
    time: int

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.coefficient_value}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("bonsai", "location"),
        "activity": ("bonsai", "activitytype"),
        "product": ("bonsai", "flowobject"),
        "sub_product": ("bonsai", "flowobject"),
    }
    _endpoints: ClassVar[Dict[str, str]] = {
        "production-shares-uncertainty/": "Endpoint for production-shares uncertainty for both list and detail view.",
    }
