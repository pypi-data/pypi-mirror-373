import datetime
from typing import ClassVar, Dict, Optional, Tuple

from pydantic import Field, PrivateAttr

import dataio.schemas.bonsai_api.PPF_fact_schemas_uncertainty as PPF_fact_schemas_uncertainty
from dataio.schemas.bonsai_api.base_models import FactBaseModel_uncertainty


class PRODCOMProductionVolume(
    PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty
):
    indicator: str

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("geonumeric", "location"),
        "product": ("prodcom_total_2_0", "flowobject"),
    }  # Total production (ds-056121)

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class PRODCOMSoldProductionVolume(
    PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty
):
    indicator: str

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("geonumeric", "location"),
        "product": ("prodcom_sold_2_0", "flowobject"),
    }  # Sold production (ds-056120)

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class IndustrialCommodityStatistic(
    PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty
):

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("regex", "location"),
        "product": ("undata_ics", "flowobject"),
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class baseExternalSchemas(FactBaseModel_uncertainty):
    # Created with Sanders. Might Not be the base
    location: str
    time: int
    unit: str
    value: float
    comment: Optional[str] = None
    flag: Optional[str] = None


class ExternalMonetarySUT(baseExternalSchemas):
    table_type: str  # Supply or use table
    product_code: str
    product_name: str
    activity_code: str
    activity_name: str
    price_type: str = Field(  # Current price or previous year price.
        default="current prices"
    )
    consumer_price: bool = Field(default=False)  # Consumer price vs production price
    money_unit: Optional[str] = None  # Millions, billions etc.
    diagonal: Optional[bool] = None


# For annual data tables that start on a day other than January 1st. E.g. the fiscal year of India.
class BrokenYearMonetarySUT(ExternalMonetarySUT):
    time: datetime.date  # Start date of fiscal year


class EuropeanMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("cpa_2_1_lvl2", "flowobject"),
        "activity_code": ("nace_rev2", "activitytype"),
    }


class OldEuropeanMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("cpa_2008", "flowobject"),
        "activity_code": ("nace_rev2", "activitytype"),
    }


class OlderEuropeanMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("cpa_2008", "flowobject"),
        "activity_code": ("nace_rev1_1", "activitytype"),
    }


class InternationalMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("cpc_2_1", "flowobject"),
        "activity_code": ("isic_rev4", "activitytype"),
    }


class NACEMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("nace_rev2", "flowobject"),
        "activity_code": ("nace_rev2", "activitytype"),
    }


class OECDMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("cpa_2008", "flowobject"),
        "activity_code": ("isic_rev4", "activitytype"),
    }


class AfricanMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("africa_flow", "flowobject"),
        "activity_code": ("isic_africa", "activitytype"),
    }


class AustralianMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("suic", "flowobject"),
        "activity_code": ("anzsic_2006", "activitytype"),
    }


class USAMonetarySUT(ExternalMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("bea_prod", "flowobject"),
        "activity_code": ("bea_activ", "activitytype"),
    }


class EgyptianMonetarySUT(BrokenYearMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("cpc_1_1", "flowobject"),
        "activity_code": ("isic_rev4", "activitytype"),
    }


class IndianMonetarySUT(BrokenYearMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("india_sut", "flowobject"),
        "activity_code": ("india_sut", "activitytype"),
    }


class JapanMonetarySUT(BrokenYearMonetarySUT):
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product_code": ("japan_sut", "flowobject"),
        "activity": ("japan_sut", "activitytype"),
    }


class FAOstat(FactBaseModel_uncertainty):
    product_name: str
    product: str
    fao_element: str
    location: str
    time: int
    value: float
    unit: str
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("faostat", "location"),
        "product": ("faostat", "flowobject"),
    }


class FAOtrade(FactBaseModel_uncertainty):
    product_name: str
    product: str
    export_location: str  # Exporter
    import_location: str  # Importer
    time: int
    value: float
    unit: str
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("faostat", "location"),
        "partner": ("fao_area", "location"),
        "product": ("fao_items", "flowobject"),
    }


class UNdataEnergyBalance(FactBaseModel_uncertainty):
    activity: str
    product: str
    location: str
    time: int
    value: float
    unit: str
    comment: Optional[str] = None
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("iso_3166_1_numeric", "location"),
        "product": ("undata_energy_stats", "flowobject"),  # or prodcom_sold_2_0
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}"


class UNdataEnergyStatistic(FactBaseModel_uncertainty):
    activity: str
    product: str
    location: str
    time: int
    value: float
    unit: str
    comment: Optional[str] = None
    flag: Optional[str] = None
    conversion_factor: Optional[float] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("iso_3166_1_numeric", "location"),
        "product": ("undata_energy_stats", "flowobject_pair"),
        "activity": ("undata_energy_stats", "activitytype_pair"),
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}"


