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
std(powersystems.V - matpower.V) = 0.015236205131202447
std(powersystems.gen - matpower.gen) = 11.97074542784354
std(powersystems.load - matpower.load) = 0.21226371552333712

std(abs.(powersystems.V - matpower.V)) = 0.014277239790601925
std(abs.(powersystems.gen - matpower.gen)) = 10.899848476857096
std(abs.(powersystems.load - matpower.load)) = 0.2122637155233371

                ┌                                        ┐
   [0.0 , 0.01) ┤████████████████████████████████████  64
   [0.01, 0.02) ┤██▊ 5
   [0.02, 0.03) ┤  0
   [0.03, 0.04) ┤  0
   [0.04, 0.05) ┤▌ 1
   [0.05, 0.06) ┤▌ 1
   [0.06, 0.07) ┤  0
   [0.07, 0.08) ┤▌ 1
   [0.08, 0.09) ┤▌ 1
                └                                        ┘
                                  Voltage
                ┌                                        ┐
   [ 0.0, 10.0) ┤████████████████████████████████████  62
   [10.0, 20.0) ┤██▊ 5
   [20.0, 30.0) ┤█▋ 3
   [30.0, 40.0) ┤  0
   [40.0, 50.0) ┤█▎ 2
   [50.0, 60.0) ┤▌ 1
                └                                        ┘
                                Generation
              ┌                                        ┐
   [0.0, 0.2) ┤████████████████████████████████████  70
   [0.2, 0.4) ┤  0
   [0.4, 0.6) ┤  0
   [0.6, 0.8) ┤  0
   [0.8, 1.0) ┤  0
   [1.0, 1.2) ┤█▌ 3
              └                                        ┘
                                 Load

    ┌                                        ┐
     ┬┐                                 ╷
     │├─────────────────────────────────┤
     ┴┘                                 ╵
    └                                        ┘
     0                0.045              0.09
                      Voltage
    ┌                                        ┐
     ┬┐                               ╷
     │├───────────────────────────────┤
     ┴┘                               ╵
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
std(powersystems.from - matpower.from) = 15.15287848616078
std(powersystems.to - matpower.to) = 23.94424378225801
std(powersystems.loss - matpower.loss) = 42.762907563954535

std(abs.(powersystems.from - matpower.from)) = 13.500391116956802
std(abs.(powersystems.to - matpower.to)) = 21.505032113005313
std(abs.(powersystems.loss - matpower.loss)) = 42.751605619079534

                  ┌                                        ┐
   [  0.0,  20.0) ┤███████████████████████████████████  108
   [ 20.0,  40.0) ┤█▉ 6
   [ 40.0,  60.0) ┤█▍ 4
   [ 60.0,  80.0) ┤▍ 1
   [ 80.0, 100.0) ┤▍ 1
                  └                                        ┘
                                     From
                ┌                                        ┐
   [ 0.0, 10.0) ┤████████████████████████████████████  88
   [10.0, 20.0) ┤██▏ 5
   [20.0, 30.0) ┤██▌ 6
   [30.0, 40.0) ┤██▏ 5
   [40.0, 50.0) ┤██▊ 7
   [50.0, 60.0) ┤▍ 1
   [60.0, 70.0) ┤▊ 2
   [70.0, 80.0) ┤█▎ 3
   [80.0, 90.0) ┤█▎ 3
                └                                        ┘
                                    To
                  ┌                                        ┐
   [  0.0,  50.0) ┤███████████████████████████████████  108
   [ 50.0, 100.0) ┤██▊ 9
   [100.0, 150.0) ┤  0
   [150.0, 200.0) ┤  0
   [200.0, 250.0) ┤  0
   [250.0, 300.0) ┤▉ 3
                  └                                        ┘
                                     Loss

    ┌                                        ┐
     ┬─┐                                    ╷
     │ ├────────────────────────────────────┤
     ┴─┘                                    ╵
    └                                        ┘
     0                 45                  90
                       From
    ┌                                        ┐
     ┬─────┐                               ╷
     │     ├───────────────────────────────┤
     ┴─────┘                               ╵
    └                                        ┘
     0                 45                  90
                        To
    ┌                                        ┐
     ┬─┐                               ╷
     │ ├───────────────────────────────┤
     ┴─┘                               ╵
    └                                        ┘
     0                 150                300
                       Loss
```
