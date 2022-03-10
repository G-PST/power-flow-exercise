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

In order to load a grid model from MATPOWER format, use the pandapower converter function `net = pandapower.converter.from_mpc(filepath)`.
Note that filepath must point to a ".mpc" file (".m" is not supported).

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

### Performance

```python
In [1]: from main import *
21:33:26 main INFO failed to import pypsa!

In [2]: timings()
21:33:46 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:33:48 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:33:50 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:33:52 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:33:54 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:33:55 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:33:57 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:33:59 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:34:01 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:34:03 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:34:03 main INFO .mat file loading mean execution time 1.8515627166256308 seconds
21:34:05 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:34:18 main INFO Power flow mean execution time 0.013541021002456546 seconds
21:34:20 pandapower.converter.matpower.from_mpc INFO added fields ['areas', 'bus_name', 'gen_name'] in net._options
21:34:20 main INFO .json output file mean execution time 0.020278214011341333 seconds
```

### Performance of File I/O

Timing of the file I/O operations is shown in the following table.

|            | Format     |  Read        |  Write      |
|------------|------------|--------------|-------------|
|  1000 runs | JSON       |  212.765 s   | 32.147 s    |
|  per run   | JSON       |  212.765 ms  | 32.147 ms   |
|  100 runs  | mpc        |  243 s       | 0.63 s      |
|  per run   | mpc        |  2.43 s      | 6.31 ms     |

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