class BACITrade(FactBaseModel_uncertainty):
    time: int
    product: str
    export_location: str
    import_location: str
    value: float
    unit: str
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product": ("hs1992", "flowobject"),
        "export_location": ("iso_3166_1_numeric", "location"),
        "import_location": ("iso_3166_1_numeric", "location"),
    }


class USGSProductionVolume(PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty):

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("usgs", "location"),
        "product": ("usgs", "flowobject"),
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


# class StatCanChemProductionVolume(
#    PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty
# ):
#
#    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
#        "product": ("statcan_chemicals", "flowobject_pair"),
#        "activity": ("statcan_chemicals", "activitytype_pair"),
#        "location": ("iso_3166_1_alpha2", "location"),
#    }
#
#    def __str__(self) -> str:
#        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"
class StatCanChemProductionVolume(FactBaseModel_uncertainty):
    activity: Optional[str] = None
    product: str
    location: str
    time: int
    value: float
    unit: str
    comment: Optional[str] = None
    flag: Optional[str] = None
    conversion_factor: Optional[float] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("iso_3166_1_alpha2", "location"),
        "product": ("statcan_chemicals", "flowobject_pair"),
        "activity": ("statcan_chemicals", "activitytype_pair"),
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}"


class ComexTrade(FactBaseModel_uncertainty):
    time: int
    product: str
    activity: str
    export_location: str
    import_location: str
    value: float
    unit: str
    transport_mode: Optional[str] = None
    country_active_transport_mode: Optional[str] = None
    container: Optional[str] = None
    flag: Optional[str] = None

    def __str__(self) -> str:
        return f"{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product": ("comext", "flowobject"),
        "activity": ("comext", "activitytype"),
        "export_location": ("iso_3166_1_alpha2", "location"),
        "import_location": ("iso_3166_1_alpha2", "location"),
    }


class UNdataWDI(FactBaseModel_uncertainty):
    location: str
    time: int
    value: float
    unit: str
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("iso_3166_1_alpha3", "location"),
    }


class ProdcomTrade(FactBaseModel_uncertainty):
    time: int
    product: int
    export_location: str
    import_location: str
    value: float
    unit: str
    flag: Optional[str] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "product": ("prodcom_sold_2_0", "flowobject"),
        "export_location": ("geonumeric", "location"),
        "import_location": ("geonumeric", "location"),
    }


class UnfcccProductionVolume(
    PPF_fact_schemas_uncertainty.ProductionVolumes_uncertainty
):

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("iso_3166_1_alpha3", "location"),
        "product": (
            "unfccc_prodvol",
            "flowobject",
        ),  # I'd  add in the correspondence next sprint
    }

    def __str__(self) -> str:
        return f"{self.location}-{self.product}-{self.activity}-{self.time}-{self.value}-{self.unit}"


class ADBMonetaryIOT(baseExternalSchemas):
    supplier_name: str  # Supplying activity
    supplier_code: str
    user_name: str  # Using activity
    user_code: str
    price_type: str = Field(  # Current price or previous year price.
        default="current prices"
    )
    money_unit: Optional[str] = None  # Millions, billions etc.
    diagonal: Optional[bool] = None

    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "supplier_code": ("adb_supplier", "flow"),
        "user_code": ("adb_user", "flow"),
        "location": ("adb", "location"),
    }


class ExternalWaste(FactBaseModel_uncertainty):
    time: int
    location: str
    indicator: Optional[str] = None
    product: Optional[str] = None
    activity: str
    value: float
    unit: str
    comment: Optional[str] = None
    flag: Optional[str] = None

    # TODO needs update from Anne
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("", "location"),
        "product": ("", "flowobject"),
        "activity": ("", "activitytype"),
    }


class EurostatWaste(FactBaseModel_uncertainty):
    time: int
    location: str
    import_location: Optional[str] = None
    export_location: Optional[str] = None
    indicator: Optional[str] = None
    product: Optional[str] = None
    activity: str
    nace_r2: Optional[str] = None
    hazard: Optional[str] = None
    value: float
    unit: str
    comment: Optional[str] = None
    flag: Optional[str] = None

    # TODO needs update from Anne
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("", "location"),
        "product": ("", "flowobject"),
        "activity": ("", "activitytype"),
    }


class OECDWaste(FactBaseModel_uncertainty):
    time: int
    location: str
    indicator: Optional[str] = None
    product: Optional[str] = None
    activity: str
    property: Optional[str] = None
    economic_activity: Optional[str] = None
    value: float
    unit: str
    comment: Optional[str] = None
    flag: Optional[str] = None

    # TODO needs update from Anne
    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "location": ("", "location"),
        "product": ("", "flowobject"),
        "activity": ("", "activitytype"),
    }

    
