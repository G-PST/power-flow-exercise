#!/usr/bin/env python
# coding: utf-8

# # Imports and helper functions

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
# 
# Open the jupyter lab notebook by typing `jupyter lab` in the terminal.
# 



# In[2]:

import cartopy.crs as ccrs
import os
import timeit
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import pandapower as pp
import pandapower.converter
import yaml
import re
        
import logging

logger = logging.getLogger(__name__)

from helpers import _sets_path_to_root
from helpers import add_nice_carrier_names
from helpers import load_costs
from helpers import load_rts_grid
from helpers import convert_to_pypsa
from matplotlib.patches import Circle, Ellipse
from matplotlib.legend_handler import HandlerPatch
from pathlib import Path
    

# Show all pandas columns in jupyter
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)


# In[3]:


# Optional. Take local PyPSA-Dev installation to make adjustments
print(os.getcwd())
pypsa_path = os.getcwd()+"/example-pypsa/PyPSA"  # require to have `PyPSA` cloned in ~/power-flow-exercise/example_pypsa/<PyPSA>`
print(pypsa_path)
import sys
sys.path.insert(0, f"{pypsa_path}")


# In[4]:


import pypsa
from pypsa.linopf import (get_var, define_constraints, linexpr, join_exprs,
                            network_lopf, ilopf)


# # Pandapower import of Matpower

# In[5]:

_sets_path_to_root("power-flow-exercise")
net=load_rts_grid()


# # Scenarios

# In[67]:


d = {
    "scenario": [
    "RTS_GMLC_base", # no expansion but opf
    "RTS_GMLC_base+line_expansion",  # line expansion and opf
    "RTS_GMLS_base+gen_expansion",  # generation expansion and constraints, and opf
    "RTS_GMLS_base+gen_and_line_expansion",  # generation expansion and constraints, line expansion and opf
    "RTS_GMLS_1p5xload+0emission+gen_and_line_expansion",  # generation expansion and constraints, line expansion, load growth, "net 0" CO2 constraint and opf
    ],
    "co2_budget": [np.inf, np.inf, np.inf, np.inf, 0],  # sets the total CO2 budget tCO2/kWh in the energy system, i.e. np.inf = unlimited, 0 = net-zero
    "gen_expansion": [False, False, True, True, True],
    "line_expansion": [False, True, False, True, True],
    "load_scale": [1, 1, 1, 1, 1.5],  # multiplies load by factor 1.5 = 150%
    "nodal_constraint": [False, False, False, False, True],  # nodal constraint. At least x% of the demand must be locally supplied
    "total_transmission_limit": [False, False, False, False, False]
    # "res_scale": [100, 100, 100, 100, 100],  # multiplies the installable amount by a factor
    # "expansion_per_line": [np.inf, np.inf, np.inf, np.inf, np.inf],       
}

scenarios = pd.DataFrame(data=d)


