# PowerSystemsExample

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

julia> @btime load_solve_output()
  81.316 ms (813244 allocations: 44.14 MiB)
```

```julia
julia> @benchmark load_solve_output()
BenchmarkTools.Trial: 57 samples with 1 evaluation.
 Range (min … max):  81.106 ms … 94.895 ms  ┊ GC (min … max): 0.00% … 11.93%
 Time  (median):     92.188 ms              ┊ GC (median):    0.00%
 Time  (mean ± σ):   87.900 ms ±  5.560 ms  ┊ GC (mean ± σ):  6.34% ±  6.14%

    ▁  ▁▆                                             █▁▁
  ▇▇█▆▄██▁▁▁▆▄▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▄▁▁▁▄▄▇███▇▆▄▄ ▁
  81.1 ms         Histogram: frequency by time        94.3 ms <

 Memory estimate: 44.14 MiB, allocs estimate: 813244.
```

**Benchmarks for loading the system**:

```julia
julia> @benchmark load()
BenchmarkTools.Trial: 71 samples with 1 evaluation.
 Range (min … max):  63.689 ms … 84.467 ms  ┊ GC (min … max): 0.00% … 18.04%
 Time  (median):     67.277 ms              ┊ GC (median):    0.00%
 Time  (mean ± σ):   71.132 ms ±  6.847 ms  ┊ GC (mean ± σ):  5.46% ±  7.67%

         ▃▅█▃▂
  ▅▄▄▄▁▄▇██████▁▄▄▁▁▁▁▁▅▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▄▁▁▁▁▁▄▁▁▅▁▁▄▄▇▄▄█▄▇▁▄ ▁
  63.7 ms         Histogram: frequency by time        83.6 ms <

 Memory estimate: 25.73 MiB, allocs estimate: 644172.
```

**Benchmarks for solving the model**:

```julia
julia> @benchmark solve(system) setup=(system = load())
BenchmarkTools.Trial: 57 samples with 1 evaluation.
 Range (min … max):  11.921 ms … 31.811 ms  ┊ GC (min … max):  0.00% … 51.55%
 Time  (median):     13.158 ms              ┊ GC (median):     0.00%
 Time  (mean ± σ):   15.247 ms ±  5.281 ms  ┊ GC (mean ± σ):  12.22% ± 17.44%

     █▁
  ▇▅████▃▁▅▁▃▁▄▁▁▁▁▁▁▁▃▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▃▃▁▁▃▁▁▃▁▁▃▁▃ ▁
  11.9 ms         Histogram: frequency by time        30.5 ms <

 Memory estimate: 10.25 MiB, allocs estimate: 164222.
```

**Benchmarks for writing the results**:

```julia
julia> @benchmark output(results) setup = (results = solve(system))
BenchmarkTools.Trial: 305 samples with 1 evaluation.
 Range (min … max):  768.933 μs … 31.928 ms  ┊ GC (min … max):  0.00% …  0.00%
 Time  (median):     890.851 μs              ┊ GC (median):     0.00%
 Time  (mean ± σ):     1.964 ms ±  3.382 ms  ┊ GC (mean ± σ):  45.92% ± 25.82%

  █▃▁
  ███▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▄▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▁▄▄▅▇▇▇▆▄▆ ▆
  769 μs        Histogram: log(frequency) by time      11.5 ms <

 Memory estimate: 8.16 MiB, allocs estimate: 4785.
```

### Validation

```julia
julia> compare_v_gen_load()
std(powersystems.V - matpower.V) = 1.0846725152604795
std(powersystems.gen - matpower.gen) = 11.963799430340854
std(powersystems.load - matpower.load) = 0.21226371552333712

std(abs.(powersystems.V - matpower.V)) = 0.6501915632257282
std(abs.(powersystems.gen - matpower.gen)) = 10.89340864013202
std(abs.(powersystems.load - matpower.load)) = 0.2122637155233371

    ┌                                        ┐
     ╷         ┌─────────┬───┐  ╷
     ├─────────┤         │   ├──┤
     ╵         └─────────┴───┘  ╵
    └                                        ┘
     0                 1.5                  3
                      Voltage
    ┌                                        ┐
     ┬─┐                              ╷
     │ ├──────────────────────────────┤
     ┴─┘                              ╵
    └                                        ┘
     0                 30                  60
                    Generation
    ┌                                        ┐
     ┐                   ╷
     ├───────────────────┤
     ┘                   ╵
    └                                        ┘
     0                  1                   2
                       Load
```

```julia
julia> compare_from_to_loss()
propertynames(powersystems) = [:line_name, :bus_from, :bus_to, :P_from_to, :Q_from_to, :P_to_from, :Q_to_from, :P_losses, :Q_losses]
propertynames(matpower) = [:branch_n, :from_bus_inj_p, :from_bus_inj_q, :to_bus_inj_p, :to_bus_inj_q, :loss_p, :loss_q]
std(powersystems.from - matpower.from) = 167.69767501921993
std(powersystems.to - matpower.to) = 215.32787080252334
std(powersystems.loss - matpower.loss) = 112.16819358651611

std(abs.(powersystems.from - matpower.from)) = 145.98373012164475
std(abs.(powersystems.to - matpower.to)) = 156.48583073998023
std(abs.(powersystems.loss - matpower.loss)) = 78.83015730009632

    ┌                                        ┐
     ╷        ┌──────┬────┐            ╷
     ├────────┤      │    ├────────────┤
     ╵        └──────┴────┘            ╵
    └                                        ┘
     100               450                800
                       From
    ┌                                        ┐
     ╷   ┌───────┬──────┐                   ╷
     ├───┤       │      ├───────────────────┤
     ╵   └───────┴──────┘                   ╵
    └                                        ┘
     0                 350                700
                        To
    ┌                                        ┐
     ╷  ┌───────┬─────┐                ╷
     ├──┤       │     ├────────────────┤
     ╵  └───────┴─────┘                ╵
    └                                        ┘
     0                 200                400
                       Loss
```
