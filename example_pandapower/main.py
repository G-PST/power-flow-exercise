import os
import timeit
import pandas as pd

import logging

import numpy as np
import pandapower as pp
import pandapower.converter
import pandapower.plotting
import pandapower.timeseries
import pandapower.control

logging.basicConfig(  # filename=os.path.join("example_pandapower", "log.out"),
    # filemode='w',
    format='%(asctime)s %(name)s %(levelname)s %(message)s',
    datefmt='%H:%M:%S',
    level=logging.INFO)

logger = logging.getLogger(__name__)

try:
    import pypsa
except ImportError:
    logger.info("failed to import pypsa!")


def compare_to_matpower(net):
    bus_results = pd.read_csv(os.path.join("reference-matpower", "results", "bus.csv"), index_col=0)
    branch_results = pd.read_csv(os.path.join("reference-matpower", "results", "flow.csv"), index_col=0)

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


def process_rts_grid(net):
    # Attention: PyPSA takes name as index!!!!! Must be unique!
    # make bus name match MATPOWER bus name
    pp.toolbox.reindex_buses(net, net.bus.name + 1)
    assign_additional_data(net)
    pp.runpp(net)

    # zone information
    net.bus.loc[net.bus.index < 200, 'zone'] = 1
    net.bus.loc[(net.bus.index >= 200) & (net.bus.index < 300), 'zone'] = 2
    net.bus.loc[net.bus.index >= 300, 'zone'] = 3
    pp.add_column_from_node_to_elements(net, 'zone', replace=True, elements=['load', 'gen', 'sgen'])

    # add data for installed power sn_mva
    for element in ('gen', 'sgen', 'load'):
        net[element]["sn_mva"] = net[element]["p_mw"]
        net[element]["p_mw"] = 0
        net[element]["scaling"] = 1

    # switching all sgens on to preserve information
    # net.sgen.drop(net.sgen[~net.sgen.in_service].index, inplace=True)
    net.sgen.in_service = True

    # set up distributed slack
    slack_type = ["CC", "CT", "STEAM", "NUCLEAR"]
    net.gen.loc[net.gen.type.isin(slack_type), "slack_weight"] = net.gen.loc[net.gen.type.isin(slack_type), "sn_mva"]
    net.ext_grid.slack_weight = 0
    pp.set_user_pf_options(net, distributed_slack=True)

    check_net_ensure_unique_names(net)
    set_up_geodata(net)


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
    net.gen.loc[gen_lookup_gen.element.values, ['name', 'type', 'fuel']] = gen_name[gen_lookup_gen.index.values][:,
                                                                           [0, 1, 2]]
    net.sgen.loc[gen_lookup_sgen.element.values, ['name', 'type', 'fuel']] = gen_name[gen_lookup_sgen.index.values][:,
                                                                             [0, 1, 2]]


def set_up_geodata(net):
    pp.plotting.create_generic_coordinates(net)
    pp.plotting.set_line_geodata_from_bus_geodata(net)
    pp.plotting.geo.convert_geodata_to_gis(net)


def create_controllers_gen_sgen(net, category, path):
    filename = f"DAY_AHEAD_{category}.csv"
    file = os.path.join(path, filename)
    profiles = pd.read_csv(file)
    unnecessary = ['Year', 'Month', 'Day', 'Period']
    profiles.drop(np.intersect1d(unnecessary, profiles.columns), axis=1, inplace=True)

    ds = pp.timeseries.DFData(profiles)

    gen_index = net.gen.loc[net.gen.name.isin(profiles.columns)].index

    if len(gen_index) > 0:
        pp.control.ConstControl(net, element='gen', variable='p_mw', element_index=gen_index,
                                data_source=ds, profile_name=net.gen.loc[gen_index, 'name'].values)

    sgen_index = net.sgen.loc[net.sgen.name.isin(profiles.columns)].index

    if len(sgen_index) > 0:
        pp.control.ConstControl(net, element='sgen', variable='p_mw', element_index=sgen_index,
                                data_source=ds, profile_name=net.sgen.loc[sgen_index, 'name'].values)

    assert set(net.gen.loc[gen_index, 'name'].values) | set(net.sgen.loc[sgen_index, 'name'].values) == set(
        profiles.columns)
    assert len(set(net.gen.loc[gen_index, 'name'].values) & set(net.sgen.loc[sgen_index, 'name'].values)) == 0


