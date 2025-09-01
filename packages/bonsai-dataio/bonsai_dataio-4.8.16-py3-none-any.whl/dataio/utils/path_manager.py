from datetime import datetime
from pathlib import Path
from typing import Optional

from dataio.utils.accounts import AccountRepository
from dataio.utils.versions import VersionCollection


class PathBuilder:
    """
    PathBuilder provides shorthand paths for files on a cloud storage specified by `root_path` to be used by the algorithms
    to create the full exiobase database.

    You can provide a version_source so that you can link to files of previous versions.
    Please resort to `default_version` for the structure of the version file.

    for entries that are not specified in the dictionary, the path to the latest available version is generated.

    Additionally, it is possible to provide the path to an alternative version file that is used instead of the standard one.
    """

    def __init__(
        self,
        root_path: str | Path,
        version_repo: VersionCollection = None,
        account_repository: AccountRepository = None,
    ):
        if not isinstance(root_path, Path):
            root_path = Path(root_path)
        self.root_path = root_path
        self.bonsai_root = self.root_path / "_bonsai"
        if not self.bonsai_root.exists():
            print("bonsai_root is ", self.bonsai_root)
            self.bonsai_root = self.root_path

            if not self.bonsai_root.exists():
                raise FileNotFoundError(
                    f"Root path <{self.bonsai_root}> is not set correctly. Please reinstantiate"
                )

        self.exiobase4 = self.bonsai_root / "_b Next version" / "Exiobase_4"
        self.correspondence = (
            self.bonsai_root / "Classification and other data" / "corrspondence"
        )
        self.classification = (
            self.bonsai_root / "Classification and other data" / "classifications_exiob"
        )
        self.data_collection = self.bonsai_root / "collect"
        self.data_clean = self.bonsai_root / "clean"
        self.versions = version_repo
        self.account_repo = account_repository

    @property
    def merged_collected_data(self) -> Path:
        return self.data_collection / "Merged_data"

    def compose(
        self,
        path: Path,
        account_name: Optional[str] = None,
        version_date: Optional[str] = "latest",
    ) -> Path:
        """Ensures a path exists by creating it if necessary.

        This method constructs a path by appending optional account and version date
        components. If the account name is provided, it retrieves the account, adding
        it if it doesn't exist. The version date can be specified or default to the
        latest version. The final path is created if it does not already exist.

            Parameters
            ----------
            path : Path
                The base path to compose.
            account_name : Optional[str], optional
                The account name to include in the path.
            If the account does not exist, it will be added. Defaults to None.
            version_date : Optional[str], optional
                The version date to include in the path.
            It can be "latest" to use the latest version date, a specific date in
            "YYYY-MM-DD" format, or None to exclude the version date. Defaults to "latest".

            Returns
            -------
            Path
                The composed path, created if it didn't already exist.
            Raises
            ------
                KeyError: If the account name is not found in the account repository.
                ValueError: If the provided version date is invalid.
        """
        path_components = [path]
        if account_name:
            try:
                account = self.account_repo.get_account(name=account_name)
            except KeyError:
                print(f"{account_name} not found in accounts")
                account = self.account_repo.add_account(account_name)
            path_components.append(account.name)

            if version_date == "latest":
                version = self.versions.get_latest_version(account.name)
                parsed_version_date = datetime.strptime(
                    version.version_date, "%Y-%m-%d"
                ).strftime("%Y%m%d")
            elif version_date and version_date != "latest":
                try:
                    self.versions.update_account_version_date(
                        account.name, version_date
                    )
                except ValueError:
                    self.versions.add_account_version(
                        account_name=account.name, version_date=version_date
                    )
                parsed_version_date = datetime.strptime(
                    version_date, "%Y-%m-%d"
                ).strftime("%Y%m%d")
            elif version_date is None:
                parsed_version_date = ""

            path_components.append(parsed_version_date)

        elif not account_name:

            if version_date == "latest":
                parsed_version_date = datetime.strptime(
                    version_date, "%Y-%m-%d"
                ).strftime("%Y%m%d")
                path_components.append(parsed_version_date)
            elif version_date and version_date != "latest":
                parsed_version_date = datetime.strptime(
                    version_date, "%Y-%m-%d"
                ).strftime("%Y%m%d")
            elif version_date is None:
                parsed_version_date = ""
            path_components.append(parsed_version_date)
        final_path = Path(*path_components)
        final_path.mkdir(
            parents=True, exist_ok=True
        )  # Create the path if it doesn't exist
        # TODO: append the final path to PathRepository
        return final_path

    def _construct_version(self, account: str) -> str:
        version = self.versions.get_latest_version(account)
        return datetime.strptime(version.version_date, "%Y-%m-%d").strftime("%Y%m%d")

    @property
    def supply_raw(self):
        date_supply = self._construct_version("supply")
        folder_supply = "supply_" + date_supply
        return self.compose(
            self.exiobase4 / "Supply" / "Raw" / folder_supply,
            version_date=None,
        )

    @property
    def supply_intermediate(self):
        date_supply_interm = self._construct_version("supply intermediate")
        folder_supply_final = "supply_" + date_supply_interm
        return self.compose(
            self.exiobase4 / "Supply" / "Intermediate" / folder_supply_final,
            version_date=None,
        )

    @property
    def balance_raw(self):
        date_supply_interm = self._construct_version("supply intermediate")
        return self.compose(
            self.exiobase4 / "Balanced" / date_supply_interm,
            version_date=None,
        )

    @property
    def use_raw(self):
        date_use = self._construct_version("use")
        folder_use_raw = "use_" + date_use
        return self.compose(
            self.exiobase4 / "Use" / "Raw" / folder_use_raw,
            version_date=None,
        )

    @property
    def use_intermediate(self):
        date_use_interm = self._construct_version("use intermediate")
        folder_use_final = "use_" + date_use_interm
        return self.compose(
            self.exiobase4 / "Use" / "Intermediate" / folder_use_final,
            version_date=None,
        )

    @property
    def hiot_raw(self):
        date_hiot = self._construct_version("hiot")
        folder_hiot_raw = "Raw_" + date_hiot
        return self.compose(
            self.exiobase4 / "HIOT" / "Raw" / folder_hiot_raw,
            version_date=None,
        )

    @property
    def hiot_interm(self):
        date_hiot = self._construct_version("hiot")
        return self.compose(
            self.exiobase4 / "HIOT" / "Intermediate" / date_hiot,
            version_date=None,
        )

    @property
    def prod_markets(self):
        date_prod_markets = self._construct_version("market of products")
        folder_prod_markets = "product_markets_" + date_prod_markets
        return self.compose(
            self.exiobase4 / "Markets" / "Raw" / folder_prod_markets,
            version_date=None,
        )

    @property
    def trade_raw(self):
        date_trade_merged = self._construct_version("trade_merged")
        folder_trade_raw = "raw_data_" + date_trade_merged
        return self.compose(
            self.exiobase4 / "Trade" / "Raw" / folder_trade_raw,
            version_date=None,
        )

    @property
    def trade_intermediate(self):
        date_trade_int = self._construct_version("trade intermediate")
        folder_trade_int = "trade_" + date_trade_int
        return self.compose(
            self.exiobase4 / "Trade" / "Intermediate" / folder_trade_int,
            version_date=None,
        )

    @property
    def emissions_intermediate(self):
        date_emissions = self._construct_version("emissions")
        folder_emissions = "emissions_" + date_emissions
        return self.compose(
            self.exiobase4 / "Emissions" / "Intermediate" / folder_emissions,
            version_date=None,
        )

    @property
    def emissions_raw(self):
        date_emissions = self._construct_version("emissions")
        folder_emissions = "emissions_" + date_emissions
        return self.compose(
            self.exiobase4 / "Emissions" / "Raw" / folder_emissions,
            version_date=None,
        )

    @property
    def emissions_coeff(self):
        return self.correspondence.parent / "Emissions_coeffs"

    @property
    def fao_collection(self):
        return self.data_collection / "Faostat"

    @property
    def fao_processed(self):
        return self.data_collection / "Faostat" / "processed"

    @property
    def fao_store(self):
        return self.data_collection / "Faostat" / "store"

    @property
    def ferts_collection(self):
        return self.data_collection / "Fertiliser data"

    @property
    def iLUC_param(self):
        return self.data_collection / "iLUC"

    @property
    def dm_coeff(self):
        return self.data_collection / "Dry_matter"

    @property
    def iLUC_raw(self):
        date_iluc = self._construct_version("iluc")
        folder_iLUC = "Input_data_" + date_iluc
        return self.compose(
            self.exiobase4 / "iLUC" / "Raw" / folder_iLUC,
            version_date=None,
        )

    @property
    def iLUC_interm(self):
        date_iluc = self._construct_version("iluc")
        folder_iLUC = "Derived_data_" + date_iluc
        return self.compose(
            self.exiobase4 / "iLUC" / "Intermediate" / folder_iLUC,
            version_date=None,
        )

    @property
    def land_use(self):
        date_land = self._construct_version("land use")
        folder_land_use = "Raw_" + date_land
        return self.compose(
            self.exiobase4 / "Land" / "Raw" / folder_land_use,
            version_date=None,
        )

    @property
    def fertilisers(self):
        date_ferts = self._construct_version("fertilisers_prod")
        folder_fers = "Raw_" + date_ferts
        return self.compose(
            self.exiobase4 / "Fertilisers" / "Raw" / folder_fers,
            version_date=None,
        )

    @property
    def fert_interm(self):
        date_ferts = self._construct_version("fertilisers_prod")
        folder_fers = "Raw_" + date_ferts
        return self.compose(
            self.exiobase4 / "Fertilisers" / "Intermediate" / folder_fers,
            version_date=None,
        )

    @property
    def property_param(self):
        date_property = self._construct_version("property matrix")
        folder_proper = "Raw_" + date_property
        return self.compose(
            self.exiobase4 / "Properties" / folder_proper, version_date=None
        )

    @property
    def ipcc_param(self):
        return self.data_collection / "IPCC"

    @property
    def gams_inputs(self):
        return self.data_collection / "GAMS" / "data_source_for_GAMS"

    @property
    def corresp_fao(self):
        return self.correspondence / "fao"

    @property
    def hiot_with_iluc(self):
        date_hiot = self._construct_version("hiot")
        folder_iluc_out = "source_data_" + date_hiot
        return self.compose(
            self.exiobase4 / "HIOT" / "HIOT_with_iluc" / folder_iluc_out,
            version_date=None,
        )

    @property
    def hiot_with_marg_elect(self):
        date_hiot = self._construct_version("hiot")
        folder_elec_out = "source_data_" + date_hiot
        return self.compose(
            self.exiobase4 / "HIOT" / "HIOT_with_marg_electricity" / folder_elec_out,
            version_date=None,
        )

    @property
    def hiot_with_capital(self):
        date_hiot = self._construct_version("hiot")
        folder_capital_out = "source_data_" + date_hiot

        return self.compose(
            self.exiobase4 / "HIOT" / "b2_version" / folder_capital_out,
            version_date=None,
        )

    @property
    def value_added(self):
        date_hiot = self._construct_version("hiot")
        folder_value_added = "source_data_" + date_hiot

        return self.compose(
            self.exiobase4 / "HIOT" / "value_added" / folder_value_added,
            version_date=None,
        )

    @property
    def matrix_of_invest(self):
        date_hiot = self._construct_version("hiot")
        folder_capital_mat = "source_data_" + date_hiot
        return self.compose(
            self.exiobase4
            / "HIOT"
            / "b2_version"
            / "matrix_investments"
            / folder_capital_mat,
            version_date=None,
        )

    @property
    def iea_clean(self):
        return self.data_clean / "IEA"

    @property
    def iea_raw_exio(self):
        date_iea = self._construct_version("IEA")
        folder_iea = "raw_data_" + date_iea
        return self.compose(
            self.exiobase4 / "IEA" / "Raw" / folder_iea, version_date=None
        )

    @property
    def iea_interm(self):
        date_iea = self._construct_version("IEA")
        folder_iea_interm = "iea_data_" + date_iea
        return self.compose(
            self.exiobase4 / "IEA" / "Intermediate" / folder_iea_interm,
            version_date=None,
        )

    @property
    def lci_raw(self):
        return self.data_collection / "LCI"

    @property
    def lci_cleaned(self):
        return self.compose(self.data_clean, account_name="LCI", version_date=None)

    @property
    def lci_vehicles(self):
        return (
            self.data_collection
            / "Product_statistics"
            / "Vehicles"
            / "ready_for_exiobase"
        )

    @property
    def lci_products(self):
        return self.data_collection / "Product_statistics"

    @property
    def lci_concito(self):
        return self.data_collection / "Concito_DB"

    @property
    def lci_exio4(self):
        date_use = self._construct_version("use")
        folder_lci = "Raw_" + date_use
        return self.compose(
            self.exiobase4 / "Product_statistics" / folder_lci,
            version_date=None,
        )

    @property
    def heat_markets(self):
        date_heatmarket = self._construct_version("heatmarket")
        folder_heatmarket = "heat_markets_" + date_heatmarket
        return self.compose(
            self.exiobase4 / "Markets" / "Raw" / folder_heatmarket,
            version_date=None,
        )

    @property
    def fish_markets(self):
        date_fish = self._construct_version("fish prod mix")
        folder_fishmarket = "fish_prod_mix_" + date_fish
        return self.compose(
            self.exiobase4 / "Markets" / "Raw" / folder_fishmarket,
            version_date=None,
        )

    @property
    def waste_accounts(self):
        date_waste = self._construct_version("waste supply")
        folder_waste = "Raw_" + date_waste
        return self.compose(
            self.exiobase4 / "Waste" / "Raw" / folder_waste,
            version_date=None,
        )

    @property
    def waste_markets(self):
        date_wastemarkets = self._construct_version("waste markets")
        folder_waste_markets = "waste_markets_" + date_wastemarkets
        return self.compose(
            self.exiobase4 / "Markets" / "Raw" / folder_waste_markets,
            version_date=None,
        )

    @property
    def monetary_tables(self):
        return self.data_collection / "MRSUT_2016"

    @property
    def property_values(self):
        date_property = self._construct_version("property matrix")
        folder_property = "Raw_" + date_property
        return self.compose(
            self.exiobase4 / "Properties" / folder_property,
            version_date=None,
        )

    @property
    def prices(self):
        return self.compose(
            self.exiobase4,
            account_name="prices",
            version_date="latest",
        )

    @property
    def cleaned_exio_3(self):
        return self.compose(self.data_clean / "Exiobase_v3", version_date=None)

    @property
    def un_data(self):
        return self.compose(self.data_collection / "UN_commodities", version_date=None)

    @property
    def un_data_elab(self):
        date_un = self._construct_version("UNcd")
        folder_un = "intermediate_" + date_un
        return self.compose(self.exiobase4 / "UN_data" / folder_un, version_date=None)

    @property
    def b2_version(self):
        date_hiot = self._construct_version("hiot")
        folder_b2_version = "data_" + date_hiot
        return self.compose(
            self.exiobase4 / "HIOT" / "b2_simapro_version" / folder_b2_version,
            version_date=None,
        )

    @property
    def outlier(self):
        date_hiot = self._construct_version("hiot")
        folder_outlier = "version_" + date_hiot
        return self.compose(
            self.exiobase4 / "analyses" / "outlier_analysis" / folder_outlier
        )

    @property
    def simapro(self) -> Path:
        return self.compose(self.exiobase4 / "SimaPro")

    @property
    def cement(self):
        # TODO: Why cement have the same version as hiot?
        date_hiot = self._construct_version("hiot")
        folder_cement = "version_" + date_hiot
        return self.compose(
            self.exiobase4 / "parameterized_functions" / "cement" / folder_cement
        )

    @property
    def cement_data(self):
        return self.compose(self.exiobase4 / "parameterized_functions" / "cement_data")

    @property
    def natural_resource(self) -> Path:
        date_raw = self._construct_version("natural_resource")
        folder_res = "raw_data_" + date_raw
        return self.compose(
            self.exiobase4 / "Resource_extraction" / folder_res,
            version_date=None,
        )

    @property
    def cleaned_fao(self) -> Path:
        return self.data_clean / "Faostat" / "new format"

    @property
    def cleaned_forestry(self):
        date_forestry = self._construct_version("forestry")
        folder_fores = "cleaned_data_" + date_forestry
        return self.compose(
            self.exiobase4 / "Faostat" / "forestry" / folder_fores,
            version_date=None,
        )

    @property
    def lci_fish(self):
        date_lci_fish = self._construct_version("lci_fish")
        folder_lci_fish = "raw_data_" + date_lci_fish
        return self.compose(
            self.exiobase4 / "LCI" / "aquaculture" / folder_lci_fish,
            version_date=None,
        )

    @property
    def fao_raw(self):
        date_lci_fish = self._construct_version("lci_fish")
        folder_fao = "raw_data_" + date_lci_fish
        return self.compose(self.exiobase4 / "Faostat" / folder_fao, version_date=None)

    @property
    def lci_country(self):
        return self.exiobase4 / "LCI" / "country_activ_specific"

    @property
    def lci_act_generic(self):
        return self.exiobase4 / "LCI" / "default_act_specific"

    @property
    def lci_prod_generic(self):
        return self.exiobase4 / "LCI" / "default_prod_specific"

    @property
    def trade_route(self):
        date_trade_route = self._construct_version("trade_route")
        folder_trade_route = "trade_route_" + date_trade_route
        return self.compose(
            self.exiobase4 / "trade_route" / "raw" / folder_trade_route,
            version_date=None,
        )

    def list_path_attributes(self):
        import inspect

        paths = []
        for name, _ in inspect.getmembers(
            self.__class__, lambda v: isinstance(v, property)
        ):
            paths.append(name)
        return paths
