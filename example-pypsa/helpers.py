# support functions

import os
import numpy as np
import timeit
import pandas as pd
import pandapower as pp
import pandapower.converter
import logging

### PLANNING HELPERS
import yaml
from vresutils.costdata import annuity

# Optional. Take local PyPSA-Dev installation to make adjustments
pypsa_path = os.getcwd()+"/PyPSA"  # require to have `PyPSA` cloned in ~/power-flow-exercise/example_pandapower/<PyPSA>`
import sys
sys.path.insert(0, f"{pypsa_path}")
import pypsa


def _sets_path_to_root(root_directory_name):
    """
    Search and sets path to the given root directory (root/path/file).

    Parameters
    ----------
    root_directory_name : str
        Name of the root directory.
    n : int
        Number of folders the function will check upwards/root directed.

    """
    import os

    repo_name = root_directory_name
    n = 8  # check max 8 levels above. Random default.
    n0 = n

    while n >= 0:
        n -= 1
        # if repo_name is current folder name, stop and set path
        if repo_name == os.path.basename(os.path.abspath(".")):
            repo_path = os.getcwd()  # os.getcwd() = current_path
            os.chdir(repo_path)  # change dir_path to repo_path
            print("This is the repository path: ", repo_path)
            print("Had to go %d folder(s) up." % (n0 - 1 - n))
            break
        # if repo_name NOT current folder name for 5 levels then stop
        if n == 0:
            print("Cant find the repo path.")
        # if repo_name NOT current folder name, go one dir higher
        else:
            upper_path = os.path.dirname(
                os.path.abspath("."))  # name of upper folder
            os.chdir(upper_path)

