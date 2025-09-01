from dataclasses import dataclass
from enum import Enum


class IndexNames(Enum):
    OJBECT_CODE = "object_code"
    PROD_CODE = "Exio prod code"
    ACT_CODE = "Exio act code"
    COUNTRY_CODE = "Exio country code"
    AGGREGATION = "Aggregation"
    SUBSTITUTION_FACTOR = "substitution factor"
    REPLACED_PRODUCT = "replaced product"
    REPL_FACTOR = "repl factor"
    PRODUCT = "product"
    PRODUCTION = "production"
    UNIT = "unit"
    VALUE = "Value"
    MARKET = "market"
    FLAG = "flag"
    ORIGIN_COUNTRY = "Exio origin country code"
    DESTIN_COUNTRY = "Exio destin. country code"
    FACTOR = "factor"
    SHARE = "share"
    EXIO3 = "nace-related code"
    EMIS_SUBSTANCE = "Exio substance"
    EMIS_COMPARTMENT = "Exio compartment"
    GLOBAL_AREA = "Global"
    RESOURCE = "Exio resource"
    EXIO_ACT = "Exiobase activity"  # TODO: used at the beginning in IEA when the workflow was not clear, to be replaced with "Exio act code"
    EXIO_CNT = "Exiobase country"
    EXIO_CNT_acron = "Exiobase cnt"
    EXIO_PRD = "Exiobase product"
    EXIO_CODE = "Exiobase code"
    DESCRIP = "description"
    REPLACED_MRK = "Replaced market"
    POSITION = "position"
    PACK_CODE = "exio4_pack_id"
    WASTE_FRACTION = "Exio waste"
    WASTE_MARKET = "Exio waste market"
    PACK_PROD = "Exio packaging prod code"
    PACKAGED = "Packaged product"
    PACK_MARKET = "Exio packaging market"
    INPUT_PROD = "Exio prod code (input)"
    VALUE_IN = "Value (input)"
    VALUE_FOOTPRINT = "Value (footprint)"
    UNIT_DESTIN = "unit (source)"
    UNIT_SOURCE = "unit (input)"
    UNIT_FOOTPRINT = "unit (footprint)"
    CLIMATE_METRIC = "climate metric"
    ANIMAL_CATEGORY = "animal categ"
    PERIOD = "time"
    AGRI_SYSTEM = "system"
    EXIO_ACCOUNT = "Account"
    NUTRIENT_CONT = "nutrient content"
    COEFFICIENT = "coeff"
    REF_PROD_CODE = "Exio ref. prod code"
    LCI_VALUE = "Value_lci"
    LCI_UNIT = "unit_lci"
    LCI_FLAG = "flag_lci"
    SOURCE = "source"
    SOURCE_CODE = "source_code"
    SOURCE_NAME = "source_name"
    SOURCE_CLASS = "source_class"
    SOURCE_LINK = "source_link"
    TARGET_CODE = "target_code"
    TARGET_NAME = "target_name"
    TARGET_CLASS = "target_class"
    TARGET_LINK = "target_link"
    PARENT_CODE = "parent_code"
    PARENT_NAME = "parent_name"
    PARENT_CLASS = "parent_class"
    PARENT_LINK = "parent_link"
    SCENARIO = "scenario"
    TRADE_ROUTE_ID = "trade route ID"
    TRANSPORT_MODE = "transport mode"
    EDGE = "edge"
    ORIGIN_COUNTRY_EDGE = "Exio origin country code edge"
    DESTIN_COUNTRY_EDGE = "Exio destin. country code edge"
    TRANSPORT_MODE_EDGE = "transport mode edge"
    EXIO3_ACT = "exio_v3"
    PERIOD_DELAY = "time delay"
    ASSOCIATED_TREAT = "associated treatment service"


class EmissCompartment(Enum):
    AIR = "Air"
    WATER = "Water"
    SOIL = "Soil"


class land_use_categ(Enum):
    sf_to_cp = "secondary forest to crop"
    pf_to_mf = "primary forest to managed forest"
    sf_to_mf = "secondary forest to managed forest"
    gr_to_ps = "grassland to pasture"
    int_cp = "intensification of cropland"
    int_ps = "intensification of pasture"
    unit_land = "ha-weighted"  # TODO: to be replaced by PropertyEnum.LAND.unit


class global_land_categ(Enum):
    arable = "Arable Land"
    forest = "Forest Land"
    grass = "Grassland"


class fao_categ(Enum):
    ITEM = "Item"
    ELEM = "Element"
    UNIT = "Unit"
    AREA = "Area"


class animal_system(Enum):
    MILK = "milk"
    MEAT = "meat"


class ipcc_categ(Enum):
    ef4_wet = "Wet climate"
    ef4_dry = "Dry climate"
    fract_leach_wet = "Wet climate"


@dataclass
class Property:
    name: str
    value: float
    unit: str
    upperbound: float | None = None
    lowerbound: float | None = None


