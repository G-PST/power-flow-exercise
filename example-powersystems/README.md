# example-powersystems

### Setup

- Install [Julia](https://julialang.org/downloads/)
- Run the following in a terminal:

  ```
  git clone https://github.com/G-PST/power-flow-exercise
  cd power-flow-exercise/PowerSystemsExample
  julia --project -e "using Pkg; Pkg.instantiate()"
  julia --project
  ```

### Performance benchmarks

Benchmarks for loading the system, solving the model, and writing the results:

```julia
julia> using PowerSystemsExample

julia> using BenchmarkTools

julia>  @btime load_solve_output()
  91.558 ms (770684 allocations: 42.55 MiB)
```

```julia
julia>  @benchmark load_solve_output()
BenchmarkTools.Trial: 50 samples with 1 evaluation.
 Range (min … max):   89.397 ms … 112.019 ms  ┊ GC (min … max): 0.00% … 10.47%
 Time  (median):     101.321 ms               ┊ GC (median):    8.85%
 Time  (mean ± σ):   100.588 ms ±   4.620 ms  ┊ GC (mean ± σ):  7.65% ±  3.63%

                           ▄█ ▄▄   ▄█▄  █   ▁ ▁
  ▆▆▁▁▆▁▆▁▆▆▁▁▆▁▁▁▁▁▆▁▁▁▆▆▁██▆██▁▆▆███▁▆█▆▆▁█▁█▁▆▁▁▁▆▁▁▁▁▁▁▁▁▁▆ ▁
  89.4 ms          Histogram: frequency by time          112 ms <

 Memory estimate: 42.55 MiB, allocs estimate: 770684.

```

**Benchmarks for loading the system**:

```julia
julia>  @benchmark load()
BenchmarkTools.Trial: 62 samples with 1 evaluation.
 Range (min … max):  75.334 ms … 92.629 ms  ┊ GC (min … max): 0.00% … 14.06%
 Time  (median):     77.371 ms              ┊ GC (median):    0.00%
 Time  (mean ± σ):   82.043 ms ±  6.286 ms  ┊ GC (mean ± σ):  6.64% ±  6.63%

   █▄ ▆                                          ▃ ▁  ▁
  ▇██▇█▇▁▄▄▁▁▁▁▄▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▄▁▆█▆█▆▄█▆▆▄▄▁▄ ▁
  75.3 ms         Histogram: frequency by time        90.6 ms <

 Memory estimate: 24.93 MiB, allocs estimate: 610377.
```

**Benchmarks for solving the model**:

```julia
julia>  @benchmark solve(system) setup=(system = load())
BenchmarkTools.Trial: 52 samples with 1 evaluation.
 Range (min … max):  12.773 ms … 24.979 ms  ┊ GC (min … max):  0.00% … 44.28%
 Time  (median):     13.300 ms              ┊ GC (median):     0.00%
 Time  (mean ± σ):   15.241 ms ±  4.303 ms  ┊ GC (mean ± σ):  12.50% ± 17.14%

  ▁█▄ ▄
  █████▁▄▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁█▆ ▁
  12.8 ms         Histogram: frequency by time        24.7 ms <

 Memory estimate: 9.45 MiB, allocs estimate: 155346.
```

**Benchmarks for writing the results**:

```julia
julia> @benchmark output(res, PowerSystemsExample.RTS_GMLC_MATPOWER_FILENAME) setup = (res = solve(load()))
BenchmarkTools.Trial: 20 samples with 1 evaluation.
 Range (min … max):  682.315 μs … 8.338 ms  ┊ GC (min … max):  0.00% … 89.24%
 Time  (median):       1.078 ms             ┊ GC (median):     0.00%
 Time  (mean ± σ):     2.049 ms ± 2.481 ms  ┊ GC (mean ± σ):  50.03% ± 32.28%

  ▅ ██
  █▅██▅▁▁▁▁▅▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▅▁▁▁▁▁▅▁▁▅ ▁
  682 μs          Histogram: frequency by time        8.34 ms <

 Memory estimate: 8.16 MiB, allocs estimate: 4896.
```

### Validation

```julia
julia> compare_v_gen_load()
std(powersystems.V - matpower.V) = 3.474609089123329e-8
std(real.(powersystems.V) - real.(matpower.V)) = 1.8293489061758463e-8
std(imag.(powersystems.V) - imag.(matpower.V)) = 2.9540465300485174e-8
std(powersystems.gen - matpower.gen) = 2.1221046360035455e-6
std(real.(powersystems.gen) - real.(matpower.gen)) = 1.7998536925033516e-7
std(imag.(powersystems.gen) - imag.(matpower.gen)) = 2.114458170076571e-6
std(powersystems.load - matpower.load) = 0.21064623072269945
std(real.(powersystems.load) - real.(matpower.load)) = 0.0
std(imag.(powersystems.load) - imag.(matpower.load)) = 0.21064623072269945

std(abs.(powersystems.V - matpower.V)) = 1.625731086313144e-8
std(abs.(powersystems.gen - matpower.gen)) = 1.7129545896898402e-6
std(abs.(powersystems.load - matpower.load)) = 0.2106462307226994
────────────────────────────────────────────────────────────────
                                      Voltage
                    ┌                                        ┐
   [0.0   , 1.0e-8) ┤███████████████████████▍ 11
   [1.0e-8, 2.0e-8) ┤███████████████████▏ 9
   [2.0e-8, 3.0e-8) ┤█████████████████████████████▋ 14
   [3.0e-8, 4.0e-8) ┤███████████████████████████████▊ 15
   [4.0e-8, 5.0e-8) ┤████████████████████████████████████  17
   [5.0e-8, 6.0e-8) ┤████████████▋ 6
   [6.0e-8, 7.0e-8) ┤██▎ 1
                    └                                        ┘
────────────────────────────────────────────────────────────────
                                    Generation
                    ┌                                        ┐
   [0.0   , 1.0e-6) ┤████████████████████████████████████  47
   [1.0e-6, 2.0e-6) ┤███▏ 4
   [2.0e-6, 3.0e-6) ┤████▋ 6
   [3.0e-6, 4.0e-6) ┤██████▎ 8
   [4.0e-6, 5.0e-6) ┤██████▎ 8
                    └                                        ┘
────────────────────────────────────────────────────────────────
                                 Load
              ┌                                        ┐
   [0.0, 0.2) ┤████████████████████████████████████  70
   [0.2, 0.4) ┤  0
   [0.4, 0.6) ┤  0
   [0.6, 0.8) ┤  0
   [0.8, 1.0) ┤  0
   [1.0, 1.2) ┤█▌ 3
              └                                        ┘
────────────────────────────────────────────────────────────────
                      Voltage
    ┌                                        ┐
     ╷        ┌──────┬─────────┐           ╷
     ├────────┤      │         ├───────────┤
     ╵        └──────┴─────────┘           ╵
    └                                        ┘
     0               3.5e-8            7.0e-8
────────────────────────────────────────────────────────────────
                    Generation
    ┌                                        ┐
     ┬─────────────────────┐                ╷
     │                     ├────────────────┤
     ┴─────────────────────┘                ╵
    └                                        ┘
     0               2.5e-6            5.0e-6
────────────────────────────────────────────────────────────────
                       Load
    ┌                                        ┐
     ┐                   ╷
     ├───────────────────┤
     ┘                   ╵
    └                                        ┘
     0                  1                   2
────────────────────────────────────────────────────────────────

```

```julia
julia> compare_from_to_loss()
compare_from_to_loss()
std(powersystems.from - matpower.from) = 12.356407430100854
std(powersystems.to - matpower.to) = 21.50003909965975
std(powersystems.loss - matpower.loss) = 42.34182353817387

std(abs.(powersystems.from - matpower.from)) = 12.0929882641272
std(abs.(powersystems.to - matpower.to)) = 20.57463646354224
std(abs.(powersystems.loss - matpower.loss)) = 42.336233562612655
────────────────────────────────────────────────────────────────
                  ┌                                        ┐
   [  0.0,  20.0) ┤███████████████████████████████████  114
   [ 20.0,  40.0) ┤▋ 2
   [ 40.0,  60.0) ┤▋ 2
   [ 60.0,  80.0) ┤▍ 1
   [ 80.0, 100.0) ┤▍ 1
                  └                                        ┘
                                     From
────────────────────────────────────────────────────────────────
                ┌                                        ┐
   [ 0.0, 10.0) ┤████████████████████████████████████  98
   [10.0, 20.0) ┤▍ 1
   [20.0, 30.0) ┤▋ 2
   [30.0, 40.0) ┤███▍ 9
   [40.0, 50.0) ┤▍ 1
   [50.0, 60.0) ┤▍ 1
   [60.0, 70.0) ┤▋ 2
   [70.0, 80.0) ┤█▊ 5
   [80.0, 90.0) ┤▍ 1
                └                                        ┘
                                    To
────────────────────────────────────────────────────────────────
                  ┌                                        ┐
   [  0.0,  50.0) ┤███████████████████████████████████  108
   [ 50.0, 100.0) ┤██▊ 9
   [100.0, 150.0) ┤  0
   [150.0, 200.0) ┤  0
   [200.0, 250.0) ┤  0
   [250.0, 300.0) ┤▉ 3
                  └                                        ┘
                                     Loss
────────────────────────────────────────────────────────────────
    ┌                                        ┐
     ┐                                      ╷
     ├──────────────────────────────────────┤
     ┘                                      ╵
    └                                        ┘
     0                 45                  90
                       From
────────────────────────────────────────────────────────────────
    ┌                                        ┐
     ┐                                     ╷
     ├─────────────────────────────────────┤
     ┘                                     ╵
    └                                        ┘
     0                 45                  90
                        To
────────────────────────────────────────────────────────────────
    ┌                                        ┐
     ┬┐                                 ╷
     │├─────────────────────────────────┤
     ┴┘                                 ╵
    └                                        ┘
     0                 150                300
                       Loss
────────────────────────────────────────────────────────────────

```
