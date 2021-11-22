# MatpowerReference

- [RTS-GMLC matpower data (with dcline removed)](./RTS_GMLC.m)

### Setup

- Run MATPOWER
- Install [Julia](https://julialang.org/downloads/)
- Run the following in a terminal:

  ```bash
  git clone https://github.com/G-PST/power-flow-exercise
  cd MatpowerReference
  julia --project -e "using Pkg; Pkg.instantiate()"
  julia --project parse-matpower-results.jl
  ```

  The output is generated in the results folder:

  ```bash
  tree results
  ```

  ```
  results
  ├── bus.csv
  └── flow.csv
  ```

  ```bash
  head results/bus.csv
  ```

  ```
  bus_n,v_mag,v_ang,p_gen,q_gen,p_load,q_load,λ_p,λ_q
  101.0,1.047,-8.575,168.0,10.21,108.0,22.0,37.993,
  102.0,1.047,-8.635,168.0,5.14,97.0,20.0,38.008,
  103.0,1.011,-7.98,,,180.0,37.0,38.083,0.514
  104.0,1.017,-10.745,,,74.0,15.0,38.938,0.265
  105.0,1.035,-10.928,,,71.0,14.0,38.766,0.047
  106.0,1.032,-13.158,,,136.0,28.0,39.401,-0.034
  107.0,1.05,-3.989,355.0,49.51,125.0,25.0,36.258,
  108.0,1.017,-9.343,,,171.0,35.0,38.279,0.322
  109.0,1.027,-8.46,,,175.0,36.0,38.194,0.183
  ```

  ```bash
  head results/flow.csv
  ```

  ```
  branch_n,from_bus_inj_p,from_bus_inj_q,to_bus_inj_p,to_bus_inj_q,loss_p,loss_q
  1.0,101.0,102.0,7.84,-26.64,-7.84,-23.87
  2.0,101.0,103.0,-0.58,14.64,0.73,-20.07
  3.0,101.0,105.0,52.74,0.2,-52.18,-0.54
  4.0,102.0,104.0,34.94,13.74,-34.5,-15.66
  5.0,102.0,106.0,43.9,-4.73,-43.02,2.49
  6.0,103.0,109.0,3.67,-15.57,-3.61,12.49
  7.0,103.0,124.0,-184.41,-1.36,185.09,30.13
  8.0,104.0,109.0,-39.5,0.66,39.91,-2.01
  9.0,105.0,110.0,-18.82,-13.46,18.93,11.27
  ```