def create_controllers_load(net, category, path):
    filename = f"DAY_AHEAD_{category}.csv"
    file = os.path.join(path, filename)
    profiles = pd.read_csv(file)
    unnecessary = ['Year', 'Month', 'Day', 'Period']
    profiles.drop(np.intersect1d(unnecessary, profiles.columns), axis=1, inplace=True)

    scale_factor = pd.Series(index=net.load.index, dtype=np.float64)
    for i in range(1, 4):
        idx = net.load.zone == i
        scale_factor[idx] = net.load.loc[idx, 'sn_mva'] / net.load.loc[idx, 'sn_mva'].sum()

    assert np.isclose(scale_factor.sum(), 3, atol=1e-6, rtol=0)

    ds = pp.timeseries.DFData(profiles)

    pp.control.ConstControl(net, element='load', variable='p_mw', element_index=net.load.index,
                            data_source=ds, profile_name=net.load.zone.values.astype(str),
                            scale_factor=scale_factor.values)


def set_up_ow(net, time_steps, output_path=None):
    ow = pp.timeseries.OutputWriter(net, time_steps=time_steps, output_path=output_path,
                                    output_file_type=".csv", # csv_separator=",",
                                    log_variables=list())

    ow.log_variable('res_bus', 'vm_pu')
    ow.log_variable('res_line', 'loading_percent')
    ow.log_variable('res_line', 'i_ka')
    ow.log_variable('res_ext_grid', 'p_mw')

    for element in ['load', 'gen', 'sgen']:
        categories = net[element].type.unique()
        for category in categories:
            for i in range(1, 4):
                ow.log_variable(f"res_{element}", 'p_mw', index=net[element].query("zone==@i & type==@category").index,
                                eval_function=np.nansum, eval_name=f"{element}_{category}_{i}")

    if output_path is not None and not os.path.exists(output_path):
        os.mkdir(output_path)

    return ow


def timings():
    logger.info("timing of loading of pandapower net from JSON")
    # logger.info(timeit.timeit('_=pp.from_json(os.path.join("example_pandapower", "pandapower_net.json"))', globals=globals(), number=1000))
    logger.info(
        timeit.timeit('_=pp.converter.from_mpc(os.path.join("reference-matpower", "RTS_GMLC.mat"))', globals=globals(),
                      number=100))
    logger.info("timing of saving of pandapower net to JSON")
    # logger.info(timeit.timeit('pp.to_json(net, os.path.join("example_pandapower", "temp.json"))', globals=globals(), number=1000))
    logger.info(
        timeit.timeit('pp.converter.to_mpc(net, os.path.join("example_pandapower", "temp.mpc"))', globals=globals(),
                      number=100))
    logger.info('running power flow calculation')
    pp.runpp(net, enforce_q_lims=False)

    logger.info('power flow calculation successful. validating results')
    compare_to_matpower(net)
    logger.info("timing for 1000 iterations:")

    logger.info(timeit.timeit("pp.runpp(net)", globals=globals(), number=1000))


if __name__ == "__main__":
    # from example_pandapower.main import *
    logger.info("loading pandapower net")
    net = pp.converter.from_mpc(os.path.join("reference-matpower", "RTS_GMLC", "RTS_GMLC.mat"))
    process_rts_grid(net)

    ts_path = os.path.join("reference-matpower", "RTS_GMLC", "timeseries_data")
    for category in ['hydro', 'Natural_Inflow', 'pv', 'rtpv', 'wind']:
        create_controllers_gen_sgen(net, category, ts_path)
    create_controllers_load(net, 'regional_Load', ts_path)

    time_steps=range(24*30)
    ow = set_up_ow(net, time_steps)

    pp.timeseries.run_timeseries(net, time_steps=time_steps)

