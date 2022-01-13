################
# REQUIREMENTS #
################
# To import packages and modules to Jupyter notebook, you need to setup a conda environment. Here we call it `gpst`.
# ```
# conda create --name gpst
# conda install -c conda-forge pypsa pandapower jupyterlab
# pip install yaml vresutils==0.3.1
# ```
# Upgrade to pandapower to develop branch
# ```
# pip install git+git://github.com/e2nIEE/pandapower@develop
# ```
# To  add the kernel for the jupyter notebook
# ```
# pip install ipykernel
# ipython kernel install --user --name=gpst
# ```

# Open the jupyter lab notebook by typing `jupyter lab` in the terminal.


# %%
import os
import timeit
import pandas as pd

import numpy as np
import pandapower as pp
import pandapower.converter
        
import logging

logger = logging.getLogger(__name__)

from helpers import _sets_path_to_root
from helpers import compare_to_matpower
from helpers import make_name_to_index
from helpers import pypsa_validation
from helpers import add_nice_carrier_names
from helpers import load_costs

# Show all pandas columns in jupyter
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

# %%
# Optional. Take local PyPSA-Dev installation to make adjustments
print(os.getcwd())
pypsa_path = os.getcwd()+"/example-pypsa/PyPSA"  # requires to have `PyPSA` cloned in ~/power-flow-exercise/example_pypsa/<PyPSA>`
print(pypsa_path)
import sys
sys.path.insert(0, f"{pypsa_path}")

# %%
import pypsa

# %% [markdown]
# # Pandapower import of Matpower

# %%
net = pp.converter.from_mpc(os.path.join("reference-matpower", "RTS_GMLC.mat"))

# %%
net.sgen.drop(net.sgen[~net.sgen.in_service].index, inplace=True)  # TODO: check if this is correct (dropping not in_service elements from net.sgen
pp.runpp(net)
compare_to_matpower(net)  # Info: Will be saved in logger 'log.out'
make_name_to_index(net)


# # PyPSA import of Pandapower network
# %%
# Build empty PyPSA network
network = pypsa.Network()
# Import pandapower
network.import_from_pandapower_net(net, True, use_pandapower_index=True)
pypsa_validation(network, net)
n = network

# EXPORT AS CSV
path = os.path.join(os.getcwd(), "unsolved_network")
n.export_to_csv_folder(path)

# Run AC powerflow
# %%
# n.pf()


# Load costs and data modification 
# %%
costs = load_costs(Nyears=1., tech_costs=None, config=None, elec_config=None)
add_nice_carrier_names(n)

# Data  modifications
n.generators.loc[:,"carrier"] = "OCGT"
n.generators.loc[:,"capital_cost"] = costs.loc["OCGT", "capital_cost"]
n.generators.loc[:,"marginal_cost"] = costs.loc["OCGT", "marginal_cost"]
n.generators.loc[:,"lifetime"] = costs.loc["OCGT", "lifetime"]
n.generators.loc[:,"p_nom_extendable"] = True
n.lines.loc[:,'capital_cost'] = (n.lines['length'] * 1 * costs.at['HVAC overhead', 'capital_cost'])
n.lines.loc[:,"s_nom_extendable"] = True
n.transformers.loc[:,"s_nom_extendable"] = True
n.loads["p_set"] = n.loads["p_set"] * 2

# ### Constraints
# %%
from pypsa.linopf import (get_var, define_constraints, linexpr, join_exprs,
                          network_lopf, ilopf)
import yaml

# %%
### Loads raw config.yaml
path = os.getcwd()+"/example-pypsa/config.yaml"
with open(path, "r") as stream:
    try:
        config = yaml.safe_load(stream)
    except yaml.YAMLError as exc:
        print(exc)
config = config

# %%
def fix_bus_production(n, snapshots):
    total_demand = n.loads_t.p.sum().sum()
    prod_per_bus = linexpr((1, get_var(n, 'Generator', 'p'))).groupby(n.generators.bus, axis=1).apply(join_exprs)
    define_constraints(n, prod_per_bus, '>=', str(total_demand/1000), 'Bus', 'production_share')
    print(total_demand)
    print(prod_per_bus)

def extra_functionality(n, snapshots):
    fix_bus_production(n, snapshots)


# # Solve network
# %%
def solve_network(n, config, opts='',  **kwargs):
    solver_options = config['solving']['solver'].copy()
    solver_name = solver_options.pop('name')
    cf_solving = config['solving']['options']
    track_iterations = cf_solving.get('track_iterations', False)
    min_iterations = cf_solving.get('min_iterations', 4)
    max_iterations = cf_solving.get('max_iterations', 6)

    # add to network for extra_functionality
    n.config = config
    n.opts = opts

    if cf_solving.get('skip_iterations', False):
        network_lopf(n, solver_name=solver_name, solver_options=solver_options,
                     extra_functionality=extra_functionality, **kwargs)
    else:
        ilopf(n, solver_name=solver_name, solver_options=solver_options,
              track_iterations=track_iterations,
              min_iterations=min_iterations,
              max_iterations=max_iterations,
              extra_functionality=extra_functionality, **kwargs)
    return n

# Solver execution
from pathlib import Path
tmpdir = config['solving'].get('tmpdir')
if tmpdir is not None:
        Path(tmpdir).mkdir(parents=True, exist_ok=True)

n = solve_network(n, config=config,
                          solver_dir=tmpdir,)

# # Inspect PyPSA network before solving
# %%
logger.info("\n {}".format(n.snapshots))
logger.info("\n {}".format(n.global_constraints.to_string()))
logger.info("\n {}".format(n.carriers.to_string()))
logger.info("\n {}".format(n.generators.to_string()))
logger.info("\n {}".format(n.loads.to_string()))
logger.info("\n {}".format(n.lines.to_string()))
logger.info("\n {}".format(n.links.to_string()))
logger.info("\n {}".format(n.transformers.to_string()))
logger.info("\n {}".format(n.shunt_impedances.to_string()))

print("Summary in log.out file")

# EXPORT AS CSV
path = os.path.join(os.getcwd(), "solved_network")
n.export_to_csv_folder(path)