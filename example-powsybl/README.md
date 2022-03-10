This is a fork of https://github.com/powsybl/powsybl-benchmark in which
- the case case9241.mat is added, as well as the class Case9241pegaseNetworkState.java
- annotation @Benchmark are commented in BenchmarkRunner.java to reduce the test to the Pegase case.

## Performances results:
# Simple Load flow
The performances result based on 20 runs are:
| lf paramters                     | results
| ---                              | --- 
| **```BASIC_LF_PARAMTERS```**     | 1.456 s stdev 304 ms
| **```STANDARD_LF_PARAMTERS```**  | 2.474 s stdev 637 ms

# Security analysis
| lf paramters                     | results
| ---                              | --- 
|**```BASIC_LF_PARAMTERS```**      | 6 ms / contingency
|**```STANDARD_LF_PARAMTERS```**   | 2 ms / contingency