_sets_path_to_root("power-flow-exercise")  # name of the git # n.generators_t.p_set = clone folder
# Set logger
logging.basicConfig(filename=os.path.join("example-pypsa", "log.out"),
                    filemode='w',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def check_net_ensure_unique_names(net):
    for elm in net.keys():
        if elm.startswith("_") or not isinstance(net[elm], pd.DataFrame) or len(net[elm]) == 0:
            continue
        # let's keep the bus names from mpc
        if elm in ['bus', 'gen', 'sgen']:
            continue
        net[elm]['name'] = [f"{elm}_{i}" for i in net[elm].index.values]
        # checking because in_service not supported by pypsa
        if 'in_service' in net[elm].columns:
            assert np.alltrue(net[elm]['in_service']), f"not in_service elements found in {elm}"
        # checking because switches are not supported by pypsa
        if elm == 'switch':
            assert np.alltrue(net[elm]['closed']), "open switches found"
        if elm == "trafo3w" and len(net[elm]) > 0:
            logger.warning("found trafo3w in net (not supported by pypsa converter!!!)")
        if elm == "shunt" and len(net[elm]) > 0:
            logger.warning("found shunt in net (not supported by pypsa converter!!!)")


def load_rts_grid():
    # Attention: PyPSA takes name as index!!!!! Must be unique!
    net = pp.converter.from_mpc(os.path.join("reference-matpower", "RTS_GMLC", "RTS_GMLC.mat"))
    # make bus name match MATPOWER bus name
    pp.toolbox.reindex_buses(net, net.bus.name + 1)
    assign_additional_data(net)

    # switching all sgens on to preserve information
    # net.sgen.drop(net.sgen[~net.sgen.in_service].index, inplace=True)
    net.sgen.in_service = True
    check_net_ensure_unique_names(net)
    pp.runpp(net)
    return net


def convert_to_pypsa(net):
    network = pypsa.Network()
    network.import_from_pandapower_net(net, True)

    # now let's check some basic infos
    assert len(network.buses) == len(net.bus)
    assert len(network.generators) == (len(net.gen) + len(net.sgen) + len(net.ext_grid))
    assert len(network.loads) == len(net.load)
    assert len(network.transformers) == len(net.trafo)
    # todo: shunt impedances are not supported
    # todo: trafo tap positions are not supported
    # todo: trafo3w are not supported
    return network


def assign_additional_data(net):
    net.bus.name = net._options["bus_name"]
    gen_lookup = net._options["gen_lookup"]
    gen_name = net._options["gen_name"]
    gen_lookup_gen = gen_lookup.query("element_type=='gen'")
    gen_lookup_sgen = gen_lookup.query("element_type=='sgen'")
    net.gen.loc[gen_lookup_gen.element.values, ['name', 'type', 'fuel']] = gen_name[gen_lookup_gen.index.values][:, [0, 1, 2]]
    net.sgen.loc[gen_lookup_sgen.element.values, ['name', 'type', 'fuel']] = gen_name[gen_lookup_sgen.index.values][:, [0, 1, 2]]


# # Comparing Pandapower to solved Matpower network
def compare_to_matpower(net):
    """
    Compares pandapower network to matpower network.
    """
    bus_results = pd.read_csv(os.path.join("reference-matpower", "RTS_GMLC","results", "bus.csv"), index_col=0)
    branch_results = pd.read_csv(os.path.join("reference-matpower", "RTS_GMLC", "results", "flow.csv"), index_col=0)

    # compare bus results
    # merged_results = pd.merge(bus_results, net.res_bus, how='inner', left_index=True, right_on=net.bus.id)
    merged_results = pd.merge(bus_results, net.res_bus, how='inner', left_index=True, right_on=net.bus.name)
    merged_results['diff_vm_pu'] = merged_results.v_mag - merged_results.vm_pu
    merged_results['diff_va_degree'] = merged_results.v_ang - merged_results.va_degree
    logger.info(f"\n{merged_results[['diff_vm_pu', 'diff_va_degree']].describe()}")

    # compare branch results
    merged_results_line = pd.merge(branch_results, net.res_line, how='inner', left_index=True, right_index=True)
    merged_results_line['diff_from_p_mw'] = merged_results_line.p_from_mw - merged_results_line.from_bus_inj_p
    merged_results_line['diff_to_p_mw'] = merged_results_line.p_to_mw - merged_results_line.to_bus_inj_p
    merged_results_line['diff_from_q_mvar'] = merged_results_line.q_from_mvar - merged_results_line.from_bus_inj_q
    merged_results_line['diff_to_q_mvar'] = merged_results_line.q_to_mvar - merged_results_line.to_bus_inj_q
    merged_results_line['diff_loss_p'] = merged_results_line.pl_mw - merged_results_line.loss_p
    cols = ['diff_from_p_mw', 'diff_to_p_mw', 'diff_from_q_mvar', 'diff_to_q_mvar', 'diff_loss_p']
    logger.info(f"\n{merged_results_line[cols].describe()}")


def make_name_to_index(net):
    """
    Makes name as index.
    
    PyPSA requires a unique name as index.
    """
    for elm in net.keys():
        if elm.startswith("_") or not isinstance(net[elm], pd.DataFrame) or len(net[elm]) == 0:
            continue
        # let's keep the bus names from mpc
        if elm == 'bus':
            continue
        net[elm]['name'] = [f"{elm}_{i}" for i in net[elm].index.values]
        # checking because in_service not supported by pypsa
        if 'in_service' in net[elm].columns:
            assert np.alltrue(net[elm]['in_service']), f"not in_service elements found in {elm}"
        # checking because switches are not supported by pypsa
        if elm == 'switch':
            assert np.alltrue(net[elm]['closed']), "open switches found"
        if elm == "trafo3w" and len(net[elm]) > 0:
            logger.warning("found trafo3w in net (not supported by pypsa converter!!!)")
        if elm == "shunt" and len(net[elm]) > 0:
            logger.warning("found shunt in net (not supported by pypsa converter!!!)")


def pypsa_validation(network, net):
    assert len(network.buses) == len(net.bus)
    assert len(network.generators) == (len(net.gen) + len(net.sgen) + len(net.ext_grid))
    assert len(network.loads) == len(net.load)
    assert len(network.transformers) == len(net.trafo)
    assert len(network.shunt_impedances) == len(net.shunt)
    logger.info("Validation successfull. No difference between pandapower and pypsa")


def load_costs(Nyears=1., tech_costs=None, config=None, elec_config=None):
    if tech_costs is None:
        tech_costs = os.getcwd()+"/example-pypsa/costs.csv"

    if config is None:
        ### Loads raw config.yaml
        path = os.getcwd()+"/example-pypsa/config.yaml"
        with open(path, "r") as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        config = config['costs']

    # set all asset costs and other parameters
    costs = pd.read_csv(tech_costs, index_col=list(range(3))).sort_index()

    # correct units to MW and EUR
    costs.loc[costs.unit.str.contains("/kW"),"value"] *= 1e3
    costs.loc[costs.unit.str.contains("USD"),"value"] *= config['USD2013_to_EUR2013']

    idx = pd.IndexSlice
    costs = (costs.loc[idx[:,config['year'],:], "value"]
             .unstack(level=2).groupby("technology").sum(min_count=1))

    costs = costs.fillna({"CO2 intensity" : 0,
                          "FOM" : 0,
                          "VOM" : 0,
                          "discount rate" : config['discountrate'],
                          "efficiency" : 1,
                          "fuel" : 0,
                          "investment" : 0,
                          "lifetime" : 25})

    costs["capital_cost"] = ((annuity(costs["lifetime"], costs["discount rate"]) +
                             costs["FOM"]/100.) *
                             costs["investment"] * Nyears)

    costs.at['OCGT', 'fuel'] = costs.at['gas', 'fuel']
    costs.at['CCGT', 'fuel'] = costs.at['gas', 'fuel']

    costs['marginal_cost'] = costs['VOM'] + costs['fuel'] / costs['efficiency']

    costs = costs.rename(columns={"CO2 intensity": "co2_emissions"})

    costs.at['OCGT', 'co2_emissions'] = costs.at['gas', 'co2_emissions']
    costs.at['CCGT', 'co2_emissions'] = costs.at['gas', 'co2_emissions']

    costs.at['solar', 'capital_cost'] = 0.5*(costs.at['solar-rooftop', 'capital_cost'] +
                                             costs.at['solar-utility', 'capital_cost'])

    return costs


def add_nice_carrier_names(n, config=None):
    if config is None:
        path = os.getcwd()+"/example-pypsa/config.yaml"
        with open(path, "r") as stream:
            try:
                config = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                print(exc)
        config = config

    carrier_i = n.carriers.index
    nice_names = (pd.Series(config['plotting']['nice_names'])
                  .reindex(carrier_i).fillna(carrier_i.to_series().str.title()))
    n.carriers['nice_name'] = nice_names
    colors = pd.Series(config['plotting']['tech_colors']).reindex(carrier_i)
    if colors.isna().any():
        missing_i = list(colors.index[colors.isna()])
        logger.warning(f'tech_colors for carriers {missing_i} not defined '
                       'in config.')
    n.carriers['color'] = colors