class PropertyEnum(Enum):
    MASS = ("tonnes", Property)
    ENERGY = ("TJ", Property)
    CURRENCY = ("Meuro", Property)
    ITEM_COUNT = ("items", Property)
    WASTE_SERVICE = ("tonnes (service)", Property)
    LAND = ("ha-weighted", Property)
    FREIGHT = ("tkm", Property)
    NA = ("undefined", Property)

    def __init__(self, unit: str, cls: Property) -> None:
        self.unit = unit
        self.cls = cls

    def create_property(
        self, value, upperbound=float("inf"), lowerbound=float("-inf")
    ) -> Property:
        return self.cls(
            value=value,
            unit=self.unit,
            name=self.name,
            upperbound=upperbound,
            lowerbound=lowerbound,
        )


# TODO: Use service discovery tools when we get more endpoints. (@Fan)
class APIEndpoints(Enum):
    BASE_URL = "https://lca.aau.dk/api/"
    ACTIVITIES = "activity-names/"
    ACTIVITY_CORR = "activity-corr/"
    PRODUCTS = "products/"
    PRODUCT = "product/"  # TODO: use plural form (@Fan 2024-10-03 15:15:15)
    PRODUCT_CORR = "product-corr/"
    LOCATIONS = "locations/"
    LOCATION_CORR = "location-corr/"
    METADATA = "datasets/"
    FOOTPRINT = "footprint/"
    PROPERTIES = "properties/"
    SUPPLY = "supply/"
    USE = "use/"
    RECIPES = "recipes/"
    TOKEN = "user/token/"

    @classmethod
    def get_url(cls, name: str) -> str:
        """
        Return the full URL for a given endpoint name.

        Parameters:
        - name: The name of the endpoint to retrieve.

        Returns:
        - The full URL of the requested endpoint.
        """
        # Ensure the requested name is a valid enum member
        if name in cls.__members__:
            endpoint = cls[name].value
            # Special handling for BASE_URL
            if name == "BASE_URL":
                return endpoint
            return f"{cls.BASE_URL.value}{endpoint}"
        else:
            raise ValueError(f"{name} is not a valid API endpoint")


class Exio_fert_nutrients:
    nutrients = ["N", "P2O5", "K2O"]
    market_dict = {"N": "M_Nfert", "P2O5": "M_P2O5fert", "K2O": "M_K2Ofert"}


@dataclass
class data_index_categ:
    # data structure of emissions df
    emiss_categ = [
        IndexNames.COUNTRY_CODE.value,
        IndexNames.EMIS_SUBSTANCE.value,
        IndexNames.EMIS_COMPARTMENT.value,
        IndexNames.ACT_CODE.value,
        IndexNames.UNIT.value,
    ]

    # data  use and supply
    general_categ = [
        IndexNames.ORIGIN_COUNTRY.value,
        IndexNames.PROD_CODE.value,
        IndexNames.DESTIN_COUNTRY.value,
        IndexNames.ACT_CODE.value,
        IndexNames.UNIT.value,
    ]

    # data  use and supply
    trade_categ = [
        IndexNames.ORIGIN_COUNTRY.value,
        IndexNames.PROD_CODE.value,
        IndexNames.DESTIN_COUNTRY.value,
        IndexNames.UNIT.value,
    ]

    balance_categ = [
        IndexNames.ORIGIN_COUNTRY.value,
        IndexNames.PROD_CODE.value,
        IndexNames.DESTIN_COUNTRY.value,
        IndexNames.ACT_CODE.value,
    ]

    balance_columns = [
        IndexNames.VALUE.value,
        IndexNames.FLAG.value,
        IndexNames.UNIT.value,
    ]

    # data  use and supply
    column_categ = [IndexNames.VALUE.value, IndexNames.FLAG.value]

    pack_index = [
        IndexNames.ORIGIN_COUNTRY.value,
        IndexNames.PROD_CODE.value,
        IndexNames.DESTIN_COUNTRY.value,
        IndexNames.ACT_CODE.value,
        IndexNames.PACK_CODE.value,
    ]

    waste_sup_index = [
        IndexNames.ORIGIN_COUNTRY.value,
        IndexNames.PROD_CODE.value,
        IndexNames.DESTIN_COUNTRY.value,
        IndexNames.ACT_CODE.value,
        IndexNames.WASTE_FRACTION.value,
    ]

    waste_sup_col = [
        IndexNames.VALUE.value,
        IndexNames.FLAG.value,
        IndexNames.UNIT.value,
    ]

    fao_clean_index = [
        IndexNames.COUNTRY_CODE.value,
        fao_categ.ITEM.value,
        fao_categ.ELEM.value,
        fao_categ.UNIT.value,
    ]

    fao_animal_system_index = [
        IndexNames.COUNTRY_CODE.value,
        fao_categ.ITEM.value,
        fao_categ.ELEM.value,
        IndexNames.AGRI_SYSTEM.value,
        IndexNames.ANIMAL_CATEGORY.value,
        IndexNames.UNIT.value,
        IndexNames.PERIOD.value,
    ]
