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
std(powersystems.V - matpower.V) = 0.016089446824980754
std(real.(powersystems.V) - real.(matpower.V)) = 0.014622362711930513
std(imag.(powersystems.V) - imag.(matpower.V)) = 0.006712436804516485
std(powersystems.gen - matpower.gen) = 10.897897211045988
std(real.(powersystems.gen) - real.(matpower.gen)) = 0.40785445604582554
std(imag.(powersystems.gen) - imag.(matpower.gen)) = 10.890262548038383
std(powersystems.load - matpower.load) = 0.21064623072269945
std(real.(powersystems.load) - real.(matpower.load)) = 0.0
std(imag.(powersystems.load) - imag.(matpower.load)) = 0.21064623072269945

std(abs.(powersystems.V - matpower.V)) = 0.01551730288777533
std(abs.(powersystems.gen - matpower.gen)) = 10.892815283057843
std(abs.(powersystems.load - matpower.load)) = 0.2106462307226994
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                                  Voltage
                ┌                                        ┐
   [0.0 , 0.01) ┤████████████████████████████████████  62
   [0.01, 0.02) ┤██▊ 5
   [0.02, 0.03) ┤█▋ 3
   [0.03, 0.04) ┤  0
   [0.04, 0.05) ┤  0
   [0.05, 0.06) ┤  0
   [0.06, 0.07) ┤  0
   [0.07, 0.08) ┤█▋ 3
                └                                        ┘
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                                Generation
                ┌                                        ┐
   [ 0.0,  5.0) ┤████████████████████████████████████  55
   [ 5.0, 10.0) ┤█▉ 3
   [10.0, 15.0) ┤███▍ 5
   [15.0, 20.0) ┤██▋ 4
   [20.0, 25.0) ┤  0
   [25.0, 30.0) ┤█▉ 3
   [30.0, 35.0) ┤  0
   [35.0, 40.0) ┤  0
   [40.0, 45.0) ┤█▉ 3
                └                                        ┘
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                                 Load
              ┌                                        ┐
   [0.0, 0.2) ┤████████████████████████████████████  70
   [0.2, 0.4) ┤  0
   [0.4, 0.6) ┤  0
   [0.6, 0.8) ┤  0
   [0.8, 1.0) ┤  0
   [1.0, 1.2) ┤█▌ 3
              └                                        ┘
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                      Voltage
    ┌                                        ┐
     ┬──┐                                 ╷
     │  ├─────────────────────────────────┤
     ┴──┘                                 ╵
    └                                        ┘
     0                0.04               0.08
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                    Generation
    ┌                                        ┐
     ┬┐                                ╷
     │├────────────────────────────────┤
     ┴┘                                ╵
    └                                        ┘
     0                 25                  50
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                       Load
    ┌                                        ┐
     ┐                   ╷
     ├───────────────────┤
     ┘                   ╵
    └                                        ┘
     0                  1                   2
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

```

```julia
julia> compare_from_to_loss()
std(powersystems.from - matpower.from) = 19.356021018491624
std(powersystems.to - matpower.to) = 26.681276093826803
std(powersystems.loss - matpower.loss) = 42.83176228389373

std(abs.(powersystems.from - matpower.from)) = 16.57169205823745
std(abs.(powersystems.to - matpower.to)) = 22.984848234424454
std(abs.(powersystems.loss - matpower.loss)) = 42.82669560529537
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                  ┌                                        ┐
   [  0.0,  20.0) ┤███████████████████████████████████  102
   [ 20.0,  40.0) ┤██▋ 8
   [ 40.0,  60.0) ┤█▋ 5
   [ 60.0,  80.0) ┤█▍ 4
   [ 80.0, 100.0) ┤▍ 1
                  └                                        ┘
                                     From
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                  ┌                                        ┐
   [  0.0,  20.0) ┤████████████████████████████████████  99
   [ 20.0,  40.0) ┤█▊ 5
   [ 40.0,  60.0) ┤█▊ 5
   [ 60.0,  80.0) ┤██▌ 7
   [ 80.0, 100.0) ┤█▌ 4
                  └                                        ┘
                                      To
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
                  ┌                                        ┐
   [  0.0,  50.0) ┤███████████████████████████████████  108
   [ 50.0, 100.0) ┤██▊ 9
   [100.0, 150.0) ┤  0
   [150.0, 200.0) ┤  0
   [200.0, 250.0) ┤  0
   [250.0, 300.0) ┤▉ 3
                  └                                        ┘
                                     Loss
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    ┌                                        ┐
     ┬────┐                                 ╷
     │    ├─────────────────────────────────┤
     ┴────┘                                 ╵
    └                                        ┘
     0                 45                  90
                       From
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    ┌                                        ┐
     ┬─────┐                               ╷
     │     ├───────────────────────────────┤
     ┴─────┘                               ╵
    └                                        ┘
     0                 45                  90
                        To
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
    ┌                                        ┐
     ┬─┐                                ╷
     │ ├────────────────────────────────┤
     ┴─┘                                ╵
    └                                        ┘
     0                 150                300
                       Loss
─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────

```
