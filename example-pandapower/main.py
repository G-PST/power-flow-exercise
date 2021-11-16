import os
import pandas as pd
import pandapower as pp
import timeit

import logging

logging.basicConfig(filename='log.out',
                    filemode='w',
                    format='%(asctime)s %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.INFO)

logger = logging.getLogger(__name__)


def compare_to_matpower(net):
    bus_results = pd.read_csv(os.path.join("..", "reference-matpower", "results", "bus.csv"), index_col=0)
    branch_results = pd.read_csv(os.path.join("..", "reference-matpower", "results", "flow.csv"), index_col=0)

    # compare bus results
    merged_results = pd.merge(bus_results, net.res_bus, how='inner', left_index=True, right_on=net.bus.id)
    merged_results['diff_vm_pu'] = merged_results.v_mag - merged_results.vm_pu
    merged_results['diff_va_degree'] = merged_results.v_ang - merged_results.va_degree
    logger.info(f"\n{merged_results[['diff_vm_pu', 'diff_va_degree']].describe()}")


if __name__ == "__main__":
    logger.info("timing of loading of pandapower net from JSON")
    logger.info(timeit.timeit('_=pp.from_json("pandapower_net.json")', globals=globals(), number=1000))

    logger.info("loading pandapower net")
    net = pp.from_json("pandapower_net.json")

    logger.info("timing of saving of pandapower net to JSON")
    logger.info(timeit.timeit('pp.to_json(net, "temp.json")', globals=globals(), number=1000))

    logger.info('running power flow calculation')
    pp.runpp(net)

    logger.info('power flow calculation successful. validating results')
    compare_to_matpower(net)

    logger.info("timing for 1000 iterations:")

    logger.info(timeit.timeit("pp.runpp(net)", globals=globals(), number=1000))
