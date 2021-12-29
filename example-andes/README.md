# exmaple-andes

ANDES is a Python-based free software package for power system simulation, control and analysis. It establishes a unique hybrid symbolic-numeric framework for modeling differential algebraic equations (DAEs) for numerical analysis.

See https://docs.andes.app/en/stable/ for installation, usage and examples.

## Run the example

With the `power-flow-exercise` repository cloned and ANDES installed, you can run the example by executing the following command:

```bash
    cd andes-exercise
    python3 andes-exercise.py
```

## Results

### Performance

The load, run, and report time are the average of 100 runs:

- MATPOWER .m case load time: 98.991 ms
- Solve time: 5.019 ms
- Output report time: 2.674 ms

## Comparison with MATPOWER results


              v_ang      v_mag
count  7.300000e+01  73.000000
mean   2.270643e-04   0.000191
std    1.430270e-04   0.000170
min    1.795241e-20   0.000000
25%    1.095038e-04   0.000000
50%    2.023045e-04   0.000200
75%    3.539543e-04   0.000345
max    4.900276e-04   0.000476