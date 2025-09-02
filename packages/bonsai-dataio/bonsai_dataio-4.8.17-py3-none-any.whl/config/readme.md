# json explanation

- to_database = False  # True if write the output to database serving lca.aau.dk
- only_capital_endog = False  # scenario b1+capital endog.
- iLUC: bool = False  # run iLUC model
- estimate_elect_data = False  # estimate electricity mix if IEA data is not complete
- data_ens = True  # replace DK energy data with ENS values

- rep_glo: bool = True  # if TRUE will report in the general report (in path_exio4)
- clear_loc: bool = (
    False  # if TRUE will delete the local report (in of exported files)
)
- # TODO: deprecate task status because they are not needed for workflow
    # run part of the main
-    rerun_fao: bool = False
-   faostat: bool = False  # run import of faostat data
-    prop_lay: bool = False  # new data on properties
-    ex_msuts: bool = False  # import Monetary Exiobase
-    footprint: bool = False  # calculate footprint in physical unit
-    prices: bool = False  # calculate new prices of products
-    iea: bool = False  # process IEA data
-    un_comm: bool = False  # import and process UN data
-    use: bool = False  # calculate raw values of use table
-    supply: bool = False  # calculate initial supply table
    # supply_manual = run_supply_manual
-    new_trade: bool = False  # import new trade data
-    waste: bool = False  # calculate waste data
-    lci: bool = False  # set to True if new LCI are added
-    emissions: bool = False  # set to True if emissions need to be calculated
-    hiot: bool = False  # calculate new hiot - basic version
-    capital: bool = False  # set to True if new matrix of investments
-    marg_elect: bool = False  # run the electricity marginal production
-    balan: bool = False  # run the balance
-    fish: bool = False  # new data on fishery supply (Faostat)
-    trade_route: bool = False  # trade route distances
-    lci_fish: bool = False  # new data on fishery model (2.-0 fishery model)
-    agri: bool = False  # new data from ari module
-    combust_diven_emiss: bool = (
        False  # calculate total direct and combustrion-driven emissions
    )
-    b2: bool = False  # run version for simaPRO
-    bug = False  # run the code to fix temporarily the bugs
-    exio_mon = (
        False  # set to True if new Exio monetary tables are used (for LCI coeffs)
    )
-    replace_NO3 = True  # replace_NO3_emissions_with_N
-    # set to true if the global market of fertilisers is added exogenously in the code
    glob_fert_mrk = True  # insert_glob_fert_market

- # choose GWPs (one has to be true)
    GWP_100 = True
    GWP_30 = False
    GWP_30_only = False

    # no need to change GWP_30
    run_also_GWP30 = False

    if GWP_100:
        gwp = 100
    elif GWP_30:
        gwp = 30
    elif GWP_30_only:
        gwp = 99