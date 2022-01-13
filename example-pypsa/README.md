# Expansion excersise with pypsa

- The `pypsa-test.ipynb` is the initial development notebook.
- The final execution script is `pypsa-example.py` which logs detailed information to `log.out`
- The `helpers.py` include function that support both, the Jupyter and Python script.
- The `cost.csv` includes all read in/used default costs for the planning study
- The `config.yaml`, shortend from PyPSA-Eur, is used to read in some options/information.

TODO's:
- [x] Set up notebook and local PyPSA version for PR's (pandapower importer is in beta and requires changes)
- [x] Converging ac-powerflow
- [x] Add default cost from pypsa-eur
- [ ] Add carrier name such as ["wind"] for wind plants
- [ ] Optional. Add technical limits for installations
- [ ] Adjust capital cost of line by defining line length from voltage level and resistance?
- [ ] Add renewable constraint/ CO2 accounting
- [ ] Increase load (reflecting standard load growth, electrification, ...)
      a. Assumptions: only add conductors on existing paths, capital-costs, ...  
      b. One scenario results in a new generation porfolio 
      c. One scenario results in a new generation and transmission portfolio


TEST CASE TODO's:
- [x] Name generator carriers to "OCGT"
- [x] Make all generators, lines extendable
- [x] Add constraints
- [x] Test .lopf (linear optimal power flow with investment and dispatch optimization)
- [x] Send initial expansion results to group


Intended planning exercise: 

1. Start with RTS-GMLC
2. Adjust system requirement
  a. Remove conventional generation (remove coal) / Set RE target
  c. Increase load (reflecting standard load growth, electrification, ...)
3. Optimal expansion planning (PyPSA) 
  a. Assumptions: only add conductors on existing paths, capital-costs, ...  
  b. One scenario results in a new generation porfolio 
  c. One scenario results in a new generation and transmission porfolio
4. Optimal integration planning (Powsybl, Pandapower)
  - enforce DC security constraints
  - results in a N-1 secure, AC feasible (hopefully) network
5. System performance (no new resource)
  - Load flow
  - UC/ED analsysis
  - Production Cost Modeling
  - ...

