# Expansion exercise with PyPSA

The PyPSA scripts are highly customized and rather a quick output for the
power-flow-exercise. PyPSA's strength are highly generalized and complex workflows
for instance given in:
[PyPSA-Eur](https://github.com/PyPSA/pypsa-eur),
[PyPSA-Eur-Sec](https://github.com/PyPSA/pypsa-eur-sec),
and [PyPSA-Africa/Earth](https://github.com/pypsa-meets-africa/pypsa-africa).
Nevertheless, this repository includes the following files and scripts.
- The `pypsa-test.py` creates outputs of an solved and unsolved network.
- The `pypsa-test.ipynb` is the initial development notebook.
- The `helpers.py` include function that support both, the Jupyter and Python script.
- The `cost.csv` includes all read in/used default costs for the planning study
- The `config.yaml`, shortend from PyPSA-Eur, is used to read in some options/information.

## Requirements
- The `pypsa-test.py` and `pypsa-test.ipynb` require a custom installation of
PyPSA. To run all scripts successfully, a installation of PyPSA from
[PR#332](https://github.com/PyPSA/PyPSA/pull/332) is required that should be
located in `~/example-pypsa/PyPSA`.

Further, to import packages and modules to Jupyter notebook, you need to setup a conda environment. Here we call it `gpst`.

```python
conda create --name gpst
conda install -c conda-forge pypsa pandapower jupyterlab
pip install yaml vresutils==0.3.1
```

Upgrade to pandapower to develop branch

```python
pip install git+git://github.com/e2nIEE/pandapower@develop
```

To  add the kernel for the jupyter notebook

```python
pip install ipykernel
ipython kernel install --user --name=gpst
```

Open the jupyter lab notebook by typing `jupyter lab` in the terminal.