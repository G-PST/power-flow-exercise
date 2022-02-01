import os
import timeit
import pandas as pd

import pypsa

import numpy as np
import pandapower as pp
import pandapower.converter

import logging

logging.basicConfig(#filename=os.path.join("example_pandapower", "log.out"),
                    #filemode='w',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


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
    net.gen.loc[gen_lookup_gen.element.values, ['name', 'type']] = gen_name[gen_lookup_gen.index.values][:, [0, 1]]
    net.sgen.loc[gen_lookup_sgen.element.values, ['name', 'type']] = gen_name[gen_lookup_sgen.index.values][:, [0, 1]]


if __name__ == "__main__":
    logger.info("timing of loading of pandapower net from JSON")
    # logger.info(timeit.timeit('_=pp.from_json(os.path.join("example_pandapower", "pandapower_net.json"))', globals=globals(), number=1000))
    logger.info(timeit.timeit('_=pp.converter.from_mpc(os.path.join("reference-matpower", "RTS_GMLC.mat"))', globals=globals(), number=100))

    logger.info("loading pandapower net")
    # net = pp.from_json(os.path.join("example_pandapower", "pandapower_net.json"))
    net = pp.converter.from_mpc(os.path.join("reference-matpower", "RTS_GMLC.mat"))
    # must be clarified why this is necessary, also slope is still undefined so it is not enough to solve the error:
    # net.pwl_cost.points = net.pwl_cost.points.apply(lambda x: list(zip(x[::2], x[1::2])))
    net.pwl_cost.drop(net.pwl_cost.index, inplace=True)
    pp.runpp(net)

    logger.info("timing of saving of pandapower net to JSON")
    # logger.info(timeit.timeit('pp.to_json(net, os.path.join("example_pandapower", "temp.json"))', globals=globals(), number=1000))
    logger.info(timeit.timeit('pp.converter.to_mpc(net, os.path.join("example_pandapower", "temp.mpc"))', globals=globals(), number=100))

    logger.info('running power flow calculation')
    pp.runpp(net, enforce_q_lims=False)

    logger.info('power flow calculation successful. validating results')
    compare_to_matpower(net)

    logger.info("timing for 1000 iterations:")

    logger.info(timeit.timeit("pp.runpp(net)", globals=globals(), number=1000))
