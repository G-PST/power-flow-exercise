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
- ```BASIC_LF_PARAMETERS```: which has the closest results to those of MATPOWER and the best performances
- ```STANDARD_LF_PARAMETERS```, and None: which have very similar results. These parameters are considered delivering more realistic results (slack distribution, reactive limits on generators) that have a cost in
## Results
### Comparison with MATPOWER results RTS
With ```BASIC_LF_PARAMETERS```
| | angle | v_mag |
| :---: | :---: | :---: |
| **count** | 73 | 73 |
| **mean** | 2.507553e-07| 0.000139
| **std** | 4.322189e-07 | 0.000102
| **min** | 0.000000e+00 | 0.000000e+00
| **max** | 1.822788e-06 | 0.000476

With ```STANDARD_LF_PARAMETERS``` as well as ```Default```
| | angle | v_mag |
| :---: | :---: | :---: |
**count** | 7.300000e+01 | 73.000000
**mean** | 5.250719e-06 | 0.000286
**std** | 1.217706e-05 | 0.000267
**min** | 0.000000e+00 | 0.000000
**max** | 7.176813e-05 | 0.000994

### Performances test is run on case9241pegase
In the Jupyter notebook the results are also compared with those of MATPOWER. The same kind of observations can be made: BASIC is closer to 
MATPOWER, whild STANDARD and None are very similar.

The performances result based on 20 runs are:
| | |
| --- | --- |
| **loading** | 1.44 s ± 353 ms
| **power-flow ```BASIC_LF_PARAMTERS```**| 2.33 s ± 441 ms
| **power-flow ```STANDARD_LF_PARAMTERS```**|4.13 s ± 609 ms
| **power-flow ```Default```** | 3.8 s ± 569 ms


The same benchmark was done based on a fork of **powsybl-benchmark** in **java**: ['../example-powsybl']('../example-powsybl/')

The performances results based on 20 runs are:
| | |
| --- | --- |
| **power-flow ```BASIC_LF_PARAMTERS```**| 1.214 s stdev 299 ms
| **power-flow ```STANDARD_LF_PARAMTERS```**| 2.470 stdev 581 ms