for i in scenarios.index:
    scenario = scenarios.loc[i, "scenario"]
    co2_budget = scenarios.loc[i, "co2_budget"]
    gen_expansion = scenarios.loc[i, "gen_expansion"]
    line_expansion = scenarios.loc[i, "line_expansion"]
    load_scale = scenarios.loc[i, "load_scale"]
    nodal_constraint = scenarios.loc[i, "nodal_constraint"]
    total_transmission_limit = scenarios.loc[i, "total_transmission_limit"]


    # In[ ]:

    n_1_constraint = 0.7  # p_pu_max... max. 70% of line available for use
    expansion_limit_per_line = np.inf # i.e. 0.25 will lead limit the expansion per line by 25%, np.inf
    ll_type = "c"  # only relevant total_transmission_limit = true, optimization either for total c = cost or v = volume
    factor = "opt"  # only relevant total_transmission_limit = true, opt = as much expansion, alternatives "1.5" = 150% total expansion limit
    Nyears = "1"
    o = "EQ0.3"  #  only active if nodal_constraint = True, EQ0.3 == 30% of demand needs to be supplied locally at node
    res_scale = 100
    load_shedding = False
    hydro_expansion = False
    nuclear_expansion = False


    # ## Update pypsa network

    # and convert to pypsa
    network=convert_to_pypsa(net)
    n = network


    # ### prepare pandapower network for pypsa

    # In[6]:


    net.gen.loc[:, "fuel"] = net.gen["fuel"].replace({
            "Oil": "oil",
            "Coal": "coal",
            "Nuclear": "nuclear",
            "Hydro": "hydro",
        })
        
    ccgt_condition = (net.gen["fuel"]=="NG") & (net.gen["type"]=="CC")
    ocgt_condition = (net.gen["fuel"]=="NG") & (net.gen["type"]=="CT")
    sync_condition = (net.gen["fuel"]=="Sync_Cond")  
    net.gen.loc[ccgt_condition, "fuel"] = net.gen.loc[ccgt_condition, "fuel"].replace({"NG": "CCGT",})
    net.gen.loc[ocgt_condition, "fuel"] = net.gen.loc[ocgt_condition, "fuel"].replace({"NG": "OCGT",})
    net.gen = net.gen.drop(net.gen[sync_condition].index)  # remove sync_cond


    # In[7]:


    net.sgen.loc[:, "fuel"] = net.sgen["fuel"].replace({
            "Oil": "oil",
            "Coal": "coal",
            "Nuclear": "nuclear",
            "Hydro": "hydro",
            "Solar": "solar",
            "Wind": "onwind",
        })

    ccgt_condition = (net.sgen["fuel"]=="NG") & (net.sgen["type"]=="CC")
    ocgt_condition = (net.sgen["fuel"]=="NG") & (net.sgen["type"]=="CT")
    storage_condition = (net.sgen["fuel"]=="Storage")  

    net.sgen.loc[ccgt_condition, "fuel"] = net.sgen.loc[ccgt_condition, "fuel"].replace({"NG": "CCGT",})
    net.sgen.loc[ocgt_condition, "fuel"] = net.sgen.loc[ocgt_condition, "fuel"].replace({"NG": "OCGT",})
    net.sgen = net.sgen.drop(net.sgen[storage_condition].index)  # remove storage

    # Load costs and data modification 

    # In[8]:

    costs = load_costs(Nyears=1., tech_costs=None, config=None, elec_config=None)


    # Add carrier and static data

    # In[9]:


    carriers = ["oil", "coal", "OCGT", "CCGT", "nuclear", "hydro", "solar-rooftop", "solar-utility", "onwind", "hydrogen"]
    n.madd("Carrier", carriers)
    add_nice_carrier_names(n)  # updates n.carriers


    # In[10]:


    # add co2 emissions per carrier and custom carrier
    n.carriers.loc[:,"co2_emissions"] = list(n.carriers["co2_emissions"].index.map(costs.co2_emissions))
    n.carriers.loc[n.carriers.index=="hydrogen","color"] = "#89CFF0"
    n.carriers.loc[n.carriers.index=="hydrogen","co2_emissions"] = 0.0
    n.carriers.loc[n.carriers.index=="hydrogen","nice_name"] = "Fuel Cell"


    # In[11]:


    # update carriers according to pandapower
    n.generators.loc[:, "carrier"].update(net.gen.set_index("name")["fuel"]) 
    n.generators.loc[:, "carrier"].update(net.sgen.set_index("name")["fuel"])


    # In[12]:


    # add solar carrier
    n.generators.loc[n.generators.index.str.contains('RTPV')==True, "carrier"] = "solar-rooftop"
    n.generators.loc[n.generators.index.str.contains('_PV')==True, "carrier"] = "solar-utility"


    # In[13]:


    # Drop empty or not used carrier
    empty_carrier_condition = (n.generators.carrier.isin(carriers)==False)
    n.generators = n.generators.drop(n.generators[empty_carrier_condition].index)


    # In[14]:


    # Update line voltage according to bus
    n.lines["v_nom"] = 1
    n.lines["v_nom"] = n.lines["bus0"].map(n.buses.v_nom)


    # Add timeseries from RTS-GMLC

    # In[15]:


    load_path = os.path.join(os.getcwd(), "example-pypsa/timeseries_files/Load/bus_load.csv") 
    utpv_path = os.path.join(os.getcwd(), "example-pypsa/timeseries_files/PV/DAY_AHEAD_pv.csv")
    rtpv_path = os.path.join(os.getcwd(), "example-pypsa/timeseries_files/RTPV/DAY_AHEAD_rtpv.csv")
    wind_path = os.path.join(os.getcwd(), "example-pypsa/timeseries_files/Wind/DAY_AHEAD_wind.csv")
    hydro_path = os.path.join(os.getcwd(), "example-pypsa/timeseries_files/Hydro/DAY_AHEAD_hydro.csv")


    # In[16]:


    utpv_series = pd.read_csv(utpv_path)
    utpv_series.rename(columns={"Period": "Hour"}, errors="raise",inplace=True)
    utpv_series.index = pd.to_datetime(utpv_series[['Year', 'Month', 'Day','Hour']])
    utpv_series = utpv_series.drop(columns=['Year', 'Month', 'Day','Hour'])
    utpv_series_pu = utpv_series/utpv_series.max()
    utpv_series_max_potential = utpv_series.max() * res_scale


    # In[17]:


    rtpv_series = pd.read_csv(rtpv_path)
    rtpv_series.rename(columns={"Period": "Hour"}, errors="raise",inplace=True)
    rtpv_series.index = pd.to_datetime(rtpv_series[['Year', 'Month', 'Day','Hour']])
    rtpv_series = rtpv_series.drop(columns=['Year', 'Month', 'Day','Hour'])
    rtpv_series_pu = rtpv_series/rtpv_series.max()
    rtpv_series_max_potential = rtpv_series.max() * res_scale


    # In[18]:


    wind_series = pd.read_csv(wind_path)
    wind_series.rename(columns={"Period": "Hour"}, errors="raise",inplace=True)
    wind_series.index = pd.to_datetime(wind_series[['Year', 'Month', 'Day','Hour']])
    wind_series = wind_series.drop(columns=['Year', 'Month', 'Day','Hour'])
    wind_series_pu = wind_series/wind_series.max()
    wind_series_max_potential = wind_series.max() * res_scale


    # In[19]:


    hydro_series = pd.read_csv(hydro_path)
    hydro_series.rename(columns={"Period": "Hour"}, errors="raise",inplace=True)
    hydro_series.index = pd.to_datetime(hydro_series[['Year', 'Month', 'Day','Hour']])
    hydro_series = hydro_series.drop(columns=['Year', 'Month', 'Day','Hour'])
    hydro_series_pu = hydro_series/hydro_series.max()
    hydro_series_max_potential = hydro_series.max() * res_scale


    # In[20]:


    load_series = pd.read_csv(load_path)
    load_series["DateTime"] = pd.to_datetime(load_series["DateTime"])
    load_series.set_index("DateTime", inplace=True)
    load_series = load_series * load_scale
    load_series.columns = [element.upper() for element in load_series.columns] 


    # In[21]:


    snapshots = hydro_series_pu.index
    n.set_snapshots(snapshots)

    n.madd("Generator",
        utpv_series_pu.columns,
        bus=utpv_series_pu.columns,
        p_nom_extendable=True,
        p_max_pu=utpv_series_pu,
        p_nom_max=utpv_series_max_potential)

    n.madd("Generator",
        rtpv_series_pu.columns,
        bus=rtpv_series_pu.columns,
        p_nom_extendable=True,
        p_max_pu=rtpv_series_pu,
        p_nom_max=rtpv_series_max_potential)

    n.madd("Generator",
        wind_series_pu.columns,
        bus=wind_series_pu.columns,
        p_nom_extendable=True,
        p_max_pu=wind_series_pu,
        p_nom_max=wind_series_max_potential)

    n.madd("Generator",
        hydro_series_pu.columns,
        bus=hydro_series_pu.columns,
        p_nom_extendable=False,
        p_max_pu=hydro_series_pu,
        p_nom_max=hydro_series_max_potential)

    n.madd("Generator",
        n.buses.index,
        suffix=" Fuel Cell",
        carrier="hydrogen",
        bus=n.buses.index,
        capital_cost=200000,
        marginal_cost=130,
        lifetime=25,
        efficiency=0.4,
        p_nom_extendable=True,)

    n.mremove("Load", n.loads.index)
    n.madd("Load",
        load_series.columns,
        bus=load_series.columns,
        p_set=load_series)

    # load shedding
    if load_shedding:
        n.add("Carrier", "load")
        buses_i = n.buses.query("carrier == 'AC'").index
        n.madd("Generator", buses_i, " load",
                bus=buses_i,
                carrier='load',
                sign=1, # Adjust sign to measure p and p_nom in kW instead of MW
                # intersect between macroeconomic and surveybased
                # willingness to pay
                # http://journal.frontiersin.org/article/10.3389/fenrg.2015.00055/full
                p_nom=1e4 # kW
                )
        n.generators.loc[n.generators.carrier == "load", "marginal_cost"] = 1e6 # = 10000ct/kWh, could not be set with n.madd


    # # Planning exercise

    # ### Preparation

    # Update the network dataframe with corresponding costs and technical data

    # In[22]:


    # partly hacky update since n.madd did not update the imported pandapower network components

    n.generators.loc[:,"capital_cost"] = n.generators["carrier"].map(costs.capital_cost)
    n.generators.loc[:,"marginal_cost"] = n.generators["carrier"].map(costs.marginal_cost)
    n.generators.loc[:,"lifetime"] = n.generators["carrier"].map(costs.lifetime)
    n.generators.loc[:,"efficiency"] = n.generators["carrier"].map(costs.efficiency)
    n.generators.loc[:, "p_nom"] = abs(n.generators.loc[:, "p_set"])
    n.generators.loc[:, "p_set"] = 0.0
    n.generators.loc[n.generators.carrier=="solar-utility", "p_nom_max"] = utpv_series_max_potential
    n.generators.loc[n.generators.carrier=="solar-rooftop", "p_nom_max"] = rtpv_series_max_potential
    n.generators.loc[n.generators.carrier=="hydro", "p_nom_max"] = hydro_series_max_potential
    n.generators.loc[n.generators.carrier=="onwind", "p_nom_max"] = wind_series_max_potential

    n.generators.loc[n.generators.carrier=="hydrogen", "capital_cost"] = 100000
    n.generators.loc[n.generators.carrier=="hydrogen", "marginal_cost"] = 1000
    n.generators.loc[n.generators.carrier=="hydrogen", "lifetime"] = 25
    n.generators.loc[n.generators.carrier=="hydrogen", "efficiency"] = 0.4

    n.lines.loc[:,"lifetime"] = costs.at['HVAC overhead', 'lifetime']
    n.lines.loc[n.lines.v_nom <= 138, "length"] = n.lines.loc[n.lines.v_nom <= 138, "r"] / n.line_types.loc["305-AL1/39-ST1A 110.0"].r_per_length
    n.lines.loc[n.lines.v_nom > 138, "length"] = n.lines.loc[n.lines.v_nom > 138, "r"] / n.line_types.loc["Al/St 240/40 2-bundle 220.0"].r_per_length
    n.lines.loc[:,"capital_cost"] = (n.lines["length"] * n.lines["terrain_factor"] * costs.at["HVAC overhead", "capital_cost"])

    # hard fix
    n.lines.loc["line_104", "r"] = 1.
    n.lines.loc["line_104", "b"] = 0.000147


    # In[23]:


    # Variables included in the capacity expansion
    # partly hacky update since n.madd did not update the imported pandapower network components
    n.lines.loc[:,"s_nom_extendable"] = line_expansion
    n.transformers.loc[:,"s_nom_extendable"] = True
    n.generators.loc[:,"p_nom_extendable"] = gen_expansion
    n.generators.loc[n.generators.carrier == "hydro","p_nom_extendable"] = hydro_expansion
    n.generators.loc[n.generators.carrier == "nuclear","p_nom_extendable"] = nuclear_expansion


    # ### Constraints

    # In[25]:


    ### Loads raw config.yaml
    path = os.getcwd()+"/example-pypsa/config.yaml"
    with open(path, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    config = config


    # In[26]:


    def add_co2limit(n, co2limit, Nyears=1.):

        n.add("GlobalConstraint", "CO2Limit",
            carrier_attribute="co2_emissions", sense="<=",
            constant=co2limit * Nyears)

    def set_line_s_max_pu(n, s_max_pu = 0.7):
        n.lines['s_max_pu'] = s_max_pu
        logger.info(f"N-1 security margin of lines set to {s_max_pu}")

    def set_transmission_limit(n, ll_type, factor, costs, Nyears=1):

        _lines_s_nom = (np.sqrt(3) * n.lines.type.map(n.line_types.i_nom) *
                    n.lines.num_parallel *  n.lines.bus0.map(n.buses.v_nom))
        lines_s_nom = n.lines.s_nom.where(n.lines.type == '', _lines_s_nom)

        col = 'capital_cost' if ll_type == 'c' else 'length'
        ref = (lines_s_nom @ n.lines[col])

        if factor == 'opt' or float(factor) > 1.0:
            n.lines['s_nom_min'] = lines_s_nom
            n.lines['s_nom_extendable'] = True

        if factor != 'opt':
            con_type = 'expansion_cost' if ll_type == 'c' else 'volume_expansion'
            rhs = float(factor) * ref
            n.add('GlobalConstraint', f'l{ll_type}_limit',
                type=f'transmission_{con_type}_limit',
                sense='<=', constant=rhs, carrier_attribute='AC, DC')



    add_co2limit(n, co2_budget)
    set_line_s_max_pu(n, n_1_constraint)
    n.lines["s_nom_max"] = n.lines["s_nom"] * expansion_limit_per_line  # per line expansion limit

    if total_transmission_limit:
        set_transmission_limit(n, ll_type, factor, costs, Nyears)


    # In[27]:


    def add_EQ_constraints(n, o, scaling=1e-1):
        float_regex = "[0-9]*\.?[0-9]+"
        level = float(re.findall(float_regex, o)[0])
        ggrouper = n.generators.bus
        lgrouper = n.loads.bus
        load = n.snapshot_weightings.generators @            n.loads_t.p_set.groupby(lgrouper, axis=1).sum()
        lhs_gen = linexpr((n.snapshot_weightings.generators * scaling,
                        get_var(n, "Generator", "p").T)
                ).T.groupby(ggrouper, axis=1).apply(join_exprs)
        lhs_gen = lhs_gen[lhs_gen.index.isin(n.loads.bus)]
        lhs = lhs_gen
        rhs = scaling * ( level * load)
        rhs = rhs[rhs.index.isin(lhs.index)]
        define_constraints(n, lhs, ">=", rhs, "equity", "min")

    def extra_functionality(n, snapshots):
        if nodal_constraint:
            add_EQ_constraints(n, o)


    # # Solve network

    # In[28]:

    print(f"solve {scenario}")
    def solve_network(n, config, opts='', **kwargs):
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


    # In[29]:

    tmpdir = config['solving'].get('tmpdir')
    if tmpdir is not None:
            Path(tmpdir).mkdir(parents=True, exist_ok=True)

    #%debug
    n = solve_network(n, config=config, solver_dir=tmpdir,)


    ###map.py von Fabian
    """
    Network expansion plotting functions.
    """

    __author__ = "Fabian Neumann (KIT)"
    __copyright__ = "Copyright 2019-2020 Fabian Neumann (KIT), GNU GPL 3"


    def make_handler_map_to_scale_circles_as_in(ax, dont_resize_actively=False):
        fig = ax.get_figure()

        def axes2pt():
            return np.diff(ax.transData.transform([(0, 0), (1, 1)]), axis=0)[0] * (
                300.0 / fig.dpi
            )

        ellipses = []
        if not dont_resize_actively:

            def update_width_height(event):
                dist = axes2pt()
                for e, radius in ellipses:
                    e.width, e.height = 2.0 * radius * dist

            fig.canvas.mpl_connect("resize_event", update_width_height)
            ax.callbacks.connect("xlim_changed", update_width_height)
            ax.callbacks.connect("ylim_changed", update_width_height)

        def legend_circle_handler(
            legend, orig_handle, xdescent, ydescent, width, height, fontsize
        ):
            w, h = 2.0 * orig_handle.get_radius() * axes2pt()
            e = Ellipse(
                xy=(0.5 * width - 0.5 * xdescent, 0.5 * height - 0.5 * ydescent),
                width=w,
                height=w,
            )
            ellipses.append((e, orig_handle.get_radius()))
            return e

        return {Circle: HandlerPatch(patch_func=legend_circle_handler)}


    def make_legend_circles_for(sizes, scale=1.0, **kw):
        return [Circle((0, 0), radius=(s / scale) ** 0.5, **kw) for s in sizes]


    def add_legend(ax, bus_factor, branch_factor):

        handles = []
        labels = []
        for s in (0.1, 0.5, 1):
            handles.append(
                plt.Line2D([0], [0], color="rosybrown", linewidth=s * 1e3 / branch_factor)
            )
            labels.append(f"{s} GW")
        l1 = ax.legend(
            handles,
            labels,
            loc="upper left",
            bbox_to_anchor=(0, 0),
            frameon=False,
            labelspacing=0.8,
            handletextpad=1.5,
            title="HVAC Line Capacity",
        )
        ax.add_artist(l1)

        handles = []
        labels = []
        for s in (2, 5, 10):
            handles.append(
                plt.Line2D(
                    [0], [0], color="darkseagreen", linewidth=s * 1 / branch_factor
                )
            )
            labels.append(f"{s} GW")


        handles = []
        labels = []
        if "Load" in n.carriers.index:
            n.carriers = n.carriers.drop("Load")
        for name, carrier in n.carriers.iterrows():
            handles.append(
                plt.Line2D(
                    [0], [0], color=carrier.color, marker="o", markersize=8, linewidth=0
                )
            )
            labels.append(carrier.nice_name)
        l3 = ax.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.58, -0.0),  # bbox_to_anchor=(0.72, -0.05),
            handletextpad=0.0,
            columnspacing=0.5,
            ncol=2,
            title="Technology",
            frameon=False,
        )
        ax.add_artist(l3)

        circles = [1, 0.5, 0.1]
        handles = make_legend_circles_for(circles, scale=bus_factor, facecolor="lightgray")
        labels = [f"{int(s/0.1)} MW" for s in circles]
        l4 = ax.legend(
            handles,
            labels,
            loc="upper left",
            bbox_to_anchor=(0.82, 0.0),
            frameon=False,
            labelspacing=1.5,
            title="Generation",
            handler_map=make_handler_map_to_scale_circles_as_in(ax, True),
        )
        ax.add_artist(l4)


    def plot_network1(n, fn=None):

        bus_factor = 2e5
        branch_factor = 1e2

        fields = ["bus", "carrier", "p_nom_opt"]
        pie_components = pd.concat(
            [
                n.generators.loc[n.generators.carrier != "load", fields],
                n.storage_units[fields],
            ]
        )
        bus_sizes = pie_components.groupby(["bus", "carrier"]).p_nom_opt.sum() / bus_factor

        def clip(df, thres=0.0):
            return df.where(df > thres, other=0.0)

        line_widths = clip(n.lines.s_nom) / branch_factor
        link_widths = clip(n.links.p_nom) / branch_factor
        line_widths_opt = clip(n.lines.s_nom_opt) / branch_factor

        fig, ax = plt.subplots(
            figsize=(11, 11), subplot_kw={"projection": ccrs.PlateCarree()}
        )

        n.plot(
            ax=ax,
            bus_sizes=bus_sizes,
            color_geomap=None,
            bus_alpha=0.7,
            line_widths=line_widths_opt,
            line_colors="#dddddd",
        )

        n.plot(
            ax=ax,
            geomap=False,
            bus_sizes=0,
            line_widths=line_widths,
            link_widths=link_widths,
            color_geomap=None,
        )

        add_legend(ax, bus_factor, branch_factor)

        if fn is not None:
            plt.savefig(fn, bbox_inches="tight")
            
            
    plot_network1(n, fn=os.path.join(os.getcwd(), f"optimized_network_{scenario}"))


    # In[31]:


    ###map.py von Fabian
    """
    Network expansion plotting functions.
    """

    __author__ = "Fabian Neumann (KIT)"
    __copyright__ = "Copyright 2019-2020 Fabian Neumann (KIT), GNU GPL 3"


    def make_handler_map_to_scale_circles_as_in(ax, dont_resize_actively=False):
        fig = ax.get_figure()

        def axes2pt():
            return np.diff(ax.transData.transform([(0, 0), (1, 1)]), axis=0)[0] * (
                300.0 / fig.dpi
            )

        ellipses = []
        if not dont_resize_actively:

            def update_width_height(event):
                dist = axes2pt()
                for e, radius in ellipses:
                    e.width, e.height = 2.0 * radius * dist

            fig.canvas.mpl_connect("resize_event", update_width_height)
            ax.callbacks.connect("xlim_changed", update_width_height)
            ax.callbacks.connect("ylim_changed", update_width_height)

        def legend_circle_handler(
            legend, orig_handle, xdescent, ydescent, width, height, fontsize
        ):
            w, h = 2.0 * orig_handle.get_radius() * axes2pt()
            e = Ellipse(
                xy=(0.5 * width - 0.5 * xdescent, 0.5 * height - 0.5 * ydescent),
                width=w,
                height=w,
            )
            ellipses.append((e, orig_handle.get_radius()))
            return e

        return {Circle: HandlerPatch(patch_func=legend_circle_handler)}


    def make_legend_circles_for(sizes, scale=1.0, **kw):
        return [Circle((0, 0), radius=(s / scale) ** 0.5, **kw) for s in sizes]


    def add_legend(ax, bus_factor, branch_factor):

        handles = []
        labels = []
        for s in (0.1, 0.5, 1):
            handles.append(
                plt.Line2D([0], [0], color="rosybrown", linewidth=s * 1e3 / branch_factor)
            )
            labels.append(f"{s} GW")
        l1 = ax.legend(
            handles,
            labels,
            loc="upper left",
            bbox_to_anchor=(0, 0),
            frameon=False,
            labelspacing=0.8,
            handletextpad=1.5,
            title="HVAC Line Capacity",
        )
        ax.add_artist(l1)

        handles = []
        labels = []
        for s in (2, 5, 10):
            handles.append(
                plt.Line2D(
                    [0], [0], color="darkseagreen", linewidth=s * 1 / branch_factor
                )
            )
            labels.append(f"{s} GW")


        handles = []
        labels = []
        if "Load" in n.carriers.index:
            n.carriers = n.carriers.drop("Load")
        for name, carrier in n.carriers.iterrows():
            handles.append(
                plt.Line2D(
                    [0], [0], color=carrier.color, marker="o", markersize=8, linewidth=0
                )
            )
            labels.append(carrier.nice_name)
        l3 = ax.legend(
            handles,
            labels,
            loc="upper center",
            bbox_to_anchor=(0.58, -0.0),  # bbox_to_anchor=(0.72, -0.05),
            handletextpad=0.0,
            columnspacing=0.5,
            ncol=2,
            title="Technology",
            frameon=False,
        )
        ax.add_artist(l3)

        circles = [1, 0.5, 0.1]
        handles = make_legend_circles_for(circles, scale=bus_factor, facecolor="lightgray")
        labels = [f"{int(s/0.1)} MW" for s in circles]
        l4 = ax.legend(
            handles,
            labels,
            loc="upper left",
            bbox_to_anchor=(0.82, 0.0),
            frameon=False,
            labelspacing=1.5,
            title="Generation",
            handler_map=make_handler_map_to_scale_circles_as_in(ax, True),
        )
        ax.add_artist(l4)


    def plot_network2(n, fn=None):

        bus_factor = 1e5
        branch_factor = 1e2

        fields = ["bus", "carrier", "p_nom"]
        pie_components = pd.concat(
            [
                n.generators.loc[n.generators.carrier != "load", fields],
                n.storage_units[fields],
            ]
        )
        bus_sizes = pie_components.groupby(["bus", "carrier"]).p_nom.sum() / bus_factor

        def clip(df, thres=0.0):
            return df.where(df > thres, other=0.0)

        line_widths = clip(n.lines.s_nom) / branch_factor
        link_widths = clip(n.links.p_nom) / branch_factor
        #line_widths_opt = clip(n.lines.s_nom_opt) / branch_factor

        fig, ax = plt.subplots(
            figsize=(11, 11), subplot_kw={"projection": ccrs.PlateCarree()}
        )

        n.plot(
            ax=ax,
            bus_sizes=bus_sizes,
            color_geomap=None,
            bus_alpha=0.7,
            line_colors="#dddddd",
        )

        n.plot(
            ax=ax,
            geomap=False,
            bus_sizes=0,
            line_widths=line_widths,
            link_widths=link_widths,
            color_geomap=None,
        )

        add_legend(ax, bus_factor, branch_factor)

        if fn is not None:
            plt.savefig(fn, bbox_inches="tight")
            
            
    plot_network2(n, fn=os.path.join(os.getcwd(), f"original_network_{scenario}"))


    if hasattr(n,'objective'):
        total_costs = n.objective + n.objective_constant
        print(round(total_costs/1e9, 2), "Billion€/year")


    # EXPORT AS CSV and netcdf
    path = os.path.join(os.getcwd(), "example-pypsa", f"solved_network_{scenario}")
    n.export_to_csv_folder(path)
    path_nc = os.path.join(os.getcwd(), "example-pypsa", f"solved_network_{scenario}.nc")
    n.export_to_netcdf(path_nc)

