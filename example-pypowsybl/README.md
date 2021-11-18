# example-pypowsybl
The PyPowSyBl project gives access PowSyBl Java framework to Python developers. This Python integration relies on GraalVM to compile Java code to a native library.

## Setup
PyPowSyBl is released on [PyPi](https://pypi.org/project/pypowsybl/).

First, make sure you have an up-to-date version of pip and setuptools:
```bash
pip3 install --upgrade setuptools pip --user
```

Then you can install PyPowSyBl using pip:
```bash
pip3 install pypowsybl --user
```

## Run the example
The PowSyBl importer for MATPOWER files make use `.mat` files. The procedure to make the conversion from `.m` files is explained [here](https://www.powsybl.org/pages/documentation/grid/formats/matpower.html).
The resulting input file is [resources/RTS_GMLC.mat](resources/RTS_GMLC.mat)

The example is then executed in [script/power-flow-exercice.jpynb](script/power-flow-exercice.jpynb)

The script [script/pypowsyblexample](script/pypowsyblexample) contains functions to format the output to enable comparison with [../reference-matpower/bus.csv](../reference-matpower/bus.csv).

Note that the same function for flows is not yet working as the identification of the branches differ significantly from MATPOWER.

## Results
### Performances:
- **load**: 99.3 ms ± 7.11 ms per loop (mean ± std. dev. of 7 runs, 10 loops each)
- **run load flow**: 10.1 ms ± 375 µs per loop (mean ± std. dev. of 7 runs, 100 loops each)

### Comparison with MATPOWER results
To compare the phase, ```slack_angle_delta = - 10.564``` was added. It corresponds to the angle of *bus 121* in MATPOWER results to shift the angle reference as *bus 121* is the slack bus in pypowsybl calculation.


| | angle | v_mag |
| :---: | :---: | :---: |
| **count** | 73 | 73 |
| **mean** | 1.917808e-04| 3.802134e-17 |
| **std** | 3.964262e-04 | 8.111971e-17 |
| **min** | 0.000000e+00 | 0.000000e+00 |
| **max** | 1.000000e-03 | 2.220446e-16