class ComtradeEB10services(FactBaseModel_uncertainty):
    time: int            # period in YYYY, YYYYMM or YYYYMMDD string form
    import_location: str   # economy reporting the trade
    export_location: str      # counterpart economy (0 = world)
    product: str           # the product/commodity code within that system
    value: float
    unit: str
    flag: Optional[str] = None
    typeCode: Optional[str] = None
    freqCode: Optional[str] = None
    refPeriodID: Optional[str] = None
    refYear: Optional[int] = None
    refMonth: Optional[int] = None
    period: Optional[str] = None
    reporterCode: Optional[str] = None
    reporterISO: Optional[str] = None
    reporterDesc: Optional[str] = None
    flowCode: Optional[str] = None
    flowDesc: Optional[str] = None
    partnerCode: Optional[str] = None
    partnerISO: Optional[str] = None
    partnerDesc: Optional[str] = None
    partner2Code: Optional[str] = None
    partner2ISO: Optional[str] = None
    partner2Desc: Optional[str] = None
    classificationCode: Optional[str] = None
    classificationSearchCode: Optional[str] = None
    isOriginalClassification: Optional[float] = None
    cmdCode: Optional[str] = None
    cmdDesc: Optional[str] = None
    aggrLevel: Optional[int] = None
    isLeaf: Optional[bool] = None
    customsCode: Optional[str] = None
    customsDesc: Optional[str] = None
    mosCode: Optional[str] = None
    motCode: Optional[str] = None
    qtyUnitCode: Optional[str] = None
    qtyUnitAbbr: Optional[str] = None
    qty: Optional[float] = None
    isQtyEstimated: Optional[bool] = None
    altQtyUnitCode: Optional[str] = None
    altQtyUnitAbbr: Optional[str] = None
    altQty: Optional[float] = None
    isAltQtyEstimated: Optional[bool] = None
    netWgt: Optional[float] = None
    isNetWgtEstimated: Optional[bool] = None
    grossWgt: Optional[float] = None
    isGrossWgtEstimated: Optional[bool] = None
    cifvalue: Optional[float] = None
    fobvalue: Optional[float] = None
    primaryValue: Optional[float] = None
    legacyEstimationFlag: Optional[str] = None
    isReported: Optional[bool]  = None
    isAggregate: Optional[bool] = None



    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "import_location": ("ISO_3166_1_numeric", "location"),
        "export_location": ("ISO_3166_1_numeric", "location"),
        "product": ("eb10", "flowobject"),
    }


class ComtradeEB10servicesExt(FactBaseModel_uncertainty):
    time: int            # period in YYYY, YYYYMM or YYYYMMDD string form
    import_location: str   # economy reporting the trade
    export_location: str      # counterpart economy (0 = world)
    product: str           # the product/commodity code within that system
    value: float
    unit: str
    flag: Optional[str] = None
    typeCode: Optional[str] = None
    freqCode: Optional[str] = None
    refPeriodID: Optional[str] = None
    refYear: Optional[int] = None
    refMonth: Optional[int] = None
    period: Optional[str] = None
    reporterCode: Optional[str] = None
    reporterISO: Optional[str] = None
    reporterDesc: Optional[str] = None
    flowCode: Optional[str] = None
    flowDesc: Optional[str] = None
    partnerCode: Optional[str] = None
    partnerISO: Optional[str] = None
    partnerDesc: Optional[str] = None
    partner2Code: Optional[str] = None
    partner2ISO: Optional[str] = None
    partner2Desc: Optional[str] = None
    classificationCode: Optional[str] = None
    classificationSearchCode: Optional[str] = None
    isOriginalClassification: Optional[float] = None
    cmdCode: Optional[str] = None
    cmdDesc: Optional[str] = None
    aggrLevel: Optional[int] = None
    isLeaf: Optional[bool] = None
    customsCode: Optional[str] = None
    customsDesc: Optional[str] = None
    mosCode: Optional[str] = None
    motCode: Optional[str] = None
    qtyUnitCode: Optional[str] = None
    qtyUnitAbbr: Optional[str] = None
    qty: Optional[float] = None
    isQtyEstimated: Optional[bool] = None
    altQtyUnitCode: Optional[str] = None
    altQtyUnitAbbr: Optional[str] = None
    altQty: Optional[float] = None
    isAltQtyEstimated: Optional[bool] = None
    netWgt: Optional[float] = None
    isNetWgtEstimated: Optional[bool] = None
    grossWgt: Optional[float] = None
    isGrossWgtEstimated: Optional[bool] = None
    cifvalue: Optional[float] = None
    fobvalue: Optional[float] = None
    primaryValue: Optional[float] = None
    legacyEstimationFlag: Optional[str] = None
    isReported: Optional[bool]  = None
    isAggregate: Optional[bool] = None



    _classification: ClassVar[Dict[str, Tuple[str, str]]] = {
        "import_location": ("ISO_3166_1_numeric", "location"),
        "export_location": ("ISO_3166_1_numeric", "location"),
        "product": ("eb10s", "flowobject"),

    }

