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
The PowSyBl importer for MATPOWER files make use `.mat` files. The procedure to make the conversion from `.m` is explained [here](https://www.powsybl.org/pages/documentation/grid/formats/matpower.html).
The resulting input file is [resources/RTS_GMLC.mat](resources/RTS_GMLC.mat)

The script [script/pypowsyblexample.py](script/pypowsyblexample.py) contains functions to format the output to enable comparison with [../reference-matpower/results/bus.csv](../reference-matpower/results/bus.csv).

The example is then executed in [power-flow-exercice.ipynb](power-flow-exercice.ipynb)

Various Load-flow parameters are benchmarked:
- ```ULTRABASIC_LF_PARAMETERS```: which has the closest results to those of MATPOWER and the best performances (note that this parameter is meaninless when considering the performances as there is very little effort to converge quickly when the load flow is initiated with the expected result!)
- ```BASIC_LF_PARAMETERS```: Same as before but starting with a flat
- ```STANDARD_LF_PARAMETERS```: and None: which have very similar results. These parameters are considered delivering more realistic results (slack distribution, reactive limits on generators) that have a cost in
## Results
### Comparison with MATPOWER results on RTS
|           | ULTRABASIC: angle | ULTRABASIC: v_mag | BASIC: angle  | BASIC: v_mag  | STANDARD: angle   | STANDARD: v_mag
| :---:     | :---:             | :---:             | :---:         | :---:         | :---:             | :---:
| **count** | 73                | 73                | 73            | 73            | 73                | 73
| **mean**  | 1.16e-16          | 4.47e-14          | 2.50e-07      | 1.39e-04      | 5.25e-06          | 2.86e-04
| **std**   | 1.77e-16          | 2.20e-14          | 4.32e-07      | 1.02e-04      | 1.21e-05          | 2.67e-04
| **min**   | 0                 | 0                 | 0             | 0             | 0                 | 0
| **max**   | 8.88-16           | 8.17e-14          | 1.82-06       | 4.76e-04      | 7.17e-05          | 9.94e-04


### Performances test is run on case9241pegase
In the Jupyter notebook the results are also compared with those of MATPOWER. The same kind of observations can be made: BASIC is closer to
MATPOWER, whild STANDARD and None are very similar.

The performances result based on 20 runs are:
| process                                       | results
| ---                                           | ---
| loading                                       | 1.32 s ± 317
| power-flow ```ULTRABASIC_LF_PARAMTERS```      | 2.26 s ± 337 ms
| power-flow ```BASIC_LF_PARAMTERS```           | 2.71 s ± 337 ms
| power-flow ```STANDARD_LF_PARAMTERS```        | 4.05 s ± 760 ms
| power-flow ```Default```                      | 2.98 s ± 506 ms

### Performances test is security analysis on case9241pegase


# Java version
The same benchmark was done based on a fork of **powsybl-benchmark** in **java**: ['../example-powsybl']('../example-powsybl/')

## Simple Load flow performances
The performances result based on 20 runs are:
| lf paramters                      | results
| ---                               | ---
| **```ULTRABASIC_LF_PARAMTERS```** | 0.947 s stdev 279 ms
| **```BASIC_LF_PARAMTERS```**      | 1.456 s stdev 304 ms
| **```STANDARD_LF_PARAMTERS```**   | 2.474 s stdev 637 ms

## Simple Load flow performances
Performances result for 1000 contingencies secuirity analysis:
| Load Flow paramters           | results
| ---                           | ---
| ```BASIC_LF_PARAMTERS```      | 264.824 s ie **264 ms / contingency**
| ```STANDARD_LF_PARAMTERS```   | 427.837 s ie **427 ms / contingency**


