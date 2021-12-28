# Expansion excersise with pypsa

We use the `pypsa-test.ipynb` as initial development notebook. 


TODO's:

- [x] Set up notebook and local PyPSA version for PR's (pandapower importer is in beta and requires changes)
- [ ] Find out why powerflow is not converging
- [ ] Where is the timeseries? Now we just have one snapshot. Are we looking beyond one snapshot?
- [ ] Optional. Rename generators according to carrier
- [ ] Add carrier such as ["wind"] for wind plants for all assets
- [ ] Add default cost from pypsa-eur
- [ ] Add constraints
- [ ] Test .lopf (linear optimal power flow with investment and dispatch optimization)
- [ ] Perform below described case studies


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

