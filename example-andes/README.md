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

|       | v_ang    | v_mag    |
|-------|----------|----------|
| count | 7.30E+01 | 73       |
| mean  | 2.27E-04 | 0.000191 |
| std   | 1.43E-04 | 0.00017  |
| min   | 1.80E-20 | 0        |
| 25%   | 1.10E-04 | 0        |
| 50%   | 2.02E-04 | 0.0002   |
| 75%   | 3.54E-04 | 0.000345 |
| max   | 4.90E-04 | 0.000476 |