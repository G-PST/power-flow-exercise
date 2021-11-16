# Power flow excersise with pandapower

First, we describe the required setup for the exercise. Next, we introduce basic pandapower functions.

Finally, we present the excersise using the [RTS-GMLC](https://github.com/GridMod/RTS-GMLC/tree/v0.2.1/RTS_Data/FormattedData/pandapower)
benchmark power system. We compare the results of the power flow calculation in pandapower to the results of the calculation in MATPOWER.
Furthermore, we present performance metrics for the calculation and file I/O in pandapower.

## Introduction

The official website of pandapower is [pandapower.org](https://pandapower.org/). The project is maintained by the University of Kassel and
the Fraunhofer Institute for Energy Economics and Energy System Technology (IEE). The repository of pandapower on GitHub
is [e2nIEE/pandapower](https://github.com/e2nIEE/pandapower).

### Setting up

You should have Python 3.6 or higher installed. In the following, we describe how to set up pandapower.

#### Using pip (installs master branch)

```
pip install pandapower
```

#### Using git (develop branch)

- Run the following in a terminal:

```
 git clone https://github.com/e2nIEE/pandapower.git
 cd pandapower
 git checkout develop
 pip install -e .
```

### Getting started

To load a pandapower grid model, use the pandapower function `net = pandapower.from_json(filepath)`.

In order to create an element, use one of the pandapower create functions, for example `create_bus`, `create_ext_grid`, `create_gen`:

```
 import pandapower as pp
 net = pp.create_empty_network()
 bus0 = pp.create_bus(net, vn_kv=110., name="bus0")
 bus1 = pp.create_bus(net, vn_kv=20., name="bus1")
 bus2 = pp.create_bus(net, vn_kv=20., name="bus2")
 ext_grid = pp.create_ext_grid(net, bus=bus0, vm_pu=1.02, va_degree=0.)
 gen = pp.create_gen(net, bus=bus2, p_mw=10., vm_pu=1.02, name="gen1")
 load = pp.create_load(net, bus=bus2, p_mw=0.5, q_mvar=0.2, name="load1")
 trafo = pp.create_transformer(net, hv_bus=bus0, lv_bus=bus1, std_type="25 MVA 110/20 kV", name="trafo1")
 line = pp.create_line(net, from_bus=bus1, to_bus=bus2, length_km=0.5, std_type="243-AL1/39-ST1A 20.0")
```

To run a power flow calculation, use the pandapower function `pp.runpp(net)`. The results are stored in the `net.res_bus`, `net.res_line`,
`net.res_trafo`, etc. attributes.

To save the pandapower net, use the pandapower function `pp.to_json(net, filepath)`

For further introduction to pandapower, see the [pandapower documentation](https://pandapower.readthedocs.io/en/latest/). Examples of
specific use-cases with pandapower can be found in the [pandapower tutorials](https://github.com/e2nIEE/pandapower/tree/develop/tutorials),
either on GitHub or in your local installation of pandapower. In order to open tutorials in juypter notebooks locally on your machine, you
can execude the following code in the console:

```
cd <folder with pandapower>/pandapower/tutorials
jupyter notebooks
```

The tutorials will be opened in a browser window.

## Example using the RTS-GMLC benchmark power system

### Performance of File I/O

Timing of the file I/O operations is shown in the following table.

|            |  Read        |  Write      |
|------------|--------------|-------------|
|  1000 runs |  212.765 s   | 32.147 s    |
|  per run   |  212.765 ms  | 32.147 ms   |

### Performance of load flow calculations

Timing for 1000 calculations: 16.505 seconds (16.505 ms per calculation)

### Comparing results of power flow calculation to MATPOWER

The differences in bus voltage magnitide and angle are shown in the table below.

|       |    diff_vm_pu | diff_va_degree |
|-------|--------------|----------------|
| count |  7.300000e+01 |      73.000000 |
| mean  | -6.624892e-06 |      -0.000005 |
| std   |  2.569213e-04 |       0.000271 |
| min   | -4.757001e-04 |      -0.000482 |
| 25%   | -2.000000e-04 |      -0.000216 |
| 50%   |  2.220446e-16 |      -0.000021 |
| 75%   |  2.000000e-04 |       0.000190 |
| max   |  4.693300e-04 |       0.000482 |
