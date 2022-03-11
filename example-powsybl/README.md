This is a fork of https://github.com/powsybl/powsybl-benchmark in which

- the case case9241.mat is added, as well as the class Case9241pegaseNetworkState.java
- annotation @Benchmark are commented in BenchmarkRunner.java to reduce the test to the Pegase case.

## Performances results:
# Simple Load flow
The performances result based on 20 runs are:
| lf paramters                      | results
| ---                               | --- 
| **```ULTRABASIC_LF_PARAMTERS```** | 0.947 s stdev 279 ms
| **```BASIC_LF_PARAMTERS```**      | 1.456 s stdev 304 ms
| **```STANDARD_LF_PARAMTERS```**   | 2.474 s stdev 637 ms

### Install

Install `maven` from a package manager of your choice

```
$ conda install -c conda-forge maven
```

Run `mvn package`:

```bash
$ mvn clean verify
$ mvn package
```

Execute BenchmarkRunner class:

```bash
$ java -jar target/power-flow-exercice-1.0.0-SNAPSHOT.jar
```
