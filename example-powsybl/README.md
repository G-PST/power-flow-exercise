This is a fork of https://github.com/powsybl/powsybl-benchmark in which

- the case case9241.mat is added, as well as the class Case9241pegaseNetworkState.java
- annotation @Benchmark are commented in BenchmarkRunner.java to reduce the test to the Pegase case.

Performances results:
The performances result based on 20 runs are:
| | |
| --- | --- |
| **power-flow `BASIC_LF_PARAMTERS`**| 1.456 s stdev 304 ms
| **power-flow `STANDARD_LF_PARAMTERS`**| 2.474 stdev 637 ms

### Install

Install `maven` from a package manager of your choice

```
conda install -c conda-forge maven
```

Run `mvn package`:

```bash
mvn package
